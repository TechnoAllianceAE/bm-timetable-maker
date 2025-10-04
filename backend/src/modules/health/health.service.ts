import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { TimetableEngineClient } from '../../timetables/timetableEngine.client';

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    database: ServiceHealth;
    timetableEngine: ServiceHealth;
  };
  uptime: number;
}

export interface ServiceHealth {
  status: 'up' | 'down';
  message?: string;
  responseTime?: number;
}

@Injectable()
export class HealthService {
  private readonly logger = new Logger(HealthService.name);
  private readonly timetableEngineClient: TimetableEngineClient;
  private readonly startTime: number;

  constructor(private prisma: PrismaService) {
    this.timetableEngineClient = new TimetableEngineClient(
      process.env.PYTHON_TIMETABLE_URL || 'http://localhost:8000',
    );
    this.startTime = Date.now();
  }

  async checkHealth(): Promise<HealthStatus> {
    const timestamp = new Date().toISOString();
    const uptime = Math.floor((Date.now() - this.startTime) / 1000);

    // Check database health
    const databaseHealth = await this.checkDatabase();

    // Check Python timetable engine health
    const timetableEngineHealth = await this.checkTimetableEngine();

    // Determine overall status
    let overallStatus: 'healthy' | 'degraded' | 'unhealthy';
    if (databaseHealth.status === 'down') {
      overallStatus = 'unhealthy';
    } else if (timetableEngineHealth.status === 'down') {
      overallStatus = 'degraded';
    } else {
      overallStatus = 'healthy';
    }

    return {
      status: overallStatus,
      timestamp,
      services: {
        database: databaseHealth,
        timetableEngine: timetableEngineHealth,
      },
      uptime,
    };
  }

  private async checkDatabase(): Promise<ServiceHealth> {
    const startTime = Date.now();
    try {
      // Simple query to check database connection
      await this.prisma.$queryRaw`SELECT 1`;
      const responseTime = Date.now() - startTime;

      return {
        status: 'up',
        message: 'Database connection successful',
        responseTime,
      };
    } catch (error) {
      this.logger.error('Database health check failed:', error.message);
      return {
        status: 'down',
        message: `Database connection failed: ${error.message}`,
      };
    }
  }

  private async checkTimetableEngine(): Promise<ServiceHealth> {
    const startTime = Date.now();
    try {
      const healthResponse = await this.timetableEngineClient.health();
      const responseTime = Date.now() - startTime;

      return {
        status: 'up',
        message: `Timetable engine v${healthResponse.version || '2.5'} is running`,
        responseTime,
      };
    } catch (error) {
      this.logger.warn('Timetable engine health check failed:', error.message);
      return {
        status: 'down',
        message: `Timetable engine unreachable: ${error.message}`,
      };
    }
  }
}
