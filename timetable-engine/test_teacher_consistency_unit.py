"""
Quick unit test for teacher consistency feature (no service needed)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models_phase1_v25 import Class, Subject, Teacher, TimeSlot, Room, RoomType
from csp_solver_complete_v25 import CSPSolverCompleteV25


def test_basic_scenario():
    """Basic test: 2 classes, 2 subjects, multiple teachers"""

    subjects = [
        Subject(
            id="MATH", school_id="S1", name="Math", code="M",
            grade_level=10, periods_per_week=3, prefer_morning=False, requires_lab=False
        ),
        Subject(
            id="ENG", school_id="S1", name="English", code="E",
            grade_level=10, periods_per_week=2, prefer_morning=False, requires_lab=False
        )
    ]

    teachers = [
        Teacher(id="T1", user_id="U1", name="T1", subjects=["Math"],
                max_periods_per_day=5, max_periods_per_week=20, max_consecutive_periods=3),
        Teacher(id="T2", user_id="U2", name="T2", subjects=["Math"],
                max_periods_per_day=5, max_periods_per_week=20, max_consecutive_periods=3),
        Teacher(id="T3", user_id="U3", name="T3", subjects=["English"],
                max_periods_per_day=5, max_periods_per_week=20, max_consecutive_periods=3)
    ]

    classes = [
        Class(id="C1", school_id="S1", name="C1", grade=10, section="A", student_count=30),
        Class(id="C2", school_id="S1", name="C2", grade=10, section="B", student_count=30)
    ]

    time_slots = [
        TimeSlot(id=f"D{d}_P{p}", school_id="S1", day_of_week=day, period_number=p,
                 start_time=f"{8+p}:00", end_time=f"{8+p}:45", is_break=False)
        for d, day in enumerate(["MONDAY", "TUESDAY"])
        for p in range(1, 4)  # 3 periods per day
    ]

    rooms = [
        Room(id="R1", school_id="S1", name="R1", type=RoomType.CLASSROOM, capacity=40)
    ]

    solver = CSPSolverCompleteV25(debug=False)

    # Test WITH consistency
    timetables, _, _, _ = solver.solve(
        classes=classes, subjects=subjects, teachers=teachers,
        time_slots=time_slots, rooms=rooms, constraints=[],
        num_solutions=1, enforce_teacher_consistency=True
    )

    if not timetables:
        print("❌ FAILED: No timetable generated")
        return False

    tt = timetables[0]

    # Check consistency for each class
    for cls in classes:
        for subj in subjects:
            entries = [e for e in tt.entries if e.class_id == cls.id and e.subject_id == subj.id]
            if not entries:
                continue

            teachers_used = set(e.teacher_id for e in entries)
            if len(teachers_used) != 1:
                print(f"❌ FAILED: {cls.name} {subj.name} has {len(teachers_used)} teachers: {teachers_used}")
                return False

    print("✅ PASSED: All subjects have one teacher per class")
    return True


if __name__ == "__main__":
    success = test_basic_scenario()
    sys.exit(0 if success else 1)
