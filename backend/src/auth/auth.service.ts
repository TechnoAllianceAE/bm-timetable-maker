import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { Request } from 'express';
import Joi from 'joi';
import { ROLE_VALUES, Role, AuthPayload } from '../types';

const prisma = new PrismaClient();
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-prod';
const SALT_ROUNDS = 10;

const registerSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(6).required(),
  role: Joi.string().valid(...ROLE_VALUES).required(),
  schoolId: Joi.string().required(),
  profile: Joi.object().optional()
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});

export class AuthService {
  async register(data: { email: string; password: string; role: Role; schoolId: string; profile?: Record<string, unknown> }) {
    const { error } = registerSchema.validate(data);
    if (error) {
      throw new Error(error.details[0].message);
    }

    const existingUser = await prisma.user.findUnique({
      where: { email: data.email }
    });

    if (existingUser) {
      throw new Error('User already exists');
    }

    const passwordHash = await bcrypt.hash(data.password, SALT_ROUNDS);

    const user = await prisma.user.create({
      data: {
        schoolId: data.schoolId,
        email: data.email,
        passwordHash,
        role: data.role,
        profile: this.stringify(data.profile),
        wellnessPreferences: this.stringify({})
      }
    });

    // If teacher, create teacher record
    if (data.role === 'TEACHER') {
      await prisma.teacher.create({
        data: {
          userId: user.id,
          subjects: JSON.stringify([]),
          availability: JSON.stringify({}),
          preferences: JSON.stringify({})
        }
      });
    }

    const token = this.signToken({
      userId: user.id,
      role: user.role as Role,
      schoolId: user.schoolId,
      email: user.email
    });

    return {
      user: {
        id: user.id,
        email: user.email,
        role: user.role as Role,
        schoolId: user.schoolId,
        profile: this.parse(user.profile)
      },
      token
    };
  }

  async login(data: { email: string; password: string }) {
    const { error } = loginSchema.validate(data);
    if (error) {
      throw new Error(error.details[0].message);
    }

    const user = await prisma.user.findUnique({
      where: { email: data.email },
      include: { teacher: true }
    });

    if (!user || !user.passwordHash) {
      throw new Error('Invalid credentials');
    }

    const isValid = await bcrypt.compare(data.password, user.passwordHash);
    if (!isValid) {
      throw new Error('Invalid credentials');
    }

    const token = this.signToken({
      userId: user.id,
      role: user.role as Role,
      schoolId: user.schoolId,
      email: user.email
    });

    return {
      user: {
        id: user.id,
        email: user.email,
        role: user.role as Role,
        schoolId: user.schoolId,
        profile: this.parse(user.profile)
      },
      token
    };
  }

  verifyToken(req: Request): AuthPayload {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      throw new Error('No token provided');
    }

    try {
      const decoded = jwt.verify(token, JWT_SECRET) as AuthPayload;
      return decoded;
    } catch (err) {
      throw new Error('Invalid token');
    }
  }

  private signToken(payload: AuthPayload) {
    return jwt.sign(payload, JWT_SECRET, { expiresIn: '24h' });
  }

  private stringify(value: unknown) {
    if (value === undefined || value === null) {
      return null;
    }
    return JSON.stringify(value);
  }

  private parse(value: unknown) {
    if (!value) return null;
    if (typeof value === 'object') return value as Record<string, unknown>;
    if (typeof value === 'string') {
      try {
        return JSON.parse(value) as Record<string, unknown>;
      } catch {
        return null;
      }
    }
    return null;
  }
}

export const authService = new AuthService();
