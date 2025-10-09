import {
  Controller,
  Post,
  UploadedFile,
  UseInterceptors,
  UseGuards,
  Request,
  BadRequestException,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { ImportService } from './import.service';

@Controller('import')
@UseGuards(JwtAuthGuard)
export class ImportController {
  constructor(private readonly importService: ImportService) {}

  @Post('classes')
  @UseInterceptors(FileInterceptor('file'))
  async importClasses(
    @UploadedFile() file: Express.Multer.File,
    @Request() req: any,
  ) {
    if (!file) {
      throw new BadRequestException('No file uploaded');
    }

    console.log('User from request:', JSON.stringify(req.user, null, 2));
    const schoolId = req.user?.schoolId;

    if (!schoolId) {
      throw new BadRequestException('School ID not found in user session. Please logout and login again to refresh your authentication token.');
    }

    const result = await this.importService.importClasses(file.buffer.toString('utf-8'), schoolId);

    return {
      message: `Successfully imported ${result.count} classes`,
      recordsImported: result.count,
    };
  }

  @Post('teachers')
  @UseInterceptors(FileInterceptor('file'))
  async importTeachers(
    @UploadedFile() file: Express.Multer.File,
    @Request() req: any,
  ) {
    if (!file) {
      throw new BadRequestException('No file uploaded');
    }

    const schoolId = req.user?.schoolId;
    if (!schoolId) {
      throw new BadRequestException('School ID not found in user session');
    }

    const result = await this.importService.importTeachers(file.buffer.toString('utf-8'), schoolId);

    return {
      message: `Successfully imported ${result.count} teachers`,
      recordsImported: result.count,
    };
  }

  @Post('subjects')
  @UseInterceptors(FileInterceptor('file'))
  async importSubjects(
    @UploadedFile() file: Express.Multer.File,
    @Request() req: any,
  ) {
    if (!file) {
      throw new BadRequestException('No file uploaded');
    }

    const schoolId = req.user?.schoolId;
    if (!schoolId) {
      throw new BadRequestException('School ID not found in user session');
    }

    const result = await this.importService.importSubjects(file.buffer.toString('utf-8'), schoolId);

    return {
      message: `Successfully imported ${result.count} subjects`,
      recordsImported: result.count,
    };
  }

  @Post('rooms')
  @UseInterceptors(FileInterceptor('file'))
  async importRooms(
    @UploadedFile() file: Express.Multer.File,
    @Request() req: any,
  ) {
    if (!file) {
      throw new BadRequestException('No file uploaded');
    }

    const schoolId = req.user?.schoolId;
    if (!schoolId) {
      throw new BadRequestException('School ID not found in user session');
    }

    const result = await this.importService.importRooms(file.buffer.toString('utf-8'), schoolId);

    return {
      message: `Successfully imported ${result.count} rooms`,
      recordsImported: result.count,
    };
  }
}
