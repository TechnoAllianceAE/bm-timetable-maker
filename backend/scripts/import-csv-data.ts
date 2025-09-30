import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';
import * as path from 'path';
import * as csv from 'csv-parser';

const prisma = new PrismaClient();

interface CSVClass {
  class_id: string;
  name: string;
  grade: string;
  section: string;
  capacity: string;
}

interface CSVTeacher {
  teacher_id: string;
  name: string;
  email: string;
  phone: string;
  max_periods_per_day: string;
  max_periods_per_week: string;
  subjects_qualified: string;
}

interface CSVSubject {
  code: string;
  name: string;
  needs_lab: string;
  periods_per_week: string;
}

interface CSVRoom {
  room_id: string;
  name: string;
  type: string;
  capacity: string;
  has_projector: string;
  specialization: string;
}

async function readCSV<T>(filePath: string): Promise<T[]> {
  return new Promise((resolve, reject) => {
    const results: T[] = [];
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (data) => results.push(data))
      .on('end', () => resolve(results))
      .on('error', reject);
  });
}

async function importData() {
  const basePath = path.join(__dirname, '../../tt_tester');

  try {
    // Get or create a test school
    let school = await prisma.school.findFirst();
    if (!school) {
      school = await prisma.school.create({
        data: {
          name: 'Test School',
          address: '123 Test Street',
          settings: JSON.stringify({
            periodsPerDay: 8,
            daysPerWeek: 5,
            periodDuration: 45,
            breakDuration: 10,
            lunchDuration: 30,
          }),
        },
      });
    }

    console.log('Using school:', school.name);

    // Create academic year if needed
    let academicYear = await prisma.academicYear.findFirst({
      where: { schoolId: school.id }
    });
    if (!academicYear) {
      academicYear = await prisma.academicYear.create({
        data: {
          schoolId: school.id,
          year: '2024-2025',
          startDate: new Date('2024-09-01'),
          endDate: new Date('2025-06-30'),
        }
      });
    }

    // Import Subjects
    console.log('Importing subjects...');
    const csvSubjects = await readCSV<CSVSubject>(path.join(basePath, 'test_data_subjects.csv'));

    for (const csvSubject of csvSubjects) {
      const existingSubject = await prisma.subject.findFirst({
        where: {
          schoolId: school.id,
          name: csvSubject.name
        }
      });

      if (!existingSubject) {
        await prisma.subject.create({
          data: {
            name: csvSubject.name,
            requiresLab: csvSubject.needs_lab === 'True',
            credits: parseInt(csvSubject.periods_per_week),
            minPeriodsPerWeek: parseInt(csvSubject.periods_per_week),
            maxPeriodsPerWeek: parseInt(csvSubject.periods_per_week),
            schoolId: school.id,
          },
        });
      }
    }
    console.log(`✓ Imported ${csvSubjects.length} subjects`);

    // Import Rooms
    console.log('Importing rooms...');
    const csvRooms = await readCSV<CSVRoom>(path.join(basePath, 'test_data_rooms.csv'));

    for (const csvRoom of csvRooms) {
      const existingRoom = await prisma.room.findFirst({
        where: {
          schoolId: school.id,
          name: csvRoom.name
        }
      });

      if (!existingRoom) {
        await prisma.room.create({
          data: {
            name: csvRoom.name,
            type: csvRoom.type.toUpperCase() as any,
            capacity: parseInt(csvRoom.capacity),
            schoolId: school.id,
          },
        });
      }
    }
    console.log(`✓ Imported ${csvRooms.length} rooms`);

    // Import Classes
    console.log('Importing classes...');
    const csvClasses = await readCSV<CSVClass>(path.join(basePath, 'test_data_classes.csv'));

    for (const csvClass of csvClasses) {
      const existingClass = await prisma.class.findFirst({
        where: {
          schoolId: school.id,
          grade: parseInt(csvClass.grade),
          section: csvClass.section,
        }
      });

      if (!existingClass) {
        await prisma.class.create({
          data: {
            name: csvClass.name,
            grade: parseInt(csvClass.grade),
            section: csvClass.section,
            studentCount: parseInt(csvClass.capacity),
            schoolId: school.id,
          },
        });
      }
    }
    console.log(`✓ Imported ${csvClasses.length} classes`);

    // Import Teachers
    console.log('Importing teachers...');
    const csvTeachers = await readCSV<CSVTeacher>(path.join(basePath, 'test_data_teachers.csv'));

    for (const csvTeacher of csvTeachers) {
      // Create user first
      const user = await prisma.user.upsert({
        where: { email: csvTeacher.email },
        update: {},
        create: {
          email: csvTeacher.email,
          passwordHash: '$2b$10$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', // Default hash
          role: 'TEACHER',
          schoolId: school.id,
          profile: JSON.stringify({
            name: csvTeacher.name,
            phone: csvTeacher.phone,
          }),
        },
      });

      // Create teacher
      const subjects = csvTeacher.subjects_qualified.split(',').map(s => s.trim());

      await prisma.teacher.upsert({
        where: { userId: user.id },
        update: {},
        create: {
          userId: user.id,
          subjects: JSON.stringify(subjects),
          maxPeriodsPerDay: parseInt(csvTeacher.max_periods_per_day),
          maxPeriodsPerWeek: parseInt(csvTeacher.max_periods_per_week),
          availability: JSON.stringify({
            monday: { available: true, periods: [1,2,3,4,5,6,7,8] },
            tuesday: { available: true, periods: [1,2,3,4,5,6,7,8] },
            wednesday: { available: true, periods: [1,2,3,4,5,6,7,8] },
            thursday: { available: true, periods: [1,2,3,4,5,6,7,8] },
            friday: { available: true, periods: [1,2,3,4,5,6,7,8] },
          }),
          preferences: JSON.stringify([]),
        },
      });
    }
    console.log(`✓ Imported ${csvTeachers.length} teachers`);

    console.log('\n🎉 Data import completed successfully!');
    console.log(`School: ${school.name} (ID: ${school.id})`);

    // Print summary
    const counts = await Promise.all([
      prisma.subject.count({ where: { schoolId: school.id } }),
      prisma.room.count({ where: { schoolId: school.id } }),
      prisma.class.count({ where: { schoolId: school.id } }),
      prisma.teacher.count({ where: { user: { schoolId: school.id } } }),
    ]);

    console.log('\nImported data summary:');
    console.log(`- Subjects: ${counts[0]}`);
    console.log(`- Rooms: ${counts[1]}`);
    console.log(`- Classes: ${counts[2]}`);
    console.log(`- Teachers: ${counts[3]}`);

  } catch (error) {
    console.error('Error importing data:', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

if (require.main === module) {
  importData()
    .catch((error) => {
      console.error('Import failed:', error);
      process.exit(1);
    });
}

export { importData };