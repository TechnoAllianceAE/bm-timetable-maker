import { Router } from 'express';
import { userService } from './user.service';
import { authMiddleware } from '../shared/middleware/auth';

const router = Router();

// GET /users - List users in school
router.get('/', authMiddleware, async (req, res) => {
  try {
    const schoolId = (req.query.schoolId as string) || req.user?.schoolId;
    if (!schoolId) {
      return res.status(400).json({ message: 'schoolId is required' });
    }
    const users = await userService.getAll(schoolId, req.user!);
    res.json(users);
  } catch (error: any) {
    res.status(400).json({ message: error.message });
  }
});

// POST /users - Create user
router.post('/', authMiddleware, async (req, res) => {
  try {
    const user = await userService.create(req.body, req.user!);
    res.status(201).json(user);
  } catch (error: any) {
    res.status(400).json({ message: error.message });
  }
});

// GET /users/:id
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const user = await userService.getById(req.params.id, req.user!);
    res.json(user);
  } catch (error: any) {
    if (error.message === 'User not found') {
      res.status(404).json({ message: error.message });
    } else {
      res.status(400).json({ message: error.message });
    }
  }
});

// PUT /users/:id
router.put('/:id', authMiddleware, async (req, res) => {
  try {
    const user = await userService.update(req.params.id, req.body, req.user!);
    res.json(user);
  } catch (error: any) {
    res.status(400).json({ message: error.message });
  }
});

// DELETE /users/:id
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    await userService.delete(req.params.id, req.user!);
    res.status(204).send();
  } catch (error: any) {
    res.status(400).json({ message: error.message });
  }
});

export default router;
