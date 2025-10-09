import { IsString, IsOptional, IsNumber, IsBoolean, IsEnum, IsArray, Min, Max } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum RoomType {
  CLASSROOM = 'CLASSROOM',
  LAB = 'LAB',
  LIBRARY = 'LIBRARY',
  COMPUTER_LAB = 'COMPUTER_LAB',
  SCIENCE_LAB = 'SCIENCE_LAB',
  AUDITORIUM = 'AUDITORIUM',
  GYMNASIUM = 'GYMNASIUM',
  MUSIC_ROOM = 'MUSIC_ROOM',
  ART_ROOM = 'ART_ROOM',
  SPECIAL = 'SPECIAL',
}

export class CreateRoomDto {
  @ApiPropertyOptional({ example: 'school-id-123' })
  @IsOptional()
  @IsString()
  schoolId?: string;

  @ApiProperty({ example: 'Room 101' })
  @IsString()
  name: string;

  @ApiPropertyOptional({ example: 'R101' })
  @IsOptional()
  @IsString()
  code?: string;

  @ApiPropertyOptional({ example: 40, minimum: 1, maximum: 200 })
  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(200)
  capacity?: number;

  @ApiPropertyOptional({ example: 'CLASSROOM', description: 'Type of room' })
  @IsOptional()
  @IsString()
  type?: string;
}