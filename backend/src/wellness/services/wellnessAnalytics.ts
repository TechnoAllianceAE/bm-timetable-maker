import { PrismaClient } from '@prisma/client';
import { BurnoutRiskLevel } from '@prisma/client';

const prisma = new PrismaClient();

export class WellnessAnalyticsService {
  /**
   * Generate comprehensive wellness report for a teacher
   */
  async generateTeacherWellnessReport(teacherId: string, timeRange?: { start: Date; end: Date }) {
    const defaultRange = {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
      end: new Date()
    };
    const range = timeRange || defaultRange;

    const [
      teacher,
      wellnessMetrics,
      alerts,
      interventions,
      predictions
    ] = await Promise.all([
      // Teacher info
      prisma.teacher.findUnique({
        where: { id: teacherId },
        include: {
          user: true,
          workloadConfig: true
        }
      }),

      // Wellness metrics over time
      prisma.teacherWellnessMetric.findMany({
        where: {
          teacherId,
          metricDate: {
            gte: range.start,
            lte: range.end
          }
        },
        orderBy: { metricDate: 'asc' }
      }),

      // Recent alerts
      prisma.workloadAlert.findMany({
        where: {
          teacherId,
          createdAt: {
            gte: range.start,
            lte: range.end
          }
        },
        orderBy: { createdAt: 'desc' }
      }),

      // Interventions
      prisma.wellnessIntervention.findMany({
        where: {
          teacherId,
          createdAt: {
            gte: range.start,
            lte: range.end
          }
        },
        orderBy: { createdAt: 'desc' }
      }),

      // Predictions
      prisma.wellnessPrediction.findMany({
        where: {
          teacherId,
          predictionDate: {
            gte: range.start,
            lte: range.end
          }
        },
        orderBy: { predictionDate: 'desc' }
      })
    ]);

    if (!teacher) {
      throw new Error('Teacher not found');
    }

    // Calculate trends and insights
    const trends = this.calculateWellnessTrends(wellnessMetrics);
    const riskFactors = this.identifyRiskFactors(wellnessMetrics, alerts);
    const recommendations = this.generateRecommendations(teacher, trends, riskFactors);

    return {
      teacher: {
        id: teacher.id,
        name: teacher.user.profile?.name || teacher.user.email,
        email: teacher.user.email,
        currentWellnessScore: teacher.wellnessScore,
        currentBurnoutRisk: teacher.burnoutRiskLevel
      },
      timeRange: range,
      metrics: {
        wellnessMetrics,
        trends,
        riskFactors
      },
      alerts: {
        total: alerts.length,
        bySeverity: this.groupBySeverity(alerts),
        recent: alerts.slice(0, 5)
      },
      interventions: {
        total: interventions.length,
        implemented: interventions.filter(i => i.implemented).length,
        recent: interventions.slice(0, 3)
      },
      predictions: predictions.slice(0, 3),
      recommendations,
      summary: this.generateSummary(trends, alerts, interventions)
    };
  }

  /**
   * Generate department wellness overview
   */
  async generateDepartmentWellnessOverview(schoolId: string, department?: string) {
    const whereClause = {
      user: { schoolId },
      ...(department ? { 
        timetableEntries: {
          some: {
            subject: { department }
          }
        }
      } : {})
    };

    const [
      teachers,
      recentMetrics,
      activeAlerts,
      departmentSummary
    ] = await Promise.all([
      // All teachers in department
      prisma.teacher.findMany({
        where: whereClause,
        include: {
          user: true,
          workloadConfig: true
        }
      }),

      // Recent wellness metrics
      prisma.teacherWellnessMetric.findMany({
        where: {
          teacher: whereClause,
          metricDate: {
            gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // Last 7 days
          }
        },
        include: {
          teacher: {
            include: {
              user: true
            }
          }
        }
      }),

      // Active alerts
      prisma.workloadAlert.findMany({
        where: {
          teacher: whereClause,
          resolved: false
        },
        include: {
          teacher: {
            include: {
              user: true
            }
          }
        }
      }),

      // Department summary if exists
      department ? prisma.departmentWellnessSummary.findFirst({
        where: {
          schoolId,
          department,
          summaryDate: {
            gte: new Date(Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
          }
        },
        orderBy: { summaryDate: 'desc' }
      }) : null
    ]);

    // Calculate department statistics
    const stats = this.calculateDepartmentStats(teachers, recentMetrics, activeAlerts);

    return {
      department: department || 'All Departments',
      teacherCount: teachers.length,
      stats,
      riskDistribution: this.calculateRiskDistribution(teachers),
      activeAlerts: {
        total: activeAlerts.length,
        bySeverity: this.groupBySeverity(activeAlerts),
        byTeacher: this.groupAlertsByTeacher(activeAlerts)
      },
      trends: this.calculateDepartmentTrends(recentMetrics),
      recommendations: this.generateDepartmentRecommendations(stats, activeAlerts),
      summary: departmentSummary
    };
  }

  /**
   * Generate school-wide wellness dashboard data
   */
  async generateSchoolWellnessDashboard(schoolId: string) {
    const [
      schoolInfo,
      teacherStats,
      alertStats,
      recentTrends,
      departmentOverviews
    ] = await Promise.all([
      // School information
      prisma.school.findUnique({
        where: { id: schoolId }
      }),

      // Teacher statistics
      this.getSchoolTeacherStats(schoolId),

      // Alert statistics
      this.getSchoolAlertStats(schoolId),

      // Recent trends (last 30 days)
      this.getSchoolWellnessTrends(schoolId, 30),

      // Department overviews
      this.getDepartmentOverviews(schoolId)
    ]);

    return {
      school: schoolInfo,
      overview: {
        totalTeachers: teacherStats.total,
        teachersAtRisk: teacherStats.atRisk,
        activeAlerts: alertStats.active,
        averageWellnessScore: teacherStats.averageWellness
      },
      riskDistribution: teacherStats.riskDistribution,
      alertSummary: alertStats,
      trends: recentTrends,
      departments: departmentOverviews,
      recommendations: this.generateSchoolRecommendations(teacherStats, alertStats)
    };
  }

  /**
   * Calculate wellness trends from metrics
   */
  private calculateWellnessTrends(metrics: any[]) {
    if (metrics.length < 2) {
      return { trend: 'insufficient_data', change: 0 };
    }

    const recent = metrics.slice(-7); // Last 7 data points
    const older = metrics.slice(-14, -7); // Previous 7 data points

    const recentAvg = recent.reduce((sum, m) => sum + (m.wellnessScore || 0), 0) / recent.length;
    const olderAvg = older.length > 0 
      ? older.reduce((sum, m) => sum + (m.wellnessScore || 0), 0) / older.length
      : recentAvg;

    const change = recentAvg - olderAvg;
    const trend = change > 5 ? 'improving' : change < -5 ? 'declining' : 'stable';

    return {
      trend,
      change: Math.round(change * 10) / 10,
      recentAverage: Math.round(recentAvg * 10) / 10,
      previousAverage: Math.round(olderAvg * 10) / 10,
      dataPoints: metrics.length
    };
  }

  /**
   * Identify risk factors from metrics and alerts
   */
  private identifyRiskFactors(metrics: any[], alerts: any[]) {
    const factors = [];

    // Analyze metrics for patterns
    const recentMetrics = metrics.slice(-7);
    
    // High stress scores
    const highStressCount = recentMetrics.filter(m => (m.stressScore || 0) > 70).length;
    if (highStressCount > 3) {
      factors.push({
        type: 'high_stress',
        severity: 'high',
        description: 'Consistently high stress scores detected',
        frequency: `${highStressCount}/7 days`
      });
    }

    // Excessive work hours
    const highWorkloadCount = recentMetrics.filter(m => (m.totalWorkHours || 0) > 45).length;
    if (highWorkloadCount > 2) {
      factors.push({
        type: 'excessive_hours',
        severity: 'medium',
        description: 'Working excessive hours regularly',
        frequency: `${highWorkloadCount}/7 days`
      });
    }

    // Frequent alerts
    const recentAlerts = alerts.filter(a => 
      new Date(a.createdAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    );
    if (recentAlerts.length > 3) {
      factors.push({
        type: 'frequent_alerts',
        severity: 'high',
        description: 'Multiple wellness alerts in recent period',
        frequency: `${recentAlerts.length} alerts in 7 days`
      });
    }

    return factors;
  }

  /**
   * Generate personalized recommendations
   */
  private generateRecommendations(teacher: any, trends: any, riskFactors: any[]) {
    const recommendations = [];

    // Based on trends
    if (trends.trend === 'declining') {
      recommendations.push({
        category: 'immediate',
        priority: 'high',
        title: 'Address Declining Wellness',
        description: 'Wellness scores have been declining. Consider workload adjustment.',
        actions: [
          'Review current timetable for optimization opportunities',
          'Schedule wellness consultation',
          'Implement stress reduction techniques'
        ]
      });
    }

    // Based on risk factors
    riskFactors.forEach(factor => {
      switch (factor.type) {
        case 'high_stress':
          recommendations.push({
            category: 'wellness',
            priority: 'high',
            title: 'Manage Stress Levels',
            description: 'Consistently high stress detected',
            actions: [
              'Reduce consecutive teaching periods',
              'Increase break time between classes',
              'Consider mindfulness or relaxation techniques'
            ]
          });
          break;
        case 'excessive_hours':
          recommendations.push({
            category: 'workload',
            priority: 'medium',
            title: 'Optimize Work Hours',
            description: 'Working hours exceed recommended limits',
            actions: [
              'Redistribute some teaching responsibilities',
              'Streamline preparation processes',
              'Use time management tools'
            ]
          });
          break;
      }
    });

    // Based on current wellness score
    if (teacher.wellnessScore && teacher.wellnessScore < 50) {
      recommendations.push({
        category: 'urgent',
        priority: 'critical',
        title: 'Critical Wellness Intervention',
        description: 'Wellness score is critically low',
        actions: [
          'Immediate workload reduction',
          'Professional wellness support',
          'Temporary schedule adjustment'
        ]
      });
    }

    return recommendations;
  }

  /**
   * Helper methods for statistics calculation
   */
  private async getSchoolTeacherStats(schoolId: string) {
    const teachers = await prisma.teacher.findMany({
      where: {
        user: { schoolId }
      }
    });

    const total = teachers.length;
    const atRisk = teachers.filter(t => 
      t.burnoutRiskLevel === BurnoutRiskLevel.HIGH || 
      t.burnoutRiskLevel === BurnoutRiskLevel.CRITICAL
    ).length;

    const averageWellness = teachers.reduce((sum, t) => sum + (t.wellnessScore || 0), 0) / total;

    const riskDistribution = {
      [BurnoutRiskLevel.LOW]: teachers.filter(t => t.burnoutRiskLevel === BurnoutRiskLevel.LOW).length,
      [BurnoutRiskLevel.MEDIUM]: teachers.filter(t => t.burnoutRiskLevel === BurnoutRiskLevel.MEDIUM).length,
      [BurnoutRiskLevel.HIGH]: teachers.filter(t => t.burnoutRiskLevel === BurnoutRiskLevel.HIGH).length,
      [BurnoutRiskLevel.CRITICAL]: teachers.filter(t => t.burnoutRiskLevel === BurnoutRiskLevel.CRITICAL).length
    };

    return {
      total,
      atRisk,
      averageWellness: Math.round(averageWellness * 10) / 10,
      riskDistribution
    };
  }

  private async getSchoolAlertStats(schoolId: string) {
    const alerts = await prisma.workloadAlert.findMany({
      where: {
        teacher: {
          user: { schoolId }
        }
      }
    });

    const active = alerts.filter(a => !a.resolved).length;
    const bySeverity = this.groupBySeverity(alerts);

    return {
      total: alerts.length,
      active,
      bySeverity
    };
  }

  private async getSchoolWellnessTrends(schoolId: string, days: number) {
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);

    const metrics = await prisma.teacherWellnessMetric.findMany({
      where: {
        teacher: {
          user: { schoolId }
        },
        metricDate: {
          gte: startDate
        }
      },
      orderBy: { metricDate: 'asc' }
    });

    // Group by date and calculate daily averages
    const dailyAverages = new Map();
    
    metrics.forEach(metric => {
      const date = metric.metricDate.toISOString().split('T')[0];
      if (!dailyAverages.has(date)) {
        dailyAverages.set(date, { wellnessSum: 0, stressSum: 0, count: 0 });
      }
      
      const day = dailyAverages.get(date);
      day.wellnessSum += metric.wellnessScore || 0;
      day.stressSum += metric.stressScore || 0;
      day.count++;
    });

    const trends = Array.from(dailyAverages.entries()).map(([date, data]) => ({
      date,
      averageWellness: Math.round((data.wellnessSum / data.count) * 10) / 10,
      averageStress: Math.round((data.stressSum / data.count) * 10) / 10,
      teacherCount: data.count
    }));

    return trends;
  }

  private async getDepartmentOverviews(schoolId: string) {
    // Get unique departments
    const departments = await prisma.subject.findMany({
      where: { schoolId },
      select: { department: true },
      distinct: ['department']
    });

    const overviews = [];
    for (const dept of departments) {
      if (dept.department) {
        const overview = await this.generateDepartmentWellnessOverview(schoolId, dept.department);
        overviews.push(overview);
      }
    }

    return overviews;
  }

  private groupBySeverity(alerts: any[]) {
    return alerts.reduce((acc, alert) => {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1;
      return acc;
    }, {});
  }

  private groupAlertsByTeacher(alerts: any[]) {
    return alerts.reduce((acc, alert) => {
      const teacherId = alert.teacherId;
      if (!acc[teacherId]) {
        acc[teacherId] = {
          teacherName: alert.teacher?.user?.profile?.name || alert.teacher?.user?.email,
          alerts: []
        };
      }
      acc[teacherId].alerts.push(alert);
      return acc;
    }, {});
  }

  private calculateDepartmentStats(teachers: any[], metrics: any[], alerts: any[]) {
    const totalTeachers = teachers.length;
    const teachersWithMetrics = new Set(metrics.map(m => m.teacherId)).size;
    
    const avgWellness = metrics.length > 0 
      ? metrics.reduce((sum, m) => sum + (m.wellnessScore || 0), 0) / metrics.length
      : 0;
    
    const avgStress = metrics.length > 0
      ? metrics.reduce((sum, m) => sum + (m.stressScore || 0), 0) / metrics.length
      : 0;

    return {
      totalTeachers,
      teachersWithMetrics,
      averageWellness: Math.round(avgWellness * 10) / 10,
      averageStress: Math.round(avgStress * 10) / 10,
      activeAlerts: alerts.length
    };
  }

  private calculateRiskDistribution(teachers: any[]) {
    return teachers.reduce((acc, teacher) => {
      const risk = teacher.burnoutRiskLevel || BurnoutRiskLevel.LOW;
      acc[risk] = (acc[risk] || 0) + 1;
      return acc;
    }, {});
  }

  private calculateDepartmentTrends(metrics: any[]) {
    if (metrics.length < 2) return { trend: 'insufficient_data' };

    const sortedMetrics = metrics.sort((a, b) => 
      new Date(a.metricDate).getTime() - new Date(b.metricDate).getTime()
    );

    const recent = sortedMetrics.slice(-Math.ceil(sortedMetrics.length / 2));
    const older = sortedMetrics.slice(0, Math.floor(sortedMetrics.length / 2));

    const recentAvg = recent.reduce((sum, m) => sum + (m.wellnessScore || 0), 0) / recent.length;
    const olderAvg = older.reduce((sum, m) => sum + (m.wellnessScore || 0), 0) / older.length;

    const change = recentAvg - olderAvg;
    const trend = change > 3 ? 'improving' : change < -3 ? 'declining' : 'stable';

    return { trend, change: Math.round(change * 10) / 10 };
  }

  private generateDepartmentRecommendations(stats: any, alerts: any[]) {
    const recommendations = [];

    if (stats.averageWellness < 60) {
      recommendations.push({
        priority: 'high',
        title: 'Department Wellness Intervention',
        description: 'Department average wellness is below acceptable threshold',
        actions: [
          'Review department workload distribution',
          'Implement department-wide wellness initiatives',
          'Consider additional staffing'
        ]
      });
    }

    if (alerts.length > stats.totalTeachers * 0.3) {
      recommendations.push({
        priority: 'medium',
        title: 'Alert Management',
        description: 'High number of active alerts in department',
        actions: [
          'Address common alert causes',
          'Implement preventive measures',
          'Regular wellness check-ins'
        ]
      });
    }

    return recommendations;
  }

  private generateSchoolRecommendations(teacherStats: any, alertStats: any) {
    const recommendations = [];

    if (teacherStats.atRisk > teacherStats.total * 0.2) {
      recommendations.push({
        priority: 'critical',
        title: 'School-wide Wellness Crisis',
        description: 'More than 20% of teachers are at high burnout risk',
        actions: [
          'Implement emergency wellness protocols',
          'Review school-wide policies',
          'Consider external wellness support'
        ]
      });
    }

    if (alertStats.active > teacherStats.total * 0.5) {
      recommendations.push({
        priority: 'high',
        title: 'Alert System Overload',
        description: 'Excessive number of active wellness alerts',
        actions: [
          'Prioritize critical alerts',
          'Implement systematic resolution process',
          'Review alert thresholds'
        ]
      });
    }

    return recommendations;
  }

  private generateSummary(trends: any, alerts: any[], interventions: any[]) {
    const summary = {
      status: 'good', // good, concerning, critical
      keyPoints: [],
      nextActions: []
    };

    // Determine overall status
    if (trends.trend === 'declining' || alerts.filter(a => !a.resolved).length > 3) {
      summary.status = alerts.some(a => a.severity === 'CRITICAL') ? 'critical' : 'concerning';
    }

    // Key points
    summary.keyPoints.push(`Wellness trend: ${trends.trend}`);
    if (alerts.length > 0) {
      summary.keyPoints.push(`${alerts.filter(a => !a.resolved).length} active alerts`);
    }
    if (interventions.length > 0) {
      summary.keyPoints.push(`${interventions.filter(i => i.implemented).length}/${interventions.length} interventions implemented`);
    }

    // Next actions based on status
    switch (summary.status) {
      case 'critical':
        summary.nextActions = [
          'Immediate workload reduction required',
          'Schedule urgent wellness consultation',
          'Implement emergency support measures'
        ];
        break;
      case 'concerning':
        summary.nextActions = [
          'Review and adjust current workload',
          'Monitor wellness metrics closely',
          'Consider preventive interventions'
        ];
        break;
      default:
        summary.nextActions = [
          'Continue current wellness practices',
          'Regular monitoring and check-ins',
          'Maintain work-life balance'
        ];
    }

    return summary;
  }
}