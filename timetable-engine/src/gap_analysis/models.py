"""
Data models for gap analysis and slot classification.

This module defines the data structures used by the Gap Analysis Engine
to represent unfilled slots, their constraints, difficulty classifications,
and assignment suggestions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class SlotPriority(Enum):
    """Priority levels for unfilled slots."""
    CRITICAL = "critical"    # Must be filled for basic functionality
    HIGH = "high"           # Important for quality timetable
    MEDIUM = "medium"       # Standard requirement
    LOW = "low"            # Nice to have
    OPTIONAL = "optional"   # Can be skipped if necessary


class SlotDifficulty(Enum):
    """Difficulty levels for filling slots."""
    IMPOSSIBLE = "impossible"      # Cannot be filled due to hard constraints
    VERY_HARD = "very_hard"       # Multiple severe constraints
    HARD = "hard"                 # Several conflicting constraints  
    MODERATE = "moderate"         # Some constraints to work around
    EASY = "easy"                # Few or no constraints
    TRIVIAL = "trivial"          # Multiple valid options available


class ConstraintType(Enum):
    """Types of constraints that prevent slot filling."""
    TEACHER_UNAVAILABLE = "teacher_unavailable"
    TEACHER_OVERLOADED = "teacher_overloaded"
    TEACHER_CONSECUTIVE = "teacher_consecutive"
    ROOM_UNAVAILABLE = "room_unavailable"
    ROOM_INCOMPATIBLE = "room_incompatible"
    CLASS_CONFLICT = "class_conflict"
    CLASS_GAP_CREATED = "class_gap_created"
    TIME_PREFERENCE = "time_preference"
    CURRICULUM_CONSTRAINT = "curriculum_constraint"
    RESOURCE_CONFLICT = "resource_conflict"


@dataclass
class SlotConstraint:
    """Represents a constraint that prevents filling a slot."""
    constraint_type: ConstraintType
    description: str
    severity: float  # 0.0-1.0, higher = more severe
    entities_involved: List[str]  # IDs of teachers, rooms, classes involved
    details: Optional[Dict[str, Any]] = None


@dataclass
class UnfilledSlot:
    """
    Represents an unfilled slot in the timetable with analysis.
    """
    # Basic slot identification
    class_id: str
    subject_id: str
    day_of_week: str
    period_number: int
    
    # Classification
    priority: SlotPriority
    difficulty: SlotDifficulty
    
    # Constraint analysis
    blocking_constraints: List[SlotConstraint]
    
    # Requirements
    required_teacher_qualifications: List[str]
    required_room_features: List[str]
    duration_periods: int = 1
    
    # Context
    weekly_requirement: int = 1  # How many times per week this subject should occur
    current_weekly_count: int = 0  # How many times it's already scheduled
    
    # Metadata
    subject_metadata: Optional[Dict[str, Any]] = None
    class_metadata: Optional[Dict[str, Any]] = None
    
    @property
    def is_fillable(self) -> bool:
        """Check if slot can potentially be filled."""
        return self.difficulty != SlotDifficulty.IMPOSSIBLE
    
    @property
    def constraint_severity_score(self) -> float:
        """Calculate total constraint severity."""
        if not self.blocking_constraints:
            return 0.0
        return sum(c.severity for c in self.blocking_constraints) / len(self.blocking_constraints)


@dataclass
class AssignmentSuggestion:
    """
    Suggested assignment for an unfilled slot.
    """
    # Assignment details
    teacher_id: str
    room_id: Optional[str]
    confidence: float  # 0.0-1.0, higher = better suggestion
    
    # Impact analysis
    quality_impact: float  # Change in overall timetable quality
    constraint_violations: List[SlotConstraint]  # New constraints created
    constraint_resolutions: List[SlotConstraint]  # Existing constraints resolved
    
    # Alternative options
    alternative_teachers: List[str]
    alternative_rooms: List[str]
    alternative_times: List[Dict[str, Any]]  # [{day, period}, ...]
    
    # Justification
    reasoning: str
    trade_offs: List[str]  # What compromises are being made


@dataclass
class GapAnalysisResult:
    """
    Complete analysis of gaps in a timetable.
    """
    timetable_id: Optional[str]
    analysis_timestamp: str
    
    # Gap summary
    total_unfilled_slots: int
    fillable_slots: int
    impossible_slots: int
    
    # Classification breakdown
    slots_by_priority: Dict[SlotPriority, List[UnfilledSlot]]
    slots_by_difficulty: Dict[SlotDifficulty, List[UnfilledSlot]]
    
    # Constraint analysis
    common_constraints: List[ConstraintType]
    constraint_frequency: Dict[ConstraintType, int]
    
    # Suggestions
    suggested_assignments: List[AssignmentSuggestion]
    quick_wins: List[UnfilledSlot]  # Easy slots to fill first
    
    # Coverage metrics
    subject_coverage: Dict[str, float]  # % coverage per subject
    class_coverage: Dict[str, float]   # % coverage per class
    overall_coverage: float
    
    # Recommendations
    filling_strategy: str
    priority_order: List[UnfilledSlot]
    estimated_completion_difficulty: float


@dataclass
class GapFillingStrategy:
    """
    Strategy for systematically filling gaps.
    """
    name: str
    description: str
    
    # Ordering strategy
    priority_weights: Dict[SlotPriority, float]
    difficulty_weights: Dict[SlotDifficulty, float]
    
    # Filling approach
    batch_size: int  # How many slots to fill at once
    constraint_tolerance: float  # Acceptable constraint violation level
    
    # Quality thresholds
    min_acceptable_quality: float
    target_coverage: float


class GapAnalysisConfig:
    """Configuration for gap analysis engine."""
    
    def __init__(self,
                 priority_weights: Optional[Dict[SlotPriority, float]] = None,
                 difficulty_thresholds: Optional[Dict[str, float]] = None,
                 constraint_severities: Optional[Dict[ConstraintType, float]] = None,
                 suggestion_limit: int = 5,
                 min_confidence_threshold: float = 0.3):
        """
        Initialize gap analysis configuration.
        
        Args:
            priority_weights: Weights for different priority levels
            difficulty_thresholds: Thresholds for difficulty classification
            constraint_severities: Default severities for constraint types
            suggestion_limit: Maximum suggestions per slot
            min_confidence_threshold: Minimum confidence for suggestions
        """
        self.priority_weights = priority_weights or {
            SlotPriority.CRITICAL: 10.0,
            SlotPriority.HIGH: 5.0,
            SlotPriority.MEDIUM: 2.0,
            SlotPriority.LOW: 1.0,
            SlotPriority.OPTIONAL: 0.5
        }
        
        self.difficulty_thresholds = difficulty_thresholds or {
            'impossible': 0.95,      # >95% constraint severity = impossible
            'very_hard': 0.8,        # >80% = very hard
            'hard': 0.6,             # >60% = hard
            'moderate': 0.3,         # >30% = moderate
            'easy': 0.1              # >10% = easy, <=10% = trivial
        }
        
        self.constraint_severities = constraint_severities or {
            ConstraintType.TEACHER_UNAVAILABLE: 1.0,     # Absolute constraint
            ConstraintType.CLASS_CONFLICT: 1.0,          # Absolute constraint
            ConstraintType.ROOM_UNAVAILABLE: 0.9,        # Very severe
            ConstraintType.TEACHER_OVERLOADED: 0.7,      # Severe but manageable
            ConstraintType.TEACHER_CONSECUTIVE: 0.6,     # Moderate constraint
            ConstraintType.ROOM_INCOMPATIBLE: 0.5,       # Can find alternatives
            ConstraintType.TIME_PREFERENCE: 0.4,         # Soft constraint
            ConstraintType.CLASS_GAP_CREATED: 0.3,       # Mild quality issue
            ConstraintType.CURRICULUM_CONSTRAINT: 0.8,   # Important but flexible
            ConstraintType.RESOURCE_CONFLICT: 0.6        # Moderate issue
        }
        
        self.suggestion_limit = suggestion_limit
        self.min_confidence_threshold = min_confidence_threshold