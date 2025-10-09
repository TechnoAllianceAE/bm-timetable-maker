import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateRoomDto } from './dto/create-room.dto';
import { UpdateRoomDto } from './dto/update-room.dto';

@Injectable()
export class RoomsService {
  constructor(private prisma: PrismaService) {}

  async create(createRoomDto: CreateRoomDto) {
    return this.prisma.room.create({
      data: {
        schoolId: createRoomDto.schoolId!,
        name: createRoomDto.name,
        code: createRoomDto.code,
        capacity: createRoomDto.capacity,
        type: createRoomDto.type,
      },
      include: {
        school: true,
      },
    });
  }

  async createBulk(createRoomDtos: CreateRoomDto[]) {
    const rooms = await Promise.all(
      createRoomDtos.map(dto => this.create(dto))
    );
    return rooms;
  }

  async findAll(schoolId?: string, type?: string, page: number = 1, limit: number = 10) {
    const skip = (page - 1) * limit;
    const where: any = {};

    if (schoolId) where.schoolId = schoolId;
    if (type) where.type = type;

    const [rooms, total] = await Promise.all([
      this.prisma.room.findMany({
        where,
        skip,
        take: limit,
        include: {
          school: true,
        },
        orderBy: [
          { name: 'asc' },
        ],
      }),
      this.prisma.room.count({ where }),
    ]);

    return {
      data: rooms,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string) {
    const room = await this.prisma.room.findUnique({
      where: { id },
      include: {
        school: true,
        timetableEntries: {
          include: {
            timetable: true,
            timeSlot: true,
            teacher: true,
            subject: true,
          },
        },
      },
    });

    if (!room) {
      throw new NotFoundException(`Room with ID ${id} not found`);
    }

    return room;
  }

  async update(id: string, updateRoomDto: UpdateRoomDto) {
    try {
      return await this.prisma.room.update({
        where: { id },
        data: updateRoomDto,
        include: {
          school: true,
        },
      });
    } catch (error) {
      throw new NotFoundException(`Room with ID ${id} not found`);
    }
  }

  async remove(id: string) {
    try {
      return await this.prisma.room.delete({
        where: { id },
      });
    } catch (error) {
      throw new NotFoundException(`Room with ID ${id} not found`);
    }
  }
}