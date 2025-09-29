import { IsString, IsOptional, IsArray, IsNumber, IsObject, Min, Max } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateTeacherDto {
  @ApiProperty({ example: 'user-id-123' })
  @IsString()
  userId: string;

  @ApiPropertyOptional({
    example: ['subject-id-1', 'subject-id-2'],
    description: 'Array of subject IDs the teacher can teach'
  })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  subjects?: string[];

  @ApiPropertyOptional({
    example: {
      Monday: { start: '08:00', end: '16:00', unavailable: ['12:00-13:00'] },
      Tuesday: { start: '08:00', end: '16:00', unavailable: [] },
      Wednesday: { start: '08:00', end: '16:00', unavailable: [] },
      Thursday: { start: '08:00', end: '16:00', unavailable: [] },
      Friday: { start: '08:00', end: '14:00', unavailable: [] }
    },
    description: 'Teacher availability schedule'
  })
  @IsOptional()
  @IsObject()
  availability?: any;

  @ApiPropertyOptional({
    example: 6,
    description: 'Maximum teaching periods per day',
    minimum: 1,
    maximum: 10
  })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(10)
  maxPeriodsPerDay?: number;

  @ApiPropertyOptional({
    example: 25,
    description: 'Maximum teaching periods per week',
    minimum: 1,
    maximum: 50
  })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(50)
  maxPeriodsPerWeek?: number;

  @ApiPropertyOptional({
    example: ['No early morning classes', 'Prefers continuous periods'],
    description: 'Teacher preferences'
  })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  preferences?: string[];
}