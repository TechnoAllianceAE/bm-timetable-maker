import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateTeacherDto } from './dto/create-teacher.dto';
import { UpdateTeacherDto } from './dto/update-teacher.dto';

@Injectable()
export class TeachersService {
  constructor(private prisma: PrismaService) {}

  async create(createTeacherDto: CreateTeacherDto) {
    const { subjects, preferences, availability, ...teacherData } = createTeacherDto;

    return this.prisma.teacher.create({
      data: {
        ...teacherData,
        subjects: JSON.stringify(subjects || []),
        preferences: JSON.stringify(preferences || []),
        availability: JSON.stringify(availability || {}),
      },
      include: {
        user: true,
      },
    });
  }

  async createBulk(createTeacherDtos: CreateTeacherDto[]) {
    const teachers = await Promise.all(
      createTeacherDtos.map(dto => this.create(dto))
    );
    return teachers;
  }

  async findAll(schoolId?: string, page?: number, limit?: number) {
    const pageNum = page || 1;
    const limitNum = limit || 10;
    const skip = (pageNum - 1) * limitNum;
    const where = schoolId ? { user: { schoolId } } : {};

    const [teachers, total] = await Promise.all([
      this.prisma.teacher.findMany({
        where,
        skip,
        take: limitNum,
        include: {
          user: true,
        },
      }),
      this.prisma.teacher.count({ where }),
    ]);

    return {
      data: teachers,
      meta: {
        total,
        page: pageNum,
        limit: limitNum,
        totalPages: Math.ceil(total / limitNum),
      },
    };
  }

  async findOne(id: string) {
    const teacher = await this.prisma.teacher.findUnique({
      where: { id },
      include: {
        user: true,
        timetableEntries: {
          include: {
            class: true,
            subject: true,
            timeSlot: true,
            room: true,
          },
        },
      },
    });

    if (!teacher) {
      throw new NotFoundException(`Teacher with ID ${id} not found`);
    }

    return teacher;
  }

  async update(id: string, updateTeacherDto: UpdateTeacherDto) {
    const { subjects, preferences, availability, ...teacherData } = updateTeacherDto;

    try {
      return await this.prisma.teacher.update({
        where: { id },
        data: {
          ...teacherData,
          ...(subjects && {
            subjects: JSON.stringify(subjects),
          }),
          ...(preferences && {
            preferences: JSON.stringify(preferences),
          }),
          ...(availability && {
            availability: JSON.stringify(availability),
          }),
        },
        include: {
          user: true,
        },
      });
    } catch (error) {
      throw new NotFoundException(`Teacher with ID ${id} not found`);
    }
  }

  async remove(id: string) {
    try {
      return await this.prisma.teacher.delete({
        where: { id },
      });
    } catch (error) {
      throw new NotFoundException(`Teacher with ID ${id} not found`);
    }
  }
}