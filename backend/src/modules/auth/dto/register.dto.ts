import { IsEmail, IsString, IsEnum, IsOptional, MinLength, IsObject } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum UserRole {
  ADMIN = 'ADMIN',
  PRINCIPAL = 'PRINCIPAL',
  TEACHER = 'TEACHER',
  STUDENT = 'STUDENT',
  PARENT = 'PARENT',
}

export class RegisterDto {
  @ApiProperty({ example: 'john.doe@example.com' })
  @IsEmail()
  email: string;

  @ApiProperty({ example: 'Password123!', minLength: 6 })
  @IsString()
  @MinLength(6)
  password: string;

  @ApiProperty({ example: 'school-id-123' })
  @IsString()
  schoolId: string;

  @ApiProperty({ enum: UserRole, example: UserRole.TEACHER })
  @IsEnum(UserRole)
  role: UserRole;

  @ApiPropertyOptional({
    example: {
      firstName: 'John',
      lastName: 'Doe',
      phone: '+1234567890'
    }
  })
  @IsOptional()
  @IsObject()
  profile?: {
    firstName: string;
    lastName: string;
    phone?: string;
  };
}