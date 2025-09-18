import { PrismaClient } from '@prisma/client';
import { AlertSeverity } from '@prisma/client';
import { WebSocketService } from '../../shared/websocket/websocketService';

const prisma = new PrismaClient();

export class AlertManagerService {
  private wsService: WebSocketService;

  constructor(wsService: WebSocketService) {
    this.wsService = wsService;
  }

  /**
   * Create a new workload alert
   */
  async createAlert(alertData: {
    teacherId: string;
    alertType: string;
    severity: AlertSeverity;
    title: string;
    message: string;
    recommendations?: any;
  }) {
    const alert = await prisma.workloadAlert.create({
      data: alertData,
      include: {
        teacher: {
          include: {
            user: true
          }
        }
      }
    });

    // Send real-time notification
    await this.sendRealTimeAlert(alert);

    // Send email notification for critical alerts
    if (alert.severity === AlertSeverity.CRITICAL) {
      await this.sendEmailAlert(alert);
    }

    return alert;
  }

  /**
   * Get active alerts for a teacher
   */
  async getTeacherAlerts(teacherId: string, includeResolved = false) {
    return prisma.workloadAlert.findMany({
      where: {
        teacherId,
        ...(includeResolved ? {} : { resolved: false })
      },
      orderBy: [
        { severity: 'desc' },
        { createdAt: 'desc' }
      ]
    });
  }

  /**
   * Get all active alerts for a school
   */
  async getSchoolAlerts(schoolId: string, severity?: AlertSeverity) {
    return prisma.workloadAlert.findMany({
      where: {
        teacher: {
          user: {
            schoolId
          }
        },
        resolved: false,
        ...(severity ? { severity } : {})
      },
      include: {
        teacher: {
          include: {
            user: {
              select: {
                id: true,
                email: true,
                profile: true
              }
            }
          }
        }
      },
      orderBy: [
        { severity: 'desc' },
        { createdAt: 'desc' }
      ]
    });
  }

  /**
   * Acknowledge an alert
   */
  async acknowledgeAlert(alertId: string, acknowledgedBy: string) {
    const alert = await prisma.workloadAlert.update({
      where: { id: alertId },
      data: {
        acknowledged: true,
        acknowledgedBy,
        acknowledgedAt: new Date()
      },
      include: {
        teacher: {
          include: {
            user: true
          }
        }
      }
    });

    // Notify relevant parties
    await this.wsService.sendToUser(alert.teacher.userId, {
      type: 'ALERT_ACKNOWLEDGED',
      data: { alertId, acknowledgedBy }
    });

    return alert;
  }

  /**
   * Resolve an alert
   */
  async resolveAlert(alertId: string, resolvedBy?: string) {
    const alert = await prisma.workloadAlert.update({
      where: { id: alertId },
      data: {
        resolved: true,
        resolvedAt: new Date()
      },
      include: {
        teacher: {
          include: {
            user: true
          }
        }
      }
    });

    // Notify relevant parties
    await this.wsService.sendToUser(alert.teacher.userId, {
      type: 'ALERT_RESOLVED',
      data: { alertId, resolvedBy }
    });

    return alert;
  }

  /**
   * Get alert statistics for dashboard
   */
  async getAlertStatistics(schoolId: string, timeRange?: { start: Date; end: Date }) {
    const whereClause = {
      teacher: {
        user: {
          schoolId
        }
      },
      ...(timeRange ? {
        createdAt: {
          gte: timeRange.start,
          lte: timeRange.end
        }
      } : {})
    };

    const [
      totalAlerts,
      activeAlerts,
      criticalAlerts,
      alertsBySeverity,
      alertsByType,
      recentTrends
    ] = await Promise.all([
      // Total alerts
      prisma.workloadAlert.count({ where: whereClause }),
      
      // Active alerts
      prisma.workloadAlert.count({ 
        where: { ...whereClause, resolved: false } 
      }),
      
      // Critical alerts
      prisma.workloadAlert.count({ 
        where: { ...whereClause, severity: AlertSeverity.CRITICAL, resolved: false } 
      }),
      
      // Alerts by severity
      prisma.workloadAlert.groupBy({
        by: ['severity'],
        where: { ...whereClause, resolved: false },
        _count: true
      }),
      
      // Alerts by type
      prisma.workloadAlert.groupBy({
        by: ['alertType'],
        where: whereClause,
        _count: true
      }),
      
      // Recent trends (last 7 days)
      prisma.workloadAlert.groupBy({
        by: ['createdAt'],
        where: {
          ...whereClause,
          createdAt: {
            gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
          }
        },
        _count: true
      })
    ]);

    return {
      totalAlerts,
      activeAlerts,
      criticalAlerts,
      alertsBySeverity: alertsBySeverity.reduce((acc, item) => {
        acc[item.severity] = item._count;
        return acc;
      }, {} as Record<string, number>),
      alertsByType: alertsByType.reduce((acc, item) => {
        acc[item.alertType] = item._count;
        return acc;
      }, {} as Record<string, number>),
      recentTrends
    };
  }

  /**
   * Auto-resolve alerts based on conditions
   */
  async autoResolveAlerts(teacherId: string, currentWorkload: any) {
    // Get active alerts for teacher
    const activeAlerts = await this.getTeacherAlerts(teacherId, false);

    for (const alert of activeAlerts) {
      let shouldResolve = false;

      switch (alert.alertType) {
        case 'OVERWORK_WARNING':
          // Resolve if workload is back to acceptable levels
          if (currentWorkload.weeklyMetrics.workloadPercentage < 80) {
            shouldResolve = true;
          }
          break;
          
        case 'BURNOUT_RISK':
          // Resolve if wellness score improved significantly
          if (currentWorkload.wellnessScore > 60) {
            shouldResolve = true;
          }
          break;
          
        case 'CONSECUTIVE_PERIODS':
          // Resolve if consecutive periods are within limits
          const maxConsecutive = Math.max(
            ...Object.values(currentWorkload.dailyMetrics)
              .map((d: any) => d.consecutivePeriods)
          );
          if (maxConsecutive <= 3) {
            shouldResolve = true;
          }
          break;
      }

      if (shouldResolve) {
        await this.resolveAlert(alert.id, 'SYSTEM_AUTO_RESOLVE');
      }
    }
  }

  /**
   * Send real-time alert notification
   */
  private async sendRealTimeAlert(alert: any) {
    // Send to teacher
    await this.wsService.sendToUser(alert.teacher.userId, {
      type: 'NEW_WELLNESS_ALERT',
      data: {
        id: alert.id,
        severity: alert.severity,
        title: alert.title,
        message: alert.message,
        recommendations: alert.recommendations
      }
    });

    // Send to school administrators
    const admins = await prisma.user.findMany({
      where: {
        schoolId: alert.teacher.user.schoolId,
        role: { in: ['ADMIN', 'PRINCIPAL'] }
      }
    });

    for (const admin of admins) {
      await this.wsService.sendToUser(admin.id, {
        type: 'TEACHER_WELLNESS_ALERT',
        data: {
          teacherId: alert.teacherId,
          teacherName: alert.teacher.user.profile?.name || alert.teacher.user.email,
          alertId: alert.id,
          severity: alert.severity,
          title: alert.title,
          message: alert.message
        }
      });
    }
  }

  /**
   * Send email alert notification
   */
  private async sendEmailAlert(alert: any) {
    // Implementation would depend on your email service
    // This is a placeholder for email notification logic
    console.log(`Sending email alert for ${alert.id} to ${alert.teacher.user.email}`);
    
    // Example email content
    const emailData = {
      to: alert.teacher.user.email,
      subject: `Wellness Alert: ${alert.title}`,
      body: `
        Dear ${alert.teacher.user.profile?.name || 'Teacher'},
        
        A wellness alert has been triggered for your account:
        
        Alert: ${alert.title}
        Severity: ${alert.severity}
        Message: ${alert.message}
        
        ${alert.recommendations ? `
        Recommendations:
        ${JSON.stringify(alert.recommendations, null, 2)}
        ` : ''}
        
        Please log in to your dashboard to view more details and take appropriate action.
        
        Best regards,
        School Timetable Management System
      `
    };

    // TODO: Integrate with actual email service (SendGrid, AWS SES, etc.)
  }

  /**
   * Create bulk alerts for multiple teachers
   */
  async createBulkAlerts(alerts: Array<{
    teacherId: string;
    alertType: string;
    severity: AlertSeverity;
    title: string;
    message: string;
    recommendations?: any;
  }>) {
    const createdAlerts = [];

    for (const alertData of alerts) {
      try {
        const alert = await this.createAlert(alertData);
        createdAlerts.push(alert);
      } catch (error) {
        console.error(`Failed to create alert for teacher ${alertData.teacherId}:`, error);
      }
    }

    return createdAlerts;
  }

  /**
   * Get alert trends and analytics
   */
  async getAlertTrends(schoolId: string, days = 30) {
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);

    const trends = await prisma.workloadAlert.groupBy({
      by: ['alertType', 'severity'],
      where: {
        teacher: {
          user: {
            schoolId
          }
        },
        createdAt: {
          gte: startDate
        }
      },
      _count: true,
      orderBy: {
        _count: {
          _all: 'desc'
        }
      }
    });

    // Calculate resolution rates
    const resolutionStats = await prisma.workloadAlert.groupBy({
      by: ['resolved'],
      where: {
        teacher: {
          user: {
            schoolId
          }
        },
        createdAt: {
          gte: startDate
        }
      },
      _count: true
    });

    const totalAlerts = resolutionStats.reduce((sum, stat) => sum + stat._count, 0);
    const resolvedAlerts = resolutionStats.find(stat => stat.resolved)?._count || 0;
    const resolutionRate = totalAlerts > 0 ? (resolvedAlerts / totalAlerts) * 100 : 0;

    return {
      trends,
      resolutionRate,
      totalAlerts,
      resolvedAlerts,
      period: `${days} days`
    };
  }
}