import { IsEmail, IsString, IsEnum, IsOptional, MinLength, IsObject } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { UserRole } from '../../auth/dto/register.dto';

export class CreateUserDto {
  @ApiProperty({ example: 'john.doe@example.com' })
  @IsEmail()
  email: string;

  @ApiProperty({ example: 'hashedPassword123!', description: 'Hashed password' })
  @IsString()
  @IsOptional()
  passwordHash?: string;

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
  profile?: any;
}