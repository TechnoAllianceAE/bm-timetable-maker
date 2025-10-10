import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards, Request, BadRequestException } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiResponse } from '@nestjs/swagger';
import { ClassesService } from './classes.service';
import { CreateClassDto } from './dto/create-class.dto';
import { UpdateClassDto } from './dto/update-class.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('classes')
@Controller('classes')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class ClassesController {
  constructor(private readonly classesService: ClassesService) {}

  @Post()
  @ApiOperation({ summary: 'Create a new class' })
  @ApiResponse({ status: 201, description: 'Class created successfully' })
  create(@Body() createClassDto: CreateClassDto, @Request() req: any) {
    // Extract schoolId from JWT token
    const schoolId = req.user?.schoolId;
    if (!schoolId) {
      throw new BadRequestException('School ID not found in user session');
    }

    // Set schoolId from token
    createClassDto.schoolId = schoolId;
    return this.classesService.create(createClassDto);
  }

  @Get()
  @ApiOperation({ summary: 'Get all classes' })
  @ApiResponse({ status: 200, description: 'Return all classes' })
  findAll(
    @Query('schoolId') schoolId?: string,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.classesService.findAll(schoolId, page, limit);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get a class by ID' })
  @ApiResponse({ status: 200, description: 'Return the class' })
  @ApiResponse({ status: 404, description: 'Class not found' })
  findOne(@Param('id') id: string) {
    return this.classesService.findOne(id);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update a class' })
  @ApiResponse({ status: 200, description: 'Class updated successfully' })
  @ApiResponse({ status: 404, description: 'Class not found' })
  update(@Param('id') id: string, @Body() updateClassDto: UpdateClassDto) {
    return this.classesService.update(id, updateClassDto);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete a class' })
  @ApiResponse({ status: 200, description: 'Class deleted successfully' })
  @ApiResponse({ status: 404, description: 'Class not found' })
  remove(@Param('id') id: string) {
    return this.classesService.remove(id);
  }

  @Post('bulk')
  @ApiOperation({ summary: 'Create multiple classes' })
  @ApiResponse({ status: 201, description: 'Classes created successfully' })
  createBulk(@Body() createClassDtos: CreateClassDto[]) {
    return this.classesService.createBulk(createClassDtos);
  }
}