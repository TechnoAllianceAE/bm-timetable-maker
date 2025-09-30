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

  @ApiProperty({ example: 'Class 10A', description: 'Name of the class' })
  @IsString()
  name: string;

  @ApiProperty({ example: 10, description: 'Grade level (1-12)' })
  @IsNumber()
  @Min(1)
  @Max(12)
  grade: number;

  @ApiPropertyOptional({ example: 'A', description: 'Section (A, B, C, etc.)' })
  @IsOptional()
  @IsString()
  section?: string;

  @ApiPropertyOptional({ example: 'SCIENCE', description: 'Stream for grades 11-12' })
  @IsOptional()
  @IsString()
  stream?: string;

  @ApiPropertyOptional({ example: 35, minimum: 1, maximum: 60 })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(60)
  studentCount?: number;
}