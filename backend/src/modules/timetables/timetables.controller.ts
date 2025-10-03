import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiResponse } from '@nestjs/swagger';
import { TimetablesService } from './timetables.service';
import { GenerateTimetableDto } from './dto/generate-timetable.dto';
import { UpdateTimetableDto } from './dto/update-timetable.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('timetables')
@Controller('timetables')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class TimetablesController {
  constructor(private readonly timetablesService: TimetablesService) {}

  @Post('generate')
  @ApiOperation({ summary: 'Generate a new timetable' })
  @ApiResponse({ status: 201, description: 'Timetable generated successfully' })
  @ApiResponse({ status: 400, description: 'Invalid constraints' })
  generate(@Body() generateTimetableDto: GenerateTimetableDto) {
    console.log('Received timetable generation request:', generateTimetableDto);
    return this.timetablesService.generate(generateTimetableDto);
  }

  @Get()
  @ApiOperation({ summary: 'Get all timetables' })
  @ApiResponse({ status: 200, description: 'Return all timetables' })
  findAll(
    @Query('schoolId') schoolId?: string,
    @Query('status') status?: string,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.timetablesService.findAll(schoolId, status, page, limit);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get a timetable by ID' })
  @ApiResponse({ status: 200, description: 'Return the timetable' })
  @ApiResponse({ status: 404, description: 'Timetable not found' })
  findOne(@Param('id') id: string) {
    return this.timetablesService.findOne(id);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update a timetable' })
  @ApiResponse({ status: 200, description: 'Timetable updated successfully' })
  @ApiResponse({ status: 404, description: 'Timetable not found' })
  update(@Param('id') id: string, @Body() updateTimetableDto: UpdateTimetableDto) {
    return this.timetablesService.update(id, updateTimetableDto);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete a timetable' })
  @ApiResponse({ status: 200, description: 'Timetable deleted successfully' })
  @ApiResponse({ status: 404, description: 'Timetable not found' })
  remove(@Param('id') id: string) {
    return this.timetablesService.remove(id);
  }

  @Post(':id/activate')
  @ApiOperation({ summary: 'Activate a timetable' })
  @ApiResponse({ status: 200, description: 'Timetable activated successfully' })
  @ApiResponse({ status: 404, description: 'Timetable not found' })
  activate(@Param('id') id: string) {
    return this.timetablesService.activate(id);
  }

  @Post(':id/deactivate')
  @ApiOperation({ summary: 'Deactivate a timetable' })
  @ApiResponse({ status: 200, description: 'Timetable deactivated successfully' })
  @ApiResponse({ status: 404, description: 'Timetable not found' })
  deactivate(@Param('id') id: string) {
    return this.timetablesService.deactivate(id);
  }

  @Get(':id/entries')
  @ApiOperation({ summary: 'Get timetable entries with details' })
  @ApiResponse({ status: 200, description: 'Return timetable entries with class, teacher, subject, room, and timeslot details' })
  @ApiResponse({ status: 404, description: 'Timetable not found' })
  getEntries(@Param('id') id: string) {
    return this.timetablesService.getEntries(id);
  }
}