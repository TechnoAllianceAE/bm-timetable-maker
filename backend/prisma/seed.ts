import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('Start seeding...');

  // Create super admin user (not tied to any school)
  const hashedPassword = await bcrypt.hash('Admin123', 10);

  const adminUser = await prisma.user.upsert({
    where: { email: 'admin@test.com' },
    update: {},
    create: {
      email: 'admin@test.com',
      passwordHash: hashedPassword,
      role: 'ADMIN',
      schoolId: null,  // Super admin with no school
      profile: JSON.stringify({
        firstName: 'Admin',
        lastName: 'User',
      }),
    },
  });

  console.log('Created super admin user:', { email: adminUser.email, role: adminUser.role });
  console.log('Seeding completed. Database is clean - users can create their own schools.');
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