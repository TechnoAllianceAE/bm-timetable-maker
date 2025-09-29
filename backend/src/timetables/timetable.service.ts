import { PrismaClient } from '@prisma/client';
import { randomUUID } from 'crypto';
import { AuthPayload, TimetableStatus } from '../types';
import { TimetableEngineClient, TimetableEngineGeneratePayload, TimetableEngineGenerateResponse } from './timetableEngine.client';

interface CreateTimetableInput {
  academicYearId: string;
  name?: string;
  metadata?: Record<string, unknown>;
}

interface WeightPreset {
  academic: number;
  wellness: number;
  efficiency: number;
  preference: number;
}

interface GenerateOptions {
  options?: number;
  timeout?: number;
  weights?: Partial<WeightPreset>;
}

interface ResolvedGenerateOptions {
  options: number;
  timeout: number;
  weights: WeightPreset;
}

const DEFAULT_GENERATE_OPTIONS: ResolvedGenerateOptions = {
  options: 3,
  timeout: 120,
  weights: {
    academic: 0.4,
    wellness: 0.1,
    efficiency: 0.3,
    preference: 0.2
  }
};

export class TimetableService {
  private prisma: PrismaClient;
  private engine: TimetableEngineClient;

  constructor(prismaClient?: PrismaClient, engineClient?: TimetableEngineClient) {
    this.prisma = prismaClient ?? new PrismaClient();
    this.engine = engineClient ?? new TimetableEngineClient();
  }

  async listTimetables(schoolId: string) {
    const timetables = await this.prisma.timetable.findMany({
      where: { schoolId },
      orderBy: { createdAt: 'desc' },
      select: {
        id: true,
        academicYearId: true,
        status: true,
        version: true,
        wellnessScore: true,
        workloadBalanceScore: true,
        metadata: true,
        createdAt: true,
        createdBy: true,
        approvedBy: true
      }
    });

    return timetables.map((timetable: any) => ({
      ...timetable,
      metadata: this.parse(timetable.metadata)
    }));
  }

  async createTimetable(input: CreateTimetableInput, user: AuthPayload) {
    const academicYear = await this.prisma.academicYear.findFirst({
      where: { id: input.academicYearId, schoolId: user.schoolId }
    });

    if (!academicYear) {
      throw new Error('Academic year not found for this school');
    }

    const timetable = await this.prisma.timetable.create({
      data: {
        schoolId: user.schoolId,
        academicYearId: input.academicYearId,
        status: 'DRAFT',
        metadata: this.stringify(input.metadata ?? { name: input.name ?? 'Untitled Timetable' }),
        createdBy: user.userId
      }
    });

    return {
      ...timetable,
      metadata: this.parse(timetable.metadata)
    };
  }

  async getTimetableById(id: string, user: AuthPayload) {
    const timetable = await this.prisma.timetable.findFirst({
      where: { id, schoolId: user.schoolId },
      include: {
        academicYear: true,
        entries: {
          include: {
            class: true,
            subject: true,
            teacher: {
              include: { user: true }
            },
            timeSlot: true,
            room: true
          },
          orderBy: [{ timeSlot: { day: 'asc' } }, { timeSlot: { startTime: 'asc' } }]
        }
      }
    });

    if (!timetable) {
      throw new Error('Timetable not found');
    }

    return {
      ...timetable,
      metadata: this.parse((timetable as any).metadata)
    };
  }

  async getEntries(timetableId: string, user: AuthPayload) {
    const timetable = await this.prisma.timetable.findFirst({
      where: { id: timetableId, schoolId: user.schoolId },
      select: { id: true }
    });

    if (!timetable) {
      throw new Error('Timetable not found');
    }

    return this.prisma.timetableEntry.findMany({
      where: { timetableId },
      include: {
        class: true,
        subject: true,
        teacher: {
          include: { user: true }
        },
        timeSlot: true,
        room: true
      },
      orderBy: [{ timeSlot: { day: 'asc' } }, { timeSlot: { startTime: 'asc' } }]
    });
  }

  async generateTimetable(timetableId: string, user: AuthPayload, options?: GenerateOptions) {
    const timetable = await this.prisma.timetable.findFirst({
      where: { id: timetableId, schoolId: user.schoolId }
    });

    if (!timetable) {
      throw new Error('Timetable not found');
    }

    if (!['ADMIN', 'PRINCIPAL'].includes(user.role)) {
      throw new Error('Only administrators can generate timetables');
    }

    const generationOptions = this.mergeOptions(options);

    await this.prisma.timetable.update({
      where: { id: timetableId },
      data: { status: 'GENERATING' }
    });

    try {
      const dataset = await this.collectGenerationData(user.schoolId, timetable.academicYearId);
      const payload = this.buildEnginePayload(user.schoolId, timetable.academicYearId, dataset, generationOptions);
      const response = await this.engine.generate(payload);

      const bestSolution = this.pickBestSolution(response);
      if (!bestSolution) {
        throw new Error('No feasible solutions returned by engine');
      }

      await this.persistGeneratedTimetable(timetableId, bestSolution);

      return {
        status: 'ACTIVE' as TimetableStatus,
        generationTime: response.generation_time,
        metrics: bestSolution.metrics,
        totalScore: bestSolution.total_score
      };
    } catch (error) {
      await this.prisma.timetable.update({
        where: { id: timetableId },
        data: { status: 'FAILED', metadata: this.stringify({ error: (error as Error).message }) }
      });
      throw error;
    }
  }

  private mergeOptions(options?: GenerateOptions): ResolvedGenerateOptions {
    const weights: WeightPreset = {
      academic: options?.weights?.academic ?? DEFAULT_GENERATE_OPTIONS.weights.academic,
      wellness: options?.weights?.wellness ?? DEFAULT_GENERATE_OPTIONS.weights.wellness,
      efficiency: options?.weights?.efficiency ?? DEFAULT_GENERATE_OPTIONS.weights.efficiency,
      preference: options?.weights?.preference ?? DEFAULT_GENERATE_OPTIONS.weights.preference
    };

    return {
      options: options?.options ?? DEFAULT_GENERATE_OPTIONS.options,
      timeout: options?.timeout ?? DEFAULT_GENERATE_OPTIONS.timeout,
      weights
    };
  }

  private async collectGenerationData(schoolId: string, academicYearId: string) {
    const [classes, subjects, teachers, timeSlots, rooms, constraints] = await Promise.all([
      this.prisma.class.findMany({ where: { schoolId } }),
      this.prisma.subject.findMany({ where: { schoolId } }),
      this.prisma.teacher.findMany({
        where: { user: { schoolId } },
        include: { user: true, workloadConfig: true }
      }),
      this.prisma.timeSlot.findMany({ where: { schoolId } }),
      this.prisma.room.findMany({ where: { schoolId } }),
      this.prisma.constraint.findMany({ where: { schoolId } })
    ]);

    if (!classes.length) {
      throw new Error('No classes found for this school');
    }
    if (!subjects.length) {
      throw new Error('No subjects found for this school');
    }
    if (!teachers.length) {
      throw new Error('No teachers found for this school');
    }
    if (!timeSlots.length) {
      throw new Error('No time slots found for this school');
    }

    return { classes, subjects, teachers, timeSlots, rooms, constraints };
  }

  private buildEnginePayload(
    schoolId: string,
    academicYearId: string,
    dataset: Awaited<ReturnType<TimetableService['collectGenerationData']>>,
    options: ResolvedGenerateOptions
  ): TimetableEngineGeneratePayload {
    const periodMap = this.computePeriodNumbers(dataset.timeSlots);

    return {
      school_id: schoolId,
      academic_year_id: academicYearId,
      classes: dataset.classes.map((clazz: any) => ({
        id: clazz.id,
        school_id: clazz.schoolId,
        name: clazz.name,
        grade: clazz.grade,
        section: clazz.section ?? '',
        stream: clazz.stream,
        student_count: clazz.studentCount ?? null
      })),
      subjects: dataset.subjects.map((subject: any) => ({
        id: subject.id,
        school_id: subject.schoolId,
        name: subject.name,
        code: subject.name.toUpperCase().replace(/\s+/g, '_'),
        periods_per_week: subject.maxPeriodsPerWeek ?? subject.minPeriodsPerWeek ?? 4,
        requires_lab: subject.requiresLab ?? false,
        is_elective: false
      })),
      teachers: dataset.teachers.map((teacher: any) => ({
        id: teacher.id,
        user_id: teacher.userId,
        subjects: this.ensureArray(teacher.subjects),
        availability: this.parseJson(teacher.availability) ?? {},
        max_periods_per_day: teacher.maxPeriodsPerDay,
        max_periods_per_week: teacher.maxPeriodsPerWeek,
        max_consecutive_periods: teacher.maxConsecutivePeriods
      })),
      time_slots: dataset.timeSlots.map((slot: any) => ({
        id: slot.id,
        school_id: slot.schoolId,
        day_of_week: slot.day,
        period_number: periodMap.get(slot.id) ?? 1,
        start_time: slot.startTime,
        end_time: slot.endTime,
        is_break: slot.isBreak ?? false
      })),
      rooms: dataset.rooms.map((room: any) => ({
        id: room.id,
        school_id: room.schoolId,
        name: room.name,
        capacity: room.capacity ?? 30,
        type: room.type ?? 'CLASSROOM',
        facilities: []
      })),
      constraints: dataset.constraints.map((constraint: any) => ({
        id: constraint.id,
        school_id: constraint.schoolId,
        type: constraint.type ?? 'TEACHER_AVAILABILITY',
        priority: constraint.priority ?? 'MANDATORY',
        entity_type: constraint.entityType ?? null,
        entity_id: constraint.entityId ?? null,
        parameters: this.parseJson(constraint.value) ?? {},
        description: ''
      })),
      options: options.options,
      timeout: options.timeout,
      weights: {
        academic_requirements: options.weights.academic,
        resource_utilization: options.weights.efficiency,
        gap_minimization: options.weights.preference,
        teacher_preferences: options.weights.wellness
      }
    };
  }

  private computePeriodNumbers(timeSlots: Array<{ id: string; day: string; startTime: string }>) {
    const map = new Map<string, number>();
    const grouped = new Map<string, { id: string; startTime: string }[]>();

    timeSlots.forEach((slot) => {
      const day = slot.day;
      if (!grouped.has(day)) {
        grouped.set(day, []);
      }
      grouped.get(day)!.push({ id: slot.id, startTime: slot.startTime });
    });

    grouped.forEach((slots) => {
      slots.sort((a, b) => a.startTime.localeCompare(b.startTime));
      slots.forEach((slot, index) => {
        map.set(slot.id, index + 1);
      });
    });

    return map;
  }

  private pickBestSolution(response: TimetableEngineGenerateResponse) {
    if (!response.solutions || response.solutions.length === 0) {
      return null;
    }

    const sorted = [...response.solutions].sort((a, b) => b.total_score - a.total_score);
    return sorted[0];
  }

  private async persistGeneratedTimetable(timetableId: string, solution: TimetableEngineGenerateResponse['solutions'][number]) {
    const entries = solution.timetable.entries ?? [];

    await this.prisma.$transaction(async (tx: PrismaClient) => {
      await tx.timetableEntry.deleteMany({ where: { timetableId } });

      if (entries.length) {
        await tx.timetableEntry.createMany({
          data: entries.map((entry: any) => ({
            id: entry.id ?? randomUUID(),
            timetableId,
            classId: entry.class_id,
            subjectId: entry.subject_id,
            teacherId: entry.teacher_id,
            timeSlotId: entry.time_slot_id,
            roomId: entry.room_id,
            workloadImpact: entry.workload_impact ?? null,
            wellnessImpact: entry.wellness_impact ?? null
          }))
        });
      }

      await tx.timetable.update({
        where: { id: timetableId },
        data: {
          status: 'ACTIVE',
          wellnessScore: typeof solution.metrics?.wellness_score === 'number' ? solution.metrics?.wellness_score : null,
          workloadBalanceScore: typeof solution.metrics?.workload_balance === 'number' ? solution.metrics?.workload_balance : null,
          metadata: this.stringify({
            ...(solution.metrics ?? {}),
            totalScore: solution.total_score
          })
        }
      });
    });
  }

  private ensureArray(value: unknown): string[] {
    if (Array.isArray(value)) {
      return value as string[];
    }
    if (typeof value === 'string') {
      try {
        const parsed = JSON.parse(value);
        return Array.isArray(parsed) ? parsed : [];
      } catch {
        return value ? [value] : [];
      }
    }
    return [];
  }

  private parseJson(value: unknown): Record<string, unknown> | null {
    if (!value) return null;
    if (typeof value === 'object') {
      return value as Record<string, unknown>;
    }
    if (typeof value === 'string') {
      try {
        return JSON.parse(value) as Record<string, unknown>;
      } catch {
        return null;
      }
    }
    return null;
  }

  private stringify(value: unknown) {
    if (value === undefined || value === null) {
      return null;
    }
    if (typeof value === 'string') {
      return value;
    }
    try {
      return JSON.stringify(value);
    } catch {
      return null;
    }
  }

  private parse(value: unknown) {
    if (!value) return null;
    if (typeof value === 'object') return value as Record<string, unknown>;
    if (typeof value === 'string') {
      try {
        return JSON.parse(value);
      } catch {
        return null;
      }
    }
    return null;
  }
}

export const timetableService = new TimetableService();
