import { PrismaClient } from '@prisma/client';
import { AlertSeverity, BurnoutRiskLevel } from '@prisma/client';

const prisma = new PrismaClient();

export class WorkloadMonitorService {
  /**
   * Calculate current workload metrics for a teacher
   */
  async calculateTeacherWorkload(teacherId: string, date: Date = new Date()) {
    const teacher = await prisma.teacher.findUnique({
      where: { id: teacherId },
      include: {
        workloadConfig: true,
        timetableEntries: {
          include: {
            subject: true,
            timeSlot: true,
            class: true
          }
        }
      }
    });

    if (!teacher) {
      throw new Error('Teacher not found');
    }

    const config = teacher.workloadConfig;
    const entries = teacher.timetableEntries;

    // Calculate daily metrics
    const dailyMetrics = this.calculateDailyMetrics(entries, config);
    
    // Calculate weekly metrics
    const weeklyMetrics = this.calculateWeeklyMetrics(entries, config);

    // Calculate stress indicators
    const stressIndicators = this.calculateStressIndicators(dailyMetrics, weeklyMetrics, config);

    // Calculate wellness score
    const wellnessScore = this.calculateWellnessScore(stressIndicators);

    // Store metrics
    await this.storeWellnessMetrics(teacherId, date, {
      ...dailyMetrics,
      ...weeklyMetrics,
      stressScore: stressIndicators.overallStress,
      wellnessScore
    });

    return {
      teacherId,
      date,
      dailyMetrics,
      weeklyMetrics,
      stressIndicators,
      wellnessScore,
      burnoutRisk: this.assessBurnoutRisk(wellnessScore, stressIndicators)
    };
  }

  /**
   * Calculate daily workload metrics
   */
  private calculateDailyMetrics(entries: any[], config: any) {
    const dailyStats = new Map();

    entries.forEach(entry => {
      const day = entry.timeSlot.day;
      if (!dailyStats.has(day)) {
        dailyStats.set(day, {
          periods: 0,
          consecutivePeriods: 0,
          gaps: 0,
          teachingHours: 0,
          prepHours: 0
        });
      }

      const dayStats = dailyStats.get(day);
      dayStats.periods++;
      dayStats.teachingHours += this.getSlotDuration(entry.timeSlot);
      dayStats.prepHours += entry.subject.prepTime || 0;
    });

    // Calculate consecutive periods and gaps for each day
    dailyStats.forEach((stats, day) => {
      const dayEntries = entries.filter(e => e.timeSlot.day === day)
        .sort((a, b) => a.timeSlot.startTime.localeCompare(b.timeSlot.startTime));
      
      stats.consecutivePeriods = this.calculateMaxConsecutivePeriods(dayEntries);
      stats.gaps = this.calculateGaps(dayEntries);
    });

    return Object.fromEntries(dailyStats);
  }

  /**
   * Calculate weekly workload metrics
   */
  private calculateWeeklyMetrics(entries: any[], config: any) {
    const totalPeriods = entries.length;
    const totalTeachingHours = entries.reduce((sum, entry) => 
      sum + this.getSlotDuration(entry.timeSlot), 0);
    const totalPrepHours = entries.reduce((sum, entry) => 
      sum + (entry.subject.prepTime || 0), 0);
    
    return {
      totalPeriods,
      totalTeachingHours,
      totalPrepHours,
      totalWorkHours: totalTeachingHours + totalPrepHours,
      averagePeriodsPerDay: totalPeriods / 5, // Assuming 5-day week
      workloadPercentage: (totalPeriods / (config?.maxPeriodsPerWeek || 30)) * 100
    };
  }

  /**
   * Calculate stress indicators
   */
  private calculateStressIndicators(dailyMetrics: any, weeklyMetrics: any, config: any) {
    const indicators = {
      overworkIndicator: 0,
      consecutivePeriodsStress: 0,
      gapStress: 0,
      workloadImbalance: 0,
      overallStress: 0
    };

    // Overwork indicator
    if (weeklyMetrics.workloadPercentage > 90) {
      indicators.overworkIndicator = 100;
    } else if (weeklyMetrics.workloadPercentage > 80) {
      indicators.overworkIndicator = 70;
    } else if (weeklyMetrics.workloadPercentage > 70) {
      indicators.overworkIndicator = 40;
    }

    // Consecutive periods stress
    const maxConsecutive = Math.max(...Object.values(dailyMetrics).map((d: any) => d.consecutivePeriods));
    if (maxConsecutive > (config?.maxConsecutivePeriods || 3)) {
      indicators.consecutivePeriodsStress = Math.min(100, (maxConsecutive - 3) * 25);
    }

    // Calculate overall stress
    indicators.overallStress = Math.round(
      (indicators.overworkIndicator * 0.4) +
      (indicators.consecutivePeriodsStress * 0.3) +
      (indicators.gapStress * 0.2) +
      (indicators.workloadImbalance * 0.1)
    );

    return indicators;
  }

  /**
   * Calculate wellness score (0-100, higher is better)
   */
  private calculateWellnessScore(stressIndicators: any): number {
    return Math.max(0, 100 - stressIndicators.overallStress);
  }

  /**
   * Assess burnout risk level
   */
  private assessBurnoutRisk(wellnessScore: number, stressIndicators: any): BurnoutRiskLevel {
    if (wellnessScore < 30 || stressIndicators.overallStress > 80) {
      return BurnoutRiskLevel.CRITICAL;
    } else if (wellnessScore < 50 || stressIndicators.overallStress > 60) {
      return BurnoutRiskLevel.HIGH;
    } else if (wellnessScore < 70 || stressIndicators.overallStress > 40) {
      return BurnoutRiskLevel.MEDIUM;
    }
    return BurnoutRiskLevel.LOW;
  }

  /**
   * Store wellness metrics in database
   */
  private async storeWellnessMetrics(teacherId: string, date: Date, metrics: any) {
    await prisma.teacherWellnessMetric.upsert({
      where: {
        teacherId_metricDate: {
          teacherId,
          metricDate: date
        }
      },
      update: {
        teachingHours: metrics.totalTeachingHours,
        prepHours: metrics.totalPrepHours,
        totalWorkHours: metrics.totalWorkHours,
        consecutivePeriodsMax: Math.max(...Object.values(metrics).map((d: any) => d?.consecutivePeriods || 0)),
        stressScore: metrics.stressScore,
        wellnessScore: metrics.wellnessScore,
        burnoutIndicators: metrics.burnoutIndicators || {}
      },
      create: {
        teacherId,
        metricDate: date,
        teachingHours: metrics.totalTeachingHours,
        prepHours: metrics.totalPrepHours,
        totalWorkHours: metrics.totalWorkHours,
        consecutivePeriodsMax: Math.max(...Object.values(metrics).map((d: any) => d?.consecutivePeriods || 0)),
        stressScore: metrics.stressScore,
        wellnessScore: metrics.wellnessScore,
        burnoutIndicators: metrics.burnoutIndicators || {}
      }
    });
  }

  /**
   * Monitor all teachers and trigger alerts
   */
  async monitorAllTeachers(schoolId: string) {
    const teachers = await prisma.teacher.findMany({
      where: {
        user: {
          schoolId
        }
      },
      include: {
        user: true,
        workloadConfig: true
      }
    });

    const results = [];
    for (const teacher of teachers) {
      try {
        const workload = await this.calculateTeacherWorkload(teacher.id);
        
        // Check for alert conditions
        await this.checkAndCreateAlerts(teacher.id, workload);
        
        results.push(workload);
      } catch (error) {
        console.error(`Error monitoring teacher ${teacher.id}:`, error);
      }
    }

    return results;
  }

  /**
   * Check workload and create alerts if needed
   */
  private async checkAndCreateAlerts(teacherId: string, workload: any) {
    const alerts = [];

    // Check for overwork
    if (workload.weeklyMetrics.workloadPercentage > 90) {
      alerts.push({
        teacherId,
        alertType: 'OVERWORK_WARNING',
        severity: AlertSeverity.CRITICAL,
        title: 'Critical Workload Exceeded',
        message: `Teacher workload is at ${workload.weeklyMetrics.workloadPercentage.toFixed(1)}% of maximum capacity`,
        recommendations: {
          immediate: ['Reduce teaching load', 'Assign substitute for some classes'],
          longTerm: ['Review timetable distribution', 'Consider hiring additional staff']
        }
      });
    }

    // Check for burnout risk
    if (workload.burnoutRisk === BurnoutRiskLevel.CRITICAL) {
      alerts.push({
        teacherId,
        alertType: 'BURNOUT_RISK',
        severity: AlertSeverity.CRITICAL,
        title: 'Critical Burnout Risk Detected',
        message: `Teacher wellness score is critically low (${workload.wellnessScore})`,
        recommendations: {
          immediate: ['Schedule wellness consultation', 'Reduce workload immediately'],
          longTerm: ['Implement wellness intervention plan', 'Regular monitoring']
        }
      });
    }

    // Create alerts in database
    for (const alert of alerts) {
      await prisma.workloadAlert.create({
        data: alert
      });
    }
  }

  /**
   * Helper methods
   */
  private getSlotDuration(timeSlot: any): number {
    // Convert time strings to minutes and calculate duration
    const start = this.timeToMinutes(timeSlot.startTime);
    const end = this.timeToMinutes(timeSlot.endTime);
    return (end - start) / 60; // Return hours
  }

  private timeToMinutes(timeString: string): number {
    const [hours, minutes] = timeString.split(':').map(Number);
    return hours * 60 + minutes;
  }

  private calculateMaxConsecutivePeriods(dayEntries: any[]): number {
    if (dayEntries.length === 0) return 0;
    
    let maxConsecutive = 1;
    let currentConsecutive = 1;
    
    for (let i = 1; i < dayEntries.length; i++) {
      const prevEnd = this.timeToMinutes(dayEntries[i-1].timeSlot.endTime);
      const currentStart = this.timeToMinutes(dayEntries[i].timeSlot.startTime);
      
      // If gap is less than 15 minutes, consider consecutive
      if (currentStart - prevEnd < 15) {
        currentConsecutive++;
        maxConsecutive = Math.max(maxConsecutive, currentConsecutive);
      } else {
        currentConsecutive = 1;
      }
    }
    
    return maxConsecutive;
  }

  private calculateGaps(dayEntries: any[]): number {
    if (dayEntries.length <= 1) return 0;
    
    let totalGaps = 0;
    for (let i = 1; i < dayEntries.length; i++) {
      const prevEnd = this.timeToMinutes(dayEntries[i-1].timeSlot.endTime);
      const currentStart = this.timeToMinutes(dayEntries[i].timeSlot.startTime);
      const gap = currentStart - prevEnd;
      
      if (gap > 15) { // Only count significant gaps
        totalGaps += gap;
      }
    }
    
    return totalGaps;
  }
}