#!/usr/bin/env python3
"""
v3.0 Test Configuration 1: SMALL SCHOOL
- 5 classes (LKG, UKG, G1-A/B/C)
- 10 teachers
- 5 subjects (English, Math, Hindi, EVS, Art)
- 2 shared amenities (Art Room, Library)
- Tests basic v3.0 room allocation with minimal shared rooms
"""

import sys
import os
import json
import csv
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'timetable-engine'))

from src.models_phase1_v30 import (
    Class, Subject, Teacher, TimeSlot, Room, RoomType,
    V30Validator, get_version_info
)
from src.csp_solver_complete_v30 import CSPSolverCompleteV30

def generate_cuid():
    """Generate a simple ID for testing."""
    import random
    import string
    return 'test_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def create_small_school_data():
    """Create test data for small school configuration."""
    school_id = "test_school_small"

    # 1. Create Rooms (5 home classrooms + 2 shared amenities)
    rooms = []

    # Home classrooms
    for i in range(1, 6):
        rooms.append(Room(
            id=f"room_home_{i}",
            school_id=school_id,
            name=f"Classroom {i}",
            type=RoomType.CLASSROOM,
            capacity=30,
            facilities=[]
        ))

    # Shared amenities
    rooms.append(Room(
        id="room_art",
        school_id=school_id,
        name="Art Room",
        type=RoomType.CLASSROOM,  # Art uses classroom type
        capacity=25,
        facilities=["art_supplies", "easels"]
    ))

    rooms.append(Room(
        id="room_library",
        school_id=school_id,
        name="Library",
        type=RoomType.LIBRARY,
        capacity=50,
        facilities=["books", "reading_area"]
    ))

    # 2. Create Classes (5 classes with home classrooms assigned)
    classes = [
        Class(
            id="class_lkg",
            school_id=school_id,
            name="LKG",
            grade=0,
            section="A",
            student_count=25,
            home_room_id="room_home_1"
        ),
        Class(
            id="class_ukg",
            school_id=school_id,
            name="UKG",
            grade=1,
            section="A",
            student_count=28,
            home_room_id="room_home_2"
        ),
        Class(
            id="class_g1a",
            school_id=school_id,
            name="Grade 1-A",
            grade=1,
            section="A",
            student_count=30,
            home_room_id="room_home_3"
        ),
        Class(
            id="class_g1b",
            school_id=school_id,
            name="Grade 1-B",
            grade=1,
            section="B",
            student_count=28,
            home_room_id="room_home_4"
        ),
        Class(
            id="class_g1c",
            school_id=school_id,
            name="Grade 1-C",
            grade=1,
            section="C",
            student_count=27,
            home_room_id="room_home_5"
        ),
    ]

    # 3. Create Subjects (5 subjects, Art requires special room)
    subjects = [
        Subject(
            id="subj_english",
            school_id=school_id,
            name="English",
            code="ENG",
            periods_per_week=5,
            requires_lab=False,
            requires_sports_facility=False
        ),
        Subject(
            id="subj_math",
            school_id=school_id,
            name="Mathematics",
            code="MATH",
            periods_per_week=5,
            requires_lab=False,
            requires_sports_facility=False
        ),
        Subject(
            id="subj_hindi",
            school_id=school_id,
            name="Hindi",
            code="HIN",
            periods_per_week=3,
            requires_lab=False,
            requires_sports_facility=False
        ),
        Subject(
            id="subj_evs",
            school_id=school_id,
            name="EVS",
            code="EVS",
            periods_per_week=3,
            requires_lab=False,
            requires_sports_facility=False
        ),
        Subject(
            id="subj_art",
            school_id=school_id,
            name="Art & Craft",
            code="ART",
            periods_per_week=2,
            requires_lab=False,
            requires_sports_facility=False,
            subject_metadata={"prefer_morning": False, "requires_special_room": True}
        ),
    ]

    # 4. Create Teachers (10 teachers)
    teachers = []
    teacher_configs = [
        ("T001", "Mrs. Sharma", "English"),
        ("T002", "Mr. Kumar", "English"),
        ("T003", "Ms. Patel", "Mathematics"),
        ("T004", "Mr. Singh", "Mathematics"),
        ("T005", "Mrs. Gupta", "Hindi"),
        ("T006", "Ms. Verma", "Hindi"),
        ("T007", "Mr. Reddy", "EVS"),
        ("T008", "Mrs. Rao", "EVS"),
        ("T009", "Ms. Desai", "Art & Craft"),
        ("T010", "Mr. Joshi", "Physical Education"),
    ]

    for code, name, subject in teacher_configs:
        teachers.append(Teacher(
            id=f"teacher_{code.lower()}",
            user_id=f"user_{code.lower()}",
            name=name,
            subjects=[],
            max_periods_per_day=6,
            max_periods_per_week=30
        ))

    # 5. Create Time Slots (5 days × 5 periods = 25 slots)
    time_slots = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    periods = ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5"]

    for day in days:
        for period in periods:
            time_slots.append(TimeSlot(
                id=f"slot_{day.lower()[:3]}_{period.replace(' ', '').lower()}",
                school_id=school_id,
                day_of_week=day,
                period_number=periods.index(period) + 1,
                start_time=f"{8 + periods.index(period)}:00",
                end_time=f"{9 + periods.index(period)}:00"
            ))

    return classes, subjects, teachers, time_slots, rooms

def run_v30_test_small():
    """Run v3.0 timetable generation test with small configuration."""
    print("=" * 80)
    print("v3.0 TEST CONFIGURATION 1: SMALL SCHOOL")
    print("=" * 80)

    # Get version info
    version_info = get_version_info()
    print(f"\nEngine Version: {version_info['version']} - {version_info['version_name']}")

    # Create test data
    print("\n[1/5] Creating test data...")
    classes, subjects, teachers, time_slots, rooms = create_small_school_data()

    print(f"  ✓ Classes: {len(classes)}")
    print(f"  ✓ Subjects: {len(subjects)}")
    print(f"  ✓ Teachers: {len(teachers)}")
    print(f"  ✓ Time Slots: {len(time_slots)}")
    print(f"  ✓ Rooms: {len(rooms)} (5 home + 2 shared)")

    # Validate home classrooms
    print("\n[2/5] Validating v3.0 requirements...")
    is_valid, errors = V30Validator.validate_home_classrooms_assigned(classes)
    if not is_valid:
        print("  ✗ Home classroom validation FAILED:")
        for error in errors:
            print(f"    - {error}")
        return None
    print("  ✓ All classes have home classrooms assigned")

    # Extract shared rooms
    shared_rooms = V30Validator.extract_shared_rooms(rooms)
    print(f"  ✓ Shared amenities identified: {len(shared_rooms)}")
    for sr in shared_rooms:
        print(f"    - {sr.name} ({sr.type.value})")

    # Initialize solver
    print("\n[3/5] Initializing CSP Solver v3.0...")
    solver = CSPSolverCompleteV30(debug=False)

    # Generate timetable
    print("\n[4/5] Generating timetable...")
    start_time = datetime.now()

    timetables, quality_score, errors, warnings = solver.solve(
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        time_slots=time_slots,
        rooms=rooms,
        constraints=[],
        subject_requirements={}
    )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Extract all assignments from timetables
    assignments = []
    if timetables:
        for tt in timetables:
            assignments.extend(tt.entries)

    print(f"\n  Generation completed in {duration:.2f} seconds")
    print(f"  Timetables generated: {len(timetables)}")
    print(f"  Total assignments: {len(assignments)}")
    print(f"  Quality score: {quality_score:.2f}")

    if errors:
        print(f"\n  ✗ Errors: {len(errors)}")
        for error in errors[:5]:
            print(f"    - {error}")

    if warnings:
        print(f"\n  ⚠ Warnings: {len(warnings)}")
        for warning in warnings[:5]:
            print(f"    - {warning}")

    # Export to CSV
    print("\n[5/5] Exporting results to CSV...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"v30_test_small_{timestamp}.csv"

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'assignment_id', 'class_name', 'subject_name', 'teacher_name',
            'day', 'period', 'time', 'room_name', 'room_type', 'is_shared_room',
            'home_classroom', 'uses_home_classroom'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for assignment in assignments:
            # Find related objects
            class_obj = next((c for c in classes if c.id == assignment.class_id), None)
            subject_obj = next((s for s in subjects if s.id == assignment.subject_id), None)
            teacher_obj = next((t for t in teachers if t.id == assignment.teacher_id), None)
            slot_obj = next((ts for ts in time_slots if ts.id == assignment.time_slot_id), None)
            room_obj = next((r for r in rooms if r.id == assignment.room_id), None)

            uses_home = room_obj.id == class_obj.home_room_id if (room_obj and class_obj) else False

            writer.writerow({
                'assignment_id': assignment.id,
                'class_name': class_obj.name if class_obj else 'Unknown',
                'subject_name': subject_obj.name if subject_obj else 'Unknown',
                'teacher_name': teacher_obj.name if teacher_obj else 'Unknown',
                'day': slot_obj.day_of_week if slot_obj else 'Unknown',
                'period': f"Period {slot_obj.period_number}" if slot_obj else 'Unknown',
                'time': f"{slot_obj.start_time}-{slot_obj.end_time}" if slot_obj else 'Unknown',
                'room_name': room_obj.name if room_obj else 'Unknown',
                'room_type': room_obj.type.value if room_obj else 'Unknown',
                'is_shared_room': assignment.is_shared_room,
                'home_classroom': next((r.name for r in rooms if r.id == class_obj.home_room_id), 'Unknown') if class_obj else 'Unknown',
                'uses_home_classroom': 'YES' if uses_home else 'NO'
            })

    print(f"  ✓ Results exported to: {csv_filename}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    shared_room_count = sum(1 for a in assignments if a.is_shared_room)
    home_room_count = len(assignments) - shared_room_count

    print(f"\nRoom Allocation Breakdown:")
    print(f"  Home classroom usage: {home_room_count} ({home_room_count/len(assignments)*100:.1f}%)")
    print(f"  Shared amenity usage: {shared_room_count} ({shared_room_count/len(assignments)*100:.1f}%)")

    print(f"\nv3.0 Efficiency:")
    print(f"  Total assignments: {len(assignments)}")
    print(f"  Shared room conflicts tracked: {len(shared_rooms)} × {len(time_slots)} = {len(shared_rooms) * len(time_slots)} checks")
    print(f"  v2.5 would track: {len(rooms)} × {len(time_slots)} = {len(rooms) * len(time_slots)} checks")
    print(f"  Reduction: {(1 - (len(shared_rooms) * len(time_slots)) / (len(rooms) * len(time_slots))) * 100:.1f}%")

    return {
        'assignments': assignments,
        'csv_file': csv_filename,
        'stats': {
            'total': len(assignments),
            'home_room': home_room_count,
            'shared_room': shared_room_count,
            'quality_score': quality_score,
            'duration': duration
        }
    }

if __name__ == "__main__":
    result = run_v30_test_small()

    if result:
        print("\n✅ Test completed successfully!")
        print(f"📄 CSV file: {result['csv_file']}")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
