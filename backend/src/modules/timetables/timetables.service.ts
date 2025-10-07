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
  'FR': 'French',  // Fixed: Changed from 'FRE' to 'FR' to match teacher assignments
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
        this.prisma.class.findMany({
          where: { schoolId },
          include: { homeRoom: true },
        }),
        this.prisma.subject.findMany({ where: { schoolId } }),
        this.prisma.room.findMany({ where: { schoolId } }),
        this.prisma.teacher.findMany({
          where: { user: { schoolId } },
          include: { user: true },
        }),
      ]);

      console.log('Found', classes.length, 'classes,', subjects.length, 'subjects,', rooms.length, 'rooms,', teachers.length, 'teachers');
      console.log('Sample teacher from database:', teachers[0] ? { id: teachers[0].id, user: teachers[0].user } : 'none');

      // Debug: Check if user relation is loaded
      console.log('Teachers with user data:', teachers.filter(t => t.user).length, '/', teachers.length);

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

      // Debug: Log first 3 mapped teachers to verify name field
      console.log('First 3 mapped teachers:', JSON.stringify(mappedTeachers.slice(0, 3), null, 2));

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

      // ALWAYS ENFORCED: Core physical constraints (cannot be disabled)
      // These are fundamental impossibilities, not preferences
      constraints.push({
        id: 'no_teacher_conflicts',
        school_id: school.id,
        type: 'TEACHER_AVAILABILITY',
        priority: 'MANDATORY',
        entity_type: 'TEACHER',
        parameters: {},
        description: 'No teacher should be assigned to multiple classes at the same time',
      });

      constraints.push({
        id: 'no_room_conflicts',
        school_id: school.id,
        type: 'ROOM_CAPACITY',
        priority: 'MANDATORY',
        entity_type: 'ROOM',
        parameters: {},
        description: 'No room should be assigned to multiple classes at the same time',
      });

      constraints.push({
        id: 'complete_slot_coverage',
        school_id: school.id,
        type: 'SLOT_COVERAGE',
        priority: 'MANDATORY',
        entity_type: 'CLASS',
        parameters: {},
        description: 'All class periods must be filled with no gaps',
      });

      // Configurable hard constraints

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

      if (hardRules.oneTeacherPerSubject) {
        constraints.push({
          id: 'one_teacher_per_subject',
          school_id: school.id,
          type: 'ONE_TEACHER_PER_SUBJECT',
          priority: 'MANDATORY',
          entity_type: 'TEACHER',
          parameters: {},
          description: 'One teacher should teach a subject consistently to the same class',
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
          home_room_id: cls.homeRoomId || null,
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
          name: teacher.name, // Teacher name for display and debugging
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
        subject_requirements: generateTimetableDto.subjectRequirements?.map(req => ({
          grade: req.grade,
          subject_id: req.subjectId,
          periods_per_week: req.periodsPerWeek,
          constraint_type: req.constraintType || 'exact', // Default to exact if not specified
        })) || null,
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

      // Debug: Log first 3 teachers being sent to Python
      console.log('First 3 teachers being sent to Python:', JSON.stringify(timetableData.teachers.slice(0, 3), null, 2));

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

      // Update academic year dates if provided
      if (generateTimetableDto.startDate || generateTimetableDto.endDate) {
        console.log('Updating academic year dates...');
        await this.prisma.academicYear.update({
          where: { id: generateTimetableDto.academicYearId },
          data: {
            ...(generateTimetableDto.startDate && { startDate: new Date(generateTimetableDto.startDate) }),
            ...(generateTimetableDto.endDate && { endDate: new Date(generateTimetableDto.endDate) }),
          },
        });
        console.log('Updated academic year with dates:', {
          startDate: generateTimetableDto.startDate,
          endDate: generateTimetableDto.endDate,
        });
      }

      // Save timetable to database
      const timetable = await this.prisma.timetable.create({
        data: {
          schoolId,
          academicYearId: generateTimetableDto.academicYearId,
          name: generateTimetableDto.name || null,
          status: isSuccessful ? 'DRAFT' : 'FAILED',
          metadata: JSON.stringify(response.data),
        },
      });

      console.log('Saved timetable to database with ID:', timetable.id);
      console.log('Python status:', pythonStatus);

      // Store subject requirements if provided
      if (generateTimetableDto.subjectRequirements && generateTimetableDto.subjectRequirements.length > 0) {
        console.log('Storing subject requirements...');
        for (const req of generateTimetableDto.subjectRequirements) {
          try {
            await this.prisma.gradeSubjectRequirement.upsert({
              where: {
                schoolId_grade_subjectId: {
                  schoolId,
                  grade: req.grade,
                  subjectId: req.subjectId,
                },
              },
              update: {
                periodsPerWeek: req.periodsPerWeek,
              },
              create: {
                schoolId,
                grade: req.grade,
                subjectId: req.subjectId,
                periodsPerWeek: req.periodsPerWeek,
              },
            });
          } catch (error) {
            console.warn('Failed to save subject requirement:', req, error.message);
          }
        }
        console.log('Stored', generateTimetableDto.subjectRequirements.length, 'subject requirements');
      }

      // If successful, persist timetable entries
      if (isSuccessful && response.data?.solutions?.length > 0) {
        console.log('Persisting timetable entries from solution...');
        const bestSolution = response.data.solutions[0];
        const entries = bestSolution.timetable?.entries || [];
        console.log('Found', entries.length, 'entries in best solution');

        if (entries.length > 0) {
          // First, create time slots if they don't exist
          const timeSlotMap = new Map();
          for (const entry of entries) {
            const timeSlotId = entry.time_slot_id;
            if (!timeSlotMap.has(timeSlotId)) {
              const matchingSlot = timeSlots.find(ts => ts.id === timeSlotId);
              if (matchingSlot) {
                timeSlotMap.set(timeSlotId, matchingSlot);
              }
            }
          }

          // Create time slots in database
          const createdTimeSlots = new Map();
          for (const [slotId, slotData] of timeSlotMap) {
            try {
              const existingSlot = await this.prisma.timeSlot.findFirst({
                where: {
                  schoolId: slotData.school_id,
                  day: slotData.day_of_week,
                  startTime: slotData.start_time,
                },
              });

              if (existingSlot) {
                createdTimeSlots.set(slotId, existingSlot.id);
              } else {
                const newSlot = await this.prisma.timeSlot.create({
                  data: {
                    schoolId: slotData.school_id,
                    day: slotData.day_of_week,
                    startTime: slotData.start_time,
                    endTime: slotData.end_time,
                  },
                });
                createdTimeSlots.set(slotId, newSlot.id);
              }
            } catch (error) {
              console.warn('Failed to create time slot:', slotId, error.message);
            }
          }

          // Create timetable entries
          const entriesToCreate = [];
          for (const entry of entries) {
            const timeSlotDbId = createdTimeSlots.get(entry.time_slot_id);
            if (timeSlotDbId) {
              entriesToCreate.push({
                timetableId: timetable.id,
                classId: entry.class_id,
                subjectId: entry.subject_id,
                teacherId: entry.teacher_id,
                roomId: entry.room_id,
                timeSlotId: timeSlotDbId,
              });
            }
          }

          if (entriesToCreate.length > 0) {
            await this.prisma.timetableEntry.createMany({
              data: entriesToCreate,
            });
            console.log('Created', entriesToCreate.length, 'timetable entries');
          }
        }
      }

      // Return diagnostics even if generation failed
      const result = {
        status: pythonStatus,
        timetable,
        generatedData: response.data,
        generation_time: response.data?.generation_time,
        diagnostics: response.data?.diagnostics,
        solutions: response.data?.solutions,
        message: response.data?.message || (isInfeasible ? 'Timetable generation is mathematically infeasible with current constraints' : undefined),
        // Include validation results from Python service
        validation: response.data?.validation,
        conflicts: response.data?.conflicts || [],
        warnings: response.data?.warnings || [],
        suggestions: response.data?.suggestions || [],
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

        // Check for validation failure (v2.5.1 format)
        if (error.response.data?.validation && error.response.data?.conflicts) {
          const validation = error.response.data.validation;
          const conflicts = error.response.data.conflicts;

          // Build user-friendly error message
          errorMessage = `Timetable generation completed but failed validation:\n`;
          errorMessage += `- ${conflicts.length} critical issues found\n`;

          // Show first few critical issues
          if (conflicts.length > 0) {
            errorMessage += `\nCritical Issues:\n`;
            conflicts.slice(0, 5).forEach((issue, idx) => {
              errorMessage += `${idx + 1}. ${issue}\n`;
            });
            if (conflicts.length > 5) {
              errorMessage += `... and ${conflicts.length - 5} more issues\n`;
            }
          }

          // Add summary stats
          if (validation.stats) {
            errorMessage += `\nStats: ${JSON.stringify(validation.stats)}\n`;
          }
        } else if (error.response.data?.detail) {
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
          academicYear: true,
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
      // First, delete all timetable entries
      await this.prisma.timetableEntry.deleteMany({
        where: { timetableId: id },
      });

      // Then delete the timetable
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
    console.log('🔍 [getEntries] Fetching entries for timetable ID:', id);

    // First check if timetable exists
    const timetable = await this.prisma.timetable.findUnique({
      where: { id },
    });

    if (!timetable) {
      throw new NotFoundException(`Timetable with ID ${id} not found`);
    }

    console.log('✅ [getEntries] Timetable found:', timetable.id);

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

    console.log('📊 [getEntries] Found', entries.length, 'entries from database');

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

    console.log('🔄 [getEntries] Transformed', transformedEntries.length, 'entries');
    console.log('📦 [getEntries] First entry sample:', transformedEntries[0]);
    console.log('📤 [getEntries] Returning response with structure: { data: [...] }');

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

  async getSummary(id: string) {
    // Verify timetable exists
    const timetable = await this.prisma.timetable.findUnique({
      where: { id },
      include: { school: true },
    });

    if (!timetable) {
      throw new NotFoundException(`Timetable with ID ${id} not found`);
    }

    // Get all timetable entries with class and subject details
    const entries = await this.prisma.timetableEntry.findMany({
      where: { timetableId: id },
      include: {
        subject: true,
        class: true,
      },
    });

    // Get all grade-subject requirements for this school
    const requirements = await this.prisma.gradeSubjectRequirement.findMany({
      where: { schoolId: timetable.schoolId },
      include: { subject: true },
    });

    // Create a map for quick lookup: grade_subjectId -> periodsPerWeek
    const requirementMap = new Map<string, number>();
    for (const req of requirements) {
      requirementMap.set(`${req.grade}_${req.subjectId}`, req.periodsPerWeek);
    }

    // Group entries by class
    const classMap = new Map<string, {
      classId: string;
      className: string;
      grade: number;
      subjects: Map<string, {
        subjectId: string;
        subjectName: string;
        actualPeriods: number;
        requiredPeriods: number | null;
      }>;
    }>();

    for (const entry of entries) {
      if (entry.class && entry.subject) {
        let classData = classMap.get(entry.classId);
        if (!classData) {
          classData = {
            classId: entry.classId,
            className: entry.class.name,
            grade: entry.class.grade,
            subjects: new Map(),
          };
          classMap.set(entry.classId, classData);
        }

        const subjectKey = entry.subjectId;
        let subjectData = classData.subjects.get(subjectKey);
        if (!subjectData) {
          const requiredPeriods = requirementMap.get(`${entry.class.grade}_${entry.subjectId}`) || null;
          subjectData = {
            subjectId: entry.subjectId,
            subjectName: entry.subject.name,
            actualPeriods: 0,
            requiredPeriods,
          };
          classData.subjects.set(subjectKey, subjectData);
        }
        subjectData.actualPeriods += 1;
      }
    }

    // Convert to array format with compliance status
    const classes = Array.from(classMap.values()).map(classData => {
      const subjects = Array.from(classData.subjects.values()).map(subject => {
        let status: 'below' | 'meets' | 'exceeds' | 'no-requirement' = 'no-requirement';
        let percentage = 0;

        if (subject.requiredPeriods) {
          percentage = (subject.actualPeriods / subject.requiredPeriods) * 100;

          if (subject.actualPeriods < subject.requiredPeriods) {
            status = 'below';
          } else if (subject.actualPeriods === subject.requiredPeriods) {
            status = 'meets';
          } else {
            status = 'exceeds';
          }
        }

        return {
          ...subject,
          status,
          percentage: Math.round(percentage),
        };
      });

      // Sort subjects by name
      subjects.sort((a, b) => a.subjectName.localeCompare(b.subjectName));

      // Calculate totals for this class
      const totalActual = subjects.reduce((sum, s) => sum + s.actualPeriods, 0);
      const totalRequired = subjects.reduce((sum, s) => sum + (s.requiredPeriods || 0), 0);

      return {
        classId: classData.classId,
        className: classData.className,
        grade: classData.grade,
        subjects,
        totalActual,
        totalRequired,
      };
    });

    // Sort classes by grade then name
    classes.sort((a, b) => {
      if (a.grade !== b.grade) return a.grade - b.grade;
      return a.className.localeCompare(b.className);
    });

    return {
      data: {
        totalPeriods: entries.length,
        classes,
      },
    };
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