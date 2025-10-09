import { Injectable, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import * as csvParser from 'csv-parser';
import { Readable } from 'stream';

@Injectable()
export class ImportService {
  constructor(private prisma: PrismaService) {}

  private async parseCSV<T>(csvContent: string): Promise<T[]> {
    return new Promise((resolve, reject) => {
      const results: T[] = [];
      const stream = Readable.from([csvContent]);

      stream
        .pipe(csvParser())
        .on('data', (data) => results.push(data))
        .on('end', () => resolve(results))
        .on('error', (error) => reject(error));
    });
  }

  async importClasses(csvContent: string, schoolId: string) {
    try {
      const rows = await this.parseCSV<{
        class_id: string;
        name: string;
        grade: string;
        section: string;
        capacity: string;
      }>(csvContent);

      const created = [];

      for (const row of rows) {
        try {
          const classData = await this.prisma.class.create({
            data: {
              schoolId,
              name: row.name,
              grade: parseInt(row.grade),
              section: row.section,
              studentCount: parseInt(row.capacity),
            },
          });
          created.push(classData);
        } catch (error) {
          console.error(`Failed to import class ${row.name}:`, error.message);
          // Continue with next row
        }
      }

      return { count: created.length };
    } catch (error) {
      throw new BadRequestException(`Failed to import classes: ${error.message}`);
    }
  }

  async importTeachers(csvContent: string, schoolId: string) {
    try {
      const rows = await this.parseCSV<{
        teacher_id: string;
        name: string;
        email: string;
        phone: string;
        max_periods_per_day: string;
        max_periods_per_week: string;
        subjects_qualified: string;
      }>(csvContent);

      const created = [];

      for (const row of rows) {
        try {
          // Parse subjects (comma-separated or quoted comma-separated)
          let subjects: string[] = [];
          if (row.subjects_qualified) {
            // Remove quotes if present and split
            const cleanSubjects = row.subjects_qualified.replace(/^"|"$/g, '');
            subjects = cleanSubjects.split(',').map(s => s.trim());
          }

          // Create user first
          const user = await this.prisma.user.create({
            data: {
              schoolId,
              email: row.email,
              role: 'TEACHER',
              profile: JSON.stringify({
                name: row.name,
                phone: row.phone,
              }),
            },
          });

          // Then create teacher profile
          const teacher = await this.prisma.teacher.create({
            data: {
              userId: user.id,
              subjects: JSON.stringify(subjects),
              maxPeriodsPerDay: parseInt(row.max_periods_per_day) || 6,
              maxPeriodsPerWeek: parseInt(row.max_periods_per_week) || 30,
            },
          });

          created.push(teacher);
        } catch (error) {
          console.error(`Failed to import teacher ${row.name}:`, error.message);
          // Continue with next row
        }
      }

      return { count: created.length };
    } catch (error) {
      throw new BadRequestException(`Failed to import teachers: ${error.message}`);
    }
  }

  async importSubjects(csvContent: string, schoolId: string) {
    try {
      const rows = await this.parseCSV<{
        code: string;
        name: string;
        needs_lab: string;
        periods_per_week: string;
      }>(csvContent);

      const created = [];

      for (const row of rows) {
        try {
          const subject = await this.prisma.subject.create({
            data: {
              schoolId,
              name: row.name,
              department: row.code, // Use code as department for now
              credits: parseInt(row.periods_per_week),
              minPeriodsPerWeek: parseInt(row.periods_per_week),
              maxPeriodsPerWeek: parseInt(row.periods_per_week),
              requiresLab: row.needs_lab.toLowerCase() === 'true',
            },
          });
          created.push(subject);
        } catch (error) {
          console.error(`Failed to import subject ${row.name}:`, error.message);
          // Continue with next row
        }
      }

      return { count: created.length };
    } catch (error) {
      throw new BadRequestException(`Failed to import subjects: ${error.message}`);
    }
  }

  async importRooms(csvContent: string, schoolId: string) {
    try {
      const rows = await this.parseCSV<{
        room_id: string;
        name: string;
        type: string;
        capacity: string;
        has_projector: string;
        specialization: string;
      }>(csvContent);

      const created = [];

      for (const row of rows) {
        try {
          // Map type to RoomType enum
          let roomType = 'CLASSROOM';
          if (row.type.toLowerCase().includes('lab')) {
            roomType = 'LAB';
          } else if (row.type.toLowerCase().includes('auditorium')) {
            roomType = 'AUDITORIUM';
          }

          const room = await this.prisma.room.create({
            data: {
              schoolId,
              name: row.name,
              capacity: parseInt(row.capacity),
              type: roomType,
            },
          });
          created.push(room);
        } catch (error) {
          console.error(`Failed to import room ${row.name}:`, error.message);
          // Continue with next row
        }
      }

      return { count: created.length };
    } catch (error) {
      throw new BadRequestException(`Failed to import rooms: ${error.message}`);
    }
  }
}
