import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import { CreateUserRequest, UpdateUserRequest, AuthPayload, Role } from '../types';

const prisma = new PrismaClient();
const SALT_ROUNDS = 10;
const ADMIN_ROLES: Role[] = ['ADMIN', 'PRINCIPAL'];

export class UserService {
  async getAll(schoolId: string, user: AuthPayload) {
    if (!ADMIN_ROLES.includes(user.role)) {
      throw new Error('Insufficient permissions');
    }

    const users = await prisma.user.findMany({
      where: { schoolId },
      include: { teacher: true }
    });

    return users.map(this.formatUser);
  }

  async create(data: CreateUserRequest, user: AuthPayload) {
    if (!ADMIN_ROLES.includes(user.role)) {
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
        profile: profile ? JSON.stringify(profile) : null,
        wellnessPreferences: JSON.stringify({})
      },
      include: { teacher: true }
    });

    if (role === 'TEACHER') {
      await prisma.teacher.create({
        data: {
          userId: newUser.id,
          subjects: JSON.stringify([]),
          availability: JSON.stringify({}),
          preferences: JSON.stringify({})
        }
      });
    }

    return this.formatUser(newUser);
  }

  async getById(id: string, user: AuthPayload) {
    const foundUser = await prisma.user.findUnique({
      where: { id },
      include: { teacher: true }
    });

    if (!foundUser) {
      throw new Error('User not found');
    }

    if (!ADMIN_ROLES.includes(user.role) && user.userId !== id) {
      throw new Error('Insufficient permissions');
    }

    return this.formatUser(foundUser);
  }

  async update(id: string, data: UpdateUserRequest, user: AuthPayload) {
    if (!ADMIN_ROLES.includes(user.role) && user.userId !== id) {
      throw new Error('Insufficient permissions');
    }

    const { email, role, profile, wellnessPreferences } = data;

    const updatedUser = await prisma.user.update({
      where: { id },
      data: {
        email,
        role,
        profile: profile ? JSON.stringify(profile) : undefined,
        wellnessPreferences: wellnessPreferences ? JSON.stringify(wellnessPreferences) : undefined
      },
      include: { teacher: true }
    });

    return this.formatUser(updatedUser);
  }

  async delete(id: string, user: AuthPayload) {
    if (!ADMIN_ROLES.includes(user.role)) {
      throw new Error('Insufficient permissions');
    }

    await prisma.user.delete({
      where: { id }
    });
  }

  private formatUser = (user: any) => ({
    ...user,
    profile: this.parse(user.profile),
    wellnessPreferences: this.parse(user.wellnessPreferences)
  });

  private parse(value: unknown) {
    if (!value) return null;
    if (typeof value === 'object') return value as Record<string, unknown>;
    if (typeof value === 'string') {
      try {
        return JSON.parse(value);
      } catch {
        return null;
      }
    }
    return null;
  }
}

export const userService = new UserService();
