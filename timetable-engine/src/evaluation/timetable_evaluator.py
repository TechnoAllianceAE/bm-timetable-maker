"""
Standalone timetable evaluation system.

This module provides a fast, reusable evaluator for ranking and scoring
timetables without the overhead of genetic algorithm operations. It can be
used for ranking partial solutions, comparing alternatives, or providing
fitness scores to optimization algorithms.
"""

import statistics
from collections import defaultdict
from typing import Dict, List, Optional, Any, Tuple
import logging

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.models import (
    EvaluationResult, EvaluationConfig, PenaltyBreakdown, PenaltyType,
    ComparisonResult, BatchEvaluationResult
)

logger = logging.getLogger(__name__)


class TimetableEvaluator:
    """
    Fast, reusable timetable evaluation system.
    
    Provides detailed scoring and penalty breakdown for timetables,
    optimized for ranking scenarios without genetic algorithm overhead.
    """
    
    def __init__(self, config: EvaluationConfig):
        """
        Initialize evaluator with configuration.
        
        Args:
            config: EvaluationConfig with penalty weights and thresholds
        """
        self.config = config
        
    def evaluate(self, timetable: Dict[str, Any], timetable_id: Optional[str] = None) -> EvaluationResult:
        """
        Evaluate a single timetable and return detailed results.
        
        Args:
            timetable: Timetable dictionary to evaluate
            timetable_id: Optional identifier for the timetable
            
        Returns:
            EvaluationResult with score and detailed penalty breakdown
        """
        try:
            # Extract coverage information for partial solution scoring
            metadata = timetable.get('metadata', {})
            coverage = metadata.get('coverage', 1.0)
            unfilled_slots = metadata.get('unfilled_slots', [])
            
            # Scale base score by coverage (partial solutions start lower)
            base_score = 1000.0 * coverage
            
            # Extract assignments from timetable
            assignments = self._extract_assignments(timetable)
            
            if not assignments:
                return EvaluationResult(
                    timetable_id=timetable_id,
                    total_score=0.0,
                    coverage_percentage=coverage * 100,
                    base_score=0.0,
                    penalty_breakdown=[]
                )
            
            # Pre-compute groupings for efficiency
            teacher_loads = self._calculate_teacher_workloads(assignments)
            class_schedules = self._group_by_class(assignments)
            
            # Calculate all penalties
            penalty_breakdown = []
            
            # Coverage penalty (for partial solutions)
            coverage_penalty = self._calculate_coverage_penalty(unfilled_slots)
            if coverage_penalty > 0:
                penalty_breakdown.append(PenaltyBreakdown(
                    penalty_type=PenaltyType.COVERAGE,
                    raw_score=coverage_penalty,
                    weight=self.config.coverage_penalty_weight,
                    weighted_score=coverage_penalty * self.config.coverage_penalty_weight,
                    description=f"Unfilled slots penalty ({len(unfilled_slots)} slots)",
                    details={"unfilled_count": len(unfilled_slots), "unfilled_slots": unfilled_slots}
                ))
            
            # Workload imbalance penalty
            workload_penalty = self._calculate_workload_imbalance_penalty(teacher_loads)
            if workload_penalty > 0:
                penalty_breakdown.append(PenaltyBreakdown(
                    penalty_type=PenaltyType.WORKLOAD_IMBALANCE,
                    raw_score=workload_penalty,
                    weight=self.config.workload_balance_weight,
                    weighted_score=workload_penalty * self.config.workload_balance_weight,
                    description=f"Teacher workload imbalance (std dev: {workload_penalty:.2f})",
                    details={"teacher_counts": {t: len(a) for t, a in teacher_loads.items()}}
                ))
            
            # Gap penalty (adjusted for partial solutions)
            gap_penalty = self._calculate_gap_penalty_partial(class_schedules, unfilled_slots)
            if gap_penalty > 0:
                penalty_breakdown.append(PenaltyBreakdown(
                    penalty_type=PenaltyType.STUDENT_GAPS,
                    raw_score=gap_penalty,
                    weight=self.config.gap_minimization_weight,
                    weighted_score=gap_penalty * self.config.gap_minimization_weight,
                    description=f"Student schedule gaps ({gap_penalty} gaps)",
                    details={"gap_count": gap_penalty}
                ))
            
            # Time preference violations
            time_pref_penalty = self._calculate_time_preference_penalty(assignments)
            if time_pref_penalty > 0:
                penalty_breakdown.append(PenaltyBreakdown(
                    penalty_type=PenaltyType.TIME_PREFERENCES,
                    raw_score=time_pref_penalty,
                    weight=self.config.time_preferences_weight,
                    weighted_score=time_pref_penalty * self.config.time_preferences_weight,
                    description=f"Time preference violations ({time_pref_penalty} violations)",
                    details={"violation_count": time_pref_penalty}
                ))
            
            # Consecutive period violations
            consecutive_penalty = self._calculate_consecutive_period_penalty(teacher_loads)
            if consecutive_penalty > 0:
                penalty_breakdown.append(PenaltyBreakdown(
                    penalty_type=PenaltyType.CONSECUTIVE_PERIODS,
                    raw_score=consecutive_penalty,
                    weight=self.config.consecutive_periods_weight,
                    weighted_score=consecutive_penalty * self.config.consecutive_periods_weight,
                    description=f"Consecutive period violations ({consecutive_penalty} violations)",
                    details={"violation_count": consecutive_penalty}
                ))
            
            # Calculate final score
            total_penalty = sum(p.weighted_score for p in penalty_breakdown)
            total_score = max(0.0, base_score - total_penalty)
            
            return EvaluationResult(
                timetable_id=timetable_id,
                total_score=total_score,
                coverage_percentage=coverage * 100,
                base_score=base_score,
                penalty_breakdown=penalty_breakdown
            )
            
        except Exception as e:
            logger.error(f"Error evaluating timetable {timetable_id}: {e}")
            return EvaluationResult(
                timetable_id=timetable_id,
                total_score=0.0,
                coverage_percentage=0.0,
                base_score=0.0,
                penalty_breakdown=[]
            )
    
    def batch_evaluate(self, timetables: List[Dict[str, Any]], 
                      timetable_ids: Optional[List[str]] = None) -> BatchEvaluationResult:
        """
        Evaluate multiple timetables efficiently.
        
        Args:
            timetables: List of timetable dictionaries
            timetable_ids: Optional list of identifiers (must match timetables length)
            
        Returns:
            BatchEvaluationResult with all evaluations and summary statistics
        """
        if timetable_ids is None:
            timetable_ids = [None] * len(timetables)
        
        if len(timetable_ids) != len(timetables):
            raise ValueError("timetable_ids length must match timetables length")
        
        evaluations = []
        for timetable, tt_id in zip(timetables, timetable_ids):
            evaluation = self.evaluate(timetable, tt_id)
            evaluations.append(evaluation)
        
        # Calculate summary statistics
        scores = [e.total_score for e in evaluations]
        summary_stats = {
            'best_score': max(scores) if scores else 0.0,
            'worst_score': min(scores) if scores else 0.0,
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'score_std_dev': statistics.stdev(scores) if len(scores) > 1 else 0.0,
            'total_evaluated': len(evaluations)
        }
        
        return BatchEvaluationResult(
            evaluations=evaluations,
            summary_stats=summary_stats
        )
    
    def compare(self, timetable1: Dict[str, Any], timetable2: Dict[str, Any],
                tt1_id: Optional[str] = None, tt2_id: Optional[str] = None) -> ComparisonResult:
        """
        Compare two timetables and provide detailed comparison.
        
        Args:
            timetable1: First timetable to compare
            timetable2: Second timetable to compare
            tt1_id: Optional identifier for first timetable
            tt2_id: Optional identifier for second timetable
            
        Returns:
            ComparisonResult with winner and detailed breakdown
        """
        eval1 = self.evaluate(timetable1, tt1_id)
        eval2 = self.evaluate(timetable2, tt2_id)
        
        score_diff = eval1.total_score - eval2.total_score
        
        # Determine winner
        if abs(score_diff) < 0.01:  # Very close scores considered tie
            winner = 0
        elif score_diff > 0:
            winner = 1
        else:
            winner = 2
        
        # Analyze category-wise performance
        better_in = []
        worse_in = []
        
        penalty1_dict = eval1.penalty_summary
        penalty2_dict = eval2.penalty_summary
        
        for penalty_type in PenaltyType:
            penalty1 = penalty1_dict.get(penalty_type.value, 0)
            penalty2 = penalty2_dict.get(penalty_type.value, 0)
            
            if penalty1 < penalty2:  # Lower penalty is better
                better_in.append(penalty_type)
            elif penalty1 > penalty2:
                worse_in.append(penalty_type)
        
        # Generate summary
        if winner == 0:
            summary = "Timetables are essentially tied"
        elif winner == 1:
            summary = f"Timetable 1 wins by {score_diff:.2f} points"
        else:
            summary = f"Timetable 2 wins by {abs(score_diff):.2f} points"
        
        return ComparisonResult(
            timetable1_id=tt1_id,
            timetable2_id=tt2_id,
            winner=winner,
            score_difference=score_diff,
            better_in_categories=better_in,
            worse_in_categories=worse_in,
            summary=summary
        )
    
    # ===============================
    # PRIVATE HELPER METHODS
    # (Extracted from GA optimizer)
    # ===============================
    
    def _extract_assignments(self, timetable_dict: Dict) -> List[Dict]:
        """Extract assignment list from timetable dict."""
        # Primary structure: Timetable.entries (list of TimetableEntry)
        if "entries" in timetable_dict:
            return timetable_dict["entries"]
        
        # Legacy fallback structures for backward compatibility
        if "assignments" in timetable_dict:
            return timetable_dict["assignments"]
        
        if "schedule" in timetable_dict:
            # Flatten nested schedule structure (old format)
            assignments = []
            schedule = timetable_dict["schedule"]
            for class_id, class_schedule in schedule.items():
                if isinstance(class_schedule, dict):
                    for day, periods in class_schedule.items():
                        if isinstance(periods, dict):
                            for period, assignment in periods.items():
                                if assignment:
                                    assignments.append({
                                        "class_id": class_id,
                                        "day": day,
                                        "period": period,
                                        **assignment
                                    })
            return assignments
        
        # Fallback: assume it's a list at top level
        if isinstance(timetable_dict, list):
            return timetable_dict
        
        return []
    
    def _calculate_teacher_workloads(self, assignments: List[Dict]) -> Dict[str, List[Dict]]:
        """Group assignments by teacher."""
        workloads = defaultdict(list)
        for assignment in assignments:
            teacher_id = assignment.get("teacher_id")
            if teacher_id:
                workloads[teacher_id].append(assignment)
        return dict(workloads)
    
    def _group_by_class(self, assignments: List[Dict]) -> Dict[str, List[Dict]]:
        """Group assignments by class."""
        schedules = defaultdict(list)
        for assignment in assignments:
            class_id = assignment.get("class_id")
            if class_id:
                schedules[class_id].append(assignment)
        return dict(schedules)
    
    def _calculate_coverage_penalty(self, unfilled_slots: List[Dict]) -> float:
        """Calculate penalty for unfilled slots with priority weighting."""
        penalty = 0.0
        
        for slot in unfilled_slots:
            priority = slot.get('priority', 'medium')
            
            if priority == 'high':
                penalty += self.config.high_priority_penalty
            elif priority == 'medium':
                penalty += self.config.medium_priority_penalty
            else:  # low priority
                penalty += self.config.low_priority_penalty
        
        return penalty
    
    def _calculate_workload_imbalance_penalty(self, teacher_loads: Dict[str, List[Dict]]) -> float:
        """Calculate penalty for unbalanced teacher workload distribution."""
        if not teacher_loads:
            return 0.0
        
        workload_counts = [len(assignments) for assignments in teacher_loads.values()]
        
        if len(workload_counts) < 2:
            return 0.0
        
        # Use standard deviation as penalty
        std_dev = statistics.stdev(workload_counts)
        return float(std_dev)
    
    def _calculate_gap_penalty_partial(self, class_schedules: Dict, unfilled_slots: List[Dict]) -> float:
        """Calculate gap penalty for partial solutions, distinguishing gaps from unfilled slots."""
        penalty = 0.0
        
        # Create set of unfilled slot positions for quick lookup
        unfilled_positions = set()
        for slot in unfilled_slots:
            day = slot.get('day')
            period = slot.get('period')
            class_name = slot.get('class')
            if day and period and class_name:
                unfilled_positions.add((class_name, day, period))
        
        for class_name, schedule in class_schedules.items():
            # Group by day for gap detection
            daily_schedules = {}
            for entry in schedule:
                day = entry.get('day_of_week')
                period = entry.get('period_number')
                if day and period:
                    if day not in daily_schedules:
                        daily_schedules[day] = []
                    daily_schedules[day].append(period)
            
            # Calculate gaps for each day
            for day, periods in daily_schedules.items():
                periods.sort()
                
                # Check for gaps between scheduled periods
                for i in range(len(periods) - 1):
                    gap_start = periods[i] + 1
                    gap_end = periods[i + 1]
                    
                    # Count gaps that are not unfilled slots
                    for period in range(gap_start, gap_end):
                        if (class_name, day, period) not in unfilled_positions:
                            penalty += 1.0  # This is a true gap, not just unfilled
        
        return penalty
    
    def _calculate_time_preference_penalty(self, assignments: List[Dict]) -> float:
        """Calculate penalty for scheduling subjects at non-preferred times."""
        penalty = 0
        
        for assignment in assignments:
            period_num = assignment.get("period_number")
            if not period_num:
                continue
            
            # Read from subject metadata
            subject_metadata = assignment.get("subject_metadata", {})
            
            # Boolean flag preference
            prefer_morning = subject_metadata.get("prefer_morning", False)
            if prefer_morning and period_num > self.config.morning_period_cutoff:
                penalty += 1
            
            # Preferred periods list
            preferred_periods = subject_metadata.get("preferred_periods")
            if preferred_periods and period_num not in preferred_periods:
                if not prefer_morning:  # Don't double-penalize
                    penalty += 1
            
            # Avoid periods list
            avoid_periods = subject_metadata.get("avoid_periods")
            if avoid_periods and period_num in avoid_periods:
                penalty += 1
        
        return float(penalty)
    
    def _calculate_consecutive_period_penalty(self, teacher_loads: Dict[str, List[Dict]]) -> float:
        """Calculate penalty for teachers teaching too many consecutive periods."""
        penalty = 0
        default_max_consecutive = 3
        
        for teacher_id, assignments in teacher_loads.items():
            # Read teacher's specific limit from metadata
            teacher_metadata = assignments[0].get("teacher_metadata", {}) if assignments else {}
            max_consecutive = teacher_metadata.get("max_consecutive_periods", default_max_consecutive)
            
            # Group by day
            by_day = defaultdict(list)
            for assignment in assignments:
                day = assignment.get("day_of_week")
                period_num = assignment.get("period_number")
                
                if day and period_num:
                    by_day[day].append(period_num)
            
            # Check consecutive periods per day
            for day, periods in by_day.items():
                sorted_periods = sorted(periods)
                consecutive = 1
                
                # Count consecutive runs
                for i in range(len(sorted_periods) - 1):
                    if sorted_periods[i + 1] == sorted_periods[i] + 1:
                        consecutive += 1
                    else:
                        # Run ended, check if it exceeded limit
                        if consecutive > max_consecutive:
                            penalty += (consecutive - max_consecutive)
                        consecutive = 1
                
                # Check final run
                if consecutive > max_consecutive:
                    penalty += (consecutive - max_consecutive)
        
        return float(penalty)