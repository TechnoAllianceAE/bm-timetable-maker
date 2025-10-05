"""
Phase 1 Models with v2.5 Metadata Extensions

VERSION 2.5 - Metadata-Driven Optimization

ENHANCEMENTS:
- Subject: Added prefer_morning, preferred_periods, avoid_periods
- Teacher: Already has max_consecutive_periods
- TimetableEntry: Added subject_metadata, teacher_metadata
- OptimizationWeights: Added morning_period_cutoff, time_preferences, consecutive_periods

These metadata fields enable language-agnostic, school-customizable optimization.
"""
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

# Enums (unchanged from v2.0)
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
    SPORTS = "SPORTS"
    LIBRARY = "LIBRARY"
    AUDITORIUM = "AUDITORIUM"

class TimetableStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class ConstraintType(str, Enum):
    TEACHER_AVAILABILITY = "TEACHER_AVAILABILITY"
    ROOM_CAPACITY = "ROOM_CAPACITY"
    CONSECUTIVE_PERIODS = "CONSECUTIVE_PERIODS"
    MIN_PERIODS_PER_WEEK = "MIN_PERIODS_PER_WEEK"
    MAX_PERIODS_PER_WEEK = "MAX_PERIODS_PER_WEEK"
    PREFERRED_TIME_SLOT = "PREFERRED_TIME_SLOT"
    NO_GAPS = "NO_GAPS"
    LUNCH_BREAK = "LUNCH_BREAK"

class ConstraintPriority(str, Enum):
    MANDATORY = "MANDATORY"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

# Core Entities
class School(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}

class Teacher(BaseModel):
    id: str
    user_id: str
    subjects: List[str]  # List of subject names/codes they can teach
    availability: Optional[Dict[str, Any]] = {}
    max_periods_per_day: int = 6
    max_periods_per_week: int = 30
    max_consecutive_periods: int = 3  # v2.5: Used in metadata-driven optimization

class Class(BaseModel):
    id: str
    school_id: str
    name: str
    grade: int = Field(ge=1, le=12)
    section: str
    stream: Optional[Stream] = None
    student_count: Optional[int] = None

class Subject(BaseModel):
    """
    v2.5 ENHANCEMENTS:
    - prefer_morning: Boolean flag for time preference
    - preferred_periods: List of specific period numbers
    - avoid_periods: List of period numbers to avoid
    """
    id: str
    school_id: str
    name: str
    code: str
    periods_per_week: int = Field(ge=1, le=10)
    requires_lab: bool = False
    is_elective: bool = False
    # v2.5: Metadata fields for optimization
    prefer_morning: bool = False
    preferred_periods: Optional[List[int]] = None
    avoid_periods: Optional[List[int]] = None

class Room(BaseModel):
    id: str
    school_id: str
    name: str
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: int
    type: RoomType = RoomType.CLASSROOM
    facilities: List[str] = []

class TimeSlot(BaseModel):
    id: str
    school_id: str
    day_of_week: DayOfWeek
    period_number: int = Field(ge=1, le=12)
    start_time: str
    end_time: str
    is_break: bool = False

class Constraint(BaseModel):
    id: str
    school_id: str
    type: ConstraintType
    priority: ConstraintPriority
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    parameters: Dict[str, Any] = {}
    description: str

class TimetableEntry(BaseModel):
    """
    v2.5 ENHANCEMENTS:
    - subject_metadata: Subject preferences (prefer_morning, etc.)
    - teacher_metadata: Teacher constraints (max_consecutive_periods, etc.)
    """
    id: Optional[str] = None
    timetable_id: str
    class_id: str
    subject_id: str
    teacher_id: str
    room_id: str
    time_slot_id: str
    day_of_week: DayOfWeek
    period_number: int
    is_fixed: bool = False
    # v2.5: Metadata for optimization
    subject_metadata: Optional[Dict[str, Any]] = None
    teacher_metadata: Optional[Dict[str, Any]] = None

class Timetable(BaseModel):
    id: str
    school_id: str
    academic_year_id: str
    name: Optional[str] = None
    status: TimetableStatus = TimetableStatus.DRAFT
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    entries: List[TimetableEntry] = []

# API Request/Response Models
class GradeSubjectRequirement(BaseModel):
    """
    Defines required periods per week for a subject in a specific grade.
    Used to enforce curriculum requirements in timetable generation.
    """
    grade: int = Field(ge=1, le=12)
    subject_id: str
    periods_per_week: int = Field(ge=1, le=40)

class OptimizationWeights(BaseModel):
    """
    v2.5 ENHANCEMENTS:
    - time_preferences: Weight for subject time preferences
    - consecutive_periods: Weight for teacher consecutive period limits
    - morning_period_cutoff: Defines which periods are "morning"
    """
    workload_balance: float = 50.0
    gap_minimization: float = 15.0
    time_preferences: float = 25.0  # v2.5: Subject time preference weight
    consecutive_periods: float = 10.0  # v2.5: Teacher consecutive period weight
    morning_period_cutoff: int = 4  # v2.5: Which period ends "morning"

class GenerateRequest(BaseModel):
    school_id: str
    academic_year_id: str
    classes: List[Class]
    subjects: List[Subject]
    teachers: List[Teacher]
    time_slots: List[TimeSlot]
    rooms: List[Room]
    constraints: List[Constraint]
    subject_requirements: Optional[List[GradeSubjectRequirement]] = None  # Grade-subject period requirements
    options: int = Field(3, ge=1, le=5)
    timeout: int = Field(60, ge=10, le=300)
    weights: OptimizationWeights = OptimizationWeights()

class TimetableSolution(BaseModel):
    timetable: Dict[str, Any]  # Changed from Timetable to Dict for flexibility
    total_score: float
    feasible: bool
    conflicts: List[str] = []
    metrics: Dict[str, Any] = {}

class GenerateResponse(BaseModel):
    solutions: List[TimetableSolution]
    generation_time: float
    conflicts: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class ValidateRequest(BaseModel):
    entities: Dict[str, Any]
    constraints: List[Constraint]

class ValidationResult(BaseModel):
    feasible: bool
    conflicts: List[str] = []
    suggestions: List[str] = []

# Update forward references
Timetable.model_rebuild()
