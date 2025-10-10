"""
Data models for timetable evaluation and ranking.

This module defines the data structures used by the TimetableEvaluator
and RankingService to represent evaluation results, penalty breakdowns,
and comparison outcomes.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class PenaltyType(Enum):
    """Types of penalties that can be applied to timetables."""
    COVERAGE = "coverage"
    WORKLOAD_IMBALANCE = "workload_imbalance"
    STUDENT_GAPS = "student_gaps"
    TIME_PREFERENCES = "time_preferences"
    CONSECUTIVE_PERIODS = "consecutive_periods"


@dataclass
class PenaltyBreakdown:
    """Detailed breakdown of a specific penalty type."""
    penalty_type: PenaltyType
    raw_score: float
    weight: float
    weighted_score: float
    description: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class EvaluationResult:
    """
    Complete evaluation result for a single timetable.
    
    Contains both the overall score and detailed breakdown of all
    penalty components for transparency and debugging.
    """
    timetable_id: Optional[str]
    total_score: float
    coverage_percentage: float
    base_score: float
    penalty_breakdown: List[PenaltyBreakdown]
    
    @property
    def total_penalty(self) -> float:
        """Sum of all weighted penalties."""
        return sum(p.weighted_score for p in self.penalty_breakdown)
    
    @property
    def penalty_summary(self) -> Dict[str, float]:
        """Dictionary mapping penalty types to their weighted scores."""
        return {p.penalty_type.value: p.weighted_score for p in self.penalty_breakdown}
    
    def get_penalty_by_type(self, penalty_type: PenaltyType) -> Optional[PenaltyBreakdown]:
        """Get specific penalty breakdown by type."""
        for p in self.penalty_breakdown:
            if p.penalty_type == penalty_type:
                return p
        return None


@dataclass
class ComparisonResult:
    """Result of comparing two timetables."""
    timetable1_id: Optional[str]
    timetable2_id: Optional[str]
    winner: int  # 1 if timetable1 is better, 2 if timetable2 is better, 0 if tie
    score_difference: float
    better_in_categories: List[PenaltyType]
    worse_in_categories: List[PenaltyType]
    summary: str


@dataclass
class RankedTimetable:
    """Timetable with its rank and evaluation details."""
    rank: int
    timetable: Dict[str, Any]
    evaluation: EvaluationResult
    
    @property
    def score(self) -> float:
        """Convenience property for accessing total score."""
        return self.evaluation.total_score


@dataclass
class BatchEvaluationResult:
    """Result of evaluating multiple timetables at once."""
    evaluations: List[EvaluationResult]
    summary_stats: Dict[str, float]
    
    @property
    def best_score(self) -> float:
        """Highest score in the batch."""
        return max(e.total_score for e in self.evaluations)
    
    @property
    def worst_score(self) -> float:
        """Lowest score in the batch."""
        return min(e.total_score for e in self.evaluations)
    
    @property
    def average_score(self) -> float:
        """Average score across all evaluations."""
        return sum(e.total_score for e in self.evaluations) / len(self.evaluations)


class EvaluationConfig:
    """Configuration for timetable evaluation."""
    
    def __init__(self,
                 coverage_penalty_weight: float = 20.0,
                 workload_balance_weight: float = 1.0,
                 gap_minimization_weight: float = 1.0,
                 time_preferences_weight: float = 1.0,
                 consecutive_periods_weight: float = 1.0,
                 morning_period_cutoff: int = 4,
                 high_priority_penalty: float = 10.0,
                 medium_priority_penalty: float = 5.0,
                 low_priority_penalty: float = 2.0):
        """
        Initialize evaluation configuration.
        
        Args:
            coverage_penalty_weight: Weight for unfilled slots penalty
            workload_balance_weight: Weight for teacher workload imbalance
            gap_minimization_weight: Weight for student schedule gaps
            time_preferences_weight: Weight for time preference violations
            consecutive_periods_weight: Weight for consecutive period violations
            morning_period_cutoff: Period number that defines morning vs afternoon
            high_priority_penalty: Penalty per high-priority unfilled slot
            medium_priority_penalty: Penalty per medium-priority unfilled slot
            low_priority_penalty: Penalty per low-priority unfilled slot
        """
        self.coverage_penalty_weight = coverage_penalty_weight
        self.workload_balance_weight = workload_balance_weight
        self.gap_minimization_weight = gap_minimization_weight
        self.time_preferences_weight = time_preferences_weight
        self.consecutive_periods_weight = consecutive_periods_weight
        self.morning_period_cutoff = morning_period_cutoff
        self.high_priority_penalty = high_priority_penalty
        self.medium_priority_penalty = medium_priority_penalty
        self.low_priority_penalty = low_priority_penalty
    
    @classmethod
    def from_optimization_weights(cls, weights: Any) -> 'EvaluationConfig':
        """Create config from existing OptimizationWeights object."""
        return cls(
            workload_balance_weight=getattr(weights, 'workload_balance', 1.0),
            gap_minimization_weight=getattr(weights, 'gap_minimization', 1.0),
            time_preferences_weight=getattr(weights, 'time_preferences', 1.0),
            consecutive_periods_weight=getattr(weights, 'consecutive_periods', 1.0),
            morning_period_cutoff=getattr(weights, 'morning_period_cutoff', 4)
        )