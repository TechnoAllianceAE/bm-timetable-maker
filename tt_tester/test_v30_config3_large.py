#!/usr/bin/env python3
"""
v3.0 Test Configuration 3: LARGE SCHOOL (Stress Test)
- 30 classes (LKG to Grade 5, 5 sections each)
- 50 teachers
- 10 subjects (English, Math, Hindi, Science, Social, Computer, Art, Music, PE, Library)
- 8 shared amenities (3 Computer Labs, 2 Science Labs, Art Room, Music Room, Sports Complex)
- Tests v3.0 with high shared room contention
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

def create_large_school_data():
    """Create test data for large school configuration."""
    school_id = "test_school_large"

    # 1. Create Rooms (30 home classrooms + 8 shared amenities)
    rooms = []

    # Home classrooms (30)
    for i in range(1, 31):
        rooms.append(Room(
            id=f"room_home_{i:02d}",
            school_id=school_id,
            name=f"Classroom {i:02d}",
            type=RoomType.CLASSROOM,
            capacity=35,
            facilities=["whiteboard", "projector"]
        ))

    # Shared amenities (8)
    shared_amenities = [
        ("room_comp_lab1", "Computer Lab 1", RoomType.LAB, 35, ["computers_30", "projector", "ac"]),
        ("room_comp_lab2", "Computer Lab 2", RoomType.LAB, 35, ["computers_30", "smartboard", "ac"]),
        ("room_comp_lab3", "Computer Lab 3", RoomType.LAB, 30, ["computers_25", "projector"]),
        ("room_sci_lab1", "Science Lab 1", RoomType.LAB, 35, ["lab_equipment", "safety_gear"]),
        ("room_sci_lab2", "Science Lab 2", RoomType.LAB, 35, ["lab_equipment", "microscopes"]),
        ("room_art", "Art Studio", RoomType.CLASSROOM, 30, ["art_supplies", "easels", "sink"]),
        ("room_music", "Music Room", RoomType.CLASSROOM, 30, ["instruments", "soundproof"]),
        ("room_sports", "Sports Complex", RoomType.SPORTS, 100, ["indoor_outdoor", "equipment_room"]),
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

    # 2. Create Classes (30 classes: LKG to Grade 5, 5 sections each)
    classes = []
    grades_config = [
        (0, "LKG"),
        (1, "UKG"),
        (1, "Grade 1"),
        (2, "Grade 2"),
        (3, "Grade 3"),
        (4, "Grade 4"),
        (5, "Grade 5"),
    ]
    sections = ["A", "B", "C", "D", "E"]

    class_index = 0
    for grade_num, grade_name in grades_config:
        for section in sections:
            if class_index >= 30:  # Limit to 30 classes
                break
            class_index += 1
            classes.append(Class(
                id=f"class_{class_index:02d}",
                school_id=school_id,
                name=f"{grade_name}-{section}",
                grade=grade_num,
                section=section,
                student_count=28 + (class_index % 7),  # 28-34 students
                home_room_id=f"room_home_{class_index:02d}"
            ))

    # 3. Create Subjects (10 subjects with varied requirements)
    subjects = [
        Subject(
            id="subj_english",
            school_id=school_id,
            name="English",
            code="ENG",
            periods_per_week=6,
            requires_lab=False
        ),
        Subject(
            id="subj_math",
            school_id=school_id,
            name="Mathematics",
            code="MATH",
            periods_per_week=6,
            requires_lab=False
        ),
        Subject(
            id="subj_hindi",
            school_id=school_id,
            name="Hindi",
            code="HIN",
            periods_per_week=5,
            requires_lab=False
        ),
        Subject(
            id="subj_science",
            school_id=school_id,
            name="Science",
            code="SCI",
            periods_per_week=5,
            requires_lab=True  # Requires science lab
        ),
        Subject(
            id="subj_social",
            school_id=school_id,
            name="Social Studies",
            code="SST",
            periods_per_week=4,
            requires_lab=False
        ),
        Subject(
            id="subj_computer",
            school_id=school_id,
            name="Computer Science",
            code="CS",
            periods_per_week=3,
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
            id="subj_music",
            school_id=school_id,
            name="Music",
            code="MUS",
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
        Subject(
            id="subj_library",
            school_id=school_id,
            name="Library Period",
            code="LIB",
            periods_per_week=1,
            requires_lab=False
        ),
    ]

    # 4. Create Teachers (50 teachers distributed across subjects)
    teachers = []
    teacher_distribution = {
        "English": 10,
        "Math": 10,
        "Hindi": 8,
        "Science": 7,
        "Social": 5,
        "Computer": 4,
        "Art": 2,
        "Music": 2,
        "PE": 2
    }

    teacher_id = 1
    for subject, count in teacher_distribution.items():
        for i in range(count):
            teachers.append(Teacher(
                id=f"teacher_t{teacher_id:03d}",
                user_id=f"user_t{teacher_id:03d}",
                name=f"{subject} Teacher {i+1}",
                subjects=[],
                max_periods_per_day=6,
                max_periods_per_week=30
            ))
            teacher_id += 1

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

def run_v30_test_large():
    """Run v3.0 timetable generation stress test with large configuration."""
    print("=" * 80)
    print("v3.0 TEST CONFIGURATION 3: LARGE SCHOOL (STRESS TEST)")
    print("=" * 80)

    # Get version info
    version_info = get_version_info()
    print(f"\nEngine Version: {version_info['version']} - {version_info['version_name']}")

    # Create test data
    print("\n[1/5] Creating test data...")
    classes, subjects, teachers, time_slots, rooms = create_large_school_data()

    print(f"  ✓ Classes: {len(classes)}")
    print(f"  ✓ Subjects: {len(subjects)}")
    print(f"  ✓ Teachers: {len(teachers)}")
    print(f"  ✓ Time Slots: {len(time_slots)}")
    print(f"  ✓ Rooms: {len(rooms)} (30 home + 8 shared)")

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
        print(f"    - {sr.name} ({sr.type.value}, capacity: {sr.capacity})")

    # Initialize solver
    print("\n[3/5] Initializing CSP Solver v3.0...")
    solver = CSPSolverCompleteV30(debug=False)

    # Generate timetable
    print("\n[4/5] Generating timetable (this may take longer for large schools)...")
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
        for i, error in enumerate(errors[:10]):
            print(f"    {i+1}. {error}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more errors")

    if warnings:
        print(f"\n  ⚠ Warnings: {len(warnings)}")
        for i, warning in enumerate(warnings[:10]):
            print(f"    {i+1}. {warning}")
        if len(warnings) > 10:
            print(f"    ... and {len(warnings) - 10} more warnings")

    # Export to CSV
    print("\n[5/5] Exporting results to CSV...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"v30_test_large_{timestamp}.csv"

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'assignment_id', 'class_name', 'class_grade', 'subject_name', 'subject_code',
            'teacher_name', 'day', 'period', 'time',
            'room_name', 'room_type', 'room_capacity', 'is_shared_room',
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
                'class_grade': class_obj.grade if class_obj else 'Unknown',
                'subject_name': subject_obj.name if subject_obj else 'Unknown',
                'subject_code': subject_obj.code if subject_obj else 'Unknown',
                'teacher_name': teacher_obj.name if teacher_obj else 'Unknown',
                'day': slot_obj.day_of_week if slot_obj else 'Unknown',
                'period': f"P{slot_obj.period_number}" if slot_obj else 'Unknown',
                'time': f"{slot_obj.start_time}-{slot_obj.end_time}" if slot_obj else 'Unknown',
                'room_name': room_obj.name if room_obj else 'Unknown',
                'room_type': room_obj.type.value if room_obj else 'Unknown',
                'room_capacity': room_obj.capacity if room_obj else 'Unknown',
                'is_shared_room': 'YES' if assignment.is_shared_room else 'NO',
                'home_classroom': next((r.name for r in rooms if r.id == class_obj.home_room_id), 'Unknown') if class_obj else 'Unknown',
                'uses_home_classroom': 'YES' if uses_home else 'NO',
                'requires_lab': 'YES' if (subject_obj and subject_obj.requires_lab) else 'NO'
            })

    print(f"  ✓ Results exported to: {csv_filename}")

    # Detailed Summary Statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    shared_room_count = sum(1 for a in assignments if a.is_shared_room)
    home_room_count = len(assignments) - shared_room_count

    print(f"\nRoom Allocation Breakdown:")
    print(f"  Home classroom usage: {home_room_count:,} assignments ({home_room_count/len(assignments)*100:.1f}%)")
    print(f"  Shared amenity usage: {shared_room_count:,} assignments ({shared_room_count/len(assignments)*100:.1f}%)")

    # Shared room utilization
    print(f"\nShared Room Utilization:")
    shared_room_usage = {}
    for assignment in assignments:
        if assignment.is_shared_room:
            room_obj = next((r for r in rooms if r.id == assignment.room_id), None)
            if room_obj:
                shared_room_usage[room_obj.name] = shared_room_usage.get(room_obj.name, 0) + 1

    for room_name, count in sorted(shared_room_usage.items(), key=lambda x: x[1], reverse=True):
        utilization_pct = (count / len(time_slots)) * 100
        print(f"  {room_name}: {count}/{len(time_slots)} slots ({utilization_pct:.1f}% utilized)")

    # Subject-specific analysis
    print(f"\nSubject Distribution:")
    subject_counts = {}
    for assignment in assignments:
        subject_obj = next((s for s in subjects if s.id == assignment.subject_id), None)
        if subject_obj:
            subject_counts[subject_obj.name] = subject_counts.get(subject_obj.name, 0) + 1

    for subject_name, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {subject_name}: {count} periods")

    print(f"\nv3.0 Performance Metrics:")
    print(f"  Total assignments: {len(assignments):,}")
    print(f"  Generation time: {duration:.2f} seconds")
    print(f"  Assignments per second: {len(assignments)/duration:.0f}")
    print(f"\nv3.0 Efficiency Gains:")
    print(f"  Shared room conflicts tracked: {len(shared_rooms)} × {len(time_slots)} = {len(shared_rooms) * len(time_slots):,} checks")
    print(f"  v2.5 would track: {len(rooms)} × {len(time_slots)} = {len(rooms) * len(time_slots):,} checks")
    reduction = (1 - (len(shared_rooms) * len(time_slots)) / (len(rooms) * len(time_slots))) * 100
    print(f"  Reduction: {reduction:.1f}%")
    print(f"  Checks saved: {(len(rooms) - len(shared_rooms)) * len(time_slots):,}")

    return {
        'assignments': assignments,
        'csv_file': csv_filename,
        'stats': {
            'total': len(assignments),
            'home_room': home_room_count,
            'shared_room': shared_room_count,
            'quality_score': quality_score,
            'duration': duration,
            'assignments_per_second': len(assignments) / duration if duration > 0 else 0,
            'reduction_pct': reduction,
            'shared_room_usage': shared_room_usage
        }
    }

if __name__ == "__main__":
    result = run_v30_test_large()

    if result:
        print("\n" + "=" * 80)
        print("✅ STRESS TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"📄 CSV file: {result['csv_file']}")
        print(f"📊 Total assignments: {result['stats']['total']:,}")
        print(f"⚡ Performance: {result['stats']['assignments_per_second']:.0f} assignments/second")
        print(f"🎯 Quality score: {result['stats']['quality_score']:.2f}")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
