import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiResponse } from '@nestjs/swagger';
import { SchoolsService } from './schools.service';
import { CreateSchoolDto } from './dto/create-school.dto';
import { UpdateSchoolDto } from './dto/update-school.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('schools')
@Controller('schools')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class SchoolsController {
  constructor(private readonly schoolsService: SchoolsService) {}

  @Post()
  @ApiOperation({ summary: 'Create a new school' })
  @ApiResponse({ status: 201, description: 'School created successfully' })
  create(@Body() createSchoolDto: CreateSchoolDto) {
    return this.schoolsService.create(createSchoolDto);
  }

  @Get()
  @ApiOperation({ summary: 'Get all schools' })
  @ApiResponse({ status: 200, description: 'Return all schools' })
  findAll(@Query('page') page?: number, @Query('limit') limit?: number) {
    return this.schoolsService.findAll(page, limit);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get a school by ID' })
  @ApiResponse({ status: 200, description: 'Return the school' })
  @ApiResponse({ status: 404, description: 'School not found' })
  findOne(@Param('id') id: string) {
    return this.schoolsService.findOne(id);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update a school' })
  @ApiResponse({ status: 200, description: 'School updated successfully' })
  @ApiResponse({ status: 404, description: 'School not found' })
  update(@Param('id') id: string, @Body() updateSchoolDto: UpdateSchoolDto) {
    return this.schoolsService.update(id, updateSchoolDto);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete a school' })
  @ApiResponse({ status: 200, description: 'School deleted successfully' })
  @ApiResponse({ status: 404, description: 'School not found' })
  remove(@Param('id') id: string) {
    return this.schoolsService.remove(id);
  }

  @Delete(':id/data')
  @ApiOperation({ summary: 'Delete all data for a school (classes, teachers, subjects, rooms, timetables)' })
  @ApiResponse({ status: 200, description: 'School data deleted successfully' })
  @ApiResponse({ status: 404, description: 'School not found' })
  deleteSchoolData(@Param('id') id: string) {
    return this.schoolsService.deleteSchoolData(id);
  }
}