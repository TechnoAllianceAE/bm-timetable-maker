"""
Test Validators with All Size Configurations

This script tests the pre and post validators with small, medium, and large
test data to ensure they work correctly at different scales.
"""

import sys
import time
from typing import List

# Add parent directory to path
sys.path.insert(0, '../timetable-engine')

from src.models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room, RoomType, DayOfWeek,
    GenerateRequest, Constraint, OptimizationWeights, GradeSubjectRequirement
)
from src.csp_solver_complete_v25 import CSPSolverCompleteV25
from src.validators import validate_request, validate_timetable


def generate_small_dataset():
    """Generate small test dataset: 3 classes, 3 subjects, 5 teachers"""
    print("\n" + "=" * 70)
    print("GENERATING SMALL DATASET")
    print("=" * 70)

    classes = [
        Class(id='C1', school_id='S1', name='Grade 6A', grade=6, section='A', student_count=30, home_room_id='R1'),
        Class(id='C2', school_id='S1', name='Grade 6B', grade=6, section='B', student_count=30, home_room_id='R2'),
        Class(id='C3', school_id='S1', name='Grade 7A', grade=7, section='A', student_count=30, home_room_id='R3'),
    ]

    subjects = [
        Subject(id='S1', school_id='S1', name='Math', code='MATH', periods_per_week=6, requires_lab=False),
        Subject(id='S2', school_id='S1', name='Science', code='SCI', periods_per_week=5, requires_lab=True),
        Subject(id='S3', school_id='S1', name='English', code='ENG', periods_per_week=5, requires_lab=False),
    ]

    teachers = [
        Teacher(id='T1', user_id='U1', subjects=['S1'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
        Teacher(id='T2', user_id='U2', subjects=['S2'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
        Teacher(id='T3', user_id='U3', subjects=['S3'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
        Teacher(id='T4', user_id='U4', subjects=['S1', 'S3'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
        Teacher(id='T5', user_id='U5', subjects=['S2'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
    ]

    rooms = [
        Room(id='R1', school_id='S1', name='Room 1', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM),
        Room(id='R2', school_id='S1', name='Room 2', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM),
        Room(id='R3', school_id='S1', name='Room 3', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM),
        Room(id='LAB1', school_id='S1', name='Science Lab', building='Main', floor=2, capacity=30, type=RoomType.LAB),
    ]

    time_slots = []
    for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
        for p in range(1, 6):  # 5 periods per day
            time_slots.append(TimeSlot(
                id=f'{day[:3]}_{p}',
                school_id='S1',
                day_of_week=DayOfWeek[day],
                period_number=p,
                start_time=f'{8+p-1}:00',
                end_time=f'{8+p}:00',
                is_break=False
            ))

    print(f"Created: {len(classes)} classes, {len(subjects)} subjects, {len(teachers)} teachers, {len(rooms)} rooms, {len(time_slots)} time slots")
    return classes, subjects, teachers, rooms, time_slots


def generate_medium_dataset():
    """Generate medium test dataset: 10 classes, 5 subjects, 15 teachers"""
    print("\n" + "=" * 70)
    print("GENERATING MEDIUM DATASET")
    print("=" * 70)

    classes = []
    for grade in range(6, 9):  # Grades 6, 7, 8
        for section in ['A', 'B', 'C']:
            idx = (grade - 6) * 3 + ord(section) - ord('A') + 1
            classes.append(Class(
                id=f'C{idx}',
                school_id='S1',
                name=f'Grade {grade}{section}',
                grade=grade,
                section=section,
                student_count=30,
                home_room_id=f'R{idx}'
            ))

    subjects = [
        Subject(id='S1', school_id='S1', name='Math', code='MATH', periods_per_week=6, requires_lab=False),
        Subject(id='S2', school_id='S1', name='Science', code='SCI', periods_per_week=6, requires_lab=True),
        Subject(id='S3', school_id='S1', name='English', code='ENG', periods_per_week=5, requires_lab=False),
        Subject(id='S4', school_id='S1', name='History', code='HIST', periods_per_week=4, requires_lab=False),
        Subject(id='S5', school_id='S1', name='PE', code='PE', periods_per_week=3, requires_lab=False),
    ]

    teachers = []
    for i in range(1, 16):  # 15 teachers
        # Distribute subjects
        if i <= 5:
            subj_ids = ['S1']
        elif i <= 10:
            subj_ids = ['S2']
        else:
            subj_ids = ['S3', 'S4', 'S5']

        teachers.append(Teacher(
            id=f'T{i}',
            user_id=f'U{i}',
            subjects=subj_ids,
            availability={},
            max_periods_per_day=6,
            max_periods_per_week=30,
            max_consecutive_periods=3
        ))

    rooms = []
    for i in range(1, 10):
        rooms.append(Room(id=f'R{i}', school_id='S1', name=f'Room {i}', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM))
    rooms.append(Room(id='LAB1', school_id='S1', name='Science Lab 1', building='Main', floor=2, capacity=30, type=RoomType.LAB))
    rooms.append(Room(id='LAB2', school_id='S1', name='Science Lab 2', building='Main', floor=2, capacity=30, type=RoomType.LAB))

    time_slots = []
    for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
        for p in range(1, 7):  # 6 periods per day
            time_slots.append(TimeSlot(
                id=f'{day[:3]}_{p}',
                school_id='S1',
                day_of_week=DayOfWeek[day],
                period_number=p,
                start_time=f'{8+p-1}:00',
                end_time=f'{8+p}:00',
                is_break=False
            ))

    print(f"Created: {len(classes)} classes, {len(subjects)} subjects, {len(teachers)} teachers, {len(rooms)} rooms, {len(time_slots)} time slots")
    return classes, subjects, teachers, rooms, time_slots


def generate_large_dataset():
    """Generate large test dataset: 20 classes, 8 subjects, 30 teachers"""
    print("\n" + "=" * 70)
    print("GENERATING LARGE DATASET")
    print("=" * 70)

    classes = []
    for grade in range(6, 11):  # Grades 6-10
        for section in ['A', 'B', 'C', 'D']:
            idx = (grade - 6) * 4 + ord(section) - ord('A') + 1
            classes.append(Class(
                id=f'C{idx}',
                school_id='S1',
                name=f'Grade {grade}{section}',
                grade=grade,
                section=section,
                student_count=30,
                home_room_id=f'R{idx}'
            ))

    subjects = [
        Subject(id='S1', school_id='S1', name='Math', code='MATH', periods_per_week=6, requires_lab=False),
        Subject(id='S2', school_id='S1', name='Science', code='SCI', periods_per_week=6, requires_lab=True),
        Subject(id='S3', school_id='S1', name='English', code='ENG', periods_per_week=5, requires_lab=False),
        Subject(id='S4', school_id='S1', name='History', code='HIST', periods_per_week=4, requires_lab=False),
        Subject(id='S5', school_id='S1', name='Geography', code='GEO', periods_per_week=3, requires_lab=False),
        Subject(id='S6', school_id='S1', name='Art', code='ART', periods_per_week=2, requires_lab=False),
        Subject(id='S7', school_id='S1', name='PE', code='PE', periods_per_week=3, requires_lab=False),
        Subject(id='S8', school_id='S1', name='Computer', code='COMP', periods_per_week=3, requires_lab=True),
    ]

    teachers = []
    for i in range(1, 31):  # 30 teachers
        # Distribute subjects
        subj_id = f'S{(i - 1) % 8 + 1}'
        teachers.append(Teacher(
            id=f'T{i}',
            user_id=f'U{i}',
            subjects=[subj_id],
            availability={},
            max_periods_per_day=6,
            max_periods_per_week=30,
            max_consecutive_periods=3
        ))

    rooms = []
    for i in range(1, 21):
        rooms.append(Room(id=f'R{i}', school_id='S1', name=f'Room {i}', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM))
    rooms.append(Room(id='LAB1', school_id='S1', name='Science Lab 1', building='Main', floor=2, capacity=30, type=RoomType.LAB))
    rooms.append(Room(id='LAB2', school_id='S1', name='Science Lab 2', building='Main', floor=2, capacity=30, type=RoomType.LAB))
    rooms.append(Room(id='LAB3', school_id='S1', name='Computer Lab', building='Tech', floor=1, capacity=30, type=RoomType.LAB))

    time_slots = []
    for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
        for p in range(1, 8):  # 7 periods per day
            time_slots.append(TimeSlot(
                id=f'{day[:3]}_{p}',
                school_id='S1',
                day_of_week=DayOfWeek[day],
                period_number=p,
                start_time=f'{8+p-1}:00',
                end_time=f'{8+p}:00',
                is_break=False
            ))

    print(f"Created: {len(classes)} classes, {len(subjects)} subjects, {len(teachers)} teachers, {len(rooms)} rooms, {len(time_slots)} time slots")
    return classes, subjects, teachers, rooms, time_slots


def test_configuration(size_name: str, classes, subjects, teachers, rooms, time_slots):
    """Test validators with a specific configuration"""
    print("\n" + "=" * 70)
    print(f"TESTING {size_name.upper()} CONFIGURATION")
    print("=" * 70)

    # Create request
    request = GenerateRequest(
        school_id='S1',
        academic_year_id='2024-2025',
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        options=1,
        weights=OptimizationWeights()
    )

    # Test 1: PRE-VALIDATION
    print("\n[TEST 1] PRE-VALIDATION")
    print("-" * 70)
    is_valid, pre_result = validate_request(request)

    print(f"Status: {pre_result['status']}")
    print(f"Valid: {is_valid}")

    if pre_result['errors']:
        print(f"\n[X] ERRORS ({len(pre_result['errors'])}):")
        for error in pre_result['errors']:
            print(f"  - {error}")
    else:
        print(f"\n[OK] No errors")

    if pre_result['warnings']:
        print(f"\n[!] WARNINGS ({len(pre_result['warnings'])}):")
        for warning in pre_result['warnings'][:3]:
            print(f"  - {warning}")
        if len(pre_result['warnings']) > 3:
            print(f"  ... and {len(pre_result['warnings']) - 3} more")

    if not is_valid:
        print(f"\n[X] Pre-validation FAILED - skipping generation")
        return False

    # Test 2: GENERATION + POST-VALIDATION
    print("\n[TEST 2] TIMETABLE GENERATION")
    print("-" * 70)

    solver = CSPSolverCompleteV25(debug=False)
    start_time = time.time()

    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        num_solutions=1
    )

    elapsed = time.time() - start_time

    if not timetables:
        print(f"[X] Generation FAILED")
        print(f"  Conflicts: {conflicts}")
        return False

    print(f"[OK] Generated timetable in {elapsed:.2f}s")
    print(f"  Entries: {len(timetables[0].entries)}")

    # Test 3: POST-VALIDATION
    print("\n[TEST 3] POST-VALIDATION")
    print("-" * 70)

    post_result = validate_timetable(
        timetable=timetables[0],
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms
    )

    print(f"Status: {post_result['status']}")
    print(f"Valid: {post_result['is_valid']}")
    print(f"Checks: {post_result['summary']['checks_passed']}/{post_result['summary']['total_checks']} passed")

    # Show individual check results
    print(f"\nCheck Results:")
    for check_name, check_data in post_result['checks'].items():
        status = "[PASS]" if check_data['passed'] else "[FAIL]"
        critical = " [CRITICAL]" if check_data.get('critical') else " [WARNING]"
        print(f"  {status}{critical}: {check_name}")

    if post_result['critical_violations']:
        print(f"\n[X] CRITICAL VIOLATIONS ({len(post_result['critical_violations'])}):")
        for violation in post_result['critical_violations'][:5]:
            print(f"  - {violation}")
        if len(post_result['critical_violations']) > 5:
            print(f"  ... and {len(post_result['critical_violations']) - 5} more")

    if post_result['warnings']:
        print(f"\n[!] WARNINGS ({len(post_result['warnings'])}):")
        for warning in post_result['warnings'][:3]:
            print(f"  - {warning}")
        if len(post_result['warnings']) > 3:
            print(f"  ... and {len(post_result['warnings']) - 3} more")

    # Summary
    print("\n" + "=" * 70)
    if post_result['is_valid']:
        print(f"[PASS] {size_name.upper()} TEST PASSED")
    else:
        print(f"[FAIL] {size_name.upper()} TEST FAILED")
    print("=" * 70)

    return post_result['is_valid']


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("VALIDATOR TESTING - ALL SIZE CONFIGURATIONS")
    print("=" * 70)
    print("\nThis test verifies that pre and post validators work correctly")
    print("across small, medium, and large dataset configurations.\n")

    results = {}

    # Test Small
    classes, subjects, teachers, rooms, time_slots = generate_small_dataset()
    results['small'] = test_configuration('small', classes, subjects, teachers, rooms, time_slots)

    # Test Medium
    classes, subjects, teachers, rooms, time_slots = generate_medium_dataset()
    results['medium'] = test_configuration('medium', classes, subjects, teachers, rooms, time_slots)

    # Test Large
    classes, subjects, teachers, rooms, time_slots = generate_large_dataset()
    results['large'] = test_configuration('large', classes, subjects, teachers, rooms, time_slots)

    # Final Summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    for size, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {size.upper()}")

    all_passed = all(results.values())
    print("\n" + "=" * 70)
    if all_passed:
        print("[PASS] ALL TESTS PASSED")
    else:
        print("[FAIL] SOME TESTS FAILED")
    print("=" * 70 + "\n")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
