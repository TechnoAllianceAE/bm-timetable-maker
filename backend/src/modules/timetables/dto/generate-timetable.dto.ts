import { IsString, IsOptional, IsObject, IsDateString } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

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
}