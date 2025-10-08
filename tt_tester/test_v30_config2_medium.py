#!/usr/bin/env python3
"""
v3.0 Test Configuration 2: MEDIUM SCHOOL
- 15 classes (LKG to Grade 3, 3 sections each + G4-A/B/C)
- 25 teachers
- 8 subjects (English, Math, Hindi, Science, Social, Computer, Art, PE)
- 5 shared amenities (2 Computer Labs, Art Room, Sports Field, Library)
- Tests v3.0 with moderate shared room conflicts
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

def create_medium_school_data():
    """Create test data for medium school configuration."""
    school_id = "test_school_medium"

    # 1. Create Rooms (15 home classrooms + 5 shared amenities)
    rooms = []

    # Home classrooms (15)
    for i in range(1, 16):
        rooms.append(Room(
            id=f"room_home_{i}",
            school_id=school_id,
            name=f"Room {i:02d}",
            type=RoomType.CLASSROOM,
            capacity=35,
            facilities=[]
        ))

    # Shared amenities (5)
    shared_amenities = [
        ("room_comp_lab1", "Computer Lab 1", RoomType.LAB, 30, ["computers", "projector"]),
        ("room_comp_lab2", "Computer Lab 2", RoomType.LAB, 30, ["computers", "smartboard"]),
        ("room_art", "Art & Craft Room", RoomType.CLASSROOM, 30, ["art_supplies", "easels"]),
        ("room_sports", "Sports Field", RoomType.SPORTS, 60, ["outdoor", "equipment"]),
        ("room_library", "Library", RoomType.LIBRARY, 50, ["books", "reading_area"]),
    ]

    for room_id, name, room_type, capacity, facilities in shared_amenities:
        rooms.append(Room(
            id=room_id,
            school_id=school_id,
            name=name,
            type=room_type,
            capacity=capacity,
            facilities=facilities
        ))

    # 2. Create Classes (15 classes with home classrooms)
    classes = []
    grades_sections = [
        (0, "LKG", ["A", "B", "C"]),
        (1, "UKG", ["A", "B", "C"]),
        (1, "Grade 1", ["A", "B", "C"]),
        (2, "Grade 2", ["A", "B", "C"]),
        (3, "Grade 3", ["A", "B", "C"]),
    ]

    class_index = 0
    for grade_num, grade_name, sections in grades_sections:
        for section in sections:
            class_index += 1
            classes.append(Class(
                id=f"class_{class_index:02d}",
                school_id=school_id,
                name=f"{grade_name}-{section}",
                grade=grade_num,
                section=section,
                student_count=30 + (class_index % 5),
                home_room_id=f"room_home_{class_index}"
            ))

    # 3. Create Subjects (8 subjects, some require special rooms)
    subjects = [
        Subject(
            id="subj_english",
            school_id=school_id,
            name="English",
            code="ENG",
            periods_per_week=6,
            requires_lab=False,
            requires_sports_facility=False
        ),
        Subject(
            id="subj_math",
            school_id=school_id,
            name="Mathematics",
            code="MATH",
            periods_per_week=6,
            requires_lab=False,
            requires_sports_facility=False
        ),
        Subject(
            id="subj_hindi",
            school_id=school_id,
            name="Hindi",
            code="HIN",
            periods_per_week=4,
            requires_lab=False,
            requires_sports_facility=False
        ),
        Subject(
            id="subj_science",
            school_id=school_id,
            name="Science",
            code="SCI",
            periods_per_week=4,
            requires_lab=False
        ),
        Subject(
            id="subj_social",
            school_id=school_id,
            name="Social Studies",
            code="SST",
            periods_per_week=3,
            requires_lab=False
        ),
        Subject(
            id="subj_computer",
            school_id=school_id,
            name="Computer Science",
            code="CS",
            periods_per_week=2,
            requires_lab=True  # Requires computer lab
        ),
        Subject(
            id="subj_art",
            school_id=school_id,
            name="Art & Craft",
            code="ART",
            periods_per_week=2,
            requires_lab=False
        ),
        Subject(
            id="subj_pe",
            school_id=school_id,
            name="Physical Education",
            code="PE",
            periods_per_week=3,
            requires_lab=False
        ),
    ]

    # 4. Create Teachers (25 teachers)
    teachers = []
    teacher_configs = [
        # English teachers (5)
        ("T001", "Mrs. Sharma", 6), ("T002", "Mr. Kumar", 6), ("T003", "Ms. Patel", 6),
        ("T004", "Mrs. Desai", 6), ("T005", "Mr. Singh", 6),
        # Math teachers (5)
        ("T006", "Ms. Gupta", 6), ("T007", "Mr. Reddy", 6), ("T008", "Mrs. Rao", 6),
        ("T009", "Ms. Mehta", 6), ("T010", "Mr. Joshi", 6),
        # Hindi teachers (3)
        ("T011", "Mrs. Verma", 5), ("T012", "Mr. Chopra", 5), ("T013", "Ms. Malhotra", 5),
        # Science teachers (3)
        ("T014", "Mr. Iyer", 5), ("T015", "Mrs. Nair", 5), ("T016", "Ms. Pillai", 5),
        # Social Studies teachers (2)
        ("T017", "Mr. Khan", 5), ("T018", "Mrs. Bose", 5),
        # Computer teachers (3)
        ("T019", "Mr. Agarwal", 4), ("T020", "Ms. Shah", 4), ("T021", "Mr. Patel", 4),
        # Art teachers (2)
        ("T022", "Mrs. Bhatt", 4), ("T023", "Ms. Trivedi", 4),
        # PE teachers (2)
        ("T024", "Mr. Kapoor", 5), ("T025", "Mrs. Sinha", 5),
    ]

    for code, name, max_periods in teacher_configs:
        teachers.append(Teacher(
            id=f"teacher_{code.lower()}",
            user_id=f"user_{code.lower()}",
            name=name,
            subjects=[],
            max_periods_per_day=max_periods,
            max_periods_per_week=30
        ))

    # 5. Create Time Slots (5 days × 7 periods = 35 slots)
    time_slots = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    periods = 7

    for day in days:
        for period in range(1, periods + 1):
            time_slots.append(TimeSlot(
                id=f"slot_{day.lower()[:3]}_p{period}",
                school_id=school_id,
                day_of_week=day,
                period_number=period,
                start_time=f"{7 + period}:00",
                end_time=f"{8 + period}:00"
            ))

    return classes, subjects, teachers, time_slots, rooms

def run_v30_test_medium():
    """Run v3.0 timetable generation test with medium configuration."""
    print("=" * 80)
    print("v3.0 TEST CONFIGURATION 2: MEDIUM SCHOOL")
    print("=" * 80)

    # Get version info
    version_info = get_version_info()
    print(f"\nEngine Version: {version_info['version']} - {version_info['version_name']}")

    # Create test data
    print("\n[1/5] Creating test data...")
    classes, subjects, teachers, time_slots, rooms = create_medium_school_data()

    print(f"  ✓ Classes: {len(classes)}")
    print(f"  ✓ Subjects: {len(subjects)}")
    print(f"  ✓ Teachers: {len(teachers)}")
    print(f"  ✓ Time Slots: {len(time_slots)}")
    print(f"  ✓ Rooms: {len(rooms)} (15 home + 5 shared)")

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
    csv_filename = f"v30_test_medium_{timestamp}.csv"

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'assignment_id', 'class_name', 'subject_name', 'subject_code', 'teacher_name',
            'day', 'period', 'time', 'room_name', 'room_type', 'is_shared_room',
            'home_classroom', 'uses_home_classroom', 'requires_lab'
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
                'subject_code': subject_obj.code if subject_obj else 'Unknown',
                'teacher_name': teacher_obj.name if teacher_obj else 'Unknown',
                'day': slot_obj.day_of_week if slot_obj else 'Unknown',
                'period': f"P{slot_obj.period_number}" if slot_obj else 'Unknown',
                'time': f"{slot_obj.start_time}-{slot_obj.end_time}" if slot_obj else 'Unknown',
                'room_name': room_obj.name if room_obj else 'Unknown',
                'room_type': room_obj.type.value if room_obj else 'Unknown',
                'is_shared_room': assignment.is_shared_room,
                'home_classroom': next((r.name for r in rooms if r.id == class_obj.home_room_id), 'Unknown') if class_obj else 'Unknown',
                'uses_home_classroom': 'YES' if uses_home else 'NO',
                'requires_lab': 'YES' if (subject_obj and subject_obj.requires_lab) else 'NO'
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

    # Subject-specific analysis
    print(f"\nShared Room Usage by Subject:")
    subject_shared_usage = {}
    for assignment in assignments:
        if assignment.is_shared_room:
            subject_obj = next((s for s in subjects if s.id == assignment.subject_id), None)
            if subject_obj:
                subject_shared_usage[subject_obj.name] = subject_shared_usage.get(subject_obj.name, 0) + 1

    for subject_name, count in sorted(subject_shared_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"  {subject_name}: {count} periods")

    print(f"\nv3.0 Efficiency:")
    print(f"  Total assignments: {len(assignments)}")
    print(f"  Shared room conflicts tracked: {len(shared_rooms)} × {len(time_slots)} = {len(shared_rooms) * len(time_slots)} checks")
    print(f"  v2.5 would track: {len(rooms)} × {len(time_slots)} = {len(rooms) * len(time_slots)} checks")
    reduction = (1 - (len(shared_rooms) * len(time_slots)) / (len(rooms) * len(time_slots))) * 100
    print(f"  Reduction: {reduction:.1f}%")

    return {
        'assignments': assignments,
        'csv_file': csv_filename,
        'stats': {
            'total': len(assignments),
            'home_room': home_room_count,
            'shared_room': shared_room_count,
            'quality_score': quality_score,
            'duration': duration,
            'reduction_pct': reduction
        }
    }

if __name__ == "__main__":
    result = run_v30_test_medium()

    if result:
        print("\n✅ Test completed successfully!")
        print(f"📄 CSV file: {result['csv_file']}")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
