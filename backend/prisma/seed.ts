import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Start seeding...');

  // Create a test school
  const school = await prisma.school.upsert({
    where: { id: 'default-school-id' },
    update: {},
    create: {
      id: 'default-school-id',
      name: 'Test School',
      address: '123 Test Street, Test City',
      settings: JSON.stringify({
        academicYear: '2024-2025',
        timezone: 'UTC',
      }),
      subscriptionTier: 'premium',
    },
  });

  console.log('Created school:', school);

  console.log('Seeding completed.');
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });