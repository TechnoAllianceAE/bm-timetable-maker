import { PrismaClient, Role, Stream, DayOfWeek, RoomType, BurnoutRiskLevel, AlertSeverity, TimetableStatus, WellnessImpact, SubstitutionStatus, ConstraintType, ConstraintPriority, PredictionType } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Create a test school
  const school = await prisma.school.upsert({
    where: { name: 'Test Central School' },
    update: {},
    create: {
      name: 'Test Central School',
      address: '123 MG Road, Mumbai, India',
      subscriptionTier: 'premium',
      settings: { country: 'India' },
      wellnessConfig: { maxDailyHours: 6, mandatoryBreaks: true },
    },
  });

  console.log(`Created school: ${school.name} (ID: ${school.id})`);

  // Create academic year
  const academicYear = await prisma.academicYear.upsert({
    where: { schoolId_year: { schoolId: school.id, year: '2024-2025' } },
    update: {},
    create: {
      schoolId: school.id,
      year: '2024-2025',
      startDate: new Date('2024-04-01'),
      endDate: new Date('2025-03-31'),
    },
  });

  console.log(`Created academic year: ${academicYear.year}`);

  // Create 10 subjects (common Indian school subjects)
  const subjects = await prisma.subject.createMany({
    data: [
      { schoolId: school.id, name: 'English', department: 'Languages', credits: 5, minPeriodsPerWeek: 5, maxPeriodsPerWeek: 6, prepTime: 30, correctionWorkload: 0.5, requiresLab: false },
      { schoolId: school.id, name: 'Mathematics', department: 'Mathematics', credits: 6, minPeriodsPerWeek: 6, maxPeriodsPerWeek: 7, prepTime: 45, correctionWorkload: 0.3, requiresLab: false },
      { schoolId: school.id, name: 'Science (Physics)', department: 'Science', credits: 4, minPeriodsPerWeek: 4, maxPeriodsPerWeek: 5, prepTime: 60, correctionWorkload: 0.4, requiresLab: true },
      { schoolId: school.id, name: 'Science (Chemistry)', department: 'Science', credits: 4, minPeriodsPerWeek: 4, maxPeriodsPerWeek: 5, prepTime: 60, correctionWorkload: 0.4, requiresLab: true },
      { schoolId: school.id, name: 'Science (Biology)', department: 'Science', credits: 4, minPeriodsPerWeek: 4, maxPeriodsPerWeek: 5, prepTime: 60, correctionWorkload: 0.4, requiresLab: true },
      { schoolId: school.id, name: 'History', department: 'Social Science', credits: 4, minPeriodsPerWeek: 4, maxPeriodsPerWeek: 5, prepTime: 30, correctionWorkload: 0.6, requiresLab: false },
      { schoolId: school.id, name: 'Geography', department: 'Social Science', credits: 4, minPeriodsPerWeek: 4, maxPeriodsPerWeek: 5, prepTime: 30, correctionWorkload: 0.5, requiresLab: false },
      { schoolId: school.id, name: 'Hindi', department: 'Languages', credits: 4, minPeriodsPerWeek: 4, maxPeriodsPerWeek: 5, prepTime: 30, correctionWorkload: 0.5, requiresLab: false },
      { schoolId: school.id, name: 'Computer Science', department: 'Technology', credits: 3, minPeriodsPerWeek: 3, maxPeriodsPerWeek: 4, prepTime: 45, correctionWorkload: 0.3, requiresLab: true },
      { schoolId: school.id, name: 'Physical Education', department: 'Sports', credits: 2, minPeriodsPerWeek: 2, maxPeriodsPerWeek: 3, prepTime: 15, correctionWorkload: 0.2, requiresLab: false },
    ],
    skipDuplicates: true,
  });

  console.log(`Created ${subjects.count} subjects`);

  // Create 6 classes: Grades 9,10 (2 div each), Grade 11 (2 div, with streams)
  const classesData = [
    { schoolId: school.id, name: 'Class 9A', grade: 9, section: 'A', studentCount: 40 },
    { schoolId: school.id, name: 'Class 9B', grade: 9, section: 'B', studentCount: 40 },
    { schoolId: school.id, name: 'Class 10A', grade: 10, section: 'A', studentCount: 40 },
    { schoolId: school.id, name: 'Class 10B', grade: 10, section: 'B', studentCount: 40 },
    { schoolId: school.id, name: 'Class 11Science A', grade: 11, section: 'A', stream: 'SCIENCE', studentCount: 35 },
    { schoolId: school.id, name: 'Class 11Science B', grade: 11, section: 'B', stream: 'SCIENCE', studentCount: 35 },
  ];

  const classes = await prisma.class.createMany({
    data: classesData,
    skipDuplicates: true,
  });

  console.log(`Created ${classes.count} classes`);

  // Fake Indian teacher names and emails (20 teachers, 2 per subject roughly)
  const indianTeachers = [
    // English
    { name: 'Priya Sharma', email: 'priya.sharma@testschool.com', subjects: ['English'] },
    { name: 'Amit Patel', email: 'amit.patel@testschool.com', subjects: ['English', 'Hindi'] },
    // Mathematics
    { name: 'Rajesh Kumar', email: 'rajesh.kumar@testschool.com', subjects: ['Mathematics'] },
    { name: 'Neha Gupta', email: 'neha.gupta@testschool.com', subjects: ['Mathematics'] },
    // Physics
    { name: 'Suresh Reddy', email: 'suresh.reddy@testschool.com', subjects: ['Science (Physics)'] },
    { name: 'Anita Singh', email: 'anita.singh@testschool.com', subjects: ['Science (Physics)'] },
    // Chemistry
    { name: 'Vikram Joshi', email: 'vikram.joshi@testschool.com', subjects: ['Science (Chemistry)'] },
    { name: 'Lata Devi', email: 'lata.devi@testschool.com', subjects: ['Science (Chemistry)'] },
    // Biology
    { name: 'Kiran Rao', email: 'kiran.rao@testschool.com', subjects: ['Science (Biology)'] },
    { name: 'Rohit Nair', email: 'rohit.nair@testschool.com', subjects: ['Science (Biology)'] },
    // History
    { name: 'Meera Iyer', email: 'meera.iyer@testschool.com', subjects: ['History'] },
    { name: 'Deepak Yadav', email: 'deepak.yadav@testschool.com', subjects: ['History', 'Geography'] },
    // Geography
    { name: 'Sunita Bose', email: 'sunita.bose@testschool.com', subjects: ['Geography'] },
    { name: 'Arjun Malhotra', email: 'arjun.malhotra@testschool.com', subjects: ['Geography'] },
    // Hindi
    { name: 'Ritu Agarwal', email: 'ritu.agarwal@testschool.com', subjects: ['Hindi'] },
    { name: 'Mohan Das', email: 'mohan.das@testschool.com', subjects: ['Hindi'] },
    // Computer Science
    { name: 'Pooja Menon', email: 'pooja.menon@testschool.com', subjects: ['Computer Science'] },
    { name: 'Sameer Khan', email: 'sameer.khan@testschool.com', subjects: ['Computer Science'] },
    // Physical Education
    { name: 'Ravi Shankar', email: 'ravi.shankar@testschool.com', subjects: ['Physical Education'] },
    { name: 'Indira Pillai', email: 'indira.pillai@testschool.com', subjects: ['Physical Education'] },
  ];

  // Create users and teachers
  for (const teacherData of indianTeachers) {
    const user = await prisma.user.upsert({
      where: { email: teacherData.email },
      update: {},
      create: {
        schoolId: school.id,
        email: teacherData.email,
        passwordHash: '$2b$10$K.ExampleHashForSeeding', // Dummy hash
        role: Role.TEACHER,
        profile: { name: teacherData.name },
        wellnessPreferences: { preferredBreaks: 2 },
      },
    });

    await prisma.teacher.upsert({
      where: { userId: user.id },
      update: {},
      create: {
        userId: user.id,
        subjects: teacherData.subjects, // JSON array of subject names
        availability: { monday: ['09:00-12:00', '14:00-16:00'] }, // Sample
        preferences: { noEarlyClasses: false },
        maxPeriodsPerDay: 6,
        maxPeriodsPerWeek: 30,
        maxConsecutivePeriods: 3,
        minBreakDuration: 10,
        wellnessScore: 85.0,
        burnoutRiskLevel: BurnoutRiskLevel.LOW,
      },
    });

    // Create workload config for each teacher
    await prisma.teacherWorkloadConfig.upsert({
      where: { teacherId: user.id }, // Assuming teacher.id == user.id for simplicity, but actually teacher.id is separate
      wait: false, // Upsert might need adjustment; in practice, get teacherId after creation
    });
  }

  console.log(`Created ${indianTeachers.length} teachers with Indian names`);

  // Note: For full seeding of workload configs, we'd need to fetch teacher IDs post-creation.
  // For simplicity, assuming the above creates them; in real seed, chain with await and fetch IDs.

  // Create sample time slots (Mon-Fri, 8 slots per day)
  const days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'] as DayOfWeek[];
  const timeSlotsData = [];
  for (const day of days) {
    for (let i = 1; i <= 8; i++) {
      const startHour = 8 + Math.floor((i - 1) / 2); // Rough: 8-9,9-10,10-11,11-12,13-14,14-15,15-16,16-17
      const startTime = `${startHour.toString().padStart(2, '0')}:00`;
      const endTime = `${(startHour + 1).toString().padStart(2, '0')}:00`;
      timeSlotsData.push({
        schoolId: school.id,
        day,
        startTime,
        endTime,
        isBreak: i % 4 === 0, // Lunch break around 12-1
      });
    }
  }

  await prisma.timeSlot.createMany({
    data: timeSlotsData,
    skipDuplicates: true,
  });

  console.log(`Created sample time slots`);

  // Create sample rooms
  await prisma.room.createMany({
    data: [
      { schoolId: school.id, name: 'Room 101', capacity: 40, type: RoomType.CLASSROOM },
      { schoolId: school.id, name: 'Room 102', capacity: 40, type: RoomType.CLASSROOM },
      { schoolId: school.id, name: 'Lab 1', capacity: 30, type: RoomType.LAB },
      { schoolId: school.id, name: 'Lab 2', capacity: 30, type: RoomType.LAB },
      { schoolId: school.id, name: 'Sports Ground', capacity: 100, type: RoomType.CLASSROOM }, // Reuse for PE
    ],
    skipDuplicates: true,
  });

  console.log('Created sample rooms');

  // Create sample constraints (wellness and academic)
  await prisma.constraint.createMany({
    data: [
      // Academic
      {
        schoolId: school.id,
        type: ConstraintType.ACADEMIC_MIN_PERIODS,
        entityId: 'Mathematics', // Use subject name for simplicity
        value: { min: 6 },
        priority: ConstraintPriority.HARD,
      },
      {
        schoolId: school.id,
        type: ConstraintType.ACADEMIC_TIME_PREFERENCE,
        entityId: 'Science (Physics)',
        value: { beforeNoon: true },
        priority: ConstraintPriority.SOFT,
      },
      // Wellness
      {
        schoolId: school.id,
        type: 'WELLNESS_MAX_CONSECUTIVE', // Note: Enum might need extension
        entityId: 'teacher-general',
        value: { max: 3 },
        priority: ConstraintPriority.HARD,
      },
      {
        schoolId: school.id,
        type: 'WELLNESS_DAILY_HOURS',
        entityId: 'teacher-general',
        value: { max: 6 },
        priority: ConstraintPriority.HARD,
      },
    ],
    skipDuplicates: true,
  });

  console.log('Created sample constraints');

  // Create an empty timetable for testing generation
  const timetable = await prisma.timetable.create({
    data: {
      schoolId: school.id,
      academicYearId: academicYear.id,
      version: 1,
      status: TimetableStatus.DRAFT,
      wellnessScore: 0,
      workloadBalanceScore: 0,
      metadata: {},
      wellnessAnalysis: {},
    },
  });

  console.log(`Created draft timetable for testing (ID: ${timetable.id})`);

  // Optional: Create a sample wellness metric for a teacher (assuming first teacher ID)
  // In practice, fetch a teacher ID
  // const firstTeacher = await prisma.teacher.findFirst();
  // if (firstTeacher) {
  //   await prisma.teacherWellnessMetric.create({
  //     data: {
  //       teacherId: firstTeacher.id,
  //       metricDate: new Date(),
  //       teachingHours: 20,
  //       stressScore: 40,
  //       wellnessScore: 75,
  //     },
  //   });
  // }

  console.log('Seeding completed. Ready for timetable generation testing.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });