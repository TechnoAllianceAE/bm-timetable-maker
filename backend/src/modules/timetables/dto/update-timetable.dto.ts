import { IsString, IsOptional, IsEnum, IsObject } from 'class-validator';
import { ApiPropertyOptional } from '@nestjs/swagger';

export enum TimetableStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
}

export class UpdateTimetableDto {
  @ApiPropertyOptional({ example: 'Fall 2024 Timetable' })
  @IsOptional()
  @IsString()
  name?: string;

  @ApiPropertyOptional({ enum: TimetableStatus })
  @IsOptional()
  @IsEnum(TimetableStatus)
  status?: TimetableStatus;

  @ApiPropertyOptional()
  @IsOptional()
  @IsObject()
  metadata?: any;
}