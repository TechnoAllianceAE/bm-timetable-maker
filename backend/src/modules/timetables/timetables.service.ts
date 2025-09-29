import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import { GenerateTimetableDto } from './dto/generate-timetable.dto';
import { UpdateTimetableDto } from './dto/update-timetable.dto';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class TimetablesService {
  constructor(
    private prisma: PrismaService,
    private httpService: HttpService,
    private configService: ConfigService,
  ) {}

  async generate(generateTimetableDto: GenerateTimetableDto) {
    const { schoolId } = generateTimetableDto;

    // Fetch school data
    const school = await this.prisma.school.findUnique({
      where: { id: schoolId },
      include: {
        classes: true,
        teachers: {
          include: {
            user: true,
            subjects: true,
          },
        },
        subjects: true,
        rooms: true,
      },
    });

    if (!school) {
      throw new NotFoundException(`School with ID ${schoolId} not found`);
    }

    // Prepare data for Python service
    const timetableData = {
      school: {
        id: school.id,
        name: school.name,
        settings: school.settings,
      },
      classes: school.classes,
      teachers: school.teachers.map(teacher => ({
        id: teacher.id,
        name: `${teacher.user.profile?.firstName || ''} ${teacher.user.profile?.lastName || ''}`.trim(),
        subjects: teacher.subjects.map(s => s.id),
        availability: teacher.availability,
        maxPeriodsPerDay: teacher.maxPeriodsPerDay,
        maxPeriodsPerWeek: teacher.maxPeriodsPerWeek,
      })),
      subjects: school.subjects,
      rooms: school.rooms.filter(room => room.isAvailable),
      constraints: generateTimetableDto.constraints,
    };

    try {
      // Call Python timetable generation service
      const pythonUrl = this.configService.get('PYTHON_TIMETABLE_URL') || 'http://localhost:8000';
      const response = await firstValueFrom(
        this.httpService.post(`${pythonUrl}/generate`, timetableData)
      );

      // Save timetable to database
      const timetable = await this.prisma.timetable.create({
        data: {
          schoolId,
          name: generateTimetableDto.name || `Timetable ${new Date().toISOString()}`,
          status: 'DRAFT',
          metadata: response.data,
        },
      });

      return {
        timetable,
        generatedData: response.data,
      };
    } catch (error) {
      throw new BadRequestException('Failed to generate timetable: ' + error.message);
    }
  }

  async findAll(schoolId?: string, status?: string, page: number = 1, limit: number = 10) {
    const skip = (page - 1) * limit;
    const where: any = {};

    if (schoolId) where.schoolId = schoolId;
    if (status) where.status = status;

    const [timetables, total] = await Promise.all([
      this.prisma.timetable.findMany({
        where,
        skip,
        take: limit,
        include: {
          school: true,
        },
        orderBy: {
          createdAt: 'desc',
        },
      }),
      this.prisma.timetable.count({ where }),
    ]);

    return {
      data: timetables,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string) {
    const timetable = await this.prisma.timetable.findUnique({
      where: { id },
      include: {
        school: true,
        slots: {
          include: {
            class: true,
            subject: true,
            teacher: {
              include: {
                user: true,
              },
            },
            room: true,
            timeSlot: true,
          },
        },
      },
    });

    if (!timetable) {
      throw new NotFoundException(`Timetable with ID ${id} not found`);
    }

    return timetable;
  }

  async update(id: string, updateTimetableDto: UpdateTimetableDto) {
    try {
      return await this.prisma.timetable.update({
        where: { id },
        data: updateTimetableDto,
      });
    } catch (error) {
      throw new NotFoundException(`Timetable with ID ${id} not found`);
    }
  }

  async remove(id: string) {
    try {
      return await this.prisma.timetable.delete({
        where: { id },
      });
    } catch (error) {
      throw new NotFoundException(`Timetable with ID ${id} not found`);
    }
  }

  async activate(id: string) {
    const timetable = await this.findOne(id);

    // Deactivate other timetables for the same school
    await this.prisma.timetable.updateMany({
      where: {
        schoolId: timetable.schoolId,
        status: 'ACTIVE',
      },
      data: {
        status: 'INACTIVE',
      },
    });

    // Activate this timetable
    return this.prisma.timetable.update({
      where: { id },
      data: {
        status: 'ACTIVE',
      },
    });
  }

  async deactivate(id: string) {
    return this.prisma.timetable.update({
      where: { id },
      data: {
        status: 'INACTIVE',
      },
    });
  }
}