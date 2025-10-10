"""
Comprehensive Test Suite for Timetable System v3.5

Tests all new features across 5 size configurations:
- TimetableEvaluator (standalone evaluation)
- RankingService (fast timetable ranking)
- TimetableCache (persistent storage)
- GA with caching integration
- End-to-end workflow

Size configurations:
1. MICRO: 2 classes, 3 subjects, 3 teachers
2. SMALL: 5 classes, 4 subjects, 8 teachers
3. MEDIUM: 12 classes, 6 subjects, 18 teachers  
4. LARGE: 25 classes, 8 subjects, 35 teachers
5. ENTERPRISE: 50 classes, 10 subjects, 60 teachers
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import statistics
import uuid

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import all required modules
from models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room, RoomType, DayOfWeek,
    OptimizationWeights
)
from csp_solver_complete_v25 import CSPSolverCompleteV25

# Import evaluation system components
from evaluation.models import (
    EvaluationResult, EvaluationConfig, PenaltyBreakdown, PenaltyType,
    ComparisonResult, RankedTimetable
)
from evaluation.timetable_evaluator import TimetableEvaluator

# Import services  
from services.ranking_service import RankingService, RankingCriteria

# Import persistence
from persistence.timetable_cache import TimetableCache

# Import GA optimizer
from algorithms.core.ga_optimizer_v25 import GAOptimizerV25

# Global test results tracking
test_results = {
    'total_tests': 0,
    'passed_tests': 0,
    'failed_tests': 0,
    'performance_metrics': {},
    'size_results': {}
}


class DataGenerator:
    """Generate test data for different size configurations."""
    
    @staticmethod
    def generate_micro_dataset():
        """MICRO: 2 classes, 3 subjects, 3 teachers - minimal test case"""
        classes = [
            Class(id='C1', school_id='S1', name='Grade 6A', grade=6, section='A', student_count=25, home_room_id='R1'),
            Class(id='C2', school_id='S1', name='Grade 7A', grade=7, section='A', student_count=25, home_room_id='R2'),
        ]

        subjects = [
            Subject(id='MATH', school_id='S1', name='Mathematics', code='MATH', periods_per_week=4, requires_lab=False, prefer_morning=True),
            Subject(id='ENG', school_id='S1', name='English', code='ENG', periods_per_week=4, requires_lab=False, prefer_morning=False),
            Subject(id='SCI', school_id='S1', name='Science', code='SCI', periods_per_week=3, requires_lab=True, prefer_morning=True),
        ]

        teachers = [
            Teacher(id='T1', user_id='U1', name='Math Teacher', subjects=['MATH'], max_periods_per_day=5, max_periods_per_week=25, max_consecutive_periods=3),
            Teacher(id='T2', user_id='U2', name='English Teacher', subjects=['ENG'], max_periods_per_day=5, max_periods_per_week=25, max_consecutive_periods=4),
            Teacher(id='T3', user_id='U3', name='Science Teacher', subjects=['SCI'], max_periods_per_day=4, max_periods_per_week=20, max_consecutive_periods=2),
        ]

        rooms = [
            Room(id='R1', school_id='S1', name='Classroom 1', capacity=30, type=RoomType.CLASSROOM),
            Room(id='R2', school_id='S1', name='Classroom 2', capacity=30, type=RoomType.CLASSROOM),
            Room(id='LAB1', school_id='S1', name='Science Lab', capacity=25, type=RoomType.LAB),
        ]

        time_slots = []
        for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY']:
            for p in range(1, 5):  # 4 periods per day
                time_slots.append(TimeSlot(
                    id=f'{day[:3]}_{p}', school_id='S1', day_of_week=day,
                    period_number=p, start_time=f'{8+p}:00', end_time=f'{8+p}:45', is_break=False
                ))

        return classes, subjects, teachers, rooms, time_slots

    @staticmethod
    def generate_small_dataset():
        """SMALL: 5 classes, 4 subjects, 8 teachers - small school"""
        classes = [
            Class(id=f'C{i}', school_id='S1', name=f'Grade {6+(i//2)}{chr(65+(i%2))}', 
                  grade=6+(i//2), section=chr(65+(i%2)), student_count=30, home_room_id=f'R{i+1}')
            for i in range(5)
        ]

        subjects = [
            Subject(id='MATH', school_id='S1', name='Mathematics', code='MATH', periods_per_week=6, requires_lab=False, prefer_morning=True),
            Subject(id='ENG', school_id='S1', name='English', code='ENG', periods_per_week=5, requires_lab=False, prefer_morning=False),
            Subject(id='SCI', school_id='S1', name='Science', code='SCI', periods_per_week=5, requires_lab=True, prefer_morning=True),
            Subject(id='SS', school_id='S1', name='Social Studies', code='SS', periods_per_week=4, requires_lab=False, prefer_morning=False),
        ]

        teachers = [
            Teacher(id=f'T{i}', user_id=f'U{i}', name=f'Teacher {i}', 
                   subjects=[subjects[i%len(subjects)].id], max_periods_per_day=6, 
                   max_periods_per_week=30, max_consecutive_periods=3)
            for i in range(1, 9)
        ]

        rooms = [
            Room(id=f'R{i}', school_id='S1', name=f'Room {i}', capacity=35, type=RoomType.CLASSROOM)
            for i in range(1, 7)
        ]
        rooms.append(Room(id='LAB1', school_id='S1', name='Science Lab', capacity=30, type=RoomType.LAB))

        time_slots = []
        for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
            for p in range(1, 6):  # 5 periods per day
                time_slots.append(TimeSlot(
                    id=f'{day[:3]}_{p}', school_id='S1', day_of_week=day,
                    period_number=p, start_time=f'{8+p}:00', end_time=f'{8+p}:45', is_break=False
                ))

        return classes, subjects, teachers, rooms, time_slots

    @staticmethod
    def generate_medium_dataset():
        """MEDIUM: 12 classes, 6 subjects, 18 teachers - medium school"""
        classes = []
        for grade in range(6, 10):  # Grades 6-9
            for section in ['A', 'B', 'C']:
                idx = (grade-6)*3 + (ord(section)-ord('A')) + 1
                classes.append(Class(
                    id=f'C{idx}', school_id='S1', name=f'Grade {grade}{section}',
                    grade=grade, section=section, student_count=32, home_room_id=f'R{idx}'
                ))

        subjects = [
            Subject(id='MATH', school_id='S1', name='Mathematics', code='MATH', periods_per_week=6, requires_lab=False, prefer_morning=True),
            Subject(id='ENG', school_id='S1', name='English', code='ENG', periods_per_week=5, requires_lab=False, prefer_morning=False),
            Subject(id='SCI', school_id='S1', name='Science', code='SCI', periods_per_week=6, requires_lab=True, prefer_morning=True),
            Subject(id='SS', school_id='S1', name='Social Studies', code='SS', periods_per_week=4, requires_lab=False, prefer_morning=False),
            Subject(id='PE', school_id='S1', name='Physical Education', code='PE', periods_per_week=3, requires_lab=False, prefer_morning=False),
            Subject(id='ART', school_id='S1', name='Art', code='ART', periods_per_week=2, requires_lab=False, prefer_morning=False),
        ]

        teachers = []
        for i in range(1, 19):
            subj_id = subjects[(i-1) % len(subjects)].id
            teachers.append(Teacher(
                id=f'T{i}', user_id=f'U{i}', name=f'Teacher {i}', subjects=[subj_id],
                max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3
            ))

        rooms = [
            Room(id=f'R{i}', school_id='S1', name=f'Room {i}', capacity=35, type=RoomType.CLASSROOM)
            for i in range(1, 15)
        ]
        rooms.extend([
            Room(id='LAB1', school_id='S1', name='Science Lab 1', capacity=30, type=RoomType.LAB),
            Room(id='LAB2', school_id='S1', name='Science Lab 2', capacity=30, type=RoomType.LAB),
        ])

        time_slots = []
        for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
            for p in range(1, 7):  # 6 periods per day
                time_slots.append(TimeSlot(
                    id=f'{day[:3]}_{p}', school_id='S1', day_of_week=day,
                    period_number=p, start_time=f'{8+p}:00', end_time=f'{8+p}:45', is_break=False
                ))

        return classes, subjects, teachers, rooms, time_slots

    @staticmethod
    def generate_large_dataset():
        """LARGE: 25 classes, 8 subjects, 35 teachers - large school"""
        classes = []
        for grade in range(6, 11):  # Grades 6-10
            for section in ['A', 'B', 'C', 'D', 'E']:
                idx = (grade-6)*5 + (ord(section)-ord('A')) + 1
                classes.append(Class(
                    id=f'C{idx}', school_id='S1', name=f'Grade {grade}{section}',
                    grade=grade, section=section, student_count=35, home_room_id=f'R{idx}'
                ))

        subjects = [
            Subject(id='MATH', school_id='S1', name='Mathematics', code='MATH', periods_per_week=6, requires_lab=False, prefer_morning=True),
            Subject(id='ENG', school_id='S1', name='English', code='ENG', periods_per_week=5, requires_lab=False, prefer_morning=False),
            Subject(id='SCI', school_id='S1', name='Science', code='SCI', periods_per_week=6, requires_lab=True, prefer_morning=True),
            Subject(id='SS', school_id='S1', name='Social Studies', code='SS', periods_per_week=4, requires_lab=False, prefer_morning=False),
            Subject(id='PE', school_id='S1', name='Physical Education', code='PE', periods_per_week=3, requires_lab=False, prefer_morning=False),
            Subject(id='ART', school_id='S1', name='Art', code='ART', periods_per_week=2, requires_lab=False, prefer_morning=False),
            Subject(id='MUS', school_id='S1', name='Music', code='MUS', periods_per_week=2, requires_lab=False, prefer_morning=False),
            Subject(id='COMP', school_id='S1', name='Computer', code='COMP', periods_per_week=3, requires_lab=True, prefer_morning=True),
        ]

        teachers = []
        for i in range(1, 36):
            # Distribute subjects with some teachers handling multiple subjects
            if i <= 8:
                subj_ids = [subjects[i-1].id]
            elif i <= 16:
                subj_ids = [subjects[(i-9) % len(subjects)].id]
            else:
                # Multi-subject teachers
                primary = subjects[(i-1) % len(subjects)].id
                secondary = subjects[(i+2) % len(subjects)].id
                subj_ids = [primary, secondary] if primary != secondary else [primary]
            
            teachers.append(Teacher(
                id=f'T{i}', user_id=f'U{i}', name=f'Teacher {i}', subjects=subj_ids,
                max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3
            ))

        rooms = [
            Room(id=f'R{i}', school_id='S1', name=f'Room {i}', capacity=40, type=RoomType.CLASSROOM)
            for i in range(1, 28)
        ]
        rooms.extend([
            Room(id='LAB1', school_id='S1', name='Science Lab 1', capacity=30, type=RoomType.LAB),
            Room(id='LAB2', school_id='S1', name='Science Lab 2', capacity=30, type=RoomType.LAB),
            Room(id='LAB3', school_id='S1', name='Computer Lab', capacity=30, type=RoomType.LAB),
        ])

        time_slots = []
        for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
            for p in range(1, 8):  # 7 periods per day
                time_slots.append(TimeSlot(
                    id=f'{day[:3]}_{p}', school_id='S1', day_of_week=day,
                    period_number=p, start_time=f'{8+p}:00', end_time=f'{8+p}:45', is_break=False
                ))

        return classes, subjects, teachers, rooms, time_slots

    @staticmethod
    def generate_enterprise_dataset():
        """ENTERPRISE: 50 classes, 10 subjects, 60 teachers - very large school"""
        classes = []
        for grade in range(6, 13):  # Grades 6-12
            sections_per_grade = 8 if grade <= 10 else 6  # Fewer sections in higher grades
            for i in range(sections_per_grade):
                section = chr(65 + i)  # A, B, C, ...
                idx = len(classes) + 1
                classes.append(Class(
                    id=f'C{idx}', school_id='S1', name=f'Grade {grade}{section}',
                    grade=grade, section=section, student_count=38, home_room_id=f'R{idx}'
                ))

        subjects = [
            Subject(id='MATH', school_id='S1', name='Mathematics', code='MATH', periods_per_week=6, requires_lab=False, prefer_morning=True),
            Subject(id='ENG', school_id='S1', name='English', code='ENG', periods_per_week=5, requires_lab=False, prefer_morning=False),
            Subject(id='SCI', school_id='S1', name='Science', code='SCI', periods_per_week=6, requires_lab=True, prefer_morning=True),
            Subject(id='SS', school_id='S1', name='Social Studies', code='SS', periods_per_week=4, requires_lab=False, prefer_morning=False),
            Subject(id='PE', school_id='S1', name='Physical Education', code='PE', periods_per_week=3, requires_lab=False, prefer_morning=False),
            Subject(id='ART', school_id='S1', name='Art', code='ART', periods_per_week=2, requires_lab=False, prefer_morning=False),
            Subject(id='MUS', school_id='S1', name='Music', code='MUS', periods_per_week=2, requires_lab=False, prefer_morning=False),
            Subject(id='COMP', school_id='S1', name='Computer', code='COMP', periods_per_week=3, requires_lab=True, prefer_morning=True),
            Subject(id='LANG', school_id='S1', name='Foreign Language', code='LANG', periods_per_week=4, requires_lab=False, prefer_morning=False),
            Subject(id='CHEM', school_id='S1', name='Chemistry', code='CHEM', periods_per_week=4, requires_lab=True, prefer_morning=True),
        ]

        teachers = []
        for i in range(1, 61):
            # More realistic subject distribution
            if i <= 15:  # Core subject specialists
                subj_ids = [subjects[i % 4].id]  # Math, Eng, Sci, SS
            elif i <= 25:  # Lab specialists
                lab_subjects = ['SCI', 'COMP', 'CHEM']
                subj_ids = [lab_subjects[(i-16) % len(lab_subjects)]]
            elif i <= 35:  # Multi-subject teachers
                subj_ids = [subjects[(i-1) % len(subjects)].id]
            else:  # Specialized teachers
                remaining_subjects = subjects[4:]  # PE, ART, MUS, etc.
                subj_ids = [remaining_subjects[(i-36) % len(remaining_subjects)].id]
            
            teachers.append(Teacher(
                id=f'T{i}', user_id=f'U{i}', name=f'Teacher {i}', subjects=subj_ids,
                max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3
            ))

        rooms = [
            Room(id=f'R{i}', school_id='S1', name=f'Room {i}', capacity=40, type=RoomType.CLASSROOM)
            for i in range(1, 52)
        ]
        rooms.extend([
            Room(id='LAB1', school_id='S1', name='Science Lab 1', capacity=30, type=RoomType.LAB),
            Room(id='LAB2', school_id='S1', name='Science Lab 2', capacity=30, type=RoomType.LAB),
            Room(id='LAB3', school_id='S1', name='Chemistry Lab', capacity=25, type=RoomType.LAB),
            Room(id='LAB4', school_id='S1', name='Computer Lab 1', capacity=30, type=RoomType.LAB),
            Room(id='LAB5', school_id='S1', name='Computer Lab 2', capacity=30, type=RoomType.LAB),
        ])

        time_slots = []
        for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
            for p in range(1, 8):  # 7 periods per day
                time_slots.append(TimeSlot(
                    id=f'{day[:3]}_{p}', school_id='S1', day_of_week=day,
                    period_number=p, start_time=f'{8+p}:00', end_time=f'{8+p}:45', is_break=False
                ))

        return classes, subjects, teachers, rooms, time_slots


def run_test(test_name: str, test_func, *args, **kwargs):
    """Helper function to run a test and track results."""
    global test_results
    test_results['total_tests'] += 1
    
    try:
        print(f"\n{'='*80}")
        print(f"🧪 RUNNING TEST: {test_name}")
        print(f"{'='*80}")
        
        start_time = time.time()
        result = test_func(*args, **kwargs)
        end_time = time.time()
        
        test_results['passed_tests'] += 1
        test_results['performance_metrics'][test_name] = {
            'execution_time': end_time - start_time,
            'result': result
        }
        
        print(f"✅ PASSED: {test_name} ({end_time - start_time:.2f}s)")
        return True, result
        
    except Exception as e:
        test_results['failed_tests'] += 1
        print(f"❌ FAILED: {test_name}")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_evaluator_system(size_name: str, classes, subjects, teachers, rooms, time_slots):
    """Test the standalone evaluator system."""
    print(f"\n🔬 Testing TimetableEvaluator for {size_name} dataset...")
    
    # Generate a sample timetable using CSP solver
    solver = CSPSolverCompleteV25(debug=False)
    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes, subjects=subjects, teachers=teachers,
        time_slots=time_slots, rooms=rooms, constraints=[],
        num_solutions=3, enforce_teacher_consistency=True
    )
    
    if not timetables:
        raise Exception("CSP solver failed to generate timetables")
    
    # Test evaluator
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    
    # Single evaluation
    timetable_dict = timetables[0].dict() if hasattr(timetables[0], 'dict') else timetables[0]
    result = evaluator.evaluate(timetable_dict, f"{size_name}_test_tt_1")
    
    print(f"   Single evaluation: Score = {result.total_score:.2f}, Coverage = {result.coverage_percentage:.1f}%")
    
    # Batch evaluation
    tt_dicts = [tt.dict() if hasattr(tt, 'dict') else tt for tt in timetables]
    batch_result = evaluator.batch_evaluate(tt_dicts)
    
    print(f"   Batch evaluation: {len(batch_result.evaluations)} timetables")
    print(f"   Best score: {batch_result.best_score:.2f}, Avg: {batch_result.average_score:.2f}")
    
    # Penalty breakdown
    if result.penalty_breakdown:
        print("   Penalty breakdown:")
        for penalty in result.penalty_breakdown:
            print(f"     - {penalty.penalty_type.value}: {penalty.weighted_score:.2f}")
    
    return {
        'single_score': result.total_score,
        'batch_count': len(batch_result.evaluations),
        'best_score': batch_result.best_score,
        'avg_score': batch_result.average_score,
        'penalty_types': len(result.penalty_breakdown)
    }


def test_ranking_system(size_name: str, classes, subjects, teachers, rooms, time_slots):
    """Test the ranking service."""
    print(f"\n📊 Testing RankingService for {size_name} dataset...")
    
    # Generate multiple timetables
    solver = CSPSolverCompleteV25(debug=False)
    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes, subjects=subjects, teachers=teachers,
        time_slots=time_slots, rooms=rooms, constraints=[],
        num_solutions=5, enforce_teacher_consistency=True
    )
    
    if len(timetables) < 2:
        raise Exception("Need at least 2 timetables for ranking tests")
    
    # Setup ranking service
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    ranker = RankingService(evaluator)
    
    # Convert to dicts
    tt_dicts = [tt.dict() if hasattr(tt, 'dict') else tt for tt in timetables]
    tt_ids = [f"{size_name}_tt_{i+1}" for i in range(len(tt_dicts))]
    
    # Test ranking
    ranked = ranker.rank_candidates(tt_dicts, tt_ids)
    
    print(f"   Ranked {len(ranked)} timetables:")
    for i, rt in enumerate(ranked[:3]):  # Show top 3
        print(f"     {rt.rank}. {rt.evaluation.timetable_id}: {rt.score:.2f} points")
    
    # Test comparison
    if len(ranked) >= 2:
        comparison = ranker.compare_alternatives(
            ranked[0].timetable, ranked[1].timetable,
            ranked[0].evaluation.timetable_id, ranked[1].evaluation.timetable_id
        )
        print(f"   Comparison result: {comparison.summary}")
    
    # Test specialized operations
    top_3 = ranker.get_top_n(tt_dicts, 3, tt_ids)
    quality_filtered = ranker.filter_by_quality(tt_dicts, 500.0, tt_ids)
    
    print(f"   Top 3 count: {len(top_3)}")
    print(f"   Quality filtered (>500): {len(quality_filtered)}")
    
    return {
        'ranked_count': len(ranked),
        'top_score': ranked[0].score if ranked else 0,
        'score_range': ranked[0].score - ranked[-1].score if len(ranked) > 1 else 0,
        'top_3_count': len(top_3),
        'quality_filtered_count': len(quality_filtered)
    }


def test_caching_system(size_name: str, classes, subjects, teachers, rooms, time_slots):
    """Test the caching system."""
    print(f"\n💾 Testing TimetableCache for {size_name} dataset...")
    
    # Generate sample timetables
    solver = CSPSolverCompleteV25(debug=False)
    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes, subjects=subjects, teachers=teachers,
        time_slots=time_slots, rooms=rooms, constraints=[],
        num_solutions=3, enforce_teacher_consistency=True
    )
    
    if not timetables:
        raise Exception("CSP solver failed to generate timetables")
    
    # Test basic caching
    cache = TimetableCache(max_age_hours=1, max_cache_size_mb=100)
    session_id = f"test_session_{size_name}_{int(time.time())}"
    
    # Store timetables
    stored_ids = []
    tt_dicts = [tt.dict() if hasattr(tt, 'dict') else tt for tt in timetables]
    fitness_scores = [800 + i*50 for i in range(len(tt_dicts))]
    
    for i, (tt_dict, fitness) in enumerate(zip(tt_dicts, fitness_scores)):
        tt_id = cache.store_timetable(
            timetable=tt_dict,
            session_id=session_id,
            generation=0,
            fitness_score=fitness,
            metadata={'test': True, 'size': size_name}
        )
        stored_ids.append(tt_id)
    
    print(f"   Stored {len(stored_ids)} timetables")
    
    # Test retrieval
    retrieved = cache.retrieve_timetable(stored_ids[0])
    if not retrieved:
        raise Exception("Failed to retrieve cached timetable")
    
    print(f"   Successfully retrieved timetable")
    
    # Test best timetable retrieval
    best_result = cache.get_best_timetable(session_id)
    if not best_result:
        raise Exception("Failed to get best timetable")
    
    best_id, best_tt = best_result
    print(f"   Best timetable: {best_id}")
    
    # Test cache stats
    stats = cache.get_cache_stats()
    print(f"   Cache stats: {stats['total_timetables']} files, {stats['total_size_mb']:.2f} MB")
    
    # Cleanup test session
    cache.complete_session(session_id, keep_best=False)
    
    return {
        'stored_count': len(stored_ids),
        'retrieved_success': retrieved is not None,
        'best_found': best_result is not None,
        'cache_size_mb': stats['total_size_mb']
    }


def test_ga_with_caching(size_name: str, classes, subjects, teachers, rooms, time_slots):
    """Test GA optimizer with caching integration."""
    print(f"\n🧬 Testing GA with caching for {size_name} dataset...")
    
    # Generate initial population with CSP solver
    solver = CSPSolverCompleteV25(debug=False)
    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes, subjects=subjects, teachers=teachers,
        time_slots=time_slots, rooms=rooms, constraints=[],
        num_solutions=5, enforce_teacher_consistency=True
    )
    
    if not timetables:
        raise Exception("CSP solver failed to generate initial population")
    
    # Setup GA with caching
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    cache = TimetableCache()
    
    ga = GAOptimizerV25(evaluator=evaluator, cache=cache, enable_caching=True)
    
    # Convert to dicts
    tt_dicts = [tt.dict() if hasattr(tt, 'dict') else tt for tt in timetables]
    weights = OptimizationWeights()
    session_id = f"ga_test_{size_name}_{int(time.time())}"
    
    # Run GA with caching
    generations = 3 if size_name in ['MICRO', 'SMALL'] else 2  # Adjust for larger datasets
    
    optimized_population = ga.evolve(
        population=tt_dicts,
        generations=generations,
        weights=weights,
        session_id=session_id,
        cache_intermediate=True
    )
    
    print(f"   GA completed {generations} generations")
    
    # Test cache integration
    cache_stats = ga.get_cache_stats()
    if cache_stats:
        print(f"   Cache after GA: {cache_stats['total_timetables']} timetables")
        session_details = cache_stats.get('session_details', {}).get(session_id, {})
        print(f"   Session generations: {session_details.get('generations', 0)}")
    
    # Test cached best result
    best_cached = ga.get_cached_best_timetable()
    if best_cached:
        best_coverage = best_cached.get('metadata', {}).get('coverage', 1.0)
        print(f"   Best cached result coverage: {best_coverage:.1%}")
    
    # Test evolution report
    evolution_report = ga.get_evolution_report()
    print(f"   Evolution report length: {len(evolution_report)} characters")
    
    # Cleanup
    ga.cleanup_session(session_id, keep_best=False)
    
    return {
        'generations_completed': generations,
        'population_size': len(optimized_population),
        'cache_integration': cache_stats is not None,
        'best_cached': best_cached is not None,
        'evolution_report_generated': len(evolution_report) > 0
    }


def test_end_to_end_workflow(size_name: str, classes, subjects, teachers, rooms, time_slots):
    """Test complete end-to-end workflow."""
    print(f"\n🔄 Testing end-to-end workflow for {size_name} dataset...")
    
    workflow_results = {}
    
    # Step 1: Generate initial timetables
    print("   Step 1: Generating initial timetables...")
    solver = CSPSolverCompleteV25(debug=False)
    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes, subjects=subjects, teachers=teachers,
        time_slots=time_slots, rooms=rooms, constraints=[],
        num_solutions=4, enforce_teacher_consistency=True
    )
    
    if not timetables:
        raise Exception("Failed to generate initial timetables")
    
    workflow_results['initial_generation'] = {
        'timetable_count': len(timetables),
        'generation_time': gen_time,
        'conflicts': len(conflicts) if conflicts else 0
    }
    
    # Step 2: Evaluate and rank
    print("   Step 2: Evaluating and ranking timetables...")
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    ranker = RankingService(evaluator)
    
    tt_dicts = [tt.dict() if hasattr(tt, 'dict') else tt for tt in timetables]
    ranked = ranker.rank_candidates(tt_dicts, [f"workflow_{size_name}_{i+1}" for i in range(len(tt_dicts))])
    
    workflow_results['evaluation_ranking'] = {
        'ranked_count': len(ranked),
        'best_score': ranked[0].score if ranked else 0,
        'worst_score': ranked[-1].score if ranked else 0
    }
    
    # Step 3: Cache results
    print("   Step 3: Caching results...")
    cache = TimetableCache()
    session_id = f"workflow_{size_name}_{int(time.time())}"
    
    for i, rt in enumerate(ranked):
        cache.store_timetable(
            timetable=rt.timetable,
            session_id=session_id,
            generation=0,
            fitness_score=rt.score,
            metadata={'workflow_step': 'initial_ranking', 'rank': rt.rank}
        )
    
    workflow_results['caching'] = {
        'cached_count': len(ranked),
        'session_id': session_id
    }
    
    # Step 4: Optimize with GA
    print("   Step 4: Optimizing with GA...")
    ga = GAOptimizerV25(evaluator=evaluator, cache=cache, enable_caching=True)
    
    optimized_population = ga.evolve(
        population=tt_dicts[:3],  # Use top 3 as starting population
        generations=2,
        session_id=f"{session_id}_optimized",
        cache_intermediate=True
    )
    
    workflow_results['optimization'] = {
        'optimized_count': len(optimized_population),
        'ga_session': f"{session_id}_optimized"
    }
    
    # Step 5: Final evaluation and comparison
    print("   Step 5: Final evaluation and comparison...")
    final_ranked = ranker.rank_candidates(optimized_population)
    
    if len(final_ranked) > 0 and len(ranked) > 0:
        improvement = final_ranked[0].score - ranked[0].score
        workflow_results['final_comparison'] = {
            'final_best_score': final_ranked[0].score,
            'improvement': improvement,
            'improvement_percentage': (improvement / ranked[0].score) * 100 if ranked[0].score > 0 else 0
        }
        
        print(f"   Final best score: {final_ranked[0].score:.2f}")
        print(f"   Improvement: {improvement:+.2f} ({workflow_results['final_comparison']['improvement_percentage']:+.1f}%)")
    
    # Cleanup
    cache.complete_session(session_id, keep_best=False)
    ga.cleanup_session(f"{session_id}_optimized", keep_best=False)
    
    return workflow_results


def run_size_configuration_tests(size_name: str, dataset_func):
    """Run all tests for a specific size configuration."""
    print(f"\n{'🔥'*20} TESTING {size_name} CONFIGURATION {'🔥'*20}")
    
    size_results = {}
    
    # Generate dataset
    print(f"\n📋 Generating {size_name} dataset...")
    classes, subjects, teachers, rooms, time_slots = dataset_func()
    
    print(f"   Dataset: {len(classes)} classes, {len(subjects)} subjects, {len(teachers)} teachers")
    print(f"            {len(rooms)} rooms, {len(time_slots)} time slots")
    
    # Run individual component tests
    success, result = run_test(f"{size_name}_Evaluator", test_evaluator_system, 
                              size_name, classes, subjects, teachers, rooms, time_slots)
    if success:
        size_results['evaluator'] = result
    
    success, result = run_test(f"{size_name}_Ranking", test_ranking_system,
                              size_name, classes, subjects, teachers, rooms, time_slots)
    if success:
        size_results['ranking'] = result
    
    success, result = run_test(f"{size_name}_Caching", test_caching_system,
                              size_name, classes, subjects, teachers, rooms, time_slots)
    if success:
        size_results['caching'] = result
    
    success, result = run_test(f"{size_name}_GA_Caching", test_ga_with_caching,
                              size_name, classes, subjects, teachers, rooms, time_slots)
    if success:
        size_results['ga_caching'] = result
    
    success, result = run_test(f"{size_name}_End_to_End", test_end_to_end_workflow,
                              size_name, classes, subjects, teachers, rooms, time_slots)
    if success:
        size_results['end_to_end'] = result
    
    test_results['size_results'][size_name] = size_results
    return size_results


def main():
    """Run comprehensive test suite for v3.5."""
    print("🚀 TIMETABLE SYSTEM v3.5 COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    start_time = time.time()
    
    # Define size configurations and their generators
    size_configs = [
        ('MICRO', DataGenerator.generate_micro_dataset),
        ('SMALL', DataGenerator.generate_small_dataset),
        ('MEDIUM', DataGenerator.generate_medium_dataset),
        ('LARGE', DataGenerator.generate_large_dataset),
        ('ENTERPRISE', DataGenerator.generate_enterprise_dataset),
    ]
    
    # Run tests for each size configuration
    for size_name, generator_func in size_configs:
        try:
            run_size_configuration_tests(size_name, generator_func)
        except Exception as e:
            print(f"💥 CRITICAL ERROR in {size_name} tests: {e}")
            import traceback
            traceback.print_exc()
    
    # Final results
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n{'🏁'*30} FINAL RESULTS {'🏁'*30}")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Tests run: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']} ✅")
    print(f"Failed: {test_results['failed_tests']} ❌")
    print(f"Success rate: {(test_results['passed_tests'] / test_results['total_tests'] * 100):.1f}%")
    
    # Performance summary
    print(f"\n📊 PERFORMANCE SUMMARY:")
    for test_name, metrics in test_results['performance_metrics'].items():
        print(f"   {test_name}: {metrics['execution_time']:.2f}s")
    
    # Size configuration summary
    print(f"\n📏 SIZE CONFIGURATION RESULTS:")
    for size_name, results in test_results['size_results'].items():
        completed_tests = len([k for k, v in results.items() if v])
        print(f"   {size_name}: {completed_tests}/5 tests completed")
        
        if 'evaluator' in results and results['evaluator']:
            best_score = results['evaluator'].get('best_score', 0)
            print(f"      Best evaluation score: {best_score:.2f}")
        
        if 'end_to_end' in results and results['end_to_end']:
            improvement = results['end_to_end'].get('final_comparison', {}).get('improvement_percentage', 0)
            print(f"      GA improvement: {improvement:+.1f}%")
    
    # Save detailed results to file
    results_file = f"test_results_v35_{int(time.time())}.json"
    try:
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️  Failed to save results: {e}")
    
    print(f"\n{'🎉'*20} TEST SUITE COMPLETE {'🎉'*20}")
    
    return test_results


if __name__ == "__main__":
    results = main()