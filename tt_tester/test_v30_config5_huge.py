#!/usr/bin/env python3
"""
v3.0 Test Configuration 5: HUGE SCHOOL (Maximum Stress Test)
- 80 classes (LKG to Grade 12, 8 sections each for primary, 4-8 for secondary)
- 140 teachers (distributed across all subjects)
- 15 subjects (complete K-12 curriculum)
- 18 shared amenities (5 Computer Labs, 4 Science Labs, 3 Sports Facilities, 2 Libraries, Art, Music, Auditorium, Cafeteria)
- Tests v3.0 at maximum enterprise scale
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

def create_huge_school_data():
    """Create test data for huge school configuration (80 classes)."""
    school_id = "test_school_huge"

    # 1. Create Rooms (80 home classrooms + 18 shared amenities)
    rooms = []

    # Home classrooms (80)
    for i in range(1, 81):
        # Different floors/wings for organization
        floor = ((i - 1) // 20) + 1
        wing = chr(65 + ((i - 1) % 4))  # A, B, C, D wings

        rooms.append(Room(
            id=f"room_home_{i:03d}",
            school_id=school_id,
            name=f"Room {floor}{wing}{i:02d}",
            type=RoomType.CLASSROOM,
            capacity=40,
            facilities=["whiteboard", "projector", "ac", "smart_board"]
        ))

    # Shared amenities (18)
    shared_amenities = [
        # Computer Labs (5)
        ("room_comp_lab1", "Computer Lab - Block A", RoomType.LAB, 45, ["computers_45", "projector", "ac", "server"]),
        ("room_comp_lab2", "Computer Lab - Block B", RoomType.LAB, 45, ["computers_45", "smartboard", "ac"]),
        ("room_comp_lab3", "Computer Lab - Block C", RoomType.LAB, 40, ["computers_40", "projector", "ac"]),
        ("room_comp_lab4", "Computer Lab - Block D", RoomType.LAB, 40, ["computers_40", "smartboard"]),
        ("room_comp_lab5", "Advanced Computing Lab", RoomType.LAB, 35, ["computers_35", "high_end", "coding_lab"]),
        # Science Labs (4)
        ("room_sci_lab1", "Physics Lab", RoomType.LAB, 45, ["physics_equipment", "safety_gear", "storage"]),
        ("room_sci_lab2", "Chemistry Lab", RoomType.LAB, 45, ["chemistry_equipment", "fume_hood", "safety"]),
        ("room_sci_lab3", "Biology Lab", RoomType.LAB, 45, ["microscopes", "specimens", "models", "dissection"]),
        ("room_sci_lab4", "Integrated Science Lab", RoomType.LAB, 40, ["multi_discipline", "digital_tools"]),
        # Sports Facilities (3)
        ("room_sports1", "Main Sports Ground", RoomType.SPORTS, 150, ["outdoor", "track", "field", "cricket"]),
        ("room_sports2", "Indoor Sports Complex", RoomType.SPORTS, 100, ["indoor", "basketball", "volleyball", "badminton"]),
        ("room_sports3", "Gymnasium", RoomType.SPORTS, 80, ["gym_equipment", "weights", "yoga", "aerobics"]),
        # Libraries (2)
        ("room_library1", "Central Library", RoomType.LIBRARY, 100, ["books_20000", "reading_area", "digital_section"]),
        ("room_library2", "Reference Library", RoomType.LIBRARY, 60, ["reference_books", "research_area", "computers"]),
        # Arts & Others (4)
        ("room_art", "Art & Design Studio", RoomType.CLASSROOM, 40, ["art_supplies", "easels", "pottery", "digital_art"]),
        ("room_music", "Music & Performing Arts", RoomType.CLASSROOM, 40, ["instruments", "soundproof", "recording", "stage"]),
        ("room_auditorium", "School Auditorium", RoomType.AUDITORIUM, 300, ["stage", "audio_visual", "seating", "lights"]),
        ("room_cafeteria", "Multi-purpose Hall", RoomType.CLASSROOM, 200, ["cafeteria", "assembly", "events"]),
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

    # 2. Create Classes (80 classes: LKG to Grade 12)
    classes = []
    grades_config = [
        (0, "LKG", 8),       # 8 sections
        (1, "UKG", 8),       # 8 sections
        (1, "Grade 1", 8),   # 8 sections
        (2, "Grade 2", 8),   # 8 sections
        (3, "Grade 3", 8),   # 8 sections
        (4, "Grade 4", 8),   # 8 sections
        (5, "Grade 5", 6),   # 6 sections
        (6, "Grade 6", 6),   # 6 sections
        (7, "Grade 7", 5),   # 5 sections
        (8, "Grade 8", 5),   # 5 sections
        (9, "Grade 9", 4),   # 4 sections
        (10, "Grade 10", 4), # 4 sections (80 total)
    ]

    sections = ["A", "B", "C", "D", "E", "F", "G", "H"]
    class_index = 0

    for grade_num, grade_name, num_sections in grades_config:
        for i in range(num_sections):
            if class_index >= 80:
                break
            class_index += 1
            section = sections[i]

            classes.append(Class(
                id=f"class_{class_index:03d}",
                school_id=school_id,
                name=f"{grade_name}-{section}",
                grade=grade_num,
                section=section,
                student_count=35 + (class_index % 6),  # 35-40 students
                home_room_id=f"room_home_{class_index:03d}"
            ))

    # 3. Create Subjects (15 subjects - complete K-12 curriculum)
    subjects = [
        # Core subjects
        Subject(
            id="subj_english",
            school_id=school_id,
            name="English Language",
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
        # Science subjects
        Subject(
            id="subj_science",
            school_id=school_id,
            name="General Science",
            code="SCI",
            periods_per_week=5,
            requires_lab=True
        ),
        Subject(
            id="subj_physics",
            school_id=school_id,
            name="Physics",
            code="PHY",
            periods_per_week=5,
            requires_lab=True
        ),
        Subject(
            id="subj_chemistry",
            school_id=school_id,
            name="Chemistry",
            code="CHEM",
            periods_per_week=5,
            requires_lab=True
        ),
        Subject(
            id="subj_biology",
            school_id=school_id,
            name="Biology",
            code="BIO",
            periods_per_week=4,
            requires_lab=True
        ),
        # Social & Languages
        Subject(
            id="subj_social",
            school_id=school_id,
            name="Social Studies",
            code="SST",
            periods_per_week=4,
            requires_lab=False
        ),
        Subject(
            id="subj_sanskrit",
            school_id=school_id,
            name="Sanskrit",
            code="SAN",
            periods_per_week=3,
            requires_lab=False
        ),
        # Technology & Arts
        Subject(
            id="subj_computer",
            school_id=school_id,
            name="Computer Science",
            code="CS",
            periods_per_week=4,
            requires_lab=True
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
        # Physical & Others
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
        Subject(
            id="subj_moral",
            school_id=school_id,
            name="Moral Science",
            code="MS",
            periods_per_week=2,
            requires_lab=False
        ),
    ]

    # 4. Create Teachers (140 teachers distributed across subjects)
    teachers = []
    teacher_distribution = {
        "English": 20,      # High demand
        "Math": 20,         # High demand
        "Hindi": 16,
        "Science": 15,
        "Physics": 10,
        "Chemistry": 10,
        "Biology": 8,
        "Social": 10,
        "Sanskrit": 6,
        "Computer": 8,
        "Art": 4,
        "Music": 4,
        "PE": 6,
        "Library": 2,
        "Moral": 3
    }

    teacher_id = 1
    for subject, count in teacher_distribution.items():
        for i in range(count):
            teachers.append(Teacher(
                id=f"teacher_t{teacher_id:03d}",
                user_id=f"user_t{teacher_id:03d}",
                name=f"{subject} Teacher {i+1}",
                subjects=[],
                max_periods_per_day=7,
                max_periods_per_week=35
            ))
            teacher_id += 1

    # Fill remaining slots to reach 140 teachers
    while teacher_id <= 140:
        teachers.append(Teacher(
            id=f"teacher_t{teacher_id:03d}",
            user_id=f"user_t{teacher_id:03d}",
            name=f"Substitute Teacher {teacher_id}",
            subjects=[],
            max_periods_per_day=7,
            max_periods_per_week=35
        ))
        teacher_id += 1

    # 5. Create Time Slots (6 days × 8 periods = 48 slots)
    time_slots = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
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

def run_v30_test_huge():
    """Run v3.0 maximum stress test with huge school configuration (80 classes)."""
    print("=" * 80)
    print("v3.0 TEST CONFIGURATION 5: HUGE SCHOOL (80 CLASSES - MAXIMUM STRESS)")
    print("=" * 80)

    # Get version info
    version_info = get_version_info()
    print(f"\nEngine Version: {version_info['version']} - {version_info['version_name']}")
    print("⚠️  WARNING: This is a maximum stress test. Generation may take 5-10 seconds.")

    # Create test data
    print("\n[1/5] Creating test data...")
    classes, subjects, teachers, time_slots, rooms = create_huge_school_data()

    print(f"  ✓ Classes: {len(classes)}")
    print(f"  ✓ Subjects: {len(subjects)}")
    print(f"  ✓ Teachers: {len(teachers)}")
    print(f"  ✓ Time Slots: {len(time_slots)}")
    print(f"  ✓ Rooms: {len(rooms)} (80 home + 18 shared)")

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
    print(f"\n    Computer Labs: {len([r for r in shared_rooms if 'Lab' in r.name and 'Computer' in r.name])}")
    print(f"    Science Labs: {len([r for r in shared_rooms if 'Lab' in r.name and ('Physics' in r.name or 'Chemistry' in r.name or 'Biology' in r.name or 'Science' in r.name)])}")
    print(f"    Sports Facilities: {len([r for r in shared_rooms if r.type == RoomType.SPORTS])}")
    print(f"    Libraries: {len([r for r in shared_rooms if r.type == RoomType.LIBRARY])}")
    print(f"    Others: {len([r for r in shared_rooms if r.type not in [RoomType.LAB, RoomType.SPORTS, RoomType.LIBRARY]])}")

    # Initialize solver
    print("\n[3/5] Initializing CSP Solver v3.0...")
    solver = CSPSolverCompleteV30(debug=False)

    # Generate timetable
    print("\n[4/5] Generating timetable (please wait 5-10 seconds)...")
    print("      Processing 80 classes × 48 time slots = 3,840 slots to schedule...")
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
        for i, error in enumerate(errors[:15]):
            print(f"    {i+1}. {error}")
        if len(errors) > 15:
            print(f"    ... and {len(errors) - 15} more errors")

    if warnings:
        print(f"\n  ⚠ Warnings: {len(warnings)}")
        for i, warning in enumerate(warnings[:15]):
            print(f"    {i+1}. {warning}")
        if len(warnings) > 15:
            print(f"    ... and {len(warnings) - 15} more warnings")

    # Export to CSV
    print("\n[5/5] Exporting results to CSV (this may take a moment)...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"v30_test_huge_{timestamp}.csv"

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
    print(f"\nTop 10 Shared Room Utilization:")
    shared_room_usage = {}
    for assignment in assignments:
        if assignment.is_shared_room:
            room_obj = next((r for r in rooms if r.id == assignment.room_id), None)
            if room_obj:
                shared_room_usage[room_obj.name] = shared_room_usage.get(room_obj.name, 0) + 1

    for i, (room_name, count) in enumerate(sorted(shared_room_usage.items(), key=lambda x: x[1], reverse=True)[:10]):
        utilization_pct = (count / len(time_slots)) * 100
        print(f"  {i+1}. {room_name}: {count}/{len(time_slots)} slots ({utilization_pct:.1f}% utilized)")

    # Subject-specific analysis
    print(f"\nTop 10 Subject Distribution:")
    subject_counts = {}
    for assignment in assignments:
        subject_obj = next((s for s in subjects if s.id == assignment.subject_id), None)
        if subject_obj:
            subject_counts[subject_obj.name] = subject_counts.get(subject_obj.name, 0) + 1

    for i, (subject_name, count) in enumerate(sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)[:10]):
        print(f"  {i+1}. {subject_name}: {count} periods")

    print(f"\nv3.0 Performance Metrics:")
    print(f"  Total assignments: {len(assignments):,}")
    print(f"  Generation time: {duration:.2f} seconds")
    print(f"  Assignments per second: {len(assignments)/duration:.0f}")
    print(f"  Classes processed: {len(classes)}")
    print(f"  Average time per class: {duration/len(classes):.3f} seconds")

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
    result = run_v30_test_huge()

    if result:
        print("\n" + "=" * 80)
        print("✅ HUGE SCHOOL MAXIMUM STRESS TEST COMPLETED!")
        print("=" * 80)
        print(f"📄 CSV file: {result['csv_file']}")
        print(f"📊 Total assignments: {result['stats']['total']:,}")
        print(f"⚡ Performance: {result['stats']['assignments_per_second']:.0f} assignments/second")
        print(f"🎯 Quality score: {result['stats']['quality_score']:.2f}")
        print(f"💾 Efficiency: {result['stats']['reduction_pct']:.1f}% reduction in checks")
        print(f"\n🏆 Successfully handled {len(result['assignments']):,} assignments across 80 classes!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
