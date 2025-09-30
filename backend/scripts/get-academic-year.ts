import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function getAcademicYear() {
  try {
    const academicYear = await prisma.academicYear.findFirst();
    if (academicYear) {
      console.log('Academic Year ID:', academicYear.id);
      console.log('Academic Year:', academicYear.year);
      console.log('School ID:', academicYear.schoolId);
    } else {
      console.log('No academic year found');
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

getAcademicYear();