"""
Test: One Teacher Per Subject Per Class Constraint

Verifies that the CSP solver ensures the same teacher teaches
all periods of a subject to a specific class.

CRITICAL CONSTRAINT:
- If Class 10A has 6 Math periods, ALL 6 should be taught by the same teacher
- Class 10B can have a different Math teacher, but must also be consistent
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint,
    RoomType
)
from csp_solver_complete_v25 import CSPSolverCompleteV25


def test_teacher_consistency():
    """
    Test that one teacher is assigned per subject per class.
    """

    print("\n" + "="*70)
    print("TEST: One Teacher Per Subject Per Class")
    print("="*70)

    # Define subjects
    subjects = [
        Subject(
            id="MATH_10",
            school_id="SCH_001",
            name="Mathematics",
            code="MATH10",
            grade_level=10,
            periods_per_week=6,  # 6 Math periods
            prefer_morning=True,
            requires_lab=False
        ),
        Subject(
            id="ENG_10",
            school_id="SCH_001",
            name="English",
            code="ENG10",
            grade_level=10,
            periods_per_week=5,  # 5 English periods
            prefer_morning=False,
            requires_lab=False
        ),
        Subject(
            id="SCI_10",
            school_id="SCH_001",
            name="Science",
            code="SCI10",
            grade_level=10,
            periods_per_week=4,  # 4 Science periods
            prefer_morning=False,
            requires_lab=True
        )
    ]

    # Define teachers - multiple teachers can teach each subject
    teachers = [
        Teacher(
            id="T001",
            user_id="U001",
            name="Mr. Smith",
            email="smith@school.com",
            subjects=["Mathematics"],
            max_periods_per_day=6,
            max_periods_per_week=30,
            max_consecutive_periods=3
        ),
        Teacher(
            id="T002",
            user_id="U002",
            name="Ms. Johnson",
            email="johnson@school.com",
            subjects=["Mathematics"],  # Also teaches Math
            max_periods_per_day=6,
            max_periods_per_week=30,
            max_consecutive_periods=3
        ),
        Teacher(
            id="T003",
            user_id="U003",
            name="Dr. Williams",
            email="williams@school.com",
            subjects=["English"],
            max_periods_per_day=6,
            max_periods_per_week=30,
            max_consecutive_periods=3
        ),
        Teacher(
            id="T004",
            user_id="U004",
            name="Prof. Brown",
            email="brown@school.com",
            subjects=["Science"],
            max_periods_per_day=6,
            max_periods_per_week=30,
            max_consecutive_periods=3
        )
    ]

    # Define classes
    classes = [
        Class(
            id="10A",
            school_id="SCH_001",
            name="Class 10A",
            grade=10,
            section="A",
            student_count=30
        ),
        Class(
            id="10B",
            school_id="SCH_001",
            name="Class 10B",
            grade=10,
            section="B",
            student_count=28
        )
    ]

    # Define time slots (5 periods/day × 3 days = 15 slots)
    time_slots = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY"]
    for day in days:
        for period in range(1, 6):  # 5 periods per day
            time_slots.append(TimeSlot(
                id=f"{day}_P{period}",
                school_id="SCH_001",
                day_of_week=day,
                period_number=period,
                start_time=f"{8 + period}:00",
                end_time=f"{8 + period}:45",
                is_break=False
            ))

    # Define rooms
    rooms = [
        Room(
            id="R001",
            school_id="SCH_001",
            name="Room 101",
            type=RoomType.CLASSROOM,
            capacity=35
        ),
        Room(
            id="R002",
            school_id="SCH_001",
            name="Lab 201",
            type=RoomType.LAB,
            capacity=30
        )
    ]

    # Initialize solver
    solver = CSPSolverCompleteV25(debug=True)

    # Generate timetables with teacher consistency ENABLED
    print("\n" + "-"*70)
    print("Generating timetable with enforce_teacher_consistency=True")
    print("-"*70)

    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        num_solutions=1,
        enforce_teacher_consistency=True  # ENABLED
    )

    if not timetables:
        print("\n❌ FAILED: Could not generate timetable")
        if conflicts:
            print(f"Conflicts: {conflicts}")
        if suggestions:
            print(f"Suggestions: {suggestions}")
        return False

    timetable = timetables[0]

    print(f"\n✓ Generated timetable with {len(timetable.entries)} entries in {gen_time:.2f}s")

    # =================================================================
    # VERIFICATION: Check teacher consistency
    # =================================================================
    print("\n" + "="*70)
    print("VERIFICATION: Teacher Consistency Check")
    print("="*70)

    all_passed = True

    for class_obj in classes:
        print(f"\n{class_obj.name}:")

        for subject in subjects:
            # Extract all entries for this class-subject combination
            entries = [
                e for e in timetable.entries
                if e.class_id == class_obj.id and e.subject_id == subject.id
            ]

            if not entries:
                print(f"  {subject.name}: No entries (OK if not scheduled)")
                continue

            # Get unique teachers
            unique_teachers = set(e.teacher_id for e in entries)

            # Get teacher names
            teacher_names = [
                next((t.name for t in teachers if t.id == tid), tid)
                for tid in unique_teachers
            ]

            # Check consistency
            if len(unique_teachers) == 1:
                print(f"  ✓ {subject.name}: {len(entries)} periods, "
                      f"1 teacher ({teacher_names[0]})")
            else:
                print(f"  ❌ {subject.name}: {len(entries)} periods, "
                      f"{len(unique_teachers)} teachers: {', '.join(teacher_names)}")
                all_passed = False

                # Show details of inconsistency
                print(f"     DETAILS:")
                for entry in sorted(entries, key=lambda e: (e.day_of_week, e.period_number)):
                    teacher_name = next((t.name for t in teachers if t.id == entry.teacher_id), entry.teacher_id)
                    print(f"       {entry.day_of_week} P{entry.period_number}: {teacher_name}")

    # =================================================================
    # FINAL RESULT
    # =================================================================
    print("\n" + "="*70)
    if all_passed:
        print("✅ TEST PASSED: All subjects have consistent teacher per class")
    else:
        print("❌ TEST FAILED: Found inconsistent teacher assignments")
    print("="*70 + "\n")

    return all_passed


def test_teacher_consistency_disabled():
    """
    Test with enforce_teacher_consistency=False to show it can be disabled.
    """

    print("\n" + "="*70)
    print("TEST: Teacher Consistency DISABLED (for comparison)")
    print("="*70)

    # Simplified test data
    subjects = [
        Subject(
            id="MATH_10",
            school_id="SCH_001",
            name="Mathematics",
            code="MATH10",
            grade_level=10,
            periods_per_week=6,
            prefer_morning=False,
            requires_lab=False
        )
    ]

    teachers = [
        Teacher(
            id="T001",
            user_id="U001",
            name="Mr. Smith",
            email="smith@school.com",
            subjects=["Mathematics"],
            max_periods_per_day=6,
            max_periods_per_week=30,
            max_consecutive_periods=3
        ),
        Teacher(
            id="T002",
            user_id="U002",
            name="Ms. Johnson",
            email="johnson@school.com",
            subjects=["Mathematics"],
            max_periods_per_day=6,
            max_periods_per_week=30,
            max_consecutive_periods=3
        )
    ]

    classes = [
        Class(
            id="10A",
            school_id="SCH_001",
            name="Class 10A",
            grade=10,
            section="A",
            student_count=30
        )
    ]

    time_slots = []
    days = ["MONDAY", "TUESDAY"]
    for day in days:
        for period in range(1, 4):  # 3 periods per day
            time_slots.append(TimeSlot(
                id=f"{day}_P{period}",
                school_id="SCH_001",
                day_of_week=day,
                period_number=period,
                start_time=f"{8 + period}:00",
                end_time=f"{8 + period}:45",
                is_break=False
            ))

    rooms = [
        Room(
            id="R001",
            school_id="SCH_001",
            name="Room 101",
            type=RoomType.CLASSROOM,
            capacity=35
        )
    ]

    solver = CSPSolverCompleteV25(debug=False)

    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        num_solutions=1,
        enforce_teacher_consistency=False  # DISABLED
    )

    if timetables:
        timetable = timetables[0]
        entries = [e for e in timetable.entries if e.subject_id == "MATH_10"]
        unique_teachers = set(e.teacher_id for e in entries)

        print(f"\n✓ With consistency DISABLED:")
        print(f"  Math entries: {len(entries)}")
        print(f"  Unique teachers: {len(unique_teachers)}")
        print(f"  (May have multiple teachers - this is expected when disabled)")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Run main test
    passed = test_teacher_consistency()

    # Run comparison test
    test_teacher_consistency_disabled()

    # Exit with appropriate code
    sys.exit(0 if passed else 1)
