import { IsString, IsOptional, IsObject } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class GenerateTimetableDto {
  @ApiProperty({ example: 'school-id-123' })
  @IsString()
  schoolId: string;

  @ApiPropertyOptional({ example: 'Fall 2024 Timetable' })
  @IsOptional()
  @IsString()
  name?: string;

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