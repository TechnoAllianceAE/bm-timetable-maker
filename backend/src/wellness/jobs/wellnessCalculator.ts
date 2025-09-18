import cron from 'node-cron';
import { PrismaClient } from '@prisma/client';
import { WorkloadMonitorService } from '../services/workloadMonitor';
import { AlertManagerService } from '../services/alertManager';
import { WebSocketService } from '../../shared/websocket/websocketService';

const prisma = new PrismaClient();

export class WellnessCalculatorJob {
  private workloadMonitor: WorkloadMonitorService;
  private alertManager: AlertManagerService;
  private isRunning = false;

  constructor(wsService: WebSocketService) {
    this.workloadMonitor = new WorkloadMonitorService();
    this.alertManager = new AlertManagerService(wsService);
  }

  /**
   * Start the wellness calculation cron jobs
   */
  start() {
    console.log('Starting wellness calculation jobs...');

    // Run every hour during school hours (7 AM - 6 PM, Monday-Friday)
    cron.schedule('0 7-18 * * 1-5', async () => {
      await this.runHourlyWellnessCheck();
    });

    // Run comprehensive daily analysis at 7 PM
    cron.schedule('0 19 * * 1-5', async () => {
      await this.runDailyWellnessAnalysis();
    });

    // Run weekly summary on Sunday at 8 PM
    cron.schedule('0 20 * * 0', async () => {
      await this.runWeeklyWellnessSummary();
    });

    console.log('Wellness calculation jobs started successfully');
  }

  /**
   * Stop all cron jobs
   */
  stop() {
    cron.destroy();
    console.log('Wellness calculation jobs stopped');
  }

  /**
   * Hourly wellness check - lightweight monitoring
   */
  private async runHourlyWellnessCheck() {
    if (this.isRunning) {
      console.log('Wellness check already running, skipping...');
      return;
    }

    this.isRunning = true;
    console.log('Running hourly wellness check...');

    try {
      // Get all active schools
      const schools = await prisma.school.findMany({
        select: { id: true, name: true }
      });

      for (const school of schools) {
        await this.processSchoolHourlyCheck(school.id);
      }

      console.log(`Hourly wellness check completed for ${schools.length} schools`);
    } catch (error) {
      console.error('Error in hourly wellness check:', error);
    } finally {
      this.isRunning = false;
    }
  }

  /**
   * Daily comprehensive wellness analysis
   */
  private async runDailyWellnessAnalysis() {
    console.log('Running daily wellness analysis...');

    try {
      const schools = await prisma.school.findMany({
        select: { id: true, name: true }
      });

      for (const school of schools) {
        await this.processSchoolDailyAnalysis(school.id);
      }

      console.log(`Daily wellness analysis completed for ${schools.length} schools`);
    } catch (error) {
      console.error('Error in daily wellness analysis:', error);
    }
  }

  /**
   * Weekly wellness summary and trend analysis
   */
  private async runWeeklyWellnessSummary() {
    console.log('Running weekly wellness summary...');

    try {
      const schools = await prisma.school.findMany({
        select: { id: true, name: true }
      });

      for (const school of schools) {
        await this.processSchoolWeeklySummary(school.id);
      }

      console.log(`Weekly wellness summary completed for ${schools.length} schools`);
    } catch (error) {
      console.error('Error in weekly wellness summary:', error);
    }
  }

  /**
   * Process hourly check for a specific school
   */
  private async processSchoolHourlyCheck(schoolId: string) {
    try {
      // Get teachers with high-risk indicators
      const highRiskTeachers = await prisma.teacher.findMany({
        where: {
          user: { schoolId },
          OR: [
            { burnoutRiskLevel: 'HIGH' },
            { burnoutRiskLevel: 'CRITICAL' },
            { wellnessScore: { lt: 50 } }
          ]
        },
        include: {
          user: true
        }
      });

      // Monitor high-risk teachers more frequently
      for (const teacher of highRiskTeachers) {
        const workload = await this.workloadMonitor.calculateTeacherWorkload(teacher.id);
        
        // Auto-resolve alerts if conditions improved
        await this.alertManager.autoResolveAlerts(teacher.id, workload);
        
        // Check for new alert conditions
        await this.checkForNewAlerts(teacher.id, workload);
      }

      console.log(`Hourly check completed for school ${schoolId}: ${highRiskTeachers.length} high-risk teachers monitored`);
    } catch (error) {
      console.error(`Error in hourly check for school ${schoolId}:`, error);
    }
  }

  /**
   * Process daily analysis for a specific school
   */
  private async processSchoolDailyAnalysis(schoolId: string) {
    try {
      // Monitor all teachers in the school
      const results = await this.workloadMonitor.monitorAllTeachers(schoolId);
      
      // Update teacher wellness scores and risk levels
      for (const result of results) {
        await prisma.teacher.update({
          where: { id: result.teacherId },
          data: {
            wellnessScore: result.wellnessScore,
            burnoutRiskLevel: result.burnoutRisk
          }
        });
      }

      // Generate department summaries
      await this.generateDepartmentSummaries(schoolId);

      // Clean up old resolved alerts (older than 30 days)
      await this.cleanupOldAlerts(schoolId);

      console.log(`Daily analysis completed for school ${schoolId}: ${results.length} teachers analyzed`);
    } catch (error) {
      console.error(`Error in daily analysis for school ${schoolId}:`, error);
    }
  }

  /**
   * Process weekly summary for a specific school
   */
  private async processSchoolWeeklySummary(schoolId: string) {
    try {
      // Calculate weekly trends
      const weekStart = new Date();
      weekStart.setDate(weekStart.getDate() - 7);

      const weeklyMetrics = await prisma.teacherWellnessMetric.findMany({
        where: {
          teacher: {
            user: { schoolId }
          },
          metricDate: {
            gte: weekStart
          }
        },
        include: {
          teacher: {
            include: {
              user: true
            }
          }
        }
      });

      // Generate insights and recommendations
      const insights = this.generateWeeklyInsights(weeklyMetrics);
      
      // Store weekly summary (could be used for reporting)
      await this.storeWeeklySummary(schoolId, insights);

      // Send weekly reports to administrators
      await this.sendWeeklyReports(schoolId, insights);

      console.log(`Weekly summary completed for school ${schoolId}`);
    } catch (error) {
      console.error(`Error in weekly summary for school ${schoolId}:`, error);
    }
  }

  /**
   * Check for new alert conditions
   */
  private async checkForNewAlerts(teacherId: string, workload: any) {
    const alerts = [];

    // Check for sudden wellness score drop
    const recentMetrics = await prisma.teacherWellnessMetric.findMany({
      where: { teacherId },
      orderBy: { metricDate: 'desc' },
      take: 7
    });

    if (recentMetrics.length >= 2) {
      const latest = recentMetrics[0];
      const previous = recentMetrics[1];
      
      if (latest.wellnessScore && previous.wellnessScore) {
        const drop = previous.wellnessScore - latest.wellnessScore;
        if (drop > 15) {
          alerts.push({
            teacherId,
            alertType: 'WELLNESS_DECLINE',
            severity: 'WARNING' as const,
            title: 'Significant Wellness Decline',
            message: `Wellness score dropped by ${drop.toFixed(1)} points in recent period`,
            recommendations: {
              immediate: ['Review recent workload changes', 'Schedule wellness check-in'],
              longTerm: ['Monitor closely for continued decline', 'Consider workload adjustment']
            }
          });
        }
      }
    }

    // Check for pattern of late-night work
    const lateEveningClasses = workload.dailyMetrics ? 
      Object.values(workload.dailyMetrics).filter((day: any) => 
        day.lastClassTime && day.lastClassTime > '18:00'
      ).length : 0;

    if (lateEveningClasses > 3) {
      alerts.push({
        teacherId,
        alertType: 'LATE_EVENING_PATTERN',
        severity: 'INFO' as const,
        title: 'Frequent Late Evening Classes',
        message: `Teacher has late evening classes ${lateEveningClasses} days this week`,
        recommendations: {
          immediate: ['Review schedule balance'],
          longTerm: ['Consider redistributing late classes', 'Monitor for fatigue signs']
        }
      });
    }

    // Create alerts
    if (alerts.length > 0) {
      await this.alertManager.createBulkAlerts(alerts);
    }
  }

  /**
   * Generate department summaries
   */
  private async generateDepartmentSummaries(schoolId: string) {
    // Get unique departments
    const departments = await prisma.subject.findMany({
      where: { schoolId },
      select: { department: true },
      distinct: ['department']
    });

    for (const dept of departments) {
      if (!dept.department) continue;

      // Get department teachers and their metrics
      const departmentData = await prisma.teacherWellnessMetric.findMany({
        where: {
          teacher: {
            user: { schoolId },
            timetableEntries: {
              some: {
                subject: { department: dept.department }
              }
            }
          },
          metricDate: {
            gte: new Date(Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
          }
        }
      });

      if (departmentData.length === 0) continue;

      // Calculate department statistics
      const avgWorkloadHours = departmentData.reduce((sum, m) => sum + (m.totalWorkHours || 0), 0) / departmentData.length;
      const avgStressScore = departmentData.reduce((sum, m) => sum + (m.stressScore || 0), 0) / departmentData.length;
      
      // Count teachers at risk
      const teachersAtRisk = await prisma.teacher.count({
        where: {
          user: { schoolId },
          timetableEntries: {
            some: {
              subject: { department: dept.department }
            }
          },
          OR: [
            { burnoutRiskLevel: 'HIGH' },
            { burnoutRiskLevel: 'CRITICAL' }
          ]
        }
      });

      // Store department summary
      await prisma.departmentWellnessSummary.upsert({
        where: {
          schoolId_department_summaryDate: {
            schoolId,
            department: dept.department,
            summaryDate: new Date()
          }
        },
        update: {
          avgWorkloadHours,
          avgStressScore,
          teachersAtRisk,
          topStressFactors: this.identifyTopStressFactors(departmentData),
          recommendations: this.generateDepartmentRecommendations(avgStressScore, teachersAtRisk)
        },
        create: {
          schoolId,
          department: dept.department,
          summaryDate: new Date(),
          avgWorkloadHours,
          avgStressScore,
          teachersAtRisk,
          topStressFactors: this.identifyTopStressFactors(departmentData),
          recommendations: this.generateDepartmentRecommendations(avgStressScore, teachersAtRisk)
        }
      });
    }
  }

  /**
   * Clean up old resolved alerts
   */
  private async cleanupOldAlerts(schoolId: string) {
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

    await prisma.workloadAlert.deleteMany({
      where: {
        teacher: {
          user: { schoolId }
        },
        resolved: true,
        resolvedAt: {
          lt: thirtyDaysAgo
        }
      }
    });
  }

  /**
   * Generate weekly insights from metrics
   */
  private generateWeeklyInsights(metrics: any[]) {
    const insights = {
      totalTeachers: new Set(metrics.map(m => m.teacherId)).size,
      averageWellness: 0,
      averageStress: 0,
      trends: {
        wellness: 'stable',
        workload: 'stable'
      },
      topConcerns: [],
      recommendations: []
    };

    if (metrics.length === 0) return insights;

    // Calculate averages
    insights.averageWellness = metrics.reduce((sum, m) => sum + (m.wellnessScore || 0), 0) / metrics.length;
    insights.averageStress = metrics.reduce((sum, m) => sum + (m.stressScore || 0), 0) / metrics.length;

    // Identify trends (simplified)
    const recentMetrics = metrics.filter(m => 
      new Date(m.metricDate) > new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
    );
    const olderMetrics = metrics.filter(m => 
      new Date(m.metricDate) <= new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
    );

    if (recentMetrics.length > 0 && olderMetrics.length > 0) {
      const recentAvgWellness = recentMetrics.reduce((sum, m) => sum + (m.wellnessScore || 0), 0) / recentMetrics.length;
      const olderAvgWellness = olderMetrics.reduce((sum, m) => sum + (m.wellnessScore || 0), 0) / olderMetrics.length;
      
      const wellnessChange = recentAvgWellness - olderAvgWellness;
      insights.trends.wellness = wellnessChange > 5 ? 'improving' : wellnessChange < -5 ? 'declining' : 'stable';
    }

    // Generate recommendations based on insights
    if (insights.averageWellness < 60) {
      insights.recommendations.push('School-wide wellness intervention recommended');
    }
    if (insights.averageStress > 60) {
      insights.recommendations.push('Review workload distribution across departments');
    }

    return insights;
  }

  /**
   * Store weekly summary
   */
  private async storeWeeklySummary(schoolId: string, insights: any) {
    // This could be stored in a separate table for historical tracking
    console.log(`Weekly summary for school ${schoolId}:`, insights);
  }

  /**
   * Send weekly reports to administrators
   */
  private async sendWeeklyReports(schoolId: string, insights: any) {
    // Get school administrators
    const admins = await prisma.user.findMany({
      where: {
        schoolId,
        role: { in: ['ADMIN', 'PRINCIPAL'] }
      }
    });

    // Send notifications (implementation depends on notification service)
    for (const admin of admins) {
      console.log(`Sending weekly wellness report to ${admin.email}`);
      // TODO: Implement actual email/notification sending
    }
  }

  /**
   * Helper methods
   */
  private identifyTopStressFactors(metrics: any[]) {
    const factors = {
      highWorkload: metrics.filter(m => (m.totalWorkHours || 0) > 45).length,
      consecutivePeriods: metrics.filter(m => (m.consecutivePeriodsMax || 0) > 3).length,
      insufficientBreaks: metrics.filter(m => (m.gapsTotalMinutes || 0) < 60).length
    };

    return Object.entries(factors)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([factor, count]) => ({ factor, count }));
  }

  private generateDepartmentRecommendations(avgStress: number, teachersAtRisk: number) {
    const recommendations = [];

    if (avgStress > 70) {
      recommendations.push('Immediate workload review required');
    }
    if (teachersAtRisk > 0) {
      recommendations.push(`${teachersAtRisk} teachers need wellness support`);
    }
    if (avgStress > 50) {
      recommendations.push('Consider stress management workshops');
    }

    return recommendations;
  }

  /**
   * Manual trigger for wellness calculation (for testing or immediate needs)
   */
  async runManualWellnessCheck(schoolId?: string) {
    console.log('Running manual wellness check...');
    
    if (schoolId) {
      await this.processSchoolDailyAnalysis(schoolId);
    } else {
      const schools = await prisma.school.findMany({
        select: { id: true }
      });
      
      for (const school of schools) {
        await this.processSchoolDailyAnalysis(school.id);
      }
    }
    
    console.log('Manual wellness check completed');
  }
}