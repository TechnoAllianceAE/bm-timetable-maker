"""
Test: Teacher Consistency Fix v2.5.1

Verifies that the v2.5.1 solver enforces ONE teacher per subject per class.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room,
    RoomType
)
from csp_solver_complete_v25 import CSPSolverCompleteV25


def test_teacher_consistency():
    """
    Test that v2.5.1 enforces one teacher per subject per class.
    """

    print("\n" + "="*80)
    print("TEST: Teacher Consistency v2.5.1")
    print("="*80)

    # Define test data
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

    subjects = [
        Subject(
            id="MATH",
            school_id="SCH_001",
            name="Mathematics",
            code="MATH",
            grade_level=10,
            periods_per_week=6,
            prefer_morning=False,
            requires_lab=False
        ),
        Subject(
            id="ENG",
            school_id="SCH_001",
            name="English",
            code="ENG",
            grade_level=10,
            periods_per_week=5,
            prefer_morning=False,
            requires_lab=False
        ),
        Subject(
            id="SCI",
            school_id="SCH_001",
            name="Science",
            code="SCI",
            grade_level=10,
            periods_per_week=4,
            prefer_morning=False,
            requires_lab=True
        )
    ]

    teachers = [
        Teacher(
            id="T001",
            user_id="U001",
            name="Mr. Smith",
            email="smith@school.com",
            subjects=["Mathematics"],
            max_periods_per_day=8,
            max_periods_per_week=40,
            max_consecutive_periods=3
        ),
        Teacher(
            id="T002",
            user_id="U002",
            name="Ms. Johnson",
            email="johnson@school.com",
            subjects=["English"],
            max_periods_per_day=8,
            max_periods_per_week=40,
            max_consecutive_periods=3
        ),
        Teacher(
            id="T003",
            user_id="U003",
            name="Dr. Williams",
            email="williams@school.com",
            subjects=["Science"],
            max_periods_per_day=8,
            max_periods_per_week=40,
            max_consecutive_periods=3
        )
    ]

    # Create time slots
    time_slots = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"]
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

    # Create rooms
    rooms = [
        Room(
            id="R101",
            school_id="SCH_001",
            name="Room 101",
            type=RoomType.CLASSROOM,
            capacity=35
        ),
        Room(
            id="R102",
            school_id="SCH_001",
            name="Room 102",
            type=RoomType.CLASSROOM,
            capacity=35
        ),
        Room(
            id="LAB_SCI",
            school_id="SCH_001",
            name="Science Lab",
            type=RoomType.LAB,
            capacity=30
        )
    ]

    # Initialize solver
    solver = CSPSolverCompleteV25(debug=True)

    # Generate timetable
    print("\n" + "-"*80)
    print("Generating timetable with v2.5.1 solver...")
    print("-"*80)

    timetables, gen_time, conflicts, suggestions = solver.solve(
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        num_solutions=1,
        enforce_teacher_consistency=True
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

    # Verify teacher consistency
    print("\n" + "="*80)
    print("VERIFICATION: Teacher Consistency")
    print("="*80)

    class_subject_teachers = defaultdict(set)

    for entry in timetable.entries:
        key = (entry.class_id, entry.subject_id)
        class_subject_teachers[key].add(entry.teacher_id)

    violations = 0
    consistent_pairs = 0

    for key, teachers_set in class_subject_teachers.items():
        class_id, subject_id = key
        class_name = next((c.name for c in classes if c.id == class_id), class_id)
        subject_name = next((s.name for s in subjects if s.id == subject_id), subject_id)

        if len(teachers_set) == 1:
            teacher_id = list(teachers_set)[0]
            teacher_name = next((t.name for t in teachers if t.id == teacher_id), teacher_id)
            print(f"  ✅ {class_name} - {subject_name}: {teacher_name}")
            consistent_pairs += 1
        else:
            print(f"  ❌ {class_name} - {subject_name}: {len(teachers_set)} teachers (VIOLATION!)")
            violations += 1

    total_pairs = len(class_subject_teachers)
    consistency_rate = (consistent_pairs / total_pairs * 100) if total_pairs > 0 else 0

    print(f"\n📊 Summary:")
    print(f"  Total (class, subject) pairs: {total_pairs}")
    print(f"  Consistent pairs: {consistent_pairs}/{total_pairs} ({consistency_rate:.1f}%)")
    print(f"  Violations: {violations}")

    print("\n" + "="*80)
    if violations == 0:
        print("✅ TEST PASSED: 100% teacher consistency achieved!")
    else:
        print(f"❌ TEST FAILED: {violations} violations found")
    print("="*80 + "\n")

    return violations == 0


if __name__ == "__main__":
    passed = test_teacher_consistency()
    sys.exit(0 if passed else 1)
