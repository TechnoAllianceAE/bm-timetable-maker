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

  async findAll(page?: number, limit?: number) {
    const pageNum = page || 1;
    const limitNum = limit || 10;
    const skip = (pageNum - 1) * limitNum;

    const [schools, total] = await Promise.all([
      this.prisma.school.findMany({
        skip,
        take: limitNum,
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
        page: pageNum,
        limit: limitNum,
        totalPages: Math.ceil(total / limitNum),
      },
    };
  }

  async findOne(id: string) {
    const school = await this.prisma.school.findUnique({
      where: { id },
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

  async deleteSchoolData(id: string) {
    // Verify school exists
    const school = await this.prisma.school.findUnique({
      where: { id },
    });

    if (!school) {
      throw new NotFoundException(`School with ID ${id} not found`);
    }

    // Delete all related data in the correct order (to respect foreign keys)
    // Use transaction to ensure all deletes succeed or none
    const result = await this.prisma.$transaction(async (tx) => {
      // Delete timetable entries first (depends on timetables)
      const deletedEntries = await tx.timetableEntry.deleteMany({
        where: {
          timetable: {
            schoolId: id,
          },
        },
      });

      // Delete subject requirements (depends on subjects)
      const deletedRequirements = await tx.gradeSubjectRequirement.deleteMany({
        where: {
          schoolId: id,
        },
      });

      // Delete timetables
      const deletedTimetables = await tx.timetable.deleteMany({
        where: { schoolId: id },
      });

      // Delete time slots
      const deletedTimeSlots = await tx.timeSlot.deleteMany({
        where: { schoolId: id },
      });

      // Delete teachers (linked to school via user.schoolId)
      const teachers = await tx.teacher.findMany({
        where: {
          user: {
            schoolId: id,
          },
        },
        select: { id: true, userId: true },
      });

      const deletedTeachers = await tx.teacher.deleteMany({
        where: {
          id: { in: teachers.map(t => t.id) },
        },
      });

      // Delete associated user accounts
      const userIds = teachers.map(t => t.userId);
      await tx.user.deleteMany({
        where: { id: { in: userIds } },
      });

      // Delete classes
      const deletedClasses = await tx.class.deleteMany({
        where: { schoolId: id },
      });

      // Delete subjects
      const deletedSubjects = await tx.subject.deleteMany({
        where: { schoolId: id },
      });

      // Delete rooms
      const deletedRooms = await tx.room.deleteMany({
        where: { schoolId: id },
      });

      // Delete academic years
      const deletedAcademicYears = await tx.academicYear.deleteMany({
        where: { schoolId: id },
      });

      return {
        deletedEntries: deletedEntries.count,
        deletedRequirements: deletedRequirements.count,
        deletedTimetables: deletedTimetables.count,
        deletedTimeSlots: deletedTimeSlots.count,
        deletedTeachers: deletedTeachers.count,
        deletedClasses: deletedClasses.count,
        deletedSubjects: deletedSubjects.count,
        deletedRooms: deletedRooms.count,
        deletedAcademicYears: deletedAcademicYears.count,
      };
    });

    return {
      message: `Successfully deleted all data for school ${school.name}`,
      deletedCounts: result,
    };
  }
}