import { Request, Response, NextFunction } from 'express';
import { authService } from '../../auth/auth.service';
import { AuthPayload } from '../../types';

declare global {
  namespace Express {
    interface Request {
      user?: AuthPayload;
    }
  }
}

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  try {
    const payload = authService.verifyToken(req);
    req.user = payload;
    next();
  } catch (error: any) {
    res.status(401).json({ message: error.message || 'Unauthorized' });
  }
};
