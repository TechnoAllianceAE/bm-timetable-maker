import { IsString, IsOptional, IsNumber, IsBoolean, IsEnum, Min, Max } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum SubjectType {
  CORE = 'CORE',
  ELECTIVE = 'ELECTIVE',
  LAB = 'LAB',
  ACTIVITY = 'ACTIVITY',
}

export class CreateSubjectDto {
  @ApiProperty({ example: 'school-id-123' })
  @IsString()
  schoolId: string;

  @ApiProperty({ example: 'Mathematics' })
  @IsString()
  name: string;

  @ApiPropertyOptional({ example: 'Science', description: 'Department name' })
  @IsOptional()
  @IsString()
  department?: string;

  @ApiProperty({ example: 4, description: 'Credit hours' })
  @IsNumber()
  @Min(1)
  @Max(10)
  credits: number;

  @ApiPropertyOptional({ example: 4, minimum: 1, maximum: 10 })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(10)
  minPeriodsPerWeek?: number;

  @ApiPropertyOptional({ example: 6, minimum: 1, maximum: 10 })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(10)
  maxPeriodsPerWeek?: number;

  @ApiPropertyOptional({ example: 60, description: 'Preparation time in minutes' })
  @IsOptional()
  @IsNumber()
  prepTime?: number;

  @ApiPropertyOptional({ example: 0.5, description: 'Correction workload time per student' })
  @IsOptional()
  @IsNumber()
  correctionWorkload?: number;

  @ApiPropertyOptional({ example: false, description: 'Whether the subject requires a lab' })
  @IsOptional()
  @IsBoolean()
  requiresLab?: boolean;
}