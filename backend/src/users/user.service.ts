import { PrismaClient, Role } from '@prisma/client';
import bcrypt from 'bcryptjs';
import { CreateUserRequest, UpdateUserRequest, AuthPayload } from '../types';

const prisma = new PrismaClient();
const SALT_ROUNDS = 10;

export class UserService {
  async getAll(schoolId: string, user: AuthPayload) {
    if (user.role !== Role.ADMIN && user.role !== Role.PRINCIPAL) {
      throw new Error('Insufficient permissions');
    }

    return prisma.user.findMany({
      where: { schoolId },
      include: { teacher: true }
    });
  }

  async create(data: CreateUserRequest, user: AuthPayload) {
    if (user.role !== Role.ADMIN && user.role !== Role.PRINCIPAL) {
      throw new Error('Insufficient permissions');
    }

    const { email, password, role, schoolId, profile } = data;

    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      throw new Error('User already exists');
    }

    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

    const newUser = await prisma.user.create({
      data: {
        schoolId,
        email,
        passwordHash,
        role,
        profile: profile || {},
        wellnessPreferences: {}
      },
      include: { teacher: true }
    });

    // If teacher, create teacher record
    if (role === Role.TEACHER) {
      await prisma.teacher.create({
        data: {
          userId: newUser.id,
          subjects: [],
          availability: {},
          preferences: {}
        }
      });
    }

    return newUser;
  }

  async getById(id: string, user: AuthPayload) {
    const foundUser = await prisma.user.findUnique({
      where: { id },
      include: { teacher: true }
    });

    if (!foundUser) {
      throw new Error('User not found');
    }

    // Permission: Own or admin
    if (user.role !== Role.ADMIN && user.role !== Role.PRINCIPAL && user.userId !== id) {
      throw new Error('Insufficient permissions');
    }

    return foundUser;
  }

  async update(id: string, data: UpdateUserRequest, user: AuthPayload) {
    if (user.role !== Role.ADMIN && user.role !== Role.PRINCIPAL && user.userId !== id) {
      throw new Error('Insufficient permissions');
    }

    const { email, role, profile, wellnessPreferences } = data;

    const updatedUser = await prisma.user.update({
      where: { id },
      data: {
        email,
        role,
        profile,
        wellnessPreferences
      },
      include: { teacher: true }
    });

    return updatedUser;
  }

  async delete(id: string, user: AuthPayload) {
    if (user.role !== Role.ADMIN && user.role !== Role.PRINCIPAL) {
      throw new Error('Insufficient permissions');
    }

    await prisma.user.delete({
      where: { id }
    });
  }
}

export const userService = new UserService();