import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateClassDto } from './dto/create-class.dto';
import { UpdateClassDto } from './dto/update-class.dto';

@Injectable()
export class ClassesService {
  constructor(private prisma: PrismaService) {}

  async create(createClassDto: CreateClassDto) {
    return this.prisma.class.create({
      data: createClassDto,
      include: {
        school: true,
      },
    });
  }

  async createBulk(createClassDtos: CreateClassDto[]) {
    const classes = await Promise.all(
      createClassDtos.map(dto => this.create(dto))
    );
    return classes;
  }

  async findAll(schoolId?: string, page?: number, limit?: number) {
    const pageNum = page || 1;
    const limitNum = limit || 10;
    const skip = (pageNum - 1) * limitNum;
    const where = schoolId ? { schoolId } : {};

    const [classes, total] = await Promise.all([
      this.prisma.class.findMany({
        where,
        skip,
        take: limitNum,
        include: {
          school: true,
        },
        orderBy: [
          { grade: 'asc' },
          { section: 'asc' },
        ],
      }),
      this.prisma.class.count({ where }),
    ]);

    return {
      data: classes,
      meta: {
        total,
        page: pageNum,
        limit: limitNum,
        totalPages: Math.ceil(total / limitNum),
      },
    };
  }

  async findOne(id: string) {
    const classData = await this.prisma.class.findUnique({
      where: { id },
      include: {
        school: true,
        timetableEntries: {
          include: {
            teacher: {
              include: {
                user: true,
              },
            },
            subject: true,
            timeSlot: true,
            room: true,
          },
        },
      },
    });

    if (!classData) {
      throw new NotFoundException(`Class with ID ${id} not found`);
    }

    return classData;
  }

  async update(id: string, updateClassDto: UpdateClassDto) {
    try {
      return await this.prisma.class.update({
        where: { id },
        data: updateClassDto,
        include: {
          school: true,
        },
      });
    } catch (error) {
      throw new NotFoundException(`Class with ID ${id} not found`);
    }
  }

  async remove(id: string) {
    try {
      return await this.prisma.class.delete({
        where: { id },
      });
    } catch (error) {
      throw new NotFoundException(`Class with ID ${id} not found`);
    }
  }
}