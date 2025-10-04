"""
Simplified models for Phase 1 - Core timetable functionality
VERSION 2.5 - Metadata-Driven Optimization

CHANGELOG v2.5:
- Added Subject.prefer_morning, preferred_periods, avoid_periods
- Added OptimizationWeights.consecutive_periods, morning_period_cutoff
- Added TimetableEntry.subject_metadata, teacher_metadata
- All hardcoded business logic now configurable via metadata
- Language-agnostic subject preferences
- Per-school and per-teacher customization support
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
    """
    Subject model with scheduling preferences.
    
    VERSION 2.5 CHANGES:
    - Added prefer_morning: Language-agnostic alternative to hardcoded subject names
    - Added preferred_periods: Fine-grained control over scheduling
    - Added avoid_periods: Specify periods to avoid
    
    BENEFITS:
    - Works in any language (English, Spanish, Hindi, Chinese, etc.)
    - School-specific customization (different schools, different rules)
    - Per-subject granularity (Economics can prefer morning in one school, afternoon in another)
    - Zero-code curriculum updates
    """
    id: str
    school_id: str
    name: str
    code: str
    periods_per_week: int = Field(ge=1, le=10)
    requires_lab: bool = False
    is_elective: bool = False
    
    # --- v2.5: Scheduling Preferences ---
    prefer_morning: bool = Field(
        default=False,
        description="True if subject should be scheduled in morning periods (before lunch). "
                    "Typically set for cognitively-heavy subjects like Math, Physics, Chemistry. "
                    "Language-agnostic - works regardless of subject name or language."
    )
    preferred_periods: Optional[List[int]] = Field(
        default=None,
        description="Specific period numbers preferred for this subject (e.g., [1,2,3,4] for morning). "
                    "If set, takes precedence over prefer_morning flag. "
                    "Allows fine-grained control. Example: [1,2,3,4,5] for first 5 periods."
    )
    avoid_periods: Optional[List[int]] = Field(
        default=None,
        description="Period numbers to avoid scheduling this subject (e.g., [7,8] for last periods). "
                    "Useful for subjects requiring high concentration or physical activity. "
                    "Example: Avoid scheduling Math in period 8 when students are tired."
    )

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
    """
    Single timetable entry (one class, one subject, one time slot).
    
    VERSION 2.5 CHANGES:
    - Added subject_metadata: Carries subject preferences for GA optimization
    - Added teacher_metadata: Carries teacher constraints for GA optimization
    
    BENEFITS:
    - GA optimizer can read preferences without database lookups
    - Metadata flows naturally through CSP -> GA pipeline
    - Backward compatible (defaults to None if not provided)
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
    is_fixed: bool = False  # Whether this entry can be modified
    
    # --- v2.5: Metadata for GA Optimizer ---
    subject_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Subject scheduling preferences extracted from Subject model. "
                    "Includes: prefer_morning (bool), preferred_periods (list), avoid_periods (list). "
                    "Used by GA optimizer to apply time preference penalties."
    )
    teacher_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Teacher constraints extracted from Teacher model. "
                    "Includes: max_consecutive_periods (int). "
                    "Used by GA optimizer to prevent teacher burnout."
    )

# API Request/Response Models
class OptimizationWeights(BaseModel):
    """
    Weights for timetable optimization.
    
    VERSION 2.5 CHANGES:
    - Added consecutive_periods: Replaces hardcoded penalty weight
    - Added morning_period_cutoff: Replaces hardcoded period number (4)
    
    BENEFITS:
    - All tuning parameters in one place
    - Per-school customization (6-period vs 8-period days)
    - No hardcoded business logic anywhere in the system
    - Easy to adjust based on feedback
    
    USAGE:
    - workload_balance: Higher = stronger preference for equal teacher loads
    - gap_minimization: Higher = fewer gaps in student schedules
    - time_preferences: Higher = stricter adherence to subject preferences
    - consecutive_periods: Higher = more breaks enforced for teachers
    - morning_period_cutoff: Defines what "morning" means (typically 4 or 5)
    """
    
    # --- GA Fitness Penalty Weights ---
    workload_balance: float = Field(
        default=50.0,
        ge=0.0,
        description="Penalty weight for unbalanced teacher workload distribution. "
                    "Higher value = stronger preference for equal distribution. "
                    "Example: 100.0 = very strict balance, 25.0 = relaxed balance."
    )
    
    gap_minimization: float = Field(
        default=15.0,
        ge=0.0,
        description="Penalty weight per gap (empty period) in student schedules. "
                    "Higher value = fewer gaps preferred. "
                    "Example: 30.0 = minimize gaps aggressively, 5.0 = gaps acceptable."
    )
    
    time_preferences: float = Field(
        default=25.0,
        ge=0.0,
        description="Penalty weight for scheduling subjects at non-preferred times. "
                    "Higher value = stricter adherence to subject preferences. "
                    "Example: 50.0 = always respect preferences, 10.0 = preferences are suggestions."
    )
    
    consecutive_periods: float = Field(
        default=10.0,
        ge=0.0,
        description="Penalty weight for teachers exceeding max consecutive periods. "
                    "Higher value = more breaks enforced. "
                    "Example: 30.0 = strict breaks required, 5.0 = consecutive periods OK. "
                    "NEW in v2.5: Replaces hardcoded weight."
    )
    
    # --- School Structure Configuration ---
    morning_period_cutoff: int = Field(
        default=4,
        ge=1,
        le=12,
        description="Last period number considered 'morning' (typically before lunch). "
                    "Adjust based on school's daily structure. "
                    "Examples: "
                    "  4 = for 6-period schools (lunch after period 4), "
                    "  5 = for 8-period schools (lunch after period 5), "
                    "  6 = for 10-period schools (lunch after period 6). "
                    "NEW in v2.5: Replaces hardcoded period number."
    )
    
    # --- Legacy Weights (Backward Compatibility) ---
    academic_requirements: float = Field(
        default=0.4,
        description="Legacy: Weight for academic requirement satisfaction. "
                    "Kept for backward compatibility with older optimization code."
    )
    
    resource_utilization: float = Field(
        default=0.25,
        description="Legacy: Weight for resource utilization optimization. "
                    "Kept for backward compatibility with older optimization code."
    )
    
    teacher_preferences: float = Field(
        default=0.15,
        description="Legacy: Weight for teacher preference satisfaction. "
                    "Kept for backward compatibility with older optimization code."
    )

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


# =============================================================================
# VERSION 2.5 USAGE EXAMPLES
# =============================================================================

"""
Example 1: Heavy subject with morning preference (any language)
----------------------------------------------------------------
math_english = Subject(
    id="MATH_10",
    name="Mathematics",  # English
    code="MATH10",
    periods_per_week=6,
    prefer_morning=True  # Schedule in morning
)

math_spanish = Subject(
    id="MATH_10_ES",
    name="Matemáticas",  # Spanish
    code="MATH10",
    periods_per_week=6,
    prefer_morning=True  # Same preference, different language!
)

math_hindi = Subject(
    id="MATH_10_HI",
    name="गणित",  # Hindi
    code="MATH10",
    periods_per_week=6,
    prefer_morning=True  # Works in ANY language!
)


Example 2: Fine-grained period preferences
-------------------------------------------
physics_lab = Subject(
    id="PHY_LAB_12",
    name="Physics Lab",
    code="PHYLAB12",
    periods_per_week=4,
    requires_lab=True,
    preferred_periods=[2, 3, 4, 5],  # Not first period (setup time)
    avoid_periods=[7, 8]  # Not last periods (cleanup time)
)


Example 3: Different school structures
---------------------------------------
# 6-period school (lunch after period 4)
weights_6period = OptimizationWeights(
    workload_balance=50.0,
    gap_minimization=20.0,
    time_preferences=30.0,
    consecutive_periods=15.0,
    morning_period_cutoff=4  # Periods 1-4 are morning
)

# 8-period school (lunch after period 5)
weights_8period = OptimizationWeights(
    workload_balance=50.0,
    gap_minimization=20.0,
    time_preferences=30.0,
    consecutive_periods=15.0,
    morning_period_cutoff=5  # Periods 1-5 are morning
)


Example 4: Teacher with specific constraints
---------------------------------------------
experienced_teacher = Teacher(
    id="T001",
    user_id="U001",
    subjects=["Math", "Physics"],
    max_consecutive_periods=4  # Can handle 4 consecutive periods
)

new_teacher = Teacher(
    id="T002",
    user_id="U002",
    subjects=["English"],
    max_consecutive_periods=2  # Prefers more breaks
)


Example 5: TimetableEntry with metadata
----------------------------------------
entry = TimetableEntry(
    id="entry_1",
    timetable_id="TT_001",
    class_id="10A",
    subject_id="MATH_10",
    teacher_id="T001",
    room_id="R201",
    time_slot_id="MON_P1",
    day_of_week=DayOfWeek.MONDAY,
    period_number=1,
    # v2.5: Metadata included by CSP solver
    subject_metadata={
        "prefer_morning": True,
        "preferred_periods": [1, 2, 3, 4],
        "avoid_periods": None
    },
    teacher_metadata={
        "max_consecutive_periods": 3
    }
)
# GA optimizer reads this metadata and optimizes accordingly!
"""
