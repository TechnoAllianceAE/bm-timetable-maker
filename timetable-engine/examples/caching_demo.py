"""
Demonstration of timetable caching and persistence system.

This script shows how the GA optimizer now uses persistent caching
to reduce regeneration overhead and enable session continuity.
"""

import sys
import os
import time

# Add the src directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.core.ga_optimizer_v25 import GAOptimizerV25, OptimizationWeights
from persistence import TimetableCache
from evaluation import TimetableEvaluator, EvaluationConfig


def create_sample_population():
    """Create sample timetables for GA demonstration."""
    
    population = []
    
    # Sample timetables with varying quality
    for i in range(5):
        timetable = {
            "metadata": {
                "coverage": 0.8 + (i * 0.05),  # 80% to 100% coverage
                "unfilled_slots": []
            },
            "entries": [
                {
                    "class_id": "10A", 
                    "subject_id": "MATH", 
                    "teacher_id": f"T{i+1}",
                    "room_id": f"R{i+1}",
                    "time_slot_id": "MON_P1",
                    "day_of_week": "MONDAY", 
                    "period_number": 1 + i,
                    "subject_metadata": {"prefer_morning": True},
                    "teacher_metadata": {"max_consecutive_periods": 3}
                },
                {
                    "class_id": "10A", 
                    "subject_id": "ENGLISH", 
                    "teacher_id": f"T{i+2}",
                    "room_id": f"R{i+2}",
                    "time_slot_id": "TUE_P1",
                    "day_of_week": "TUESDAY", 
                    "period_number": 2 + i,
                    "subject_metadata": {"prefer_morning": False},
                    "teacher_metadata": {"max_consecutive_periods": 4}
                }
            ]
        }
        population.append(timetable)
    
    return population


def demonstrate_basic_caching():
    """Demonstrate basic caching functionality."""
    print("=== Basic Caching Demo ===")
    
    # Create cache
    cache = TimetableCache(max_age_hours=1, max_cache_size_mb=50)
    
    # Store some timetables
    sample_population = create_sample_population()
    session_id = "demo_session_1"
    
    stored_ids = []
    for i, timetable in enumerate(sample_population):
        tt_id = cache.store_timetable(
            timetable=timetable,
            session_id=session_id,
            generation=0,
            fitness_score=750.0 + (i * 25),
            metadata={'demo': True}
        )
        stored_ids.append(tt_id)
    
    print(f"Stored {len(stored_ids)} timetables")
    
    # Retrieve best timetable
    best_result = cache.get_best_timetable(session_id)
    if best_result:
        best_id, best_timetable = best_result
        print(f"Best timetable ID: {best_id}")
        print(f"Best coverage: {best_timetable['metadata']['coverage']}")
    
    # Show cache stats
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats['total_timetables']} files, {stats['total_size_mb']:.2f} MB")
    
    return cache, session_id


def demonstrate_ga_with_caching():
    """Demonstrate GA evolution with automatic caching."""
    print("\n\n=== GA with Caching Demo ===")
    
    # Create GA optimizer with caching enabled
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    cache = TimetableCache()
    
    ga = GAOptimizerV25(
        evaluator=evaluator,
        cache=cache,
        enable_caching=True
    )
    
    # Create initial population
    population = create_sample_population()
    weights = OptimizationWeights()
    
    print("Starting GA evolution with caching...")
    start_time = time.time()
    
    # Run GA with caching
    optimized_population = ga.evolve(
        population=population,
        generations=3,  # Small number for demo
        weights=weights,
        session_id="ga_demo_session",
        cache_intermediate=True
    )
    
    evolution_time = time.time() - start_time
    print(f"Evolution completed in {evolution_time:.2f} seconds")
    
    # Show cache stats after evolution
    cache_stats = ga.get_cache_stats()
    if cache_stats:
        print(f"Cache after evolution:")
        print(f"  Total timetables: {cache_stats['total_timetables']}")
        print(f"  Active sessions: {cache_stats['active_sessions']}")
        for session_id, details in cache_stats['session_details'].items():
            print(f"  Session {session_id}: {details['count']} timetables, {details['generations']} generations")
    
    # Retrieve cached best result
    best_cached = ga.get_cached_best_timetable()
    if best_cached:
        best_coverage = best_cached.get('metadata', {}).get('coverage', 0)
        print(f"Best cached timetable coverage: {best_coverage:.1%}")
    
    return ga


def demonstrate_session_management():
    """Demonstrate session lifecycle management."""
    print("\n\n=== Session Management Demo ===")
    
    cache = TimetableCache()
    
    # Create multiple sessions
    sessions = []
    for i in range(3):
        session_id = f"session_{i+1}"
        
        # Store some timetables for each session
        for gen in range(2):
            population = create_sample_population()
            fitness_scores = [700.0 + (j * 30) + (gen * 50) for j in range(len(population))]
            
            cache.store_ga_population(
                population=population,
                session_id=session_id,
                generation=gen,
                fitness_scores=fitness_scores
            )
        
        sessions.append(session_id)
    
    print(f"Created {len(sessions)} sessions with multiple generations")
    
    # Show stats before cleanup
    stats = cache.get_cache_stats()
    print(f"Before cleanup: {stats['total_timetables']} timetables")
    
    # Complete sessions (keep best, clean up intermediate)
    for session_id in sessions:
        cache.complete_session(session_id, keep_best=True)
        print(f"Completed session {session_id}")
    
    # Show stats after cleanup
    stats = cache.get_cache_stats()
    print(f"After cleanup: {stats['total_timetables']} timetables")
    
    # Clean up demo sessions
    cache.cleanup_all()
    print("All demo sessions cleaned up")


def demonstrate_resumption():
    """Demonstrate resuming GA from cached generation."""
    print("\n\n=== Resumption Demo ===")
    
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    cache = TimetableCache()
    
    ga = GAOptimizerV25(evaluator=evaluator, cache=cache, enable_caching=True)
    
    # Run initial GA evolution
    population = create_sample_population()
    weights = OptimizationWeights()
    
    print("Running initial evolution...")
    ga.evolve(
        population=population,
        generations=2,
        weights=weights,
        session_id="resumption_demo",
        cache_intermediate=True
    )
    
    # Simulate resuming from generation 1
    print("Attempting to resume from generation 1...")
    resumed_population = ga.resume_from_generation("resumption_demo", 1)
    
    if resumed_population:
        print(f"Successfully resumed with {len(resumed_population)} timetables")
        
        # Continue evolution from resumed population
        print("Continuing evolution from resumed population...")
        final_population = ga.evolve(
            population=resumed_population,
            generations=2,
            weights=weights,
            session_id="resumption_demo_continued",
            cache_intermediate=True
        )
        
        print(f"Final evolution completed with {len(final_population)} timetables")
    else:
        print("Failed to resume - generation not found in cache")
    
    # Cleanup
    ga.cleanup_session("resumption_demo")
    ga.cleanup_session("resumption_demo_continued")


def demonstrate_performance_comparison():
    """Compare performance with and without caching."""
    print("\n\n=== Performance Comparison ===")
    
    population = create_sample_population() * 3  # Larger population
    weights = OptimizationWeights()
    
    # Without caching
    print("Running GA without caching...")
    ga_no_cache = GAOptimizerV25(enable_caching=False)
    
    start_time = time.time()
    result_no_cache = ga_no_cache.evolve(
        population=population,
        generations=3,
        weights=weights
    )
    time_no_cache = time.time() - start_time
    
    # With caching
    print("Running GA with caching...")
    ga_with_cache = GAOptimizerV25(enable_caching=True)
    
    start_time = time.time()
    result_with_cache = ga_with_cache.evolve(
        population=population,
        generations=3,
        weights=weights,
        session_id="performance_test"
    )
    time_with_cache = time.time() - start_time
    
    print(f"Results:")
    print(f"  Without caching: {time_no_cache:.2f} seconds")
    print(f"  With caching:    {time_with_cache:.2f} seconds")
    print(f"  Overhead:        {((time_with_cache - time_no_cache) / time_no_cache * 100):+.1f}%")
    
    # The caching overhead is acceptable for the benefits gained
    
    # Cleanup
    ga_with_cache.cleanup_session("performance_test")


if __name__ == "__main__":
    print("Timetable Caching and Persistence System Demo")
    print("=" * 50)
    
    try:
        demonstrate_basic_caching()
        demonstrate_ga_with_caching()
        demonstrate_session_management()
        demonstrate_resumption()
        demonstrate_performance_comparison()
        
        print("\n\nDemo completed! Key benefits of caching system:")
        print("✓ Persistent storage of timetables across sessions")
        print("✓ Automatic cleanup of intermediate results") 
        print("✓ Session-based organization and management")
        print("✓ Resumption capability for interrupted processes")
        print("✓ Reduced regeneration overhead for re-evaluation")
        print("✓ Best result preservation and retrieval")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()