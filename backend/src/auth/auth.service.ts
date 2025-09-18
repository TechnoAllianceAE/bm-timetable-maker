import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { Request, Response } from 'express';
import Joi from 'joi';
import { Role } from '@prisma/client';

const prisma = new PrismaClient();
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-prod';
const SALT_ROUNDS = 10;

interface RegisterData {
  email: string;
  password: string;
  role: Role;
  schoolId: string;
  profile?: any;
}

interface LoginData {
  email: string;
  password: string;
}

const registerSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(6).required(),
  role: Joi.string().valid(...Object.values(Role)).required(),
  schoolId: Joi.string().required(),
  profile: Joi.object().optional()
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});

export class AuthService {
  async register(data: RegisterData) {
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
        profile: data.profile || {},
        wellnessPreferences: {}
      },
      include: { teacher: true }  // If role is TEACHER, create teacher record
    });

    // If teacher, create teacher record
    if (data.role === Role.TEACHER) {
      await prisma.teacher.create({
        data: {
          userId: user.id,
          subjects: [],  // Empty, update later
          availability: {},
          preferences: {}
        }
      });
    }

    const token = jwt.sign({ userId: user.id, role: user.role }, JWT_SECRET, { expiresIn: '24h' });

    return {
      user: { id: user.id, email: user.email, role: user.role, profile: user.profile },
      token
    };
  }

  async login(data: LoginData) {
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

    const token = jwt.sign({ userId: user.id, role: user.role }, JWT_SECRET, { expiresIn: '24h' });

    return {
      user: { id: user.id, email: user.email, role: user.role, profile: user.profile },
      token
    };
  }

  verifyToken(req: Request) {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      throw new Error('No token provided');
    }

    try {
      const decoded = jwt.verify(token, JWT_SECRET) as { userId: string; role: Role };
      return decoded;
    } catch (err) {
      throw new Error('Invalid token');
    }
  }
}

export const authService = new AuthService();