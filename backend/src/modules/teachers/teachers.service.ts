import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateTeacherDto } from './dto/create-teacher.dto';
import { UpdateTeacherDto } from './dto/update-teacher.dto';

@Injectable()
export class TeachersService {
  constructor(private prisma: PrismaService) {}

  async create(createTeacherDto: CreateTeacherDto) {
    const { subjects, ...teacherData } = createTeacherDto;

    return this.prisma.teacher.create({
      data: {
        ...teacherData,
        subjects: {
          connect: subjects?.map(id => ({ id })) || [],
        },
      },
      include: {
        user: true,
        subjects: true,
      },
    });
  }

  async createBulk(createTeacherDtos: CreateTeacherDto[]) {
    const teachers = await Promise.all(
      createTeacherDtos.map(dto => this.create(dto))
    );
    return teachers;
  }

  async findAll(schoolId?: string, page: number = 1, limit: number = 10) {
    const skip = (page - 1) * limit;
    const where = schoolId ? { user: { schoolId } } : {};

    const [teachers, total] = await Promise.all([
      this.prisma.teacher.findMany({
        where,
        skip,
        take: limit,
        include: {
          user: true,
          subjects: true,
        },
        orderBy: {
          createdAt: 'desc',
        },
      }),
      this.prisma.teacher.count({ where }),
    ]);

    return {
      data: teachers,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string) {
    const teacher = await this.prisma.teacher.findUnique({
      where: { id },
      include: {
        user: true,
        subjects: true,
        assignments: {
          include: {
            class: true,
            subject: true,
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
    const { subjects, ...teacherData } = updateTeacherDto;

    try {
      return await this.prisma.teacher.update({
        where: { id },
        data: {
          ...teacherData,
          ...(subjects && {
            subjects: {
              set: [],
              connect: subjects.map(id => ({ id })),
            },
          }),
        },
        include: {
          user: true,
          subjects: true,
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