import { IsString, IsOptional, IsEnum, IsObject } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum SubscriptionTier {
  BASIC = 'BASIC',
  PREMIUM = 'PREMIUM',
  ENTERPRISE = 'ENTERPRISE',
}

export class CreateSchoolDto {
  @ApiProperty({ example: 'St. Mary\'s High School' })
  @IsString()
  name: string;

  @ApiPropertyOptional({ example: '123 Main Street, New York, NY 10001' })
  @IsOptional()
  @IsString()
  address?: string;

  @ApiPropertyOptional({
    example: {
      workingDays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      startTime: '08:00',
      endTime: '15:00',
      lunchBreakStart: '12:00',
      lunchBreakEnd: '13:00',
      periodsPerDay: 8,
      periodDuration: 45
    }
  })
  @IsOptional()
  @IsObject()
  settings?: any;

  @ApiPropertyOptional({ enum: SubscriptionTier, default: SubscriptionTier.BASIC })
  @IsOptional()
  @IsEnum(SubscriptionTier)
  subscriptionTier?: SubscriptionTier;
}