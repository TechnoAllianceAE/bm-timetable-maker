import { Injectable, UnauthorizedException, BadRequestException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { UsersService } from '../users/users.service';
import { RegisterDto } from './dto/register.dto';

@Injectable()
export class AuthService {
  constructor(
    private usersService: UsersService,
    private jwtService: JwtService,
  ) {}

  async validateUser(email: string, password: string): Promise<any> {
    const user = await this.usersService.findByEmail(email);
    if (user && await bcrypt.compare(password, user.passwordHash)) {
      const { passwordHash, ...result } = user;
      return result;
    }
    return null;
  }

  async login(user: any) {
    const payload = {
      email: user.email,
      sub: user.id,
      role: user.role,
      schoolId: user.schoolId
    };

    return {
      access_token: this.jwtService.sign(payload),
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        schoolId: user.schoolId,
        profile: user.profile,
      },
    };
  }

  async register(registerDto: RegisterDto) {
    // Check if user already exists
    const existingUser = await this.usersService.findByEmail(registerDto.email);
    if (existingUser) {
      throw new BadRequestException('User with this email already exists');
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(registerDto.password, 10);

    // Create user
    const { password, profile, ...userDataWithoutPassword } = registerDto;
    const userData = {
      email: registerDto.email,
      passwordHash: hashedPassword,
      schoolId: registerDto.schoolId,
      role: registerDto.role,
      profile: profile ? JSON.stringify(profile) : undefined,
    };
    const user = await this.usersService.create(userData);

    // Remove password from response
    const { passwordHash, ...result } = user;

    // Generate token
    const payload = {
      email: user.email,
      sub: user.id,
      role: user.role,
      schoolId: user.schoolId
    };

    return {
      access_token: this.jwtService.sign(payload),
      user: result,
    };
  }
}