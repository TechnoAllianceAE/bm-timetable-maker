"""
Utopia Central School - Foundation Stage Data Generator

Generates complete school data for Foundation Stage:
- School: Utopia Central School
- Grades: LKG, UKG, G1, G2, G3 (5 grades)
- Divisions per grade: 7 (A, B, C, D, E, F, G)
- Total Classes: 35 classes
- Subjects: 6 core + 2 co-curricular = 8 subjects per grade
- Teachers: Generated using indianNames.csv
- Users: Principal, Vice Principal, Teachers
- Time Slots: 6 periods/day, 5 days/week
- Rooms: Classrooms + special rooms
"""

import sqlite3
import csv
import random
from datetime import datetime
import hashlib

# Database path
DB_PATH = "/Users/afzal/Projects/react_apps/TimeTableAI/bm-timetable-maker/backend/prisma/dev.db"
NAMES_CSV = "/Users/afzal/Projects/react_apps/TimeTableAI/bm-timetable-maker/tt_tester/indianNames.csv"

# School configuration
SCHOOL_NAME = "Utopia Central School"
GRADES = [
    {"name": "LKG", "number": 0, "full_name": "Lower Kindergarten"},
    {"name": "UKG", "number": 1, "full_name": "Upper Kindergarten"},
    {"name": "G1", "number": 2, "full_name": "Grade 1"},
    {"name": "G2", "number": 3, "full_name": "Grade 2"},
    {"name": "G3", "number": 4, "full_name": "Grade 3"},
]
SECTIONS = ["A", "B", "C", "D", "E", "F", "G"]  # 7 divisions per grade
STUDENTS_PER_CLASS = 25

# Subject configuration for Foundation Stage
FOUNDATION_SUBJECTS = {
    # Core subjects (6)
    "core": [
        {"name": "English", "code": "ENG", "periods": 6, "requires_lab": False, "prefer_morning": True},
        {"name": "Mathematics", "code": "MATH", "periods": 6, "requires_lab": False, "prefer_morning": True},
        {"name": "Environmental Studies", "code": "EVS", "periods": 5, "requires_lab": False, "prefer_morning": False},
        {"name": "Hindi", "code": "HIN", "periods": 4, "requires_lab": False, "prefer_morning": False},
        {"name": "General Knowledge", "code": "GK", "periods": 3, "requires_lab": False, "prefer_morning": False},
        {"name": "Computer Basics", "code": "COMP", "periods": 2, "requires_lab": True, "prefer_morning": False},
    ],
    # Co-curricular subjects (2)
    "co_curricular": [
        {"name": "Art & Craft", "code": "ART", "periods": 2, "requires_lab": False, "prefer_morning": False},
        {"name": "Physical Education", "code": "PE", "periods": 2, "requires_lab": False, "prefer_morning": False},
    ]
}

# Time slots configuration
DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
PERIODS_PER_DAY = 6
PERIOD_TIMES = [
    ("08:30", "09:15"),
    ("09:15", "10:00"),
    ("10:00", "10:45"),
    ("10:45", "11:00", True),  # Short break
    ("11:00", "11:45"),
    ("11:45", "12:30"),
    ("12:30", "13:00", True),  # Lunch break
    ("13:00", "13:45"),
    ("13:45", "14:30"),
]


def generate_cuid():
    """Generate a simple CUID-like ID"""
    timestamp = str(int(datetime.now().timestamp() * 1000))
    random_part = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
    return f"c{timestamp[-8:]}{random_part}"


def hash_password(password):
    """Hash password using SHA256 (bcrypt would be better in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def load_indian_names():
    """Load names from CSV file"""
    names = []
    with open(NAMES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            names.append({
                'first_name': row['First Name'],
                'last_name': row['Last Name']
            })
    return names


def generate_utopia_school():
    """Generate complete school data for Utopia Central School"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("UTOPIA CENTRAL SCHOOL - FOUNDATION STAGE DATA GENERATOR")
    print("=" * 80)
    print(f"School: {SCHOOL_NAME}")
    print(f"Grades: {len(GRADES)} (LKG, UKG, G1, G2, G3)")
    print(f"Divisions per grade: {len(SECTIONS)}")
    print(f"Total classes: {len(GRADES) * len(SECTIONS)}")
    print(f"Subjects per grade: {len(FOUNDATION_SUBJECTS['core']) + len(FOUNDATION_SUBJECTS['co_curricular'])}")
    print()

    # Load names
    print("📋 Loading Indian names from CSV...")
    names_pool = load_indian_names()
    random.shuffle(names_pool)
    print(f"   Loaded {len(names_pool)} names")
    print()

    # 1. Create School
    print("🏫 Creating School...")
    school_id = generate_cuid()
    cursor.execute("""
        INSERT INTO schools (
            id, name, address, contactEmail, contactPhone,
            principalName, totalStudents, academicYearStart, academicYearEnd,
            subscriptionTier, createdAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        school_id,
        SCHOOL_NAME,
        "123 Education Avenue, Delhi, India",
        "info@utopiacentral.edu.in",
        "+91-11-12345678",
        "Dr. Rajesh Kumar",
        len(GRADES) * len(SECTIONS) * STUDENTS_PER_CLASS,
        int(datetime(2025, 4, 1).timestamp() * 1000),
        int(datetime(2026, 3, 31).timestamp() * 1000),
        "premium",
        int(datetime.now().timestamp() * 1000)
    ))
    print(f"   ✓ School created: {SCHOOL_NAME} (ID: {school_id})")
    print()

    # 2. Create Academic Year
    print("📅 Creating Academic Year...")
    academic_year_id = generate_cuid()
    cursor.execute("""
        INSERT INTO academic_years (id, schoolId, year, startDate, endDate)
        VALUES (?, ?, ?, ?, ?)
    """, (
        academic_year_id,
        school_id,
        "2025-2026",
        int(datetime(2025, 4, 1).timestamp() * 1000),
        int(datetime(2026, 3, 31).timestamp() * 1000)
    ))
    print(f"   ✓ Academic Year: 2025-2026")
    print()

    # 3. Create Users (Principal, VP)
    print("👥 Creating Administrative Users...")
    users_created = []

    # Principal
    principal_id = generate_cuid()
    principal_user_id = generate_cuid()
    cursor.execute("""
        INSERT INTO users (id, schoolId, email, passwordHash, role, profile, createdAt)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        principal_user_id,
        school_id,
        "principal@utopiacentral.edu.in",
        hash_password("principal123"),
        "PRINCIPAL",
        '{"name": "Dr. Rajesh Kumar", "phone": "+91-9876543210", "designation": "Principal"}',
        int(datetime.now().timestamp() * 1000)
    ))
    users_created.append(("Principal", "Dr. Rajesh Kumar", "principal@utopiacentral.edu.in", "principal123"))

    # Vice Principal
    vp_user_id = generate_cuid()
    cursor.execute("""
        INSERT INTO users (id, schoolId, email, passwordHash, role, profile, createdAt)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        vp_user_id,
        school_id,
        "vp@utopiacentral.edu.in",
        hash_password("vp123"),
        "PRINCIPAL",  # Using PRINCIPAL role for VP too
        '{"name": "Mrs. Sunita Sharma", "phone": "+91-9876543211", "designation": "Vice Principal"}',
        int(datetime.now().timestamp() * 1000)
    ))
    users_created.append(("Vice Principal", "Mrs. Sunita Sharma", "vp@utopiacentral.edu.in", "vp123"))

    print(f"   ✓ Created 2 administrative users")
    print()

    # 4. Create Rooms FIRST (needed for home classroom assignment)
    print("🏛️  Creating Rooms...")
    rooms_created = []
    room_count = 0

    # Regular classrooms (one per class + extras)
    # v3.0: These will be assigned as home classrooms
    num_home_classrooms = len(GRADES) * len(SECTIONS) + 5  # 35 classes + 5 extras
    for i in range(num_home_classrooms):
        room_id = generate_cuid()
        room_number = i + 1

        cursor.execute("""
            INSERT INTO rooms (id, schoolId, name, type, capacity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            room_id,
            school_id,
            f"Room {room_number:03d}",
            "CLASSROOM",
            30
        ))

        rooms_created.append({
            'id': room_id,
            'name': f"Room {room_number:03d}",
            'type': 'CLASSROOM'
        })
        room_count += 1

    # Special rooms (shared amenities for v3.0)
    special_rooms = [
        ("Computer Lab 1", "LAB", 30),
        ("Computer Lab 2", "LAB", 30),
        ("Art Room", "CLASSROOM", 25),
        ("Music Room", "CLASSROOM", 25),
        ("Library", "LIBRARY", 50),
        ("Activity Hall", "AUDITORIUM", 100),
    ]

    for room_name, room_type, capacity in special_rooms:
        room_id = generate_cuid()
        cursor.execute("""
            INSERT INTO rooms (id, schoolId, name, type, capacity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            room_id,
            school_id,
            room_name,
            room_type,
            capacity
        ))

        rooms_created.append({
            'id': room_id,
            'name': room_name,
            'type': room_type
        })
        room_count += 1

    print(f"   ✓ Created {room_count} rooms")
    print(f"     - Home Classrooms (type=CLASSROOM): {num_home_classrooms}")
    print(f"     - Shared Amenities (LAB/LIBRARY/AUDITORIUM): {len(special_rooms)}")
    print()

    # 5. Create Classes WITH home classroom assignment (v3.0 REQUIRED)
    print("🎓 Creating Classes with Home Classroom Assignment...")
    classes_created = []
    class_count = 0
    home_classroom_assignments = []

    # Get only home classrooms (type=CLASSROOM, first 35)
    home_classrooms = [r for r in rooms_created if r['type'] == 'CLASSROOM'][:len(GRADES) * len(SECTIONS)]

    room_index = 0
    for grade in GRADES:
        for section in SECTIONS:
            class_id = generate_cuid()
            class_name = f"{grade['name']}-{section}"

            # v3.0: Assign home classroom
            if room_index < len(home_classrooms):
                home_room_id = home_classrooms[room_index]['id']
                home_room_name = home_classrooms[room_index]['name']
                room_index += 1
            else:
                # Fallback (shouldn't happen)
                home_room_id = home_classrooms[0]['id']
                home_room_name = home_classrooms[0]['name']

            cursor.execute("""
                INSERT INTO classes (id, schoolId, name, grade, section, studentCount, homeRoomId)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                class_id,
                school_id,
                class_name,
                grade['number'],
                section,
                STUDENTS_PER_CLASS,
                home_room_id  # v3.0: Home classroom assigned
            ))

            classes_created.append({
                'id': class_id,
                'name': class_name,
                'grade': grade['number'],
                'grade_name': grade['name'],
                'section': section,
                'home_room_id': home_room_id,
                'home_room_name': home_room_name
            })
            home_classroom_assignments.append((class_name, home_room_name))
            class_count += 1

    print(f"   ✓ Created {class_count} classes")
    print(f"   ✓ Assigned home classrooms to all classes")
    print()

    # 6. Create Subjects
    print("📚 Creating Subjects...")
    subjects_created = []
    subject_count = 0

    all_subjects = FOUNDATION_SUBJECTS['core'] + FOUNDATION_SUBJECTS['co_curricular']

    for subject_data in all_subjects:
        subject_id = generate_cuid()

        cursor.execute("""
            INSERT INTO subjects (
                id, schoolId, name, department, credits,
                minPeriodsPerWeek, maxPeriodsPerWeek, requiresLab
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subject_id,
            school_id,
            subject_data['name'],
            "Foundation",
            subject_data['periods'],
            subject_data['periods'],
            subject_data['periods'],
            1 if subject_data['requires_lab'] else 0
        ))

        subjects_created.append({
            'id': subject_id,
            'name': subject_data['name'],
            'code': subject_data['code'],
            'periods': subject_data['periods'],
            'requires_lab': subject_data['requires_lab']
        })
        subject_count += 1

    print(f"   ✓ Created {subject_count} subjects")
    print()

    # 6. Calculate required teachers
    print("👨‍🏫 Calculating teacher requirements...")

    # Calculate total periods per subject across all classes
    subject_period_requirements = {}
    for subject in subjects_created:
        total_periods = subject['periods'] * len(classes_created)
        subject_period_requirements[subject['id']] = {
            'name': subject['name'],
            'total_periods': total_periods,
            'teachers_needed': max(1, (total_periods // 30) + 1)  # Max 30 periods/week per teacher
        }

    total_teachers_needed = sum(s['teachers_needed'] for s in subject_period_requirements.values())

    print(f"   Total classes: {len(classes_created)}")
    print(f"   Total subjects: {len(subjects_created)}")
    print(f"   Teachers needed: {total_teachers_needed}")
    print()

    # 8. Create Teachers
    print("👩‍🏫 Creating Teachers...")
    teachers_created = []
    name_index = 0
    teacher_count = 0

    for subject_id, req in subject_period_requirements.items():
        subject_name = req['name']

        for i in range(req['teachers_needed']):
            if name_index >= len(names_pool):
                name_index = 0  # Wrap around if we run out

            name_data = names_pool[name_index]
            name_index += 1

            teacher_name = f"{name_data['first_name']} {name_data['last_name']}"
            teacher_email = f"{name_data['first_name'].lower()}.{name_data['last_name'].lower()}@utopiacentral.edu.in"

            # Create User
            user_id = generate_cuid()
            cursor.execute("""
                INSERT INTO users (id, schoolId, email, passwordHash, role, profile, createdAt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                school_id,
                teacher_email,
                hash_password("teacher123"),
                "TEACHER",
                f'{{"name": "{teacher_name}", "phone": "+91-98765{str(random.randint(10000, 99999))}", "subjects": ["{subject_name}"]}}',
                int(datetime.now().timestamp() * 1000)
            ))

            # Create Teacher
            teacher_id = generate_cuid()
            cursor.execute("""
                INSERT INTO teachers (
                    id, userId, subjects,
                    maxPeriodsPerDay, maxPeriodsPerWeek, maxConsecutivePeriods
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                teacher_id,
                user_id,
                f'["{subject_name}"]',
                6,
                30,
                3
            ))

            teachers_created.append({
                'id': teacher_id,
                'user_id': user_id,
                'name': teacher_name,
                'email': teacher_email,
                'subject_id': subject_id,
                'subject_name': subject_name
            })

            users_created.append(("Teacher", teacher_name, teacher_email, "teacher123"))
            teacher_count += 1

    print(f"   ✓ Created {teacher_count} teachers")
    print()

    # 9. Create Time Slots
    print("⏰ Creating Time Slots...")
    time_slots_created = []
    slot_count = 0

    for day in DAYS:
        period_num = 1
        for period_data in PERIOD_TIMES:
            is_break = len(period_data) == 3 and period_data[2]
            start_time = period_data[0]
            end_time = period_data[1]

            slot_id = generate_cuid()
            cursor.execute("""
                INSERT INTO time_slots (
                    id, schoolId, day, startTime, endTime, isBreak
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                slot_id,
                school_id,
                day,
                start_time,
                end_time,
                1 if is_break else 0
            ))

            if not is_break:
                time_slots_created.append({
                    'id': slot_id,
                    'day': day,
                    'period': period_num,
                    'start': start_time,
                    'end': end_time
                })
                period_num += 1

            slot_count += 1

    print(f"   ✓ Created {slot_count} time slots ({len(time_slots_created)} active periods)")
    print()

    # Commit all changes
    conn.commit()
    conn.close()

    # Print summary
    print("=" * 80)
    print("✅ UTOPIA CENTRAL SCHOOL - DATA GENERATION COMPLETE!")
    print("=" * 80)
    print()
    print("📊 Summary:")
    print(f"   School: {SCHOOL_NAME}")
    print(f"   Academic Year: 2025-2026")
    print(f"   Classes: {len(classes_created)}")
    print(f"   Subjects: {len(subjects_created)}")
    print(f"   Teachers: {len(teachers_created)}")
    print(f"   Time Slots: {len(time_slots_created)} active periods")
    print(f"   Rooms: {len(rooms_created)}")
    print(f"   Total Users: {len(users_created)}")
    print()

    print("🔐 Login Credentials:")
    print("-" * 80)
    for role, name, email, password in users_created[:10]:  # Show first 10
        print(f"   {role:20s} | {email:50s} | {password}")
    if len(users_created) > 10:
        print(f"   ... and {len(users_created) - 10} more teachers (all use password: teacher123)")
    print()

    print("📋 Class Structure (with Home Classrooms):")
    print("-" * 80)
    for grade in GRADES:
        grade_classes = [c for c in classes_created if c['grade_name'] == grade['name']]
        print(f"   {grade['full_name']:25s} ({grade['name']:3s}): {len(grade_classes)} classes - {', '.join([c['name'] for c in grade_classes])}")
    print()

    print("🏠 Home Classroom Assignments (v3.0):")
    print("-" * 80)
    print("   Each class has a pre-assigned home classroom for regular subjects.")
    print("   Special subjects (labs, PE, art) use shared amenities.")
    print()
    for i, (class_name, home_room_name) in enumerate(home_classroom_assignments[:10], 1):
        print(f"   {i:2d}. {class_name:10s} → {home_room_name}")
    if len(home_classroom_assignments) > 10:
        print(f"   ... and {len(home_classroom_assignments) - 10} more class-room assignments")
    print()

    print("📚 Subjects:")
    print("-" * 80)
    print("   Core Subjects:")
    for subj in subjects_created[:6]:
        print(f"      • {subj['name']:30s} ({subj['code']:4s}) - {subj['periods']} periods/week")
    print("   Co-curricular Subjects:")
    for subj in subjects_created[6:]:
        print(f"      • {subj['name']:30s} ({subj['code']:4s}) - {subj['periods']} periods/week")
    print()

    print("🎯 Next Steps:")
    print("-" * 80)
    print("   1. Login to frontend at http://localhost:3000")
    print("   2. Use Principal credentials: principal@utopiacentral.edu.in / principal123")
    print("   3. Navigate to Timetable Generation")
    print("   4. Select classes and generate timetable")
    print("   5. Later: Add more stages (Primary, Middle, Senior) via frontend")
    print()
    print("=" * 80)


if __name__ == "__main__":
    generate_utopia_school()
