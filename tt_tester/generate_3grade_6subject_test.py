#!/usr/bin/env python3
"""
Generate test data for 3 grades with 6 subjects
"""

import csv
import random
from datetime import datetime

def generate_test_data():
    """Generate test data for 3 grades with 6 subjects"""

    # Define subjects (6 subjects)
    subjects = [
        {"code": "MATH", "name": "Mathematics", "needs_lab": False, "periods_per_week": 6},
        {"code": "ENG", "name": "English", "needs_lab": False, "periods_per_week": 5},
        {"code": "SCI", "name": "Science", "needs_lab": True, "periods_per_week": 6},
        {"code": "SS", "name": "Social Studies", "needs_lab": False, "periods_per_week": 4},
        {"code": "CS", "name": "Computer Science", "needs_lab": True, "periods_per_week": 4},
        {"code": "PE", "name": "Physical Education", "needs_lab": False, "periods_per_week": 3}
    ]

    # Define classes (3 grades, 2 classes each = 6 classes)
    classes = []
    class_id = 1
    for grade in [8, 9, 10]:  # Grades 8, 9, 10
        for section in ['A', 'B']:
            classes.append({
                "class_id": f"CLASS_{class_id:03d}",
                "name": f"Grade {grade}{section}",
                "grade": str(grade),
                "section": section,
                "capacity": random.randint(25, 35)
            })
            class_id += 1

    # Calculate teacher requirements
    total_assignments = len(classes) * len(subjects)  # 6 classes * 6 subjects = 36
    teachers_per_subject = 2  # Each subject needs at least 2 teachers for coverage
    total_teachers = len(subjects) * teachers_per_subject  # 6 subjects * 2 = 12 teachers

    print(f"📊 Teacher calculation:")
    print(f"   Classes: {len(classes)}")
    print(f"   Subjects: {len(subjects)}")
    print(f"   Total assignments needed: {total_assignments}")
    print(f"   Teachers per subject: {teachers_per_subject}")
    print(f"   Total teachers: {total_teachers}")

    # Generate teachers
    teachers = []
    first_names = ["John", "Mary", "David", "Sarah", "Michael", "Lisa", "Robert", "Jennifer", "William", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

    for i in range(total_teachers):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        # Each teacher gets 2 subjects
        qualified_subjects = random.sample([s["code"] for s in subjects], 2)

        teacher = {
            "teacher_id": f"TEACHER_{i+1:03d}",
            "name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@school.edu",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "max_periods_per_day": 6,
            "max_periods_per_week": 30,
            "subjects_qualified": ','.join(qualified_subjects)
        }
        teachers.append(teacher)

    # Generate assignments (each class gets all 6 subjects)
    assignments = []
    assignment_id = 1

    for class_info in classes:
        for subject in subjects:
            # Find qualified teachers for this subject
            qualified_teachers = [t for t in teachers if subject["code"] in t["subjects_qualified"].split(',')]

            if qualified_teachers:
                # Assign to a random qualified teacher
                assigned_teacher = random.choice(qualified_teachers)

                assignment = {
                    "assignment_id": f"ASSIGN_{assignment_id:03d}",
                    "teacher_id": assigned_teacher["teacher_id"],
                    "teacher_name": assigned_teacher["name"],
                    "class_id": class_info["class_id"],
                    "class_name": class_info["name"],
                    "subject_code": subject["code"],
                    "subject_name": subject["name"],
                    "periods_per_week": subject["periods_per_week"],
                    "needs_lab": subject["needs_lab"]
                }
                assignments.append(assignment)
                assignment_id += 1

    # Generate rooms
    rooms = []
    # Regular classrooms
    for i in range(1, 7):  # 6 regular classrooms
        rooms.append({
            "room_id": f"ROOM_{i:03d}",
            "name": f"Classroom {i}",
            "type": "classroom",
            "capacity": random.randint(30, 40),
            "has_projector": random.choice([True, False]),
            "specialization": ""
        })

    # Lab rooms
    lab_types = ["Science Lab", "Computer Lab"]
    for i in range(2):  # 2 labs
        lab_type = lab_types[i]
        rooms.append({
            "room_id": f"LAB_{i+1:03d}",
            "name": f"{lab_type}",
            "type": "lab",
            "capacity": random.randint(20, 30),
            "has_projector": True,
            "specialization": lab_type.lower().replace(" ", "_")
        })

    return {
        'classes': classes,
        'teachers': teachers,
        'subjects': subjects,
        'assignments': assignments,
        'rooms': rooms
    }

def save_data(data, prefix="test_3grade_6subject"):
    """Save data to CSV files"""

    # Save classes
    with open(f"{prefix}_classes.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['class_id', 'name', 'grade', 'section', 'capacity']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data['classes'])

    # Save teachers
    with open(f"{prefix}_teachers.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['teacher_id', 'name', 'email', 'phone', 'max_periods_per_day', 'max_periods_per_week', 'subjects_qualified']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data['teachers'])

    # Save subjects
    with open(f"{prefix}_subjects.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['code', 'name', 'needs_lab', 'periods_per_week']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data['subjects'])

    # Save assignments
    with open(f"{prefix}_assignments.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['assignment_id', 'teacher_id', 'teacher_name', 'class_id', 'class_name', 'subject_code', 'subject_name', 'periods_per_week', 'needs_lab']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data['assignments'])

    # Save rooms
    with open(f"{prefix}_rooms.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['room_id', 'name', 'type', 'capacity', 'has_projector', 'specialization']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data['rooms'])

    print(f"\n✅ Test data saved with prefix: {prefix}")
    print(f"📄 Files: {prefix}_*.csv")

if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    data = generate_test_data()
    save_data(data)