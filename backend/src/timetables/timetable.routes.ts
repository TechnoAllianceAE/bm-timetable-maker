import { Router } from 'express';
import Joi from 'joi';
import { authMiddleware } from '../shared/middleware/auth';
import { validateRequest } from '../shared/middleware/validation';
import { timetableService } from './timetable.service';

const router = Router();

const createTimetableSchema = Joi.object({
  academicYearId: Joi.string().required(),
  name: Joi.string().optional(),
  metadata: Joi.object().optional()
});

const generateSchema = Joi.object({
  options: Joi.number().integer().min(1).max(5).optional(),
  timeout: Joi.number().integer().min(10).max(300).optional(),
  weights: Joi.object({
    academic: Joi.number().min(0).max(1).optional(),
    wellness: Joi.number().min(0).max(1).optional(),
    efficiency: Joi.number().min(0).max(1).optional(),
    preference: Joi.number().min(0).max(1).optional()
  }).optional()
});

router.get('/', authMiddleware, async (req, res) => {
  try {
    const timetables = await timetableService.listTimetables(req.user!.schoolId);
    res.json({ success: true, data: timetables });
  } catch (error: any) {
    res.status(500).json({ success: false, message: error.message });
  }
});

router.post(
  '/',
  authMiddleware,
  validateRequest({ body: createTimetableSchema }),
  async (req, res) => {
    try {
      const timetable = await timetableService.createTimetable(req.body, req.user!);
      res.status(201).json({ success: true, data: timetable });
    } catch (error: any) {
      res.status(400).json({ success: false, message: error.message });
    }
  }
);

router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const timetable = await timetableService.getTimetableById(req.params.id, req.user!);
    res.json({ success: true, data: timetable });
  } catch (error: any) {
    const status = error.message === 'Timetable not found' ? 404 : 400;
    res.status(status).json({ success: false, message: error.message });
  }
});

router.get('/:id/entries', authMiddleware, async (req, res) => {
  try {
    const entries = await timetableService.getEntries(req.params.id, req.user!);
    res.json({ success: true, data: entries });
  } catch (error: any) {
    const status = error.message === 'Timetable not found' ? 404 : 400;
    res.status(status).json({ success: false, message: error.message });
  }
});

router.post(
  '/:id/generate',
  authMiddleware,
  validateRequest({ body: generateSchema }),
  async (req, res) => {
    try {
      const result = await timetableService.generateTimetable(req.params.id, req.user!, req.body);
      res.json({ success: true, data: result });
    } catch (error: any) {
      const status = error.message === 'Timetable not found' ? 404 : 400;
      res.status(status).json({ success: false, message: error.message });
    }
  }
);

export default router;
