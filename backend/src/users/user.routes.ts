import { Router } from 'express';
import { userService } from './user.service';
import { AuthPayload } from '../types/index';
import { authService } from '../auth/auth.service';

const router = Router();

// Middleware to verify token and attach payload
const authenticate = (req: any, res: any, next: any) => {
  try {
    const payload = authService.verifyToken(req);
    req.user = payload;
    next();
  } catch (error: any) {
    res.status(401).json({ message: error.message });
  }
};

// GET /users - List users in school
router.get('/', authenticate, async (req: any, res: any) => {
  try {
    const users = await userService.getAll(req.query.schoolId, req.user);
    res.json(users);
  } catch (error: any) {
    res.status(400).json({ message: error.message });
  }
});

// POST /users - Create user
router.post('/', authenticate, async (req: any, res: any) => {
  try {
    const user = await userService.create(req.body, req.user);
    res.status(201).json(user);
  } catch (error: any) {
    res.status(400).json({ message: error.message });
  }
});

// GET /users/:id
router.get('/:id', authenticate, async (req: any, res: any) => {
  try {
    const user = await userService.getById(req.params.id, req.user);
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
router.put('/:id', authenticate, async (req: any, res: any) => {
  try {
    const user = await userService.update(req.params.id, req.body, req.user);
    res.json(user);
  } catch (error: any) {
    res.status(400).json({ message: error.message });
  }
});

// DELETE /users/:id
router.delete('/:id', authenticate, async (req: any, res: any) => {
  try {
    await userService.delete(req.params.id, req.user);
    res.status(204).send();
  } catch (error: any) {
    res.status(400).json({ message: error.message });
  }
});

export default router;