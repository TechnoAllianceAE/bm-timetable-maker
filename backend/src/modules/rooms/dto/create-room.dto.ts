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
  @ApiProperty({ example: 'school-id-123' })
  @IsString()
  schoolId: string;

  @ApiProperty({ example: '101' })
  @IsString()
  roomNumber: string;

  @ApiPropertyOptional({ example: 'Building A' })
  @IsOptional()
  @IsString()
  building?: string;

  @ApiPropertyOptional({ example: '1', description: 'Floor number' })
  @IsOptional()
  @IsString()
  floor?: string;

  @ApiPropertyOptional({ enum: RoomType, default: RoomType.CLASSROOM })
  @IsOptional()
  @IsEnum(RoomType)
  type?: RoomType;

  @ApiProperty({ example: 40, minimum: 1, maximum: 200 })
  @IsNumber()
  @Min(1)
  @Max(200)
  capacity: number;

  @ApiPropertyOptional({
    example: ['Projector', 'Whiteboard', 'Air Conditioning'],
    description: 'List of equipment/facilities available'
  })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  facilities?: string[];

  @ApiPropertyOptional({ example: true, default: true })
  @IsOptional()
  @IsBoolean()
  isAvailable?: boolean;

  @ApiPropertyOptional({ example: 'Physics and Chemistry Lab' })
  @IsOptional()
  @IsString()
  description?: string;
}