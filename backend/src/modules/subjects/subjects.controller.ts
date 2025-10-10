import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards, Request, BadRequestException } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiResponse } from '@nestjs/swagger';
import { SubjectsService } from './subjects.service';
import { CreateSubjectDto } from './dto/create-subject.dto';
import { UpdateSubjectDto } from './dto/update-subject.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('subjects')
@Controller('subjects')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class SubjectsController {
  constructor(private readonly subjectsService: SubjectsService) {}

  @Post()
  @ApiOperation({ summary: 'Create a new subject' })
  @ApiResponse({ status: 201, description: 'Subject created successfully' })
  create(@Body() createSubjectDto: CreateSubjectDto, @Request() req: any) {
    // Extract schoolId from JWT token
    const schoolId = req.user?.schoolId;
    if (!schoolId) {
      throw new BadRequestException('School ID not found in user session');
    }

    // Set schoolId from token
    createSubjectDto.schoolId = schoolId;
    return this.subjectsService.create(createSubjectDto);
  }

  @Get()
  @ApiOperation({ summary: 'Get all subjects' })
  @ApiResponse({ status: 200, description: 'Return all subjects' })
  findAll(
    @Query('schoolId') schoolId?: string,
    @Query('page') page?: string,
    @Query('limit') limit?: string,
  ) {
    const pageNum = page ? parseInt(page, 10) : undefined;
    const limitNum = limit ? parseInt(limit, 10) : undefined;
    return this.subjectsService.findAll(schoolId, pageNum, limitNum);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get a subject by ID' })
  @ApiResponse({ status: 200, description: 'Return the subject' })
  @ApiResponse({ status: 404, description: 'Subject not found' })
  findOne(@Param('id') id: string) {
    return this.subjectsService.findOne(id);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update a subject' })
  @ApiResponse({ status: 200, description: 'Subject updated successfully' })
  @ApiResponse({ status: 404, description: 'Subject not found' })
  update(@Param('id') id: string, @Body() updateSubjectDto: UpdateSubjectDto) {
    return this.subjectsService.update(id, updateSubjectDto);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete a subject' })
  @ApiResponse({ status: 200, description: 'Subject deleted successfully' })
  @ApiResponse({ status: 404, description: 'Subject not found' })
  remove(@Param('id') id: string) {
    return this.subjectsService.remove(id);
  }

  @Post('bulk')
  @ApiOperation({ summary: 'Create multiple subjects' })
  @ApiResponse({ status: 201, description: 'Subjects created successfully' })
  createBulk(@Body() createSubjectDtos: CreateSubjectDto[]) {
    return this.subjectsService.createBulk(createSubjectDtos);
  }
}