// Centralised domain types and enums for the backend API.
// We intentionally avoid importing from `@prisma/client` so that
// the application can compile even when Prisma engines are not generated yet.

export const ROLE_VALUES = ['ADMIN', 'PRINCIPAL', 'TEACHER', 'STUDENT', 'PARENT'] as const;
export type Role = typeof ROLE_VALUES[number];

export const TIMETABLE_STATUS_VALUES = ['DRAFT', 'GENERATING', 'ACTIVE', 'ARCHIVED', 'FAILED'] as const;
export type TimetableStatus = typeof TIMETABLE_STATUS_VALUES[number];

export interface AuthPayload {
  userId: string;
  schoolId: string;
  role: Role;
  email: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  role: Role;
  schoolId: string;
  profile?: Record<string, unknown>;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: {
    id: string;
    email: string;
    role: Role;
    schoolId: string;
    profile: Record<string, unknown> | null;
  };
  token: string;
}

export interface CreateUserRequest extends RegisterRequest {}

export interface UpdateUserRequest {
  email?: string;
  role?: Role;
  profile?: Record<string, unknown>;
  wellnessPreferences?: Record<string, unknown>;
}

export interface GenerateTimetableRequest {
  academicYearId: string;
  options?: number;
  timeout?: number;
  weights?: {
    academic: number;
    wellness: number;
    efficiency: number;
    preference: number;
  };
}

export interface TimetableGenerationPayload {
  schoolId: string;
  academicYearId: string;
  options: number;
  timeout: number;
  weights: {
    academic: number;
    wellness: number;
    efficiency: number;
    preference: number;
  };
}

export interface TimetableGenerationResult {
  timetableId: string;
  status: TimetableStatus;
  entries: Array<Record<string, unknown>>;
  metadata?: Record<string, unknown>;
}
