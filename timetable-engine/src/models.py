from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime

class Role(str, Enum):
    ADMIN = "ADMIN"
    PRINCIPAL = "PRINCIPAL"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    PARENT = "PARENT"

class Stream(str, Enum):
    SCIENCE = "SCIENCE"
    COMMERCE = "COMMERCE"
    ARTS = "ARTS"

class DayOfWeek(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"

class RoomType(str, Enum):
    CLASSROOM = "CLASSROOM"
    LAB = "LAB"
    AUDITORIUM = "AUDITORIUM"
    OFFICE = "OFFICE"

class BurnoutRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class TimetableStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class WellnessImpact(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"

class SubstitutionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ConstraintType(str, Enum):
    ACADEMIC_MIN_PERIODS = "ACADEMIC_MIN_PERIODS"
    ACADEMIC_TIME_PREFERENCE = "ACADEMIC_TIME_PREFERENCE"
    WELLNESS_MAX_CONSECUTIVE = "WELLNESS_MAX_CONSECUTIVE"
    WELLNESS_DAILY_HOURS = "WELLNESS_DAILY_HOURS"
    # Add more as per PRD

class ConstraintPriority(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"

class PredictionType(str, Enum):
    BURNOUT_RISK = "BURNOUT_RISK"
    WORKLOAD_TREND = "WORKLOAD_TREND"

# Core Entities
class School(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}
    wellness_config: Optional[Dict[str, Any]] = {}
    subscription_tier: Optional[str] = None
    created_at: Optional[datetime] = None

class User(BaseModel):
    id: str
    school_id: str
    email: str
    role: Role
    profile: Optional[Dict[str, Any]] = {}
    wellness_preferences: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime] = None

class Class(BaseModel):
    id: str
    school_id: str
    name: str
    grade: int = Field(..., ge=1)
    section: Optional[str] = None
    stream: Optional[Stream] = None
    student_count: Optional[int] = None

class Subject(BaseModel):
    id: str
    school_id: str
    name: str
    department: Optional[str] = None
    credits: int = Field(..., ge=1)
    min_periods_per_week: Optional[int] = None
    max_periods_per_week: Optional[int] = None
    prep_time: Optional[int] = None  # minutes
    correction_workload: Optional[float] = None  # per student
    requires_lab: bool = False

class TimeSlot(BaseModel):
    id: str
    school_id: str
    day: DayOfWeek
    start_time: str  # ISO time, e.g., "09:00"
    end_time: str    # ISO time, e.g., "10:00"
    is_break: bool = False

class Room(BaseModel):
    id: str
    school_id: str
    name: str
    capacity: Optional[int] = None
    type: Optional[RoomType] = None

class Teacher(BaseModel):
    id: str
    user_id: str
    subjects: List[str]  # subject names or IDs
    availability: Optional[Dict[str, Any]] = {}  # e.g., {"monday": ["09:00-12:00"]}
    preferences: Optional[Dict[str, Any]] = {}
    max_periods_per_day: int = 6
    max_periods_per_week: int = 30
    max_consecutive_periods: int = 3
    min_break_duration: int = 10
    wellness_score: Optional[float] = None
    burnout_risk_level: Optional[BurnoutRiskLevel] = None

class TeacherWorkloadConfig(BaseModel):
    id: str
    teacher_id: str
    max_periods_per_day: int = 6
    max_consecutive_periods: int = 3
    min_break_between_classes: int = 10
    max_periods_per_week: int = 30
    preferred_free_periods: int = 2
    max_early_morning_classes: int = 3
    max_late_evening_classes: int = 2
    prep_time_required: int = 60
    correction_time_per_student: float = 0.5
    special_requirements: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Constraint(BaseModel):
    id: Optional[str] = None
    school_id: str
    type: ConstraintType
    entity_id: str  # e.g., subject_id, teacher_id
    value: Dict[str, Any]  # flexible, e.g., {"min": 5}
    priority: ConstraintPriority = ConstraintPriority.SOFT
    created_at: Optional[datetime] = None

# Timetabling
class TimetableEntry(BaseModel):
    id: Optional[str] = None
    timetable_id: Optional[str] = None
    class_id: str
    subject_id: str
    teacher_id: str
    time_slot_id: str
    room_id: Optional[str] = None
    is_combined: bool = False
    combined_with: Optional[Dict[str, Any]] = None
    workload_impact: Optional[float] = None
    wellness_impact: Optional[WellnessImpact] = None

class Timetable(BaseModel):
    id: str
    school_id: str
    academic_year_id: str
    version: int = 1
    status: TimetableStatus = TimetableStatus.DRAFT
    wellness_score: Optional[float] = None
    workload_balance_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = {}
    wellness_analysis: Optional[Dict[str, Any]] = {}
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: Optional[datetime] = None
    entries: Optional[List[TimetableEntry]] = []

class Substitution(BaseModel):
    id: Optional[str] = None
    original_entry_id: str
    absent_teacher_id: str
    substitute_teacher_id: str
    date: datetime
    reason: Optional[str] = None
    workload_check_passed: Optional[bool] = None
    workload_override_reason: Optional[str] = None
    status: SubstitutionStatus = SubstitutionStatus.PENDING
    created_at: Optional[datetime] = None

# Wellness
class TeacherWellnessMetric(BaseModel):
    id: Optional[str] = None
    teacher_id: str
    metric_date: datetime
    teaching_hours: Optional[float] = None
    prep_hours: Optional[float] = None
    correction_hours: Optional[float] = None
    total_work_hours: Optional[float] = None
    consecutive_periods_max: Optional[int] = None
    gaps_total_minutes: Optional[int] = None
    stress_score: Optional[int] = Field(None, ge=0, le=100)
    wellness_score: Optional[int] = Field(None, ge=0, le=100)
    burnout_indicators: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class WorkloadAlert(BaseModel):
    id: Optional[str] = None
    teacher_id: str
    alert_type: str
    severity: AlertSeverity
    title: str
    message: str
    recommendations: Optional[List[str]] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class WellnessIntervention(BaseModel):
    id: Optional[str] = None
    teacher_id: str
    intervention_type: str
    description: str
    recommended_actions: Optional[Dict[str, Any]] = None
    implemented: bool = False
    implementation_date: Optional[datetime] = None
    effectiveness_score: Optional[int] = None
    notes: Optional[str] = None
    created_by: str
    created_at: Optional[datetime] = None

class WellnessAnalysis(BaseModel):
    overall_score: float
    teacher_scores: Dict[str, float]  # teacher_id: score
    department_scores: Dict[str, float]  # dept: score
    issues: List[Dict[str, Any]]  # e.g., {"teacher_id": "...", "type": "overload"}
    improvements: List[str]  # suggestions
    burnout_risks: Dict[str, BurnoutRiskLevel]  # teacher_id: level

class BurnoutPrediction(BaseModel):
    id: Optional[str] = None
    teacher_id: str
    prediction_date: datetime
    prediction_type: PredictionType
    prediction_value: float
    confidence_level: Optional[float] = None
    contributing_factors: Optional[Dict[str, Any]] = None
    recommended_interventions: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

# API Models
class OptimizationWeights(BaseModel):
    academic: float = 0.35
    wellness: float = 0.30
    efficiency: float = 0.20
    preference: float = 0.15

    @validator('academic', 'wellness', 'efficiency', 'preference')
    def weights_sum_to_one(cls, v):
        return v  # Enforce in service if needed

class GenerateRequest(BaseModel):
    school_id: str
    academic_year_id: str
    classes: List[Class]
    subjects: List[Subject]
    teachers: List[Teacher]
    teacher_configs: Optional[List[TeacherWorkloadConfig]] = None
    time_slots: List[TimeSlot]
    rooms: List[Room]
    constraints: List[Constraint]
    options: int = Field(3, ge=1, le=10)
    timeout: int = Field(60, ge=10, le=300)
    weights: OptimizationWeights = OptimizationWeights()

class TimetableSolution(BaseModel):
    timetable: Timetable
    wellness_analysis: WellnessAnalysis
    total_score: float
    feasible: bool = True

class GenerateResponse(BaseModel):
    solutions: List[TimetableSolution]
    generation_time: float  # seconds
    conflicts: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class ValidateRequest(BaseModel):
    constraints: List[Constraint]
    entities: Dict[str, List[Any]]  # e.g., {"teachers": [...], "classes": [...]}

class ValidationResult(BaseModel):
    feasible: bool
    conflicts: List[str]
    suggestions: List[str]

# Error Models
class GenerationError(BaseModel):
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None