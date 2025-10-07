import { IsString, IsOptional, IsObject, IsDateString, IsArray, ValidateNested, IsInt, IsEnum } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Type } from 'class-transformer';

export enum ConstraintType {
  EXACT = 'exact',
  MIN = 'min',
  MAX = 'max',
}

export class GradeSubjectRequirementDto {
  @ApiProperty({ example: 1, description: 'Grade number (1-12)' })
  @IsInt()
  grade: number;

  @ApiProperty({ example: 'subject-id-123' })
  @IsString()
  subjectId: string;

  @ApiProperty({ example: 6, description: 'Required periods per week' })
  @IsInt()
  periodsPerWeek: number;

  @ApiPropertyOptional({
    enum: ConstraintType,
    example: 'exact',
    description: 'Constraint type: exact (must be exactly N), min (at least N), max (at most N)',
    default: 'exact'
  })
  @IsOptional()
  @IsEnum(ConstraintType)
  constraintType?: ConstraintType;
}

export class GenerateTimetableDto {
  @ApiProperty({ example: 'school-id-123' })
  @IsString()
  schoolId: string;

  @ApiProperty({ example: 'academic-year-id-123' })
  @IsString()
  academicYearId: string;

  @ApiPropertyOptional({ example: 'Fall 2024 Timetable' })
  @IsOptional()
  @IsString()
  name?: string;

  @ApiPropertyOptional({ example: '2024-01-01' })
  @IsOptional()
  @IsDateString()
  startDate?: string;

  @ApiPropertyOptional({ example: '2024-12-31' })
  @IsOptional()
  @IsDateString()
  endDate?: string;

  @ApiPropertyOptional({
    example: {
      maxConsecutivePeriods: 3,
      minLunchBreakDuration: 30,
      preferMorningForMath: true,
      avoidFridayLastPeriod: true,
    },
    description: 'Additional constraints for timetable generation'
  })
  @IsOptional()
  @IsObject()
  constraints?: any;

  @ApiPropertyOptional({
    type: [GradeSubjectRequirementDto],
    description: 'Subject hour requirements per grade'
  })
  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => GradeSubjectRequirementDto)
  subjectRequirements?: GradeSubjectRequirementDto[];
}