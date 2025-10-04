import { Controller, Get, HttpStatus, Res } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { Response } from 'express';
import { HealthService, HealthStatus } from './health.service';

@ApiTags('health')
@Controller('health')
export class HealthController {
  constructor(private readonly healthService: HealthService) {}

  @Get()
  @ApiOperation({ summary: 'Check system health status' })
  @ApiResponse({
    status: 200,
    description: 'System is healthy',
  })
  @ApiResponse({
    status: 503,
    description: 'System is degraded or unhealthy',
  })
  async checkHealth(@Res() res: Response): Promise<Response> {
    const healthStatus: HealthStatus = await this.healthService.checkHealth();

    // Set HTTP status based on health
    let httpStatus: number;
    switch (healthStatus.status) {
      case 'healthy':
        httpStatus = HttpStatus.OK;
        break;
      case 'degraded':
        httpStatus = HttpStatus.SERVICE_UNAVAILABLE;
        break;
      case 'unhealthy':
        httpStatus = HttpStatus.SERVICE_UNAVAILABLE;
        break;
    }

    return res.status(httpStatus).json(healthStatus);
  }
}
