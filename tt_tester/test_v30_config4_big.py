#!/usr/bin/env python3
"""
v3.0 Test Configuration 4: BIG SCHOOL (Stress Test)
- 50 classes (LKG to Grade 8, 6-7 sections each)
- 85 teachers (distributed across subjects)
- 12 subjects (English, Math, Hindi, Science, Social, Computer, Physics, Chemistry, Biology, Art, Music, PE)
- 12 shared amenities (4 Computer Labs, 3 Science Labs, 2 Sports Facilities, Library, Art Studio, Music Room)
- Tests v3.0 with high class count and shared room contention
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

def create_big_school_data():
    """Create test data for big school configuration (50 classes)."""
    school_id = "test_school_big"

    # 1. Create Rooms (50 home classrooms + 12 shared amenities)
    rooms = []

    # Home classrooms (50)
    for i in range(1, 51):
        rooms.append(Room(
            id=f"room_home_{i:02d}",
            school_id=school_id,
            name=f"Classroom {i:02d}",
            type=RoomType.CLASSROOM,
            capacity=40,
            facilities=["whiteboard", "projector", "ac"]
        ))

    # Shared amenities (12)
    shared_amenities = [
        # Computer Labs (4)
        ("room_comp_lab1", "Computer Lab 1", RoomType.LAB, 40, ["computers_40", "projector", "ac"]),
        ("room_comp_lab2", "Computer Lab 2", RoomType.LAB, 40, ["computers_40", "smartboard", "ac"]),
        ("room_comp_lab3", "Computer Lab 3", RoomType.LAB, 35, ["computers_35", "projector"]),
        ("room_comp_lab4", "Computer Lab 4", RoomType.LAB, 35, ["computers_35", "smartboard"]),
        # Science Labs (3)
        ("room_sci_lab1", "Physics Lab", RoomType.LAB, 40, ["physics_equipment", "safety_gear"]),
        ("room_sci_lab2", "Chemistry Lab", RoomType.LAB, 40, ["chemistry_equipment", "fume_hood"]),
        ("room_sci_lab3", "Biology Lab", RoomType.LAB, 40, ["microscopes", "specimens", "models"]),
        # Sports & Arts (5)
        ("room_sports1", "Sports Ground", RoomType.SPORTS, 120, ["outdoor", "track", "field"]),
        ("room_sports2", "Indoor Sports Hall", RoomType.SPORTS, 80, ["indoor", "basketball", "badminton"]),
        ("room_library", "Central Library", RoomType.LIBRARY, 80, ["books_10000", "reading_area", "computers"]),
        ("room_art", "Art Studio", RoomType.CLASSROOM, 35, ["art_supplies", "easels", "sink", "storage"]),
        ("room_music", "Music Room", RoomType.CLASSROOM, 35, ["instruments", "soundproof", "recording"]),
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

    # 2. Create Classes (50 classes: LKG to Grade 8)
    classes = []
    grades_config = [
        (0, "LKG", 6),      # 6 sections
        (1, "UKG", 6),      # 6 sections
        (1, "Grade 1", 6),  # 6 sections
        (2, "Grade 2", 6),  # 6 sections
        (3, "Grade 3", 6),  # 6 sections
        (4, "Grade 4", 6),  # 6 sections
        (5, "Grade 5", 6),  # 6 sections
        (6, "Grade 6", 4),  # 4 sections (50 total)
    ]

    sections = ["A", "B", "C", "D", "E", "F", "G"]
    class_index = 0

    for grade_num, grade_name, num_sections in grades_config:
        for i in range(num_sections):
            if class_index >= 50:
                break
            class_index += 1
            section = sections[i]

            classes.append(Class(
                id=f"class_{class_index:02d}",
                school_id=school_id,
                name=f"{grade_name}-{section}",
                grade=grade_num,
                section=section,
                student_count=35 + (class_index % 6),  # 35-40 students
                home_room_id=f"room_home_{class_index:02d}"
            ))

    # 3. Create Subjects (12 subjects with realistic requirements)
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
            name="General Science",
            code="SCI",
            periods_per_week=5,
            requires_lab=True  # Uses science labs
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
            requires_lab=True  # Uses computer labs
        ),
        Subject(
            id="subj_physics",
            school_id=school_id,
            name="Physics",
            code="PHY",
            periods_per_week=4,
            requires_lab=True  # Uses physics lab
        ),
        Subject(
            id="subj_chemistry",
            school_id=school_id,
            name="Chemistry",
            code="CHEM",
            periods_per_week=4,
            requires_lab=True  # Uses chemistry lab
        ),
        Subject(
            id="subj_biology",
            school_id=school_id,
            name="Biology",
            code="BIO",
            periods_per_week=3,
            requires_lab=True  # Uses biology lab
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
    ]

    # 4. Create Teachers (85 teachers distributed across subjects)
    teachers = []
    teacher_distribution = {
        "English": 15,      # 6 periods × 50 classes / 20 periods per teacher = ~15
        "Math": 15,
        "Hindi": 13,
        "Science": 12,
        "Social": 8,
        "Computer": 6,
        "Physics": 5,
        "Chemistry": 5,
        "Biology": 4,
        "Art": 3,
        "Music": 3,
        "PE": 4
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

    # Fill remaining slots to reach 85 teachers
    while teacher_id <= 85:
        teachers.append(Teacher(
            id=f"teacher_t{teacher_id:03d}",
            user_id=f"user_t{teacher_id:03d}",
            name=f"Substitute Teacher {teacher_id}",
            subjects=[],
            max_periods_per_day=6,
            max_periods_per_week=30
        ))
        teacher_id += 1

    # 5. Create Time Slots (5 days × 8 periods = 40 slots)
    time_slots = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    periods = 8

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

def run_v30_test_big():
    """Run v3.0 timetable generation stress test with big school configuration (50 classes)."""
    print("=" * 80)
    print("v3.0 TEST CONFIGURATION 4: BIG SCHOOL (50 CLASSES)")
    print("=" * 80)

    # Get version info
    version_info = get_version_info()
    print(f"\nEngine Version: {version_info['version']} - {version_info['version_name']}")

    # Create test data
    print("\n[1/5] Creating test data...")
    classes, subjects, teachers, time_slots, rooms = create_big_school_data()

    print(f"  ✓ Classes: {len(classes)}")
    print(f"  ✓ Subjects: {len(subjects)}")
    print(f"  ✓ Teachers: {len(teachers)}")
    print(f"  ✓ Time Slots: {len(time_slots)}")
    print(f"  ✓ Rooms: {len(rooms)} (50 home + 12 shared)")

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
    print("\n[4/5] Generating timetable (this may take 2-3 seconds for 50 classes)...")
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
    print(f"  Total assignments: {len(assignments):,}")
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
    csv_filename = f"v30_test_big_{timestamp}.csv"

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
    result = run_v30_test_big()

    if result:
        print("\n" + "=" * 80)
        print("✅ BIG SCHOOL STRESS TEST COMPLETED!")
        print("=" * 80)
        print(f"📄 CSV file: {result['csv_file']}")
        print(f"📊 Total assignments: {result['stats']['total']:,}")
        print(f"⚡ Performance: {result['stats']['assignments_per_second']:.0f} assignments/second")
        print(f"🎯 Quality score: {result['stats']['quality_score']:.2f}")
        print(f"💾 Efficiency: {result['stats']['reduction_pct']:.1f}% reduction in checks")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
