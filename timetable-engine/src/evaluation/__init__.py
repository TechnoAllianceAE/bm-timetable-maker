"""
Timetable evaluation module.

Provides fast, standalone evaluation and ranking capabilities
separate from genetic algorithm operations.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from evaluation.models import (
    EvaluationResult,
    EvaluationConfig,
    PenaltyBreakdown,
    PenaltyType,
    ComparisonResult,
    RankedTimetable,
    BatchEvaluationResult
)

from evaluation.timetable_evaluator import TimetableEvaluator

__all__ = [
    'TimetableEvaluator',
    'EvaluationResult',
    'EvaluationConfig',
    'PenaltyBreakdown',
    'PenaltyType',
    'ComparisonResult',
    'RankedTimetable',
    'BatchEvaluationResult'
]