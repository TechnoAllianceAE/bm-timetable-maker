"""
Demonstration of the new TimetableEvaluator and RankingService.

This script shows how to use the separated evaluation system
for ranking timetables without genetic algorithm overhead.
"""

import sys
import os

# Add the src directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from evaluation import TimetableEvaluator, EvaluationConfig
from services import RankingService, RankingCriteria


def create_sample_timetables():
    """Create sample timetables for demonstration."""
    
    # Sample partial timetable with good coverage
    timetable1 = {
        "metadata": {
            "coverage": 0.85,  # 85% coverage
            "unfilled_slots": [
                {"day": "MONDAY", "period": 5, "class": "10A", "priority": "low"},
                {"day": "TUESDAY", "period": 3, "class": "10B", "priority": "medium"}
            ]
        },
        "entries": [
            {
                "class_id": "10A", "subject_id": "MATH", "teacher_id": "T1",
                "day_of_week": "MONDAY", "period_number": 1,
                "subject_metadata": {"prefer_morning": True},
                "teacher_metadata": {"max_consecutive_periods": 3}
            },
            {
                "class_id": "10A", "subject_id": "ENGLISH", "teacher_id": "T2",
                "day_of_week": "MONDAY", "period_number": 2,
                "subject_metadata": {"prefer_morning": False},
                "teacher_metadata": {"max_consecutive_periods": 4}
            },
            {
                "class_id": "10B", "subject_id": "MATH", "teacher_id": "T1",
                "day_of_week": "TUESDAY", "period_number": 1,
                "subject_metadata": {"prefer_morning": True},
                "teacher_metadata": {"max_consecutive_periods": 3}
            }
        ]
    }
    
    # Sample partial timetable with lower coverage but better quality
    timetable2 = {
        "metadata": {
            "coverage": 0.75,  # 75% coverage
            "unfilled_slots": [
                {"day": "MONDAY", "period": 3, "class": "10A", "priority": "high"},
                {"day": "TUESDAY", "period": 4, "class": "10B", "priority": "medium"},
                {"day": "WEDNESDAY", "period": 2, "class": "10C", "priority": "low"}
            ]
        },
        "entries": [
            {
                "class_id": "10A", "subject_id": "MATH", "teacher_id": "T1",
                "day_of_week": "MONDAY", "period_number": 1,
                "subject_metadata": {"prefer_morning": True},
                "teacher_metadata": {"max_consecutive_periods": 3}
            },
            {
                "class_id": "10A", "subject_id": "ENGLISH", "teacher_id": "T2",
                "day_of_week": "MONDAY", "period_number": 2,
                "subject_metadata": {"prefer_morning": False},
                "teacher_metadata": {"max_consecutive_periods": 4}
            }
        ]
    }
    
    # Sample complete timetable with some violations
    timetable3 = {
        "metadata": {
            "coverage": 1.0,  # 100% coverage
            "unfilled_slots": []
        },
        "entries": [
            {
                "class_id": "10A", "subject_id": "MATH", "teacher_id": "T1",
                "day_of_week": "MONDAY", "period_number": 6,  # Late period (violates prefer_morning)
                "subject_metadata": {"prefer_morning": True},
                "teacher_metadata": {"max_consecutive_periods": 3}
            },
            {
                "class_id": "10A", "subject_id": "ENGLISH", "teacher_id": "T2",
                "day_of_week": "MONDAY", "period_number": 1,
                "subject_metadata": {"prefer_morning": False},
                "teacher_metadata": {"max_consecutive_periods": 4}
            },
            {
                "class_id": "10A", "subject_id": "SCIENCE", "teacher_id": "T1",
                "day_of_week": "MONDAY", "period_number": 3,  # Creates gap between periods 1 and 3
                "subject_metadata": {"prefer_morning": False},
                "teacher_metadata": {"max_consecutive_periods": 3}
            }
        ]
    }
    
    return [timetable1, timetable2, timetable3]


def demonstrate_evaluation():
    """Demonstrate individual timetable evaluation."""
    print("=== Individual Timetable Evaluation ===")
    
    # Create evaluator with default config
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    
    timetables = create_sample_timetables()
    
    for i, timetable in enumerate(timetables, 1):
        print(f"\nEvaluating Timetable {i}:")
        result = evaluator.evaluate(timetable, f"TT{i}")
        
        print(f"  Total Score: {result.total_score:.2f}")
        print(f"  Coverage: {result.coverage_percentage:.1f}%")
        print(f"  Base Score: {result.base_score:.2f}")
        print(f"  Total Penalty: {result.total_penalty:.2f}")
        
        if result.penalty_breakdown:
            print("  Penalty Breakdown:")
            for penalty in result.penalty_breakdown:
                print(f"    - {penalty.description}: {penalty.weighted_score:.2f}")


def demonstrate_ranking():
    """Demonstrate timetable ranking."""
    print("\n\n=== Timetable Ranking ===")
    
    # Create ranking service
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    ranker = RankingService(evaluator)
    
    timetables = create_sample_timetables()
    timetable_ids = ["Partial_High_Coverage", "Partial_Better_Quality", "Complete_With_Violations"]
    
    # Rank all timetables
    ranked = ranker.rank_candidates(timetables, timetable_ids)
    
    print("Ranking Results (Best to Worst):")
    for rank_result in ranked:
        print(f"  {rank_result.rank}. {rank_result.evaluation.timetable_id}")
        print(f"     Score: {rank_result.score:.2f} | Coverage: {rank_result.evaluation.coverage_percentage:.1f}%")


def demonstrate_comparison():
    """Demonstrate timetable comparison."""
    print("\n\n=== Timetable Comparison ===")
    
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    ranker = RankingService(evaluator)
    
    timetables = create_sample_timetables()
    
    # Compare first two timetables
    comparison = ranker.compare_alternatives(
        timetables[0], timetables[1],
        "High_Coverage", "Better_Quality"
    )
    
    print(f"Comparison Result: {comparison.summary}")
    print(f"Score Difference: {comparison.score_difference:.2f}")
    
    if comparison.better_in_categories:
        winner = "High_Coverage" if comparison.winner == 1 else "Better_Quality"
        print(f"{winner} is better in: {[c.value for c in comparison.better_in_categories]}")


def demonstrate_filtering():
    """Demonstrate filtering and specialized ranking."""
    print("\n\n=== Specialized Ranking Operations ===")
    
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    ranker = RankingService(evaluator)
    
    timetables = create_sample_timetables()
    
    # Find best partial with minimum 70% coverage
    best_partial = ranker.find_best_partial(timetables, min_coverage=0.7)
    
    if best_partial:
        print(f"Best Partial Timetable (≥70% coverage):")
        print(f"  Score: {best_partial.score:.2f}")
        print(f"  Coverage: {best_partial.evaluation.coverage_percentage:.1f}%")
    
    # Get top 2 timetables only
    top_2 = ranker.get_top_n(timetables, 2, ["TT1", "TT2", "TT3"])
    print(f"\nTop 2 Timetables:")
    for tt in top_2:
        print(f"  {tt.evaluation.timetable_id}: {tt.score:.2f} points")


def demonstrate_analysis():
    """Demonstrate penalty analysis across multiple timetables."""
    print("\n\n=== Penalty Distribution Analysis ===")
    
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    ranker = RankingService(evaluator)
    
    timetables = create_sample_timetables()
    
    analysis = ranker.analyze_penalty_distribution(timetables)
    
    print(f"Analysis of {analysis['total_timetables']} timetables:")
    print(f"Score Range: {analysis['score_stats']['min']:.2f} - {analysis['score_stats']['max']:.2f}")
    print(f"Average Score: {analysis['score_stats']['mean']:.2f}")
    print(f"Coverage Range: {analysis['coverage_stats']['min']:.1f}% - {analysis['coverage_stats']['max']:.1f}%")
    
    print("\nPenalty Analysis:")
    for penalty_type, stats in analysis['penalty_analysis'].items():
        if stats['affected_timetables'] > 0:
            print(f"  {penalty_type}: {stats['affected_percentage']:.1f}% affected, "
                  f"avg penalty: {stats['mean_penalty']:.2f}")


if __name__ == "__main__":
    print("Timetable Evaluation & Ranking System Demo")
    print("==========================================")
    
    demonstrate_evaluation()
    demonstrate_ranking()
    demonstrate_comparison()
    demonstrate_filtering()
    demonstrate_analysis()
    
    print("\n\nDemo completed! The new system provides:")
    print("✓ Fast evaluation without GA overhead")
    print("✓ Detailed penalty breakdowns")
    print("✓ Flexible ranking and filtering")
    print("✓ Batch operations for efficiency") 
    print("✓ Comparison and analysis tools")