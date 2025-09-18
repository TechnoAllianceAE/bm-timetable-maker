"""
Simplified models for Phase 1 - Core timetable functionality only
"""
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime, time

# Enums
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
    availability: Optional[Dict[str, Any]] = {}  # Time slots when available
    max_periods_per_day: int = 6
    max_periods_per_week: int = 30
    max_consecutive_periods: int = 3

class Class(BaseModel):
    id: str
    school_id: str
    name: str  # e.g., "10-A"
    grade: int = Field(ge=1, le=12)
    section: str
    stream: Optional[Stream] = None  # For grades 11-12
    student_count: Optional[int] = None

class Subject(BaseModel):
    id: str
    school_id: str
    name: str
    code: str
    periods_per_week: int = Field(ge=1, le=10)
    requires_lab: bool = False
    is_elective: bool = False

class Room(BaseModel):
    id: str
    school_id: str
    name: str
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: int
    type: RoomType = RoomType.CLASSROOM
    facilities: List[str] = []  # e.g., ["projector", "whiteboard"]

class TimeSlot(BaseModel):
    id: str
    school_id: str
    day_of_week: DayOfWeek
    period_number: int = Field(ge=1, le=12)
    start_time: str  # Format: "09:00"
    end_time: str    # Format: "09:45"
    is_break: bool = False

class Constraint(BaseModel):
    id: str
    school_id: str
    type: ConstraintType
    priority: ConstraintPriority
    entity_type: Optional[str] = None  # "TEACHER", "CLASS", "SUBJECT", "ROOM"
    entity_id: Optional[str] = None
    parameters: Dict[str, Any] = {}
    description: str

class Timetable(BaseModel):
    id: str
    school_id: str
    academic_year_id: str
    name: Optional[str] = None
    status: TimetableStatus = TimetableStatus.DRAFT
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    entries: List['TimetableEntry'] = []

class TimetableEntry(BaseModel):
    id: Optional[str] = None
    timetable_id: str
    class_id: str
    subject_id: str
    teacher_id: str
    room_id: str
    time_slot_id: str
    day_of_week: DayOfWeek
    period_number: int
    is_fixed: bool = False  # Whether this entry can be modified

# API Request/Response Models
class OptimizationWeights(BaseModel):
    academic_requirements: float = 0.4
    resource_utilization: float = 0.25
    gap_minimization: float = 0.2
    teacher_preferences: float = 0.15

class GenerateRequest(BaseModel):
    school_id: str
    academic_year_id: str
    classes: List[Class]
    subjects: List[Subject]
    teachers: List[Teacher]
    time_slots: List[TimeSlot]
    rooms: List[Room]
    constraints: List[Constraint]
    options: int = Field(3, ge=1, le=5, description="Number of solutions to generate")
    timeout: int = Field(60, ge=10, le=300, description="Timeout in seconds")
    weights: OptimizationWeights = OptimizationWeights()

class TimetableSolution(BaseModel):
    timetable: Timetable
    total_score: float
    feasible: bool
    conflicts: List[str] = []
    metrics: Dict[str, Any] = {}  # constraints_satisfied, gaps, etc.

class GenerateResponse(BaseModel):
    solutions: List[TimetableSolution]
    generation_time: float
    conflicts: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class ValidateRequest(BaseModel):
    entities: Dict[str, Any]  # classes, teachers, rooms, etc.
    constraints: List[Constraint]

class ValidationResult(BaseModel):
    feasible: bool
    conflicts: List[str] = []
    suggestions: List[str] = []

# Update forward references
Timetable.model_rebuild()