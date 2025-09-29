import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateSubjectDto } from './dto/create-subject.dto';
import { UpdateSubjectDto } from './dto/update-subject.dto';

@Injectable()
export class SubjectsService {
  constructor(private prisma: PrismaService) {}

  async create(createSubjectDto: CreateSubjectDto) {
    return this.prisma.subject.create({
      data: createSubjectDto,
      include: {
        school: true,
      },
    });
  }

  async createBulk(createSubjectDtos: CreateSubjectDto[]) {
    const subjects = await Promise.all(
      createSubjectDtos.map(dto => this.create(dto))
    );
    return subjects;
  }

  async findAll(schoolId?: string, page: number = 1, limit: number = 10) {
    const skip = (page - 1) * limit;
    const where = schoolId ? { schoolId } : {};

    const [subjects, total] = await Promise.all([
      this.prisma.subject.findMany({
        where,
        skip,
        take: limit,
        include: {
          school: true,
        },
        orderBy: {
          name: 'asc',
        },
      }),
      this.prisma.subject.count({ where }),
    ]);

    return {
      data: subjects,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string) {
    const subject = await this.prisma.subject.findUnique({
      where: { id },
      include: {
        school: true,
        teachers: {
          include: {
            user: true,
          },
        },
        assignments: {
          include: {
            class: true,
            teacher: {
              include: {
                user: true,
              },
            },
          },
        },
      },
    });

    if (!subject) {
      throw new NotFoundException(`Subject with ID ${id} not found`);
    }

    return subject;
  }

  async update(id: string, updateSubjectDto: UpdateSubjectDto) {
    try {
      return await this.prisma.subject.update({
        where: { id },
        data: updateSubjectDto,
        include: {
          school: true,
        },
      });
    } catch (error) {
      throw new NotFoundException(`Subject with ID ${id} not found`);
    }
  }

  async remove(id: string) {
    try {
      return await this.prisma.subject.delete({
        where: { id },
      });
    } catch (error) {
      throw new NotFoundException(`Subject with ID ${id} not found`);
    }
  }
}