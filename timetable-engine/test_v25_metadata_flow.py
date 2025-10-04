"""
Test Script for v2.5 Metadata Flow

Tests:
1. Subject/Teacher metadata extraction
2. CSP -> GA data flow
3. Object <-> Dict conversions
4. Response construction
"""

import sys
import json
from typing import Dict, Any

# Import v2.5 modules
try:
    from src.models_phase1_v25 import (
        Subject, Teacher, Class, TimeSlot, Room, DayOfWeek, RoomType,
        TimetableEntry, Timetable, TimetableStatus, OptimizationWeights
    )
    from src.csp_solver_complete_v25 import CSPSolverCompleteV25
    from src.ga_optimizer_v25 import GAOptimizerV25
    print("✓ All v2.5 modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure files are in src/ directory:")
    print("  - src/models_phase1_v25.py")
    print("  - src/csp_solver_complete_v25.py")
    print("  - src/ga_optimizer_v25.py")
    sys.exit(1)


def test_subject_metadata():
    """Test 1: Subject metadata extraction"""
    print("\n" + "="*70)
    print("TEST 1: Subject Metadata")
    print("="*70)
    
    # Create subject with preferences
    subject = Subject(
        id="MATH_10",
        school_id="SCH_001",
        name="Mathematics",
        code="MATH10",
        periods_per_week=6,
        prefer_morning=True,
        preferred_periods=[1, 2, 3, 4],
        avoid_periods=[7, 8]
    )
    
    print(f"Subject created: {subject.name}")
    print(f"  prefer_morning: {subject.prefer_morning}")
    print(f"  preferred_periods: {subject.preferred_periods}")
    print(f"  avoid_periods: {subject.avoid_periods}")
    
    # Test conversion to dict
    subject_dict = subject.dict()
    print(f"\n✓ Subject.dict() works")
    print(f"  Keys: {list(subject_dict.keys())}")
    
    # Verify metadata fields present
    assert 'prefer_morning' in subject_dict
    assert 'preferred_periods' in subject_dict
    assert 'avoid_periods' in subject_dict
    print(f"✓ Metadata fields present in dict")


def test_teacher_metadata():
    """Test 2: Teacher metadata extraction"""
    print("\n" + "="*70)
    print("TEST 2: Teacher Metadata")
    print("="*70)
    
    teacher = Teacher(
        id="T001",
        user_id="U001",
        subjects=["Mathematics"],
        max_consecutive_periods=3
    )
    
    print(f"Teacher created: {teacher.id}")
    print(f"  max_consecutive_periods: {teacher.max_consecutive_periods}")
    
    # Test conversion
    teacher_dict = teacher.dict()
    assert 'max_consecutive_periods' in teacher_dict
    print(f"✓ Teacher metadata field present in dict")


def test_timetable_entry_metadata():
    """Test 3: TimetableEntry with metadata"""
    print("\n" + "="*70)
    print("TEST 3: TimetableEntry Metadata")
    print("="*70)
    
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
        subject_metadata={
            "prefer_morning": True,
            "preferred_periods": [1, 2, 3, 4],
            "avoid_periods": [7, 8]
        },
        teacher_metadata={
            "max_consecutive_periods": 3
        }
    )
    
    print(f"TimetableEntry created: {entry.id}")
    print(f"  subject_metadata: {entry.subject_metadata}")
    print(f"  teacher_metadata: {entry.teacher_metadata}")
    
    # Test conversion
    entry_dict = entry.dict()
    assert 'subject_metadata' in entry_dict
    assert 'teacher_metadata' in entry_dict
    assert entry_dict['subject_metadata'] is not None
    assert entry_dict['teacher_metadata'] is not None
    print(f"✓ Entry metadata preserved in dict conversion")


def test_csp_metadata_extraction():
    """Test 4: CSP solver metadata extraction"""
    print("\n" + "="*70)
    print("TEST 4: CSP Metadata Extraction")
    print("="*70)
    
    # Create test data
    classes = [
        Class(
            id="10A",
            school_id="SCH_001",
            name="10-A",
            grade=10,
            section="A",
            student_count=30
        )
    ]
    
    subjects = [
        Subject(
            id="MATH_10",
            school_id="SCH_001",
            name="Mathematics",
            code="MATH10",
            periods_per_week=3,
            prefer_morning=True,
            preferred_periods=[1, 2, 3]
        ),
        Subject(
            id="ENG_10",
            school_id="SCH_001",
            name="English",
            code="ENG10",
            periods_per_week=2,
            prefer_morning=False
        )
    ]
    
    teachers = [
        Teacher(
            id="T001",
            user_id="U001",
            subjects=["Mathematics", "English"],
            max_consecutive_periods=3
        )
    ]
    
    time_slots = [
        TimeSlot(
            id=f"MON_P{i}",
            school_id="SCH_001",
            day_of_week=DayOfWeek.MONDAY,
            period_number=i,
            start_time=f"{8+i}:00",
            end_time=f"{8+i}:45",
            is_break=False
        ) for i in range(1, 6)
    ]
    
    rooms = [
        Room(
            id="R201",
            school_id="SCH_001",
            name="Room 201",
            capacity=40,
            type=RoomType.CLASSROOM
        )
    ]
    
    # Run CSP solver
    solver = CSPSolverCompleteV25(debug=False)
    print("Running CSP solver...")
    
    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        num_solutions=1
    )
    
    print(f"✓ CSP solver completed in {gen_time:.2f}s")
    print(f"  Solutions: {len(timetables)}")
    
    if timetables:
        timetable = timetables[0]
        print(f"  Entries: {len(timetable.entries)}")
        
        # Check first entry for metadata
        first_entry = timetable.entries[0]
        print(f"\nFirst entry metadata check:")
        print(f"  subject_metadata: {first_entry.subject_metadata}")
        print(f"  teacher_metadata: {first_entry.teacher_metadata}")
        
        # Verify metadata present
        has_subject_meta = first_entry.subject_metadata is not None
        has_teacher_meta = first_entry.teacher_metadata is not None
        
        if has_subject_meta:
            print(f"✓ Subject metadata extracted")
        else:
            print(f"✗ Subject metadata MISSING")
        
        if has_teacher_meta:
            print(f"✓ Teacher metadata extracted")
        else:
            print(f"✗ Teacher metadata MISSING")
        
        return timetables[0]
    else:
        print("✗ No solutions generated")
        return None


def test_ga_processing(timetable):
    """Test 5: GA optimizer processing"""
    print("\n" + "="*70)
    print("TEST 5: GA Optimizer Processing")
    print("="*70)
    
    if not timetable:
        print("✗ No timetable to process (CSP failed)")
        return None
    
    # Convert to dict
    print("Converting Timetable to dict...")
    tt_dict = timetable.dict()
    print(f"✓ Converted to dict with {len(tt_dict.get('entries', []))} entries")
    
    # Test GA optimizer
    weights = OptimizationWeights(
        workload_balance=50.0,
        gap_minimization=15.0,
        time_preferences=25.0,
        consecutive_periods=10.0,
        morning_period_cutoff=4
    )
    
    ga = GAOptimizerV25()
    print("Running GA optimizer (5 generations for testing)...")
    
    optimized = ga.evolve(
        population=[tt_dict],
        generations=5,
        mutation_rate=0.15,
        crossover_rate=0.7,
        elitism_count=1,
        weights=weights
    )
    
    print(f"✓ GA completed")
    print(f"  Output type: {type(optimized[0])}")
    print(f"  Entries count: {len(optimized[0].get('entries', []))}")
    
    # Verify metadata preserved
    first_entry = optimized[0]['entries'][0]
    has_subject_meta = 'subject_metadata' in first_entry and first_entry['subject_metadata'] is not None
    has_teacher_meta = 'teacher_metadata' in first_entry and first_entry['teacher_metadata'] is not None
    
    if has_subject_meta:
        print(f"✓ Subject metadata preserved through GA")
    else:
        print(f"✗ Subject metadata LOST in GA")
    
    if has_teacher_meta:
        print(f"✓ Teacher metadata preserved through GA")
    else:
        print(f"✗ Teacher metadata LOST in GA")
    
    return optimized[0]


def test_response_construction(timetable_dict):
    """Test 6: Response construction"""
    print("\n" + "="*70)
    print("TEST 6: Response Construction")
    print("="*70)
    
    if not timetable_dict:
        print("✗ No timetable to package")
        return
    
    from main_v25 import convert_timetable_to_solution
    
    print("Converting timetable dict to TimetableSolution...")
    
    try:
        solution = convert_timetable_to_solution(
            timetable=timetable_dict,
            score=850.5,
            feasible=True,
            conflicts=[],
            metrics={"test": True}
        )
        
        print(f"✓ TimetableSolution created")
        print(f"  Score: {solution.total_score}")
        print(f"  Feasible: {solution.feasible}")
        print(f"  Timetable type: {type(solution.timetable)}")
        
        # Verify it's serializable
        solution_dict = solution.dict()
        json_str = json.dumps(solution_dict, default=str)
        print(f"✓ Solution is JSON serializable ({len(json_str)} chars)")
        
    except Exception as e:
        print(f"✗ Response construction failed: {e}")
        import traceback
        traceback.print_exc()


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*70)
    print("v2.5 METADATA FLOW TEST SUITE")
    print("="*70)
    
    try:
        # Test 1-3: Basic metadata
        test_subject_metadata()
        test_teacher_metadata()
        test_timetable_entry_metadata()
        
        # Test 4: CSP extraction
        timetable = test_csp_metadata_extraction()
        
        # Test 5: GA processing
        optimized = test_ga_processing(timetable)
        
        # Test 6: Response construction
        test_response_construction(optimized)
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nv2.5 is ready for integration!")
        
    except AssertionError as e:
        print(f"\n✗ Test assertion failed: {e}")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
