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

  @ApiProperty({ example: 'MATH' })
  @IsString()
  code: string;

  @ApiPropertyOptional({ enum: SubjectType, default: SubjectType.CORE })
  @IsOptional()
  @IsEnum(SubjectType)
  type?: SubjectType;

  @ApiPropertyOptional({ example: 4, minimum: 1, maximum: 10 })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(10)
  periodsPerWeek?: number;

  @ApiPropertyOptional({ example: 2, description: 'Credit hours' })
  @IsOptional()
  @IsNumber()
  credits?: number;

  @ApiPropertyOptional({ example: true, description: 'Whether the subject requires a lab' })
  @IsOptional()
  @IsBoolean()
  requiresLab?: boolean;

  @ApiPropertyOptional({ example: false, description: 'Whether the subject requires special room' })
  @IsOptional()
  @IsBoolean()
  requiresSpecialRoom?: boolean;

  @ApiPropertyOptional({ example: 'Advanced mathematics covering algebra, geometry, and calculus' })
  @IsOptional()
  @IsString()
  description?: string;
}