import { IsString, IsOptional, IsNumber, IsEnum, Min, Max } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum ClassStream {
  SCIENCE = 'SCIENCE',
  COMMERCE = 'COMMERCE',
  ARTS = 'ARTS',
}

export class CreateClassDto {
  @ApiProperty({ example: 'school-id-123' })
  @IsString()
  schoolId: string;

  @ApiProperty({ example: '10', description: 'Grade level (1-12)' })
  @IsString()
  grade: string;

  @ApiProperty({ example: 'A', description: 'Section (A, B, C, etc.)' })
  @IsString()
  section: string;

  @ApiPropertyOptional({ enum: ClassStream, description: 'Stream for grades 11-12' })
  @IsOptional()
  @IsEnum(ClassStream)
  stream?: ClassStream;

  @ApiPropertyOptional({ example: 35, minimum: 1, maximum: 60 })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(60)
  studentCount?: number;

  @ApiPropertyOptional({ example: 'Room 101', description: 'Home room for the class' })
  @IsOptional()
  @IsString()
  homeRoom?: string;

  @ApiPropertyOptional({ example: 'teacher-id-123', description: 'Class teacher ID' })
  @IsOptional()
  @IsString()
  classTeacherId?: string;
}