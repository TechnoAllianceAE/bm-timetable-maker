import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import { GenerateTimetableDto } from './dto/generate-timetable.dto';
import { UpdateTimetableDto } from './dto/update-timetable.dto';
import { firstValueFrom } from 'rxjs';

// Subject code to full name mapping
const SUBJECT_CODE_MAP: Record<string, string> = {
  'MATH': 'Mathematics',
  'ENG': 'English',
  'SCI': 'Science',
  'SS': 'Social Studies',
  'CS': 'Computer Science',
  'PE': 'Physical Education',
  'ART': 'Art',
  'MUS': 'Music',
  'HIN': 'Hindi',
  'FRE': 'French',
};

@Injectable()
export class TimetablesService {
  constructor(
    private prisma: PrismaService,
    private httpService: HttpService,
    private configService: ConfigService,
  ) {}

  async generate(generateTimetableDto: GenerateTimetableDto) {
    const { schoolId } = generateTimetableDto;
    console.log('Starting timetable generation for school:', schoolId);

    try {
      // Fetch school data
      const school = await this.prisma.school.findUnique({
        where: { id: schoolId },
      });

      if (!school) {
        console.error('School not found:', schoolId);
        throw new NotFoundException(`School with ID ${schoolId} not found`);
      }

      console.log('Found school:', school.name);

      // Fetch school data separately to avoid include issues
      const [classes, subjects, rooms, teachers] = await Promise.all([
        this.prisma.class.findMany({ where: { schoolId } }),
        this.prisma.subject.findMany({ where: { schoolId } }),
        this.prisma.room.findMany({ where: { schoolId } }),
        this.prisma.teacher.findMany({
          where: { user: { schoolId } },
          include: { user: true },
        }),
      ]);

      console.log('Found', classes.length, 'classes,', subjects.length, 'subjects,', rooms.length, 'rooms,', teachers.length, 'teachers');

      // Prepare data for Python service with better error handling
      const mappedTeachers = teachers.map(teacher => {
        try {
          let subjects = [];
          if (teacher.subjects) {
            subjects = typeof teacher.subjects === 'string'
              ? JSON.parse(teacher.subjects)
              : teacher.subjects;
          }

          return {
            id: teacher.id,
            name: teacher.user?.email || `Teacher-${teacher.id}`,
            subjects: Array.isArray(subjects) ? subjects : [],
            availability: teacher.availability || {},
            maxPeriodsPerDay: teacher.maxPeriodsPerDay || 6,
            maxPeriodsPerWeek: teacher.maxPeriodsPerWeek || 30,
          };
        } catch (parseError) {
          console.warn('Error parsing teacher data for:', teacher.id, parseError.message);
          return {
            id: teacher.id,
            name: teacher.user?.email || `Teacher-${teacher.id}`,
            subjects: [],
            availability: {},
            maxPeriodsPerDay: 6,
            maxPeriodsPerWeek: 30,
          };
        }
      });

      // Generate time slots (Monday-Friday, 8 periods per day)
      const timeSlots = [];
      const days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'];
      const periods = generateTimetableDto.constraints?.periodsPerDay || 8;

      for (let dayIndex = 0; dayIndex < days.length; dayIndex++) {
        for (let period = 1; period <= periods; period++) {
          const startHour = 8 + Math.floor((period - 1) * 0.75); // Roughly every 45 minutes
          const startMinute = ((period - 1) * 45) % 60;
          const endHour = startHour + (startMinute >= 15 ? 1 : 0);
          const endMinute = (startMinute + 45) % 60;

          timeSlots.push({
            id: `${days[dayIndex]}_P${period}`,
            school_id: school.id,
            day_of_week: days[dayIndex],
            period_number: period,
            start_time: `${startHour.toString().padStart(2, '0')}:${startMinute.toString().padStart(2, '0')}`,
            end_time: `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`,
            is_break: false,
          });
        }
      }

      // Convert constraints to the expected format
      const constraints = [];
      const hardRules = generateTimetableDto.constraints?.hardRules || {};
      const softRules = generateTimetableDto.constraints?.softRules || {};

      // Add hard constraints
      if (hardRules.noTeacherConflicts) {
        constraints.push({
          id: 'no_teacher_conflicts',
          school_id: school.id,
          type: 'TEACHER_AVAILABILITY',
          priority: 'MANDATORY',
          entity_type: 'TEACHER',
          parameters: {},
          description: 'No teacher should be assigned to multiple classes at the same time',
        });
      }

      if (hardRules.noRoomConflicts) {
        constraints.push({
          id: 'no_room_conflicts',
          school_id: school.id,
          type: 'ROOM_CAPACITY',
          priority: 'MANDATORY',
          entity_type: 'ROOM',
          parameters: {},
          description: 'No room should be assigned to multiple classes at the same time',
        });
      }

      if (hardRules.maxPeriodsPerDayPerTeacher) {
        constraints.push({
          id: 'max_periods_per_day',
          school_id: school.id,
          type: 'MAX_PERIODS_PER_WEEK',
          priority: 'MANDATORY',
          entity_type: 'TEACHER',
          parameters: { max_periods_per_day: 6 },
          description: 'Teachers should not exceed maximum periods per day',
        });
      }

      // Add soft constraints
      if (softRules.minimizeTeacherGaps) {
        constraints.push({
          id: 'minimize_gaps',
          school_id: school.id,
          type: 'NO_GAPS',
          priority: 'HIGH',
          entity_type: 'TEACHER',
          parameters: {},
          description: 'Minimize gaps in teacher schedules',
        });
      }

      // Transform data to match Python service expectations
      const timetableData = {
        school_id: school.id,
        academic_year_id: generateTimetableDto.academicYearId,
        classes: classes.map(cls => ({
          id: cls.id,
          school_id: cls.schoolId,
          name: cls.name,
          grade: cls.grade || 10,
          section: cls.section || 'A',
          stream: cls.stream || null,
          student_count: cls.studentCount || 30,
        })),
        subjects: subjects.map(subj => ({
          id: subj.id,
          school_id: subj.schoolId,
          name: subj.name,
          code: subj.name, // Use name as code since code field doesn't exist
          periods_per_week: subj.minPeriodsPerWeek || 4,
          requires_lab: subj.requiresLab || false,
          is_elective: false, // Default since field doesn't exist
        })),
        teachers: mappedTeachers.map(teacher => ({
          id: teacher.id,
          user_id: teacher.id, // Using same ID for simplicity
          subjects: this.transformTeacherSubjects(teacher.subjects),
          availability: typeof teacher.availability === 'string'
            ? JSON.parse(teacher.availability)
            : teacher.availability,
          max_periods_per_day: teacher.maxPeriodsPerDay,
          max_periods_per_week: teacher.maxPeriodsPerWeek,
          max_consecutive_periods: 3,
        })),
        rooms: rooms.map(room => ({
          id: room.id,
          school_id: room.schoolId,
          name: room.name,
          building: 'Main', // Default since field doesn't exist
          floor: 1, // Default since field doesn't exist
          capacity: room.capacity || 40,
          type: room.type || 'CLASSROOM',
        })),
        time_slots: timeSlots,
        constraints: constraints,
        options: 3,
        timeout: 60,
      };

      console.log('Prepared timetable data:', {
        school_id: timetableData.school_id,
        academic_year_id: timetableData.academic_year_id,
        classCount: classes.length,
        teacherCount: teachers.length,
        subjectCount: subjects.length,
        roomCount: rooms.length,
        timeSlotsCount: timetableData.time_slots.length,
        constraintsCount: timetableData.constraints.length,
      });

      // Call Python timetable generation service
      const pythonUrl = this.configService.get('PYTHON_TIMETABLE_URL') || 'http://localhost:8000';
      console.log('Calling Python service at:', pythonUrl);

      const response = await firstValueFrom(
        this.httpService.post(`${pythonUrl}/generate`, timetableData, {
          timeout: 120000, // 2 minute timeout for complex timetable generation
        })
      );

      console.log('Python service response status:', response.status);
      console.log('Python service response data keys:', Object.keys(response.data || {}));

      // Check if the generation was successful
      const pythonStatus = response.data?.status || 'unknown';
      const isSuccessful = pythonStatus === 'success';
      const isInfeasible = pythonStatus === 'infeasible';

      // Save timetable to database
      const timetable = await this.prisma.timetable.create({
        data: {
          schoolId,
          academicYearId: generateTimetableDto.academicYearId,
          status: isSuccessful ? 'DRAFT' : 'FAILED',
          metadata: JSON.stringify(response.data),
        },
      });

      console.log('Saved timetable to database with ID:', timetable.id);
      console.log('Python status:', pythonStatus);

      // Return diagnostics even if generation failed
      const result = {
        status: pythonStatus,
        timetable,
        generatedData: response.data,
        generation_time: response.data?.generation_time,
        diagnostics: response.data?.diagnostics,
        solutions: response.data?.solutions,
        message: response.data?.message || (isInfeasible ? 'Timetable generation is mathematically infeasible with current constraints' : undefined),
      };

      // If infeasible or failed, include detailed diagnostic info
      if (!isSuccessful && response.data?.diagnostics) {
        result.diagnostics = response.data.diagnostics;
      }

      return result;
    } catch (error) {
      console.error('=== TIMETABLE GENERATION ERROR START ===');
      console.error('Error message:', error.message);
      console.error('Error code:', error.code);

      if (error.response) {
        console.error('Python service returned error:');
        console.error('Status:', error.response.status);
        console.error('Status Text:', error.response.statusText);
        console.error('Response Data:', error.response.data);

        // Extract the detailed error from Python service
        let errorMessage = 'Unknown error from Python service';

        if (error.response.data?.detail) {
          if (Array.isArray(error.response.data.detail)) {
            // FastAPI validation errors
            const validationErrors = error.response.data.detail.map(err =>
              `${err.loc.join('.')}: ${err.msg} (input: ${JSON.stringify(err.input)})`
            ).join('; ');
            errorMessage = `Validation errors: ${validationErrors}`;
          } else if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail;
          } else {
            errorMessage = JSON.stringify(error.response.data.detail);
          }
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message;
        } else if (error.response.data?.error) {
          errorMessage = error.response.data.error;
        }

        console.error('Extracted error message:', errorMessage);
        console.error('=== TIMETABLE GENERATION ERROR END ===');

        // Create a user-friendly error message
        const userFriendlyMessage = error.response.data?.detail?.message || errorMessage;
        const suggestions = error.response.data?.detail?.suggestions || [];
        const conflicts = error.response.data?.detail?.conflicts || [];

        let fullMessage = `Timetable generation failed: ${userFriendlyMessage}`;
        if (conflicts.length > 0) {
          fullMessage += `\n\nIssues found: ${conflicts.join(', ')}`;
        }
        if (suggestions.length > 0) {
          fullMessage += `\n\nSuggestions: ${suggestions.join(', ')}`;
        }

        throw new BadRequestException(fullMessage);
      }

      if (error.code === 'ECONNREFUSED') {
        throw new BadRequestException('Python timetable service is not running. Please start the service on port 8000.');
      }

      if (error instanceof NotFoundException) {
        throw error;
      }

      throw new BadRequestException(`Failed to generate timetable: ${error.message}`);
    }
  }

  async findAll(schoolId?: string, status?: string, page?: number, limit?: number) {
    const pageNum = page || 1;
    const limitNum = limit || 10;
    const skip = (pageNum - 1) * limitNum;
    const where: any = {};

    if (schoolId) where.schoolId = schoolId;
    if (status) where.status = status;

    const [timetables, total] = await Promise.all([
      this.prisma.timetable.findMany({
        where,
        skip,
        take: limitNum,
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
        page: pageNum,
        limit: limitNum,
        totalPages: Math.ceil(total / limitNum),
      },
    };
  }

  async findOne(id: string) {
    const timetable = await this.prisma.timetable.findUnique({
      where: { id },
      include: {
        school: true,
        entries: {
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

  async getEntries(id: string) {
    // First check if timetable exists
    const timetable = await this.prisma.timetable.findUnique({
      where: { id },
    });

    if (!timetable) {
      throw new NotFoundException(`Timetable with ID ${id} not found`);
    }

    // Fetch all entries with related data
    const entries = await this.prisma.timetableEntry.findMany({
      where: { timetableId: id },
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
    });

    // Transform to match frontend expectations (compatible with TimetableViewer component)
    const transformedEntries = entries.map(entry => ({
      id: entry.id,
      dayOfWeek: this.parseDayOfWeek(entry.timeSlot.day),
      periodNumber: this.parsePeriodNumber(entry.timeSlot),
      startTime: entry.timeSlot.startTime,
      endTime: entry.timeSlot.endTime,
      classId: entry.classId,
      teacherId: entry.teacherId,
      subjectId: entry.subjectId,
      roomId: entry.roomId,
      class: {
        name: entry.class.name,
      },
      teacher: {
        name: entry.teacher.user?.email || `Teacher-${entry.teacherId}`,
      },
      subject: {
        name: entry.subject.name,
      },
      room: entry.room ? {
        name: entry.room.name,
        roomNumber: entry.room.name, // Use name as roomNumber since we don't have a separate field
      } : null,
    }));

    return { data: transformedEntries };
  }

  private parseDayOfWeek(day: string): number {
    const dayMap: Record<string, number> = {
      'MONDAY': 1,
      'TUESDAY': 2,
      'WEDNESDAY': 3,
      'THURSDAY': 4,
      'FRIDAY': 5,
      'SATURDAY': 6,
      'SUNDAY': 7,
    };
    return dayMap[day.toUpperCase()] || 1;
  }

  private parsePeriodNumber(timeSlot: any): number {
    // Try to extract period number from timeslot ID or calculate from time
    if (timeSlot.id && timeSlot.id.includes('_P')) {
      const match = timeSlot.id.match(/_P(\d+)/);
      if (match) {
        return parseInt(match[1], 10);
      }
    }

    // Fallback: calculate from start time (assuming periods start at 08:00)
    const startTime = timeSlot.startTime;
    if (startTime) {
      const [hours, minutes] = startTime.split(':').map(Number);
      const totalMinutes = (hours - 8) * 60 + minutes;
      return Math.floor(totalMinutes / 45) + 1; // Assuming 45-minute periods
    }

    return 1; // Default fallback
  }

  private transformTeacherSubjects(subjects: string[] | any): string[] {
    // If subjects is already an array, transform codes to full names
    if (Array.isArray(subjects)) {
      return subjects.map(code => SUBJECT_CODE_MAP[code] || code);
    }

    // If subjects is a string, try to parse it as JSON first
    if (typeof subjects === 'string') {
      try {
        const parsed = JSON.parse(subjects);
        if (Array.isArray(parsed)) {
          return parsed.map(code => SUBJECT_CODE_MAP[code] || code);
        }
      } catch (e) {
        // If parsing fails, return empty array
        return [];
      }
    }

    return [];
  }
}