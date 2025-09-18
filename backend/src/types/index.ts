import { User, School, AcademicYear, Class, Subject, TimeSlot, Room, Teacher, TeacherWorkloadConfig, TeacherWellnessMetric, WorkloadAlert, WellnessIntervention, Timetable, TimetableEntry, Substitution, Constraint, DepartmentWellnessSummary, WellnessPrediction, Role, Stream, DayOfWeek, RoomType, BurnoutRiskLevel, AlertSeverity, TimetableStatus, WellnessImpact, SubstitutionStatus, ConstraintType, ConstraintPriority, PredictionType } from '@prisma/client';

export type { User, School, AcademicYear, Class, Subject, TimeSlot, Room, Teacher, TeacherWorkloadConfig, TeacherWellnessMetric, WorkloadAlert, WellnessIntervention, Timetable, TimetableEntry, Substitution, Constraint, DepartmentWellnessSummary, WellnessPrediction };

export type { Role, Stream, DayOfWeek, RoomType, BurnoutRiskLevel, AlertSeverity, TimetableStatus, WellnessImpact, SubstitutionStatus, ConstraintType, ConstraintPriority, PredictionType };

// Auth types
export interface AuthPayload {
  userId: string;
  role: Role;
}

export interface RegisterRequest {
  email: string;
  password: string;
  role: Role;
  schoolId: string;
  profile?: any;
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
    profile: any;
  };
  token: string;
}

// Request/Response for routes
export interface CreateUserRequest extends RegisterRequest {}

export interface UpdateUserRequest {
  email?: string;
  role?: Role;
  profile?: any;
  wellnessPreferences?: any;
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

// Wellness
export interface WellnessDashboardRequest {
  teacherId: string;
  period?: 'day' | 'week' | 'month' | 'term';
}

export interface WorkloadAnalysisRequest {
  scope: 'teacher' | 'department' | 'school';
  id?: string;
}

// From OpenAPI/Python (simplified for backend use)
export interface GenerateRequestBackend {
  school_id: string;
  academic_year_id: string;
  classes: Class[];
  subjects: Subject[];
  teachers: Teacher[];
  teacher_configs: TeacherWorkloadConfig[];
  time_slots: TimeSlot[];
  rooms: Room[];
  constraints: Constraint[];
  options: number;
  timeout: number;
  weights: {
    academic: number;
    wellness: number;
    efficiency: number;
    preference: number;
  };
}