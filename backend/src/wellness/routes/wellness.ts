import { Router } from 'express';
import { WorkloadMonitorService } from '../services/workloadMonitor';
import { AlertManagerService } from '../services/alertManager';
import { WellnessAnalyticsService } from '../services/wellnessAnalytics';
import { authMiddleware } from '../../shared/middleware/auth';
import { validateRequest } from '../../shared/middleware/validation';
import { WebSocketService } from '../../shared/websocket/websocketService';
import Joi from 'joi';

const router = Router();
const workloadMonitor = new WorkloadMonitorService();
const wellnessAnalytics = new WellnessAnalyticsService();

// Initialize WebSocket service (this would be passed from main app)
let wsService: WebSocketService;
export const setWebSocketService = (ws: WebSocketService) => {
  wsService = ws;
};

const alertManager = new AlertManagerService(wsService);

// Validation schemas
const teacherIdSchema = Joi.object({
  teacherId: Joi.string().required()
});

const dateRangeSchema = Joi.object({
  startDate: Joi.date().optional(),
  endDate: Joi.date().optional()
});

const alertAckSchema = Joi.object({
  alertId: Joi.string().required()
});

/**
 * GET /api/wellness/teacher/:teacherId/workload
 * Get current workload metrics for a teacher
 */
router.get('/teacher/:teacherId/workload', 
  authMiddleware,
  validateRequest({ params: teacherIdSchema }),
  async (req, res) => {
    try {
      const { teacherId } = req.params;
      const workload = await workloadMonitor.calculateTeacherWorkload(teacherId);
      
      res.json({
        success: true,
        data: workload
      });
    } catch (error) {
      console.error('Error fetching teacher workload:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch workload data'
      });
    }
  }
);

/**
 * GET /api/wellness/teacher/:teacherId/report
 * Generate comprehensive wellness report for a teacher
 */
router.get('/teacher/:teacherId/report',
  authMiddleware,
  validateRequest({ 
    params: teacherIdSchema,
    query: dateRangeSchema
  }),
  async (req, res) => {
    try {
      const { teacherId } = req.params;
      const { startDate, endDate } = req.query;
      
      const timeRange = startDate && endDate ? {
        start: new Date(startDate as string),
        end: new Date(endDate as string)
      } : undefined;

      const report = await wellnessAnalytics.generateTeacherWellnessReport(teacherId, timeRange);
      
      res.json({
        success: true,
        data: report
      });
    } catch (error) {
      console.error('Error generating wellness report:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to generate wellness report'
      });
    }
  }
);

/**
 * GET /api/wellness/teacher/:teacherId/alerts
 * Get alerts for a specific teacher
 */
router.get('/teacher/:teacherId/alerts',
  authMiddleware,
  validateRequest({ params: teacherIdSchema }),
  async (req, res) => {
    try {
      const { teacherId } = req.params;
      const includeResolved = req.query.includeResolved === 'true';
      
      const alerts = await alertManager.getTeacherAlerts(teacherId, includeResolved);
      
      res.json({
        success: true,
        data: alerts
      });
    } catch (error) {
      console.error('Error fetching teacher alerts:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch alerts'
      });
    }
  }
);

/**
 * POST /api/wellness/alerts/:alertId/acknowledge
 * Acknowledge a wellness alert
 */
router.post('/alerts/:alertId/acknowledge',
  authMiddleware,
  validateRequest({ params: alertAckSchema }),
  async (req, res) => {
    try {
      const { alertId } = req.params;
      const userId = req.user?.id;
      
      if (!userId) {
        return res.status(401).json({
          success: false,
          error: 'User not authenticated'
        });
      }

      const alert = await alertManager.acknowledgeAlert(alertId, userId);
      
      res.json({
        success: true,
        data: alert
      });
    } catch (error) {
      console.error('Error acknowledging alert:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to acknowledge alert'
      });
    }
  }
);

/**
 * POST /api/wellness/alerts/:alertId/resolve
 * Resolve a wellness alert
 */
router.post('/alerts/:alertId/resolve',
  authMiddleware,
  validateRequest({ params: alertAckSchema }),
  async (req, res) => {
    try {
      const { alertId } = req.params;
      const userId = req.user?.id;

      const alert = await alertManager.resolveAlert(alertId, userId);
      
      res.json({
        success: true,
        data: alert
      });
    } catch (error) {
      console.error('Error resolving alert:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to resolve alert'
      });
    }
  }
);

/**
 * GET /api/wellness/school/dashboard
 * Get school-wide wellness dashboard data
 */
router.get('/school/dashboard',
  authMiddleware,
  async (req, res) => {
    try {
      const schoolId = req.user?.schoolId;
      
      if (!schoolId) {
        return res.status(400).json({
          success: false,
          error: 'School ID not found'
        });
      }

      const dashboard = await wellnessAnalytics.generateSchoolWellnessDashboard(schoolId);
      
      res.json({
        success: true,
        data: dashboard
      });
    } catch (error) {
      console.error('Error fetching school dashboard:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch dashboard data'
      });
    }
  }
);

/**
 * GET /api/wellness/school/alerts
 * Get all active alerts for the school
 */
router.get('/school/alerts',
  authMiddleware,
  async (req, res) => {
    try {
      const schoolId = req.user?.schoolId;
      const severity = req.query.severity as any;
      
      if (!schoolId) {
        return res.status(400).json({
          success: false,
          error: 'School ID not found'
        });
      }

      const alerts = await alertManager.getSchoolAlerts(schoolId, severity);
      
      res.json({
        success: true,
        data: alerts
      });
    } catch (error) {
      console.error('Error fetching school alerts:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch alerts'
      });
    }
  }
);

/**
 * GET /api/wellness/department/:department/overview
 * Get department wellness overview
 */
router.get('/department/:department/overview',
  authMiddleware,
  async (req, res) => {
    try {
      const { department } = req.params;
      const schoolId = req.user?.schoolId;
      
      if (!schoolId) {
        return res.status(400).json({
          success: false,
          error: 'School ID not found'
        });
      }

      const overview = await wellnessAnalytics.generateDepartmentWellnessOverview(schoolId, department);
      
      res.json({
        success: true,
        data: overview
      });
    } catch (error) {
      console.error('Error fetching department overview:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch department overview'
      });
    }
  }
);

/**
 * POST /api/wellness/monitor/run
 * Manually trigger wellness monitoring for all teachers
 */
router.post('/monitor/run',
  authMiddleware,
  async (req, res) => {
    try {
      const schoolId = req.user?.schoolId;
      
      if (!schoolId) {
        return res.status(400).json({
          success: false,
          error: 'School ID not found'
        });
      }

      // Check if user has admin privileges
      if (!['ADMIN', 'PRINCIPAL'].includes(req.user?.role)) {
        return res.status(403).json({
          success: false,
          error: 'Insufficient permissions'
        });
      }

      const results = await workloadMonitor.monitorAllTeachers(schoolId);
      
      res.json({
        success: true,
        data: {
          message: 'Wellness monitoring completed',
          teachersMonitored: results.length,
          results: results.slice(0, 5) // Return first 5 for preview
        }
      });
    } catch (error) {
      console.error('Error running wellness monitoring:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to run wellness monitoring'
      });
    }
  }
);

/**
 * GET /api/wellness/alerts/statistics
 * Get alert statistics for the school
 */
router.get('/alerts/statistics',
  authMiddleware,
  async (req, res) => {
    try {
      const schoolId = req.user?.schoolId;
      const days = parseInt(req.query.days as string) || 30;
      
      if (!schoolId) {
        return res.status(400).json({
          success: false,
          error: 'School ID not found'
        });
      }

      const timeRange = {
        start: new Date(Date.now() - days * 24 * 60 * 60 * 1000),
        end: new Date()
      };

      const statistics = await alertManager.getAlertStatistics(schoolId, timeRange);
      
      res.json({
        success: true,
        data: statistics
      });
    } catch (error) {
      console.error('Error fetching alert statistics:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch alert statistics'
      });
    }
  }
);

/**
 * GET /api/wellness/alerts/trends
 * Get alert trends and analytics
 */
router.get('/alerts/trends',
  authMiddleware,
  async (req, res) => {
    try {
      const schoolId = req.user?.schoolId;
      const days = parseInt(req.query.days as string) || 30;
      
      if (!schoolId) {
        return res.status(400).json({
          success: false,
          error: 'School ID not found'
        });
      }

      const trends = await alertManager.getAlertTrends(schoolId, days);
      
      res.json({
        success: true,
        data: trends
      });
    } catch (error) {
      console.error('Error fetching alert trends:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch alert trends'
      });
    }
  }
);

export default router;