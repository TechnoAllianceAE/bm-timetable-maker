import { Request, Response, NextFunction } from 'express';
import { PrismaClient } from '@prisma/client';
import { WorkloadMonitorService } from '../services/workloadMonitor';

const prisma = new PrismaClient();
const workloadMonitor = new WorkloadMonitorService();

/**
 * Middleware to validate wellness constraints before timetable operations
 */
export const wellnessConstraintMiddleware = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    // Only apply to timetable modification operations
    if (!req.path.includes('/timetable') || req.method === 'GET') {
      return next();
    }

    const { teacherId, timeSlotId, operation } = req.body;

    if (!teacherId || !timeSlotId) {
      return next(); // Skip if not a teacher assignment
    }

    // Get teacher's current workload and constraints
    const teacher = await prisma.teacher.findUnique({
      where: { id: teacherId },
      include: {
        workloadConfig: true,
        timetableEntries: {
          include: {
            timeSlot: true,
            subject: true
          }
        }
      }
    });

    if (!teacher) {
      return res.status(404).json({
        success: false,
        error: 'Teacher not found'
      });
    }

    // Get the time slot being assigned
    const timeSlot = await prisma.timeSlot.findUnique({
      where: { id: timeSlotId }
    });

    if (!timeSlot) {
      return res.status(404).json({
        success: false,
        error: 'Time slot not found'
      });
    }

    // Validate wellness constraints
    const violations = await validateWellnessConstraints(teacher, timeSlot, operation);

    if (violations.length > 0) {
      const criticalViolations = violations.filter(v => v.severity === 'critical');
      
      if (criticalViolations.length > 0) {
        return res.status(400).json({
          success: false,
          error: 'Wellness constraint violations detected',
          violations: criticalViolations,
          canOverride: false
        });
      }

      // For non-critical violations, allow with warning
      req.wellnessWarnings = violations;
    }

    next();
  } catch (error) {
    console.error('Wellness constraint check error:', error);
    next(); // Continue on error to avoid blocking operations
  }
};

/**
 * Middleware to check workload before substitute assignments
 */
export const substituteWorkloadCheck = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { substituteTeacherId, originalEntryId } = req.body;

    if (!substituteTeacherId || !originalEntryId) {
      return next();
    }

    // Get substitute teacher's current workload
    const currentWorkload = await workloadMonitor.calculateTeacherWorkload(substituteTeacherId);

    // Get original entry details
    const originalEntry = await prisma.timetableEntry.findUnique({
      where: { id: originalEntryId },
      include: {
        timeSlot: true,
        subject: true
      }
    });

    if (!originalEntry) {
      return res.status(404).json({
        success: false,
        error: 'Original timetable entry not found'
      });
    }

    // Check if substitute assignment would violate wellness constraints
    const workloadCheck = await checkSubstituteWorkload(
      substituteTeacherId,
      originalEntry,
      currentWorkload
    );

    if (!workloadCheck.passed) {
      if (workloadCheck.severity === 'critical') {
        return res.status(400).json({
          success: false,
          error: 'Substitute assignment would violate critical wellness constraints',
          violations: workloadCheck.violations,
          canOverride: false
        });
      }

      // Allow with override for non-critical violations
      req.workloadOverride = {
        required: true,
        reason: workloadCheck.violations.map(v => v.message).join('; '),
        violations: workloadCheck.violations
      };
    }

    next();
  } catch (error) {
    console.error('Substitute workload check error:', error);
    next();
  }
};

/**
 * Middleware to update wellness metrics after timetable changes
 */
export const updateWellnessMetrics = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // Store original response.json to intercept successful responses
  const originalJson = res.json;
  
  res.json = function(data: any) {
    // Call original json method
    const result = originalJson.call(this, data);
    
    // Update wellness metrics asynchronously after response
    if (data.success && req.body.teacherId) {
      setImmediate(async () => {
        try {
          await workloadMonitor.calculateTeacherWorkload(req.body.teacherId);
        } catch (error) {
          console.error('Error updating wellness metrics:', error);
        }
      });
    }
    
    return result;
  };

  next();
};

/**
 * Validate wellness constraints for a teacher assignment
 */
async function validateWellnessConstraints(
  teacher: any,
  timeSlot: any,
  operation: string
): Promise<Array<{ type: string; severity: string; message: string }>> {
  const violations = [];
  const config = teacher.workloadConfig;
  const currentEntries = teacher.timetableEntries;

  // Get entries for the same day
  const dayEntries = currentEntries.filter(entry => 
    entry.timeSlot.day === timeSlot.day
  );

  // Check maximum periods per day
  if (operation === 'add' && dayEntries.length >= (config?.maxPeriodsPerDay || 6)) {
    violations.push({
      type: 'max_periods_per_day',
      severity: 'critical',
      message: `Teacher already has maximum periods (${config?.maxPeriodsPerDay || 6}) for ${timeSlot.day}`
    });
  }

  // Check consecutive periods
  if (operation === 'add') {
    const wouldCreateExcessiveConsecutive = checkConsecutivePeriods(
      dayEntries,
      timeSlot,
      config?.maxConsecutivePeriods || 3
    );

    if (wouldCreateExcessiveConsecutive) {
      violations.push({
        type: 'consecutive_periods',
        severity: 'warning',
        message: `Assignment would create more than ${config?.maxConsecutivePeriods || 3} consecutive periods`
      });
    }
  }

  // Check weekly workload
  const weeklyPeriods = currentEntries.length;
  if (operation === 'add' && weeklyPeriods >= (config?.maxPeriodsPerWeek || 30)) {
    violations.push({
      type: 'max_periods_per_week',
      severity: 'critical',
      message: `Teacher already has maximum weekly periods (${config?.maxPeriodsPerWeek || 30})`
    });
  }

  // Check break requirements
  const hasAdequateBreaks = checkBreakRequirements(
    dayEntries,
    timeSlot,
    config?.minBreakBetweenClasses || 10
  );

  if (!hasAdequateBreaks) {
    violations.push({
      type: 'insufficient_breaks',
      severity: 'warning',
      message: `Assignment may not provide adequate break time between classes`
    });
  }

  return violations;
}

/**
 * Check if substitute assignment would violate workload constraints
 */
async function checkSubstituteWorkload(
  substituteTeacherId: string,
  originalEntry: any,
  currentWorkload: any
): Promise<{ passed: boolean; severity?: string; violations: any[] }> {
  const violations = [];

  // Check if substitute already has a class at this time
  const conflictingEntry = await prisma.timetableEntry.findFirst({
    where: {
      teacherId: substituteTeacherId,
      timeSlotId: originalEntry.timeSlotId,
      timetable: {
        status: 'ACTIVE'
      }
    }
  });

  if (conflictingEntry) {
    violations.push({
      type: 'time_conflict',
      severity: 'critical',
      message: 'Substitute teacher already has a class at this time'
    });
  }

  // Check daily workload limits
  const dayOfWeek = originalEntry.timeSlot.day;
  const dailyMetrics = currentWorkload.dailyMetrics[dayOfWeek];
  
  if (dailyMetrics && dailyMetrics.periods >= 6) {
    violations.push({
      type: 'daily_limit',
      severity: 'warning',
      message: 'Substitute teacher already at daily period limit'
    });
  }

  // Check weekly workload
  if (currentWorkload.weeklyMetrics.workloadPercentage > 90) {
    violations.push({
      type: 'weekly_overload',
      severity: 'critical',
      message: 'Substitute teacher is already overloaded this week'
    });
  }

  // Check burnout risk
  if (currentWorkload.burnoutRisk === 'HIGH' || currentWorkload.burnoutRisk === 'CRITICAL') {
    violations.push({
      type: 'burnout_risk',
      severity: 'warning',
      message: 'Substitute teacher is at high burnout risk'
    });
  }

  const criticalViolations = violations.filter(v => v.severity === 'critical');
  
  return {
    passed: violations.length === 0,
    severity: criticalViolations.length > 0 ? 'critical' : 'warning',
    violations
  };
}

/**
 * Helper function to check consecutive periods
 */
function checkConsecutivePeriods(
  dayEntries: any[],
  newTimeSlot: any,
  maxConsecutive: number
): boolean {
  // Sort all entries including the new one by start time
  const allSlots = [...dayEntries.map(e => e.timeSlot), newTimeSlot]
    .sort((a, b) => a.startTime.localeCompare(b.startTime));

  let consecutiveCount = 1;
  let maxFound = 1;

  for (let i = 1; i < allSlots.length; i++) {
    const prevEnd = timeToMinutes(allSlots[i-1].endTime);
    const currentStart = timeToMinutes(allSlots[i].startTime);
    
    // If gap is less than 15 minutes, consider consecutive
    if (currentStart - prevEnd < 15) {
      consecutiveCount++;
      maxFound = Math.max(maxFound, consecutiveCount);
    } else {
      consecutiveCount = 1;
    }
  }

  return maxFound > maxConsecutive;
}

/**
 * Helper function to check break requirements
 */
function checkBreakRequirements(
  dayEntries: any[],
  newTimeSlot: any,
  minBreakMinutes: number
): boolean {
  const allSlots = [...dayEntries.map(e => e.timeSlot), newTimeSlot]
    .sort((a, b) => a.startTime.localeCompare(b.startTime));

  for (let i = 1; i < allSlots.length; i++) {
    const prevEnd = timeToMinutes(allSlots[i-1].endTime);
    const currentStart = timeToMinutes(allSlots[i].startTime);
    const gap = currentStart - prevEnd;
    
    if (gap > 0 && gap < minBreakMinutes) {
      return false; // Insufficient break time
    }
  }

  return true;
}

/**
 * Helper function to convert time string to minutes
 */
function timeToMinutes(timeString: string): number {
  const [hours, minutes] = timeString.split(':').map(Number);
  return hours * 60 + minutes;
}