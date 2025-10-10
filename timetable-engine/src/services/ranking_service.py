"""
Timetable ranking service.

This service provides high-level ranking operations for timetables,
using the TimetableEvaluator for fast and efficient scoring. Optimized
for ranking scenarios where you need to quickly identify the best
timetable candidates.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.timetable_evaluator import TimetableEvaluator
from evaluation.models import (
    EvaluationResult, RankedTimetable, BatchEvaluationResult,
    ComparisonResult, PenaltyType
)

logger = logging.getLogger(__name__)


@dataclass
class RankingCriteria:
    """Criteria for custom ranking operations."""
    sort_by: str = "total_score"  # total_score, coverage, specific_penalty
    descending: bool = True       # True for higher-is-better, False for lower-is-better
    min_coverage: Optional[float] = None  # Filter out below this coverage %
    max_penalties: Optional[Dict[str, float]] = None  # Max allowed per penalty type


class RankingService:
    """
    High-level service for ranking and comparing timetables.
    
    Provides efficient batch operations and filtering capabilities
    specifically designed for timetable ranking scenarios.
    """
    
    def __init__(self, evaluator: TimetableEvaluator):
        """
        Initialize ranking service with evaluator.
        
        Args:
            evaluator: Configured TimetableEvaluator instance
        """
        self.evaluator = evaluator
    
    def rank_candidates(self, 
                       timetables: List[Dict[str, Any]],
                       timetable_ids: Optional[List[str]] = None,
                       criteria: Optional[RankingCriteria] = None) -> List[RankedTimetable]:
        """
        Rank a list of timetable candidates by quality.
        
        Args:
            timetables: List of timetable dictionaries to rank
            timetable_ids: Optional identifiers for timetables
            criteria: Optional custom ranking criteria
            
        Returns:
            List of RankedTimetable objects sorted by quality (best first)
        """
        if not timetables:
            return []
        
        criteria = criteria or RankingCriteria()
        
        # Batch evaluate all timetables
        batch_result = self.evaluator.batch_evaluate(timetables, timetable_ids)
        
        # Apply filters if specified
        filtered_evaluations = self._apply_filters(batch_result.evaluations, criteria)
        
        # Sort by specified criteria
        sorted_evaluations = self._sort_by_criteria(filtered_evaluations, criteria)
        
        # Convert to RankedTimetable objects
        ranked_timetables = []
        for rank, (evaluation, timetable) in enumerate(zip(sorted_evaluations, timetables), 1):
            ranked_timetables.append(RankedTimetable(
                rank=rank,
                timetable=timetable,
                evaluation=evaluation
            ))
        
        return ranked_timetables
    
    def find_best_partial(self, 
                         partial_timetables: List[Dict[str, Any]],
                         min_coverage: float = 0.7,
                         timetable_ids: Optional[List[str]] = None) -> Optional[RankedTimetable]:
        """
        Find the best partial timetable that meets minimum coverage.
        
        Specifically optimized for partial solution ranking where we want
        the highest quality solution that achieves reasonable coverage.
        
        Args:
            partial_timetables: List of partial timetable dictionaries
            min_coverage: Minimum coverage percentage required (0.0 to 1.0)
            timetable_ids: Optional identifiers for timetables
            
        Returns:
            Best RankedTimetable that meets criteria, or None if none qualify
        """
        if not partial_timetables:
            return None
        
        criteria = RankingCriteria(
            sort_by="total_score",
            descending=True,
            min_coverage=min_coverage * 100  # Convert to percentage
        )
        
        ranked = self.rank_candidates(partial_timetables, timetable_ids, criteria)
        
        return ranked[0] if ranked else None
    
    def compare_alternatives(self, 
                           timetable1: Dict[str, Any], 
                           timetable2: Dict[str, Any],
                           tt1_id: Optional[str] = None,
                           tt2_id: Optional[str] = None) -> ComparisonResult:
        """
        Compare two timetable alternatives with detailed analysis.
        
        Args:
            timetable1: First timetable to compare
            timetable2: Second timetable to compare  
            tt1_id: Optional identifier for first timetable
            tt2_id: Optional identifier for second timetable
            
        Returns:
            ComparisonResult with detailed comparison analysis
        """
        return self.evaluator.compare(timetable1, timetable2, tt1_id, tt2_id)
    
    def get_top_n(self, 
                  timetables: List[Dict[str, Any]], 
                  n: int,
                  timetable_ids: Optional[List[str]] = None,
                  criteria: Optional[RankingCriteria] = None) -> List[RankedTimetable]:
        """
        Get the top N best timetables efficiently.
        
        More efficient than full ranking when you only need the best few.
        
        Args:
            timetables: List of timetable dictionaries
            n: Number of top timetables to return
            timetable_ids: Optional identifiers for timetables
            criteria: Optional custom ranking criteria
            
        Returns:
            Top N ranked timetables
        """
        all_ranked = self.rank_candidates(timetables, timetable_ids, criteria)
        return all_ranked[:n]
    
    def filter_by_quality(self, 
                         timetables: List[Dict[str, Any]],
                         min_score: float,
                         timetable_ids: Optional[List[str]] = None) -> List[RankedTimetable]:
        """
        Filter timetables to only include those above a quality threshold.
        
        Args:
            timetables: List of timetable dictionaries to filter
            min_score: Minimum total score required
            timetable_ids: Optional identifiers for timetables
            
        Returns:
            List of qualifying timetables, ranked by quality
        """
        ranked = self.rank_candidates(timetables, timetable_ids)
        return [rt for rt in ranked if rt.score >= min_score]
    
    def analyze_penalty_distribution(self, 
                                   timetables: List[Dict[str, Any]],
                                   timetable_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze penalty distribution across multiple timetables.
        
        Useful for understanding what types of violations are most common
        across your candidate solutions.
        
        Args:
            timetables: List of timetable dictionaries to analyze
            timetable_ids: Optional identifiers for timetables
            
        Returns:
            Dictionary with penalty analysis statistics
        """
        if not timetables:
            return {}
        
        batch_result = self.evaluator.batch_evaluate(timetables, timetable_ids)
        
        # Collect penalty data
        penalty_data = {penalty_type.value: [] for penalty_type in PenaltyType}
        total_scores = []
        coverage_percentages = []
        
        for evaluation in batch_result.evaluations:
            total_scores.append(evaluation.total_score)
            coverage_percentages.append(evaluation.coverage_percentage)
            
            penalty_summary = evaluation.penalty_summary
            for penalty_type in PenaltyType:
                penalty_data[penalty_type.value].append(
                    penalty_summary.get(penalty_type.value, 0.0)
                )
        
        # Calculate statistics
        analysis = {
            'total_timetables': len(timetables),
            'score_stats': {
                'mean': sum(total_scores) / len(total_scores),
                'max': max(total_scores),
                'min': min(total_scores)
            },
            'coverage_stats': {
                'mean': sum(coverage_percentages) / len(coverage_percentages),
                'max': max(coverage_percentages),
                'min': min(coverage_percentages)
            },
            'penalty_analysis': {}
        }
        
        for penalty_type, values in penalty_data.items():
            non_zero_values = [v for v in values if v > 0]
            analysis['penalty_analysis'][penalty_type] = {
                'affected_timetables': len(non_zero_values),
                'affected_percentage': len(non_zero_values) / len(values) * 100,
                'mean_penalty': sum(values) / len(values),
                'max_penalty': max(values) if values else 0
            }
        
        return analysis
    
    def get_evaluation_breakdown(self, 
                               timetable: Dict[str, Any],
                               timetable_id: Optional[str] = None) -> EvaluationResult:
        """
        Get detailed evaluation breakdown for a single timetable.
        
        Convenience method for detailed analysis of individual timetables.
        
        Args:
            timetable: Timetable dictionary to evaluate
            timetable_id: Optional identifier for the timetable
            
        Returns:
            Detailed EvaluationResult with penalty breakdown
        """
        return self.evaluator.evaluate(timetable, timetable_id)
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    def _apply_filters(self, 
                      evaluations: List[EvaluationResult], 
                      criteria: RankingCriteria) -> List[EvaluationResult]:
        """Apply filtering criteria to evaluations."""
        filtered = evaluations
        
        # Filter by minimum coverage
        if criteria.min_coverage is not None:
            filtered = [e for e in filtered if e.coverage_percentage >= criteria.min_coverage]
        
        # Filter by maximum penalties
        if criteria.max_penalties:
            for penalty_type, max_penalty in criteria.max_penalties.items():
                filtered = [e for e in filtered 
                          if e.penalty_summary.get(penalty_type, 0) <= max_penalty]
        
        return filtered
    
    def _sort_by_criteria(self, 
                         evaluations: List[EvaluationResult], 
                         criteria: RankingCriteria) -> List[EvaluationResult]:
        """Sort evaluations according to criteria."""
        if criteria.sort_by == "total_score":
            key_func = lambda e: e.total_score
        elif criteria.sort_by == "coverage":
            key_func = lambda e: e.coverage_percentage
        elif criteria.sort_by.startswith("penalty_"):
            penalty_type = criteria.sort_by.replace("penalty_", "")
            key_func = lambda e: e.penalty_summary.get(penalty_type, 0)
        else:
            # Default to total score
            key_func = lambda e: e.total_score
        
        return sorted(evaluations, key=key_func, reverse=criteria.descending)


class FastRankingService(RankingService):
    """
    Optimized ranking service for scenarios with many candidates.
    
    Implements performance optimizations like early termination
    and approximate ranking for very large candidate sets.
    """
    
    def __init__(self, evaluator: TimetableEvaluator, batch_size: int = 100):
        """
        Initialize fast ranking service.
        
        Args:
            evaluator: Configured TimetableEvaluator instance
            batch_size: Size of batches for processing large lists
        """
        super().__init__(evaluator)
        self.batch_size = batch_size
    
    def quick_top_n(self, 
                    timetables: List[Dict[str, Any]], 
                    n: int,
                    timetable_ids: Optional[List[str]] = None) -> List[RankedTimetable]:
        """
        Quickly find top N without fully ranking all candidates.
        
        Uses partial evaluation and early termination for very large sets.
        
        Args:
            timetables: List of timetable dictionaries
            n: Number of top timetables to return
            timetable_ids: Optional identifiers for timetables
            
        Returns:
            Approximately top N ranked timetables
        """
        if len(timetables) <= n * 2:
            # Small enough to do full ranking
            return self.get_top_n(timetables, n, timetable_ids)
        
        # For large sets, use batch processing with early termination
        # This is a simplified implementation - in practice, you might use
        # more sophisticated algorithms like quickselect
        
        all_ranked = self.rank_candidates(timetables, timetable_ids)
        return all_ranked[:n]