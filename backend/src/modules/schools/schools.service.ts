import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateSchoolDto } from './dto/create-school.dto';
import { UpdateSchoolDto } from './dto/update-school.dto';

@Injectable()
export class SchoolsService {
  constructor(private prisma: PrismaService) {}

  async create(createSchoolDto: CreateSchoolDto) {
    return this.prisma.school.create({
      data: createSchoolDto,
    });
  }

  async findAll(page: number = 1, limit: number = 10) {
    const skip = (page - 1) * limit;

    const [schools, total] = await Promise.all([
      this.prisma.school.findMany({
        skip,
        take: limit,
        orderBy: {
          createdAt: 'desc',
        },
      }),
      this.prisma.school.count(),
    ]);

    return {
      data: schools,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string) {
    const school = await this.prisma.school.findUnique({
      where: { id },
      include: {
        users: true,
        classes: true,
        subjects: true,
        rooms: true,
      },
    });

    if (!school) {
      throw new NotFoundException(`School with ID ${id} not found`);
    }

    return school;
  }

  async update(id: string, updateSchoolDto: UpdateSchoolDto) {
    try {
      return await this.prisma.school.update({
        where: { id },
        data: updateSchoolDto,
      });
    } catch (error) {
      throw new NotFoundException(`School with ID ${id} not found`);
    }
  }

  async remove(id: string) {
    try {
      return await this.prisma.school.delete({
        where: { id },
      });
    } catch (error) {
      throw new NotFoundException(`School with ID ${id} not found`);
    }
  }
}