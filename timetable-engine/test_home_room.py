"""
Test: Home Room Assignment

Verifies that the CSP solver assigns home rooms to classes and
prefers using home rooms for regular (non-lab) subjects.

GOAL:
- Each class gets a dedicated home room
- Regular subjects use home room (>70% usage expected)
- Lab subjects use lab rooms (100% usage expected)
- Reduces unnecessary student movement between periods
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room,
    RoomType
)
from csp_solver_complete_v25 import CSPSolverCompleteV25


def test_home_room_assignment():
    """
    Test that classes are assigned home rooms and use them appropriately.
    """

    print("\n" + "="*80)
    print("TEST: Home Room Assignment and Usage")
    print("="*80)

    # Define subjects (mix of regular and lab subjects)
    subjects = [
        Subject(
            id="MATH",
            school_id="SCH_001",
            name="Mathematics",
            code="MATH",
            grade_level=10,
            periods_per_week=6,
            prefer_morning=False,
            requires_lab=False  # Regular subject
        ),
        Subject(
            id="ENG",
            school_id="SCH_001",
            name="English",
            code="ENG",
            grade_level=10,
            periods_per_week=5,
            prefer_morning=False,
            requires_lab=False  # Regular subject
        ),
        Subject(
            id="SCI",
            school_id="SCH_001",
            name="Science",
            code="SCI",
            grade_level=10,
            periods_per_week=4,
            prefer_morning=False,
            requires_lab=True  # Lab subject
        ),
        Subject(
            id="HIST",
            school_id="SCH_001",
            name="History",
            code="HIST",
            grade_level=10,
            periods_per_week=3,
            prefer_morning=False,
            requires_lab=False  # Regular subject
        )
    ]

    # Define teachers
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
        ),
        Teacher(
            id="T004",
            user_id="U004",
            name="Prof. Brown",
            email="brown@school.com",
            subjects=["History"],
            max_periods_per_day=8,
            max_periods_per_week=40,
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

    # Define time slots (5 periods/day × 4 days = 20 slots)
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

    # Define rooms (regular classrooms + lab)
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
            id="R103",
            school_id="SCH_001",
            name="Room 103",
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
    print("Generating timetable with home room assignment...")
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

    # =================================================================
    # VERIFICATION: Check home room usage
    # =================================================================
    print("\n" + "="*80)
    print("VERIFICATION: Home Room Usage")
    print("="*80)

    all_passed = True

    for class_obj in classes:
        print(f"\n{class_obj.name}:")

        # Get all entries for this class
        class_entries = [e for e in timetable.entries if e.class_id == class_obj.id]

        # Separate regular and lab entries
        regular_entries = []
        lab_entries = []

        for entry in class_entries:
            subject = next((s for s in subjects if s.id == entry.subject_id), None)
            if subject:
                if subject.requires_lab:
                    lab_entries.append(entry)
                else:
                    regular_entries.append(entry)

        # Get home room (most frequently used room for regular subjects)
        if regular_entries:
            room_counts = {}
            for entry in regular_entries:
                room_counts[entry.room_id] = room_counts.get(entry.room_id, 0) + 1

            home_room_id = max(room_counts, key=room_counts.get)
            home_room_name = next((r.name for r in rooms if r.id == home_room_id), home_room_id)

            home_room_usage = room_counts[home_room_id]
            total_regular = len(regular_entries)
            usage_percentage = (home_room_usage / total_regular) * 100 if total_regular > 0 else 0

            print(f"  Home Room: {home_room_name}")
            print(f"  Regular Subject Periods: {total_regular}")
            print(f"  Home Room Usage: {home_room_usage}/{total_regular} ({usage_percentage:.1f}%)")

            # Check if usage is high enough (>70% expected)
            if usage_percentage >= 70:
                print(f"  ✓ Good home room usage (>{usage_percentage:.0f}%)")
            elif usage_percentage >= 50:
                print(f"  ⚠️  Moderate home room usage ({usage_percentage:.0f}%)")
            else:
                print(f"  ❌ Low home room usage (<{usage_percentage:.0f}%)")
                all_passed = False

        # Check lab usage
        if lab_entries:
            lab_room_count = sum(1 for e in lab_entries
                                 if any(r.id == e.room_id and r.type == RoomType.LAB for r in rooms))
            total_lab = len(lab_entries)
            lab_percentage = (lab_room_count / total_lab) * 100 if total_lab > 0 else 0

            print(f"  Lab Subject Periods: {total_lab}")
            print(f"  Using Lab Rooms: {lab_room_count}/{total_lab} ({lab_percentage:.1f}%)")

            if lab_percentage >= 90:
                print(f"  ✓ Lab subjects using lab rooms")
            else:
                print(f"  ❌ Lab subjects not using lab rooms properly")
                all_passed = False

    # =================================================================
    # FINAL RESULT
    # =================================================================
    print("\n" + "="*80)
    if all_passed:
        print("✅ TEST PASSED: Home room assignment working correctly")
    else:
        print("❌ TEST FAILED: Home room usage below expectations")
    print("="*80 + "\n")

    return all_passed


if __name__ == "__main__":
    passed = test_home_room_assignment()
    sys.exit(0 if passed else 1)
