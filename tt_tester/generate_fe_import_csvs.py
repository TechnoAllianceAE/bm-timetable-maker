#!/usr/bin/env python3
"""
Generate CSV files for frontend import - Medium config with 10% more teachers and rooms
Compatible with the frontend CSV import interface
"""

import csv
import random
from datetime import datetime

# Configuration for medium school with 10% more teachers and rooms
MEDIUM_CONFIG = {
    "classes": 20,
    "teachers": 66,  # 10% more than standard medium (60 -> 66)
    "rooms": 39,     # 10% more than standard medium (35 -> 39)
    "subjects": 10,
    "grades": [6, 7, 8, 9, 10, 11, 12]
}

# Subject definitions (matching backend import format)
SUBJECTS = [
    {"name": "Mathematics", "code": "MATH", "needs_lab": "false", "periods_per_week": 6},
    {"name": "English", "code": "ENG", "needs_lab": "false", "periods_per_week": 5},
    {"name": "Science", "code": "SCI", "needs_lab": "true", "periods_per_week": 6},
    {"name": "Social Studies", "code": "SS", "needs_lab": "false", "periods_per_week": 4},
    {"name": "Computer Science", "code": "CS", "needs_lab": "true", "periods_per_week": 4},
    {"name": "Physical Education", "code": "PE", "needs_lab": "false", "periods_per_week": 3},
    {"name": "Art", "code": "ART", "needs_lab": "false", "periods_per_week": 3},
    {"name": "Music", "code": "MUS", "needs_lab": "false", "periods_per_week": 2},
    {"name": "Hindi", "code": "HIN", "needs_lab": "false", "periods_per_week": 4},
    {"name": "French", "code": "FR", "needs_lab": "false", "periods_per_week": 3}
]

# Name pools for random generation
FIRST_NAMES = [
    "John", "Mary", "David", "Sarah", "Michael", "Lisa", "Robert", "Jennifer",
    "William", "Karen", "James", "Nancy", "Christopher", "Betty", "Daniel",
    "Helen", "Matthew", "Sandra", "Anthony", "Donna", "Mark", "Carol", "Donald",
    "Ruth", "Steven", "Sharon", "Paul", "Michelle", "Andrew", "Laura", "Joshua",
    "Kenneth", "Kimberly", "Kevin", "Deborah", "Brian", "Dorothy", "George",
    "Edward", "Ronald", "Timothy", "Susan", "Jessica", "Emily", "Amanda",
    "Melissa", "Rebecca", "Maria", "Angela", "Brenda", "Amy", "Anna"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

def generate_classes():
    """Generate classes CSV data (matching backend import format)"""
    classes = []
    grades = MEDIUM_CONFIG["grades"]
    classes_per_grade = MEDIUM_CONFIG["classes"] // len(grades)
    remaining = MEDIUM_CONFIG["classes"] % len(grades)

    class_id = 1
    for i, grade in enumerate(grades):
        num_classes = classes_per_grade + (1 if i < remaining else 0)
        for section_idx in range(num_classes):
            section = chr(65 + section_idx)  # A, B, C, etc.
            classes.append({
                "class_id": f"CLASS_{class_id:03d}",
                "name": f"Grade {grade}{section}",
                "grade": grade,
                "section": section,
                "capacity": random.randint(25, 35)
            })
            class_id += 1

    return classes

def generate_subjects():
    """Generate subjects CSV data"""
    return SUBJECTS

def generate_teachers():
    """Generate teachers CSV data with varied subject expertise (matching backend import format)"""
    teachers = []
    used_names = set()

    for i in range(MEDIUM_CONFIG["teachers"]):
        # Generate unique name
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full_name = f"{first} {last}"
            if full_name not in used_names:
                used_names.add(full_name)
                break

        # Assign 1-3 subjects per teacher
        num_subjects = random.choices([1, 2, 3], weights=[30, 50, 20])[0]
        qualified_subjects = random.sample([s["code"] for s in SUBJECTS], num_subjects)

        teachers.append({
            "teacher_id": f"TEACHER_{i+1:03d}",
            "name": full_name,
            "email": f"{first.lower()}.{last.lower()}@school.edu",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "max_periods_per_day": random.choice([5, 6, 7]),
            "max_periods_per_week": random.choice([25, 30, 35]),
            "subjects_qualified": ",".join(qualified_subjects)
        })

    return teachers

def generate_rooms():
    """Generate rooms CSV data with varied types (matching backend import format)"""
    rooms = []

    # Calculate room distribution
    total_rooms = MEDIUM_CONFIG["rooms"]
    lab_rooms = int(total_rooms * 0.25)  # 25% labs
    regular_rooms = total_rooms - lab_rooms

    # Generate regular classrooms
    for i in range(1, regular_rooms + 1):
        rooms.append({
            "room_id": f"R{i:03d}",
            "name": f"Classroom {i}",
            "type": "classroom",
            "capacity": random.randint(30, 40),
            "has_projector": random.choice(["true", "false"]),
            "specialization": ""
        })

    # Generate specialized rooms/labs
    lab_types = [
        ("Science Lab", "lab", "science"),
        ("Computer Lab", "lab", "computer"),
        ("Physics Lab", "lab", "physics"),
        ("Chemistry Lab", "lab", "chemistry"),
        ("Biology Lab", "lab", "biology"),
        ("Language Lab", "lab", "language"),
        ("Art Studio", "lab", "art"),
        ("Music Room", "lab", "music"),
        ("Sports Hall", "lab", "sports"),
        ("Library", "lab", "library"),
        ("Auditorium", "auditorium", "auditorium")
    ]

    for i in range(lab_rooms):
        lab_name, lab_type, specialization = lab_types[i % len(lab_types)]
        lab_num = (i // len(lab_types)) + 1
        display_name = f"{lab_name} {lab_num}" if lab_num > 1 else lab_name

        rooms.append({
            "room_id": f"L{i+1:03d}",
            "name": display_name,
            "type": lab_type,
            "capacity": random.randint(20, 35),
            "has_projector": "true",
            "specialization": specialization
        })

    return rooms

def save_csv(filename, data, fieldnames):
    """Save data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Generated: {filename} ({len(data)} rows)")

def main():
    """Generate all CSV files for frontend import"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "fe_import"

    print("🚀 Generating CSV files for Frontend Import")
    print(f"📋 Configuration: Medium School (10% more teachers & rooms)")
    print(f"🆔 Timestamp: {timestamp}")
    print("=" * 60)

    # Generate data
    classes = generate_classes()
    subjects = generate_subjects()
    teachers = generate_teachers()
    rooms = generate_rooms()

    # Save CSV files
    save_csv(
        f"{prefix}_classes_{timestamp}.csv",
        classes,
        ["class_id", "name", "grade", "section", "capacity"]
    )

    save_csv(
        f"{prefix}_subjects_{timestamp}.csv",
        subjects,
        ["code", "name", "needs_lab", "periods_per_week"]
    )

    save_csv(
        f"{prefix}_teachers_{timestamp}.csv",
        teachers,
        ["teacher_id", "name", "email", "phone", "max_periods_per_day", "max_periods_per_week", "subjects_qualified"]
    )

    save_csv(
        f"{prefix}_rooms_{timestamp}.csv",
        rooms,
        ["room_id", "name", "type", "capacity", "has_projector", "specialization"]
    )

    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   Classes: {len(classes)}")
    print(f"   Subjects: {len(subjects)}")
    print(f"   Teachers: {len(teachers)} (10% more than standard)")
    print(f"   Rooms: {len(rooms)} (10% more than standard)")
    print(f"\n✨ Files ready for frontend CSV import!")
    print(f"📁 Location: {prefix}_*_{timestamp}.csv")

if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    main()
