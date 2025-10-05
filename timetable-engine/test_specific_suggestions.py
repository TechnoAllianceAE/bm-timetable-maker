"""
Test to verify that validators generate specific suggestions with class names and grades.
"""

from src.models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room, RoomType, DayOfWeek,
    GenerateRequest, GradeSubjectRequirement
)
from src.validators.pre_validator import validate_request
from src.validators.post_validator import validate_timetable
from src.csp_solver_complete_v25 import CSPSolverCompleteV25


def test_pre_validator_suggestions():
    """Test that pre-validator gives specific suggestions."""
    print("\n" + "=" * 70)
    print("TEST 1: PRE-VALIDATOR SPECIFIC SUGGESTIONS")
    print("=" * 70)

    # Create scenario with missing teacher for Math
    classes = [
        Class(id='C1', school_id='S1', name='Grade 6A', grade=6, section='A', student_count=30),
        Class(id='C2', school_id='S1', name='Grade 6B', grade=6, section='B', student_count=30),
        Class(id='C3', school_id='S1', name='Grade 7A', grade=7, section='A', student_count=30),
    ]

    subjects = [
        Subject(id='MATH', school_id='S1', name='Mathematics', code='MATH', periods_per_week=5, requires_lab=False),
        Subject(id='SCI', school_id='S1', name='Science', code='SCI', periods_per_week=4, requires_lab=True),
        Subject(id='ENG', school_id='S1', name='English', code='ENG', periods_per_week=4, requires_lab=False),
    ]

    # No teacher for Mathematics!
    teachers = [
        Teacher(id='T1', user_id='U1', subjects=['SCI'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
        Teacher(id='T2', user_id='U2', subjects=['ENG'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
    ]

    rooms = [
        Room(id='R1', school_id='S1', name='Room 1', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM),
        # No LAB room!
    ]

    time_slots = []
    for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY']:
        for p in range(1, 6):
            time_slots.append(TimeSlot(
                id=f'{day[:3]}_{p}',
                school_id='S1',
                day_of_week=DayOfWeek[day],
                period_number=p,
                start_time=f'{8+p-1}:00',
                end_time=f'{8+p}:00',
                is_break=False
            ))

    request = GenerateRequest(
        school_id='S1',
        academic_year_id='AY1',
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        subject_requirements=[]
    )

    is_valid, result = validate_request(request)

    print(f"\nValidation Status: {result['status']}")
    print(f"Is Valid: {result['is_valid']}")

    print("\nErrors:")
    for error in result['errors']:
        print(f"  - {error}")

    print("\nSuggestions (should be specific):")
    for suggestion in result['suggestions']:
        print(f"  - {suggestion}")

    # Check if suggestions mention specific subjects
    has_math_suggestion = any('Mathematics' in s for s in result['suggestions'])
    has_sci_suggestion = any('Science' in s for s in result['suggestions'])

    print(f"\n[{'PASS' if has_math_suggestion else 'FAIL'}] Suggestions mention Mathematics")
    print(f"[{'PASS' if has_sci_suggestion else 'FAIL'}] Suggestions mention Science (for lab)")

    return has_math_suggestion and has_sci_suggestion


def test_post_validator_suggestions():
    """Test that post-validator gives specific suggestions with class names."""
    print("\n" + "=" * 70)
    print("TEST 2: POST-VALIDATOR SPECIFIC SUGGESTIONS")
    print("=" * 70)

    # Create a timetable that will have some violations
    classes = [
        Class(id='C1', school_id='S1', name='Grade 6A', grade=6, section='A', student_count=30, home_room_id='R1'),
        Class(id='C2', school_id='S1', name='Grade 6B', grade=6, section='B', student_count=30, home_room_id='R2'),
        Class(id='C3', school_id='S1', name='Grade 7A', grade=7, section='A', student_count=30, home_room_id='R3'),
    ]

    subjects = [
        Subject(id='MATH', school_id='S1', name='Mathematics', code='MATH', periods_per_week=5, requires_lab=False),
        Subject(id='SCI', school_id='S1', name='Science', code='SCI', periods_per_week=4, requires_lab=True),
        Subject(id='ENG', school_id='S1', name='English', code='ENG', periods_per_week=4, requires_lab=False),
    ]

    teachers = [
        Teacher(id='T1', user_id='U1', subjects=['MATH'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
        Teacher(id='T2', user_id='U2', subjects=['SCI'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
        Teacher(id='T3', user_id='U3', subjects=['ENG'], availability={}, max_periods_per_day=6, max_periods_per_week=30, max_consecutive_periods=3),
    ]

    rooms = [
        Room(id='R1', school_id='S1', name='Room 1', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM),
        Room(id='R2', school_id='S1', name='Room 2', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM),
        Room(id='R3', school_id='S1', name='Room 3', building='Main', floor=1, capacity=40, type=RoomType.CLASSROOM),
        Room(id='LAB1', school_id='S1', name='Science Lab', building='Main', floor=2, capacity=30, type=RoomType.LAB),
    ]

    time_slots = []
    for day in ['MONDAY', 'TUESDAY']:
        for p in range(1, 6):
            time_slots.append(TimeSlot(
                id=f'{day[:3]}_{p}',
                school_id='S1',
                day_of_week=DayOfWeek[day],
                period_number=p,
                start_time=f'{8+p-1}:00',
                end_time=f'{8+p}:00',
                is_break=False
            ))

    # Generate timetable
    solver = CSPSolverCompleteV25(debug=False)
    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes, subjects, teachers, time_slots, rooms, [], 1
    )

    if not timetables:
        print("[FAIL] No timetable generated")
        return False

    # Validate
    post_result = validate_timetable(
        timetable=timetables[0],
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        subject_requirements=[]
    )

    print(f"\nValidation Status: {post_result['status']}")
    print(f"Is Valid: {post_result['is_valid']}")
    print(f"Checks: {post_result['summary']['checks_passed']}/{post_result['summary']['total_checks']} passed")

    print("\nWarnings:")
    for warning in post_result['warnings'][:5]:  # Show first 5
        print(f"  - {warning}")
    if len(post_result['warnings']) > 5:
        print(f"  ... and {len(post_result['warnings']) - 5} more")

    print("\nSuggestions (should mention specific classes):")
    for suggestion in post_result['suggestions']:
        print(f"  - {suggestion}")

    # Check if suggestions are specific
    has_class_names = any(any(cls.name in s for cls in classes) for s in post_result['suggestions'])
    has_subject_names = any(any(subj.name in s for subj in subjects) for s in post_result['suggestions'])

    print(f"\n[{'PASS' if has_class_names else 'FAIL'}] Suggestions mention specific class names")
    print(f"[{'PASS' if has_subject_names else 'FAIL'}] Suggestions mention specific subject names")

    return has_class_names or has_subject_names


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SPECIFIC SUGGESTIONS TEST SUITE")
    print("=" * 70)
    print("\nVerifying that validators provide actionable suggestions")
    print("with specific class names, grades, and subjects.")

    test1_passed = test_pre_validator_suggestions()
    test2_passed = test_post_validator_suggestions()

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"[{'PASS' if test1_passed else 'FAIL'}] Pre-validator specific suggestions")
    print(f"[{'PASS' if test2_passed else 'FAIL'}] Post-validator specific suggestions")

    if test1_passed and test2_passed:
        print("\n[PASS] ALL TESTS PASSED - Suggestions are specific and actionable")
    else:
        print("\n[FAIL] SOME TESTS FAILED")
