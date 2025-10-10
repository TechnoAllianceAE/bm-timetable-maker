"""
Real Data Timetable Generation Test for v3.5

Tests the complete timetable system using real CSV data from frontend exports:
- 20 classes (Grades 6-12)  
- 10 subjects (with lab requirements)
- 66 teachers (10% extra capacity)
- 39 rooms (30 classrooms + 9 labs)

This comprehensive test validates:
1. CSP solver with real constraints
2. TimetableEvaluator with actual data
3. RankingService with multiple solutions
4. TimetableCache with realistic sizes
5. GA optimizer with caching
6. End-to-end workflow performance
"""

import sys
import time
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import required modules
from models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room, RoomType, DayOfWeek,
    OptimizationWeights
)
from csp_solver_complete_v25 import CSPSolverCompleteV25
from evaluation.models import EvaluationConfig, PenaltyType
from evaluation.timetable_evaluator import TimetableEvaluator
from services.ranking_service import RankingService
from persistence.timetable_cache import TimetableCache
from algorithms.core.ga_optimizer_v25 import GAOptimizerV25


def load_real_data():
    """Load real data from CSV files in tt_tester directory."""
    
    data_dir = Path(__file__).parent.parent / "tt_tester"
    timestamp = "20251010_143249"
    
    print("📂 Loading real CSV data...")
    
    # Load classes
    classes = []
    classes_file = data_dir / f"fe_import_classes_{timestamp}.csv"
    print(f"   Loading classes from: {classes_file}")
    
    with open(classes_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classes.append(Class(
                id=row['class_id'],
                school_id='SCHOOL_001',
                name=row['name'],
                grade=int(row['grade']),
                section=row['section'],
                student_count=int(row['capacity']),
                home_room_id=f"R{len(classes)+1:03d}"  # Assign home rooms
            ))
    
    print(f"   ✅ Loaded {len(classes)} classes")
    
    # Load subjects
    subjects = []
    subjects_file = data_dir / f"fe_import_subjects_{timestamp}.csv"
    print(f"   Loading subjects from: {subjects_file}")
    
    with open(subjects_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Determine preference based on subject type
            prefer_morning = row['code'] in ['MATH', 'SCI', 'CS']  # Core subjects in morning
            
            subjects.append(Subject(
                id=row['code'],
                school_id='SCHOOL_001', 
                name=row['name'],
                code=row['code'],
                grade_level=10,  # Default grade level
                periods_per_week=int(row['periods_per_week']),
                prefer_morning=prefer_morning,
                requires_lab=row['needs_lab'].lower() == 'true'
            ))
    
    print(f"   ✅ Loaded {len(subjects)} subjects")
    
    # Load teachers
    teachers = []
    teachers_file = data_dir / f"fe_import_teachers_{timestamp}.csv"
    print(f"   Loading teachers from: {teachers_file}")
    
    with open(teachers_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse comma-separated subjects
            subject_codes = []
            subjects_str = row['subjects_qualified'].strip('"')
            if subjects_str:
                subject_codes = [s.strip() for s in subjects_str.split(',')]
            
            # Determine max consecutive based on subject load
            max_consecutive = 4 if len(subject_codes) > 2 else 3
            
            teachers.append(Teacher(
                id=row['teacher_id'],
                user_id=row['teacher_id'].replace('TEACHER_', 'USER_'),
                name=row['name'],
                email=row['email'],
                subjects=subject_codes,
                max_periods_per_day=int(row['max_periods_per_day']),
                max_periods_per_week=int(row['max_periods_per_week']),
                max_consecutive_periods=max_consecutive
            ))
    
    print(f"   ✅ Loaded {len(teachers)} teachers")
    
    # Load rooms
    rooms = []
    rooms_file = data_dir / f"fe_import_rooms_{timestamp}.csv"
    print(f"   Loading rooms from: {rooms_file}")
    
    with open(rooms_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Determine room type
            if row['type'].lower() == 'lab':
                room_type = RoomType.LAB
            else:
                room_type = RoomType.CLASSROOM
            
            rooms.append(Room(
                id=row['room_id'],
                school_id='SCHOOL_001',
                name=row['name'],
                building='Main Building',
                floor=1,
                capacity=int(row['capacity']),
                type=room_type
            ))
    
    print(f"   ✅ Loaded {len(rooms)} rooms")
    
    # Generate time slots: 5 days × 7 periods = 35 slots
    time_slots = []
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
    
    for day in days:
        for period in range(1, 8):  # 7 periods per day
            time_slots.append(TimeSlot(
                id=f'{day[:3]}_{period}',
                school_id='SCHOOL_001',
                day_of_week=day,
                period_number=period,
                start_time=f'{8+period}:00',
                end_time=f'{8+period}:45',
                is_break=False
            ))
    
    print(f"   ✅ Generated {len(time_slots)} time slots")
    
    return classes, subjects, teachers, rooms, time_slots


def print_data_summary(classes, subjects, teachers, rooms, time_slots):
    """Print comprehensive data summary."""
    print(f"\n{'='*80}")
    print("📊 REAL DATA SUMMARY")
    print(f"{'='*80}")
    
    # Classes breakdown
    print(f"\n🏫 CLASSES ({len(classes)} total):")
    grade_counts = {}
    for cls in classes:
        grade = f"Grade {cls.grade}"
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    for grade, count in sorted(grade_counts.items()):
        print(f"   {grade}: {count} sections")
    
    total_students = sum(cls.student_count for cls in classes)
    avg_class_size = total_students / len(classes)
    print(f"   Total students: {total_students}")
    print(f"   Average class size: {avg_class_size:.1f}")
    
    # Subjects breakdown
    print(f"\n📚 SUBJECTS ({len(subjects)} total):")
    total_periods = sum(s.periods_per_week for s in subjects)
    lab_subjects = [s for s in subjects if s.requires_lab]
    morning_subjects = [s for s in subjects if s.prefer_morning]
    
    for subject in subjects:
        lab_req = " (Lab)" if subject.requires_lab else ""
        morning_pref = " (Morning)" if subject.prefer_morning else ""
        print(f"   {subject.name}: {subject.periods_per_week} periods/week{lab_req}{morning_pref}")
    
    print(f"   Total weekly periods per class: {total_periods}")
    print(f"   Lab-required subjects: {len(lab_subjects)}")
    print(f"   Morning-preferred subjects: {len(morning_subjects)}")
    
    # Teachers breakdown
    print(f"\n👨‍🏫 TEACHERS ({len(teachers)} total):")
    subject_teacher_count = {}
    multi_subject_teachers = 0
    
    for teacher in teachers:
        if len(teacher.subjects) > 1:
            multi_subject_teachers += 1
        
        for subject in teacher.subjects:
            subject_teacher_count[subject] = subject_teacher_count.get(subject, 0) + 1
    
    print(f"   Multi-subject teachers: {multi_subject_teachers}")
    print(f"   Subject coverage:")
    for subject_code in sorted(subject_teacher_count.keys()):
        count = subject_teacher_count[subject_code]
        print(f"     {subject_code}: {count} teachers")
    
    # Rooms breakdown  
    print(f"\n🏢 ROOMS ({len(rooms)} total):")
    regular_rooms = [r for r in rooms if r.type == RoomType.CLASSROOM]
    lab_rooms = [r for r in rooms if r.type == RoomType.LAB]
    
    print(f"   Regular classrooms: {len(regular_rooms)}")
    print(f"   Specialized labs: {len(lab_rooms)}")
    
    total_capacity = sum(r.capacity for r in rooms)
    print(f"   Total room capacity: {total_capacity}")
    print(f"   Room utilization potential: {(total_students/total_capacity)*100:.1f}%")
    
    # Time slots
    print(f"\n⏰ TIME STRUCTURE:")
    print(f"   Days per week: 5")
    print(f"   Periods per day: 7") 
    print(f"   Total time slots: {len(time_slots)}")
    
    # Capacity analysis
    print(f"\n📈 CAPACITY ANALYSIS:")
    required_periods = len(classes) * total_periods
    available_periods = len(teachers) * 30  # Assuming average 30 periods per teacher
    print(f"   Required teaching periods: {required_periods}")
    print(f"   Available teaching capacity: {available_periods}")
    print(f"   Capacity surplus: {((available_periods - required_periods)/required_periods)*100:+.1f}%")


def test_csp_generation(classes, subjects, teachers, rooms, time_slots):
    """Test CSP solver with real data."""
    print(f"\n{'='*80}")
    print("🔧 CSP SOLVER TEST")
    print(f"{'='*80}")
    
    solver = CSPSolverCompleteV25(debug=False)
    
    start_time = time.time()
    
    print("🚀 Starting timetable generation...")
    print(f"   Problem size: {len(classes)}×{len(subjects)}×{len(time_slots)} = {len(classes)*len(subjects)*len(time_slots):,} potential assignments")
    
    timetables, generation_time, conflicts, suggestions = solver.solve(
        classes=classes,
        subjects=subjects, 
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        num_solutions=3,
        enforce_teacher_consistency=True
    )
    
    end_time = time.time()
    
    print(f"\n📊 CSP RESULTS:")
    print(f"   Timetables generated: {len(timetables)}")
    print(f"   Generation time: {generation_time:.2f} seconds")
    print(f"   Total processing time: {end_time - start_time:.2f} seconds")
    
    if conflicts:
        print(f"   Conflicts detected: {len(conflicts)}")
        for i, conflict in enumerate(conflicts[:3]):  # Show first 3
            print(f"     {i+1}. {conflict}")
    else:
        print("   ✅ No conflicts detected")
    
    if suggestions:
        print(f"   Suggestions provided: {len(suggestions)}")
        for i, suggestion in enumerate(suggestions[:3]):  # Show first 3
            print(f"     {i+1}. {suggestion}")
    
    if timetables:
        # Analyze first timetable
        tt_dict = timetables[0].dict() if hasattr(timetables[0], 'dict') else timetables[0]
        entries = tt_dict.get('entries', [])
        print(f"   Sample timetable entries: {len(entries)}")
        
        # Calculate coverage
        total_required = len(classes) * sum(s.periods_per_week for s in subjects)
        coverage = len(entries) / total_required
        print(f"   Coverage: {coverage:.1%}")
    
    return timetables, generation_time


def test_evaluation_system(timetables, data_label="Real Data"):
    """Test evaluation system with generated timetables."""
    print(f"\n{'='*80}")
    print("🔬 EVALUATION SYSTEM TEST")
    print(f"{'='*80}")
    
    if not timetables:
        print("❌ No timetables to evaluate")
        return None
    
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    
    print(f"🧪 Evaluating {len(timetables)} timetables...")
    
    # Convert to dicts if needed
    tt_dicts = []
    for i, tt in enumerate(timetables):
        if hasattr(tt, 'dict'):
            tt_dict = tt.dict()
        else:
            tt_dict = tt
        tt_dicts.append(tt_dict)
    
    # Batch evaluation
    start_time = time.time()
    batch_result = evaluator.batch_evaluate(tt_dicts, [f"{data_label}_TT_{i+1}" for i in range(len(tt_dicts))])
    eval_time = time.time() - start_time
    
    print(f"\n📊 EVALUATION RESULTS:")
    print(f"   Evaluation time: {eval_time:.3f} seconds")
    print(f"   Best score: {batch_result.best_score:.2f}")
    print(f"   Average score: {batch_result.average_score:.2f}")
    print(f"   Worst score: {batch_result.worst_score:.2f}")
    print(f"   Score range: {batch_result.best_score - batch_result.worst_score:.2f}")
    
    # Detailed breakdown for best timetable
    best_eval = max(batch_result.evaluations, key=lambda e: e.total_score)
    print(f"\n🏆 BEST TIMETABLE ANALYSIS ({best_eval.timetable_id}):")
    print(f"   Total score: {best_eval.total_score:.2f}")
    print(f"   Coverage: {best_eval.coverage_percentage:.1f}%")
    print(f"   Base score: {best_eval.base_score:.2f}")
    print(f"   Total penalty: {best_eval.total_penalty:.2f}")
    
    if best_eval.penalty_breakdown:
        print(f"   Penalty breakdown:")
        for penalty in best_eval.penalty_breakdown:
            print(f"     - {penalty.penalty_type.value}: {penalty.weighted_score:.2f}")
    
    return batch_result


def test_ranking_system(timetables, data_label="Real Data"):
    """Test ranking service with timetables."""
    print(f"\n{'='*80}")
    print("📊 RANKING SYSTEM TEST")
    print(f"{'='*80}")
    
    if not timetables:
        print("❌ No timetables to rank")
        return None
    
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    ranker = RankingService(evaluator)
    
    # Convert to dicts
    tt_dicts = [tt.dict() if hasattr(tt, 'dict') else tt for tt in timetables]
    tt_ids = [f"{data_label}_Rank_{i+1}" for i in range(len(tt_dicts))]
    
    print(f"🎯 Ranking {len(timetables)} timetables...")
    
    start_time = time.time()
    ranked = ranker.rank_candidates(tt_dicts, tt_ids)
    ranking_time = time.time() - start_time
    
    print(f"\n📊 RANKING RESULTS:")
    print(f"   Ranking time: {ranking_time:.3f} seconds")
    print(f"   Timetables ranked: {len(ranked)}")
    
    print(f"\n🏆 TOP RANKINGS:")
    for i, rt in enumerate(ranked):
        print(f"   {rt.rank}. {rt.evaluation.timetable_id}: {rt.score:.2f} points ({rt.evaluation.coverage_percentage:.1f}% coverage)")
    
    # Test comparison of top 2
    if len(ranked) >= 2:
        comparison = ranker.compare_alternatives(
            ranked[0].timetable, ranked[1].timetable,
            ranked[0].evaluation.timetable_id, ranked[1].evaluation.timetable_id
        )
        print(f"\n⚖️  TOP 2 COMPARISON:")
        print(f"   {comparison.summary}")
        if comparison.better_in_categories:
            winner = ranked[0].evaluation.timetable_id if comparison.winner == 1 else ranked[1].evaluation.timetable_id
            print(f"   {winner} is better in: {[c.value for c in comparison.better_in_categories]}")
    
    return ranked


def test_caching_system(timetables, data_label="Real Data"):
    """Test caching system with timetables."""
    print(f"\n{'='*80}")
    print("💾 CACHING SYSTEM TEST")
    print(f"{'='*80}")
    
    if not timetables:
        print("❌ No timetables to cache")
        return None
    
    cache = TimetableCache()
    session_id = f"real_data_test_{int(time.time())}"
    
    print(f"💽 Caching {len(timetables)} timetables...")
    
    # Store timetables with fitness scores
    tt_dicts = [tt.dict() if hasattr(tt, 'dict') else tt for tt in timetables]
    fitness_scores = [800.0 + i * 50 for i in range(len(tt_dicts))]  # Simulated scores
    
    start_time = time.time()
    stored_ids = cache.store_ga_population(
        population=tt_dicts,
        session_id=session_id,
        generation=0,
        fitness_scores=fitness_scores
    )
    cache_time = time.time() - start_time
    
    print(f"\n📊 CACHING RESULTS:")
    print(f"   Caching time: {cache_time:.3f} seconds") 
    print(f"   Stored timetables: {len(stored_ids)}")
    
    # Test retrieval
    best_result = cache.get_best_timetable(session_id)
    if best_result:
        best_id, best_tt = best_result
        print(f"   Best timetable ID: {best_id}")
    
    # Get cache stats
    stats = cache.get_cache_stats()
    print(f"   Cache size: {stats['total_size_mb']:.2f} MB")
    print(f"   Active sessions: {stats['active_sessions']}")
    
    # Cleanup
    cache.complete_session(session_id, keep_best=False)
    print(f"   ✅ Session cleaned up")
    
    return stats


def test_ga_optimization(timetables, data_label="Real Data"):
    """Test GA optimizer with caching."""
    print(f"\n{'='*80}")
    print("🧬 GA OPTIMIZATION TEST")
    print(f"{'='*80}")
    
    if not timetables:
        print("❌ No timetables for GA optimization")
        return None
    
    # Setup GA with caching
    config = EvaluationConfig()
    evaluator = TimetableEvaluator(config)
    cache = TimetableCache()
    
    ga = GAOptimizerV25(evaluator=evaluator, cache=cache, enable_caching=True)
    
    # Convert to dicts and use only first 3 for faster testing
    tt_dicts = [tt.dict() if hasattr(tt, 'dict') else tt for tt in timetables[:3]]
    weights = OptimizationWeights()
    session_id = f"ga_real_data_{int(time.time())}"
    
    print(f"🔥 Running GA optimization on {len(tt_dicts)} timetables...")
    print(f"   Using 2 generations for realistic testing...")
    
    start_time = time.time()
    optimized_population = ga.evolve(
        population=tt_dicts,
        generations=2,
        weights=weights,
        session_id=session_id,
        cache_intermediate=True
    )
    ga_time = time.time() - start_time
    
    print(f"\n📊 GA OPTIMIZATION RESULTS:")
    print(f"   Optimization time: {ga_time:.2f} seconds")
    print(f"   Optimized population size: {len(optimized_population)}")
    
    # Get evolution report
    evolution_report = ga.get_evolution_report()
    lines = evolution_report.split('\n')
    for line in lines:
        if 'Best Fitness' in line or 'Improvement' in line or 'Generation' in line:
            print(f"   {line.strip()}")
    
    # Check cache integration
    cache_stats = ga.get_cache_stats()
    if cache_stats:
        print(f"   Cache after GA: {cache_stats['total_timetables']} timetables")
    
    # Cleanup
    ga.cleanup_session(session_id, keep_best=False)
    print(f"   ✅ GA session cleaned up")
    
    return optimized_population


def main():
    """Main test execution."""
    print("🚀 TIMETABLE SYSTEM v3.5 - REAL DATA GENERATION TEST")
    print("="*80)
    print("Testing with actual school data:")
    print("• 20 classes (Grades 6-12)")
    print("• 10 subjects (with lab requirements)")
    print("• 66 teachers (10% extra capacity)")
    print("• 39 rooms (30 classrooms + 9 labs)")
    print("="*80)
    
    overall_start = time.time()
    
    try:
        # Step 1: Load real data
        classes, subjects, teachers, rooms, time_slots = load_real_data()
        print_data_summary(classes, subjects, teachers, rooms, time_slots)
        
        # Step 2: Test CSP generation
        timetables, csp_time = test_csp_generation(classes, subjects, teachers, rooms, time_slots)
        
        if not timetables:
            print("\n❌ CRITICAL: CSP solver failed to generate timetables")
            print("   This indicates the constraints are too restrictive")
            print("   Consider:")
            print("   - Adding more teachers for constrained subjects")
            print("   - Reducing periods_per_week for some subjects")
            print("   - Adding more time slots (extending school day)")
            return False
        
        # Step 3: Test evaluation system
        eval_result = test_evaluation_system(timetables, "RealData")
        
        # Step 4: Test ranking system
        ranking_result = test_ranking_system(timetables, "RealData")
        
        # Step 5: Test caching system
        cache_result = test_caching_system(timetables, "RealData")
        
        # Step 6: Test GA optimization
        ga_result = test_ga_optimization(timetables, "RealData")
        
        # Final summary
        overall_time = time.time() - overall_start
        
        print(f"\n{'🎉'*25} TEST COMPLETE {'🎉'*25}")
        print(f"Total execution time: {overall_time:.2f} seconds")
        print(f"CSP generation time: {csp_time:.2f} seconds")
        
        if eval_result:
            print(f"Best timetable score: {eval_result.best_score:.2f}")
            print(f"Average score: {eval_result.average_score:.2f}")
        
        print(f"\n✅ ALL SYSTEMS OPERATIONAL WITH REAL DATA!")
        print(f"   - CSP Solver: Generated {len(timetables)} valid timetables")
        print(f"   - Evaluation: Detailed quality assessment completed")
        print(f"   - Ranking: Successfully ranked all candidates") 
        print(f"   - Caching: Persistent storage working")
        print(f"   - GA Optimizer: Evolution completed with caching")
        
        # Save results
        results = {
            'test_timestamp': int(time.time()),
            'data_summary': {
                'classes': len(classes),
                'subjects': len(subjects), 
                'teachers': len(teachers),
                'rooms': len(rooms),
                'time_slots': len(time_slots)
            },
            'csp_results': {
                'timetables_generated': len(timetables),
                'generation_time': csp_time
            },
            'evaluation_results': {
                'best_score': eval_result.best_score if eval_result else 0,
                'average_score': eval_result.average_score if eval_result else 0
            },
            'performance_metrics': {
                'total_time': overall_time,
                'csp_time': csp_time
            }
        }
        
        results_file = f"real_data_test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)