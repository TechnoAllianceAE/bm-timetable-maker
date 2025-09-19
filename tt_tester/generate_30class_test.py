#!/usr/bin/env python3
"""
Generate test data for 30-class timetable scenario
- 30 classes with 7 subjects each
- 5 days × 8 periods = 40 periods per week
- 121 teachers (2 subjects each + 15% substitution buffer)
- 35 rooms (classrooms and labs)
"""

import csv
import random
from datetime import datetime
from typing import List, Dict, Tuple
import json

# Configuration
NUM_CLASSES = 30
SUBJECTS_PER_CLASS = 7
DAYS_PER_WEEK = 5
PERIODS_PER_DAY = 8
NUM_ROOMS = 35
# Calculate optimal teacher count (each teacher takes max 2 subjects)
# 30 classes × 7 subjects = 210 total subject-class assignments
# Each teacher handles max 2 assignments = 105 base teachers minimum
# Add 15% buffer for substitutions = 121 total teachers
BASE_TEACHERS = 105  # 210 assignments ÷ 2 subjects per teacher
SUBSTITUTE_TEACHERS = 16  # 15% buffer for substitutions
TOTAL_TEACHERS = BASE_TEACHERS + SUBSTITUTE_TEACHERS  # 121 total

# Subject definitions with lab requirements
SUBJECTS = [
    {"name": "Mathematics", "code": "MATH", "needs_lab": False, "periods_per_week": 6},
    {"name": "English", "code": "ENG", "needs_lab": False, "periods_per_week": 5},
    {"name": "Science", "code": "SCI", "needs_lab": True, "periods_per_week": 6},
    {"name": "Social Studies", "code": "SS", "needs_lab": False, "periods_per_week": 4},
    {"name": "Computer Science", "code": "CS", "needs_lab": True, "periods_per_week": 4},
    {"name": "Physical Education", "code": "PE", "needs_lab": False, "periods_per_week": 3},
    {"name": "Art", "code": "ART", "needs_lab": False, "periods_per_week": 3},
    {"name": "Music", "code": "MUS", "needs_lab": False, "periods_per_week": 2},
    {"name": "Hindi", "code": "HIN", "needs_lab": False, "periods_per_week": 4},
    {"name": "French", "code": "FR", "needs_lab": False, "periods_per_week": 3}
]

# Grade levels
GRADES = ["6", "7", "8", "9", "10", "11", "12"]

def generate_classes() -> List[Dict]:
    """Generate 30 classes across different grades"""
    classes = []
    class_id = 1
    
    # Distribute classes across grades
    classes_per_grade = NUM_CLASSES // len(GRADES)
    remaining = NUM_CLASSES % len(GRADES)
    
    for i, grade in enumerate(GRADES):
        num_classes_this_grade = classes_per_grade + (1 if i < remaining else 0)
        
        for section in range(num_classes_this_grade):
            section_letter = chr(65 + section)  # A, B, C, etc.
            classes.append({
                "class_id": f"CLASS_{class_id:03d}",
                "name": f"Grade {grade}{section_letter}",
                "grade": grade,
                "section": section_letter,
                "capacity": random.randint(25, 35)
            })
            class_id += 1
    
    return classes

def generate_rooms() -> List[Dict]:
    """Generate 35 rooms (mix of classrooms and labs)"""
    rooms = []
    
    # 25 regular classrooms
    for i in range(1, 26):
        rooms.append({
            "room_id": f"ROOM_{i:03d}",
            "name": f"Classroom {i}",
            "type": "classroom",
            "capacity": random.randint(30, 40),
            "has_projector": random.choice([True, False])
        })
    
    # 10 specialized labs
    lab_types = ["Science Lab", "Computer Lab", "Physics Lab", "Chemistry Lab", 
                 "Biology Lab", "Language Lab", "Art Studio", "Music Room", 
                 "PE Hall", "Library"]
    
    for i, lab_type in enumerate(lab_types):
        rooms.append({
            "room_id": f"LAB_{i+1:03d}",
            "name": f"{lab_type} {i+1}",
            "type": "lab",
            "capacity": random.randint(20, 35),
            "has_projector": True,
            "specialization": lab_type.lower().replace(" ", "_")
        })
    
    return rooms

def generate_teachers_and_assignments() -> Tuple[List[Dict], List[Dict]]:
    """Generate teachers ensuring each takes exactly 1-2 subjects maximum"""
    teachers = []
    assignments = []
    
    # Generate teacher names
    first_names = ["John", "Mary", "David", "Sarah", "Michael", "Lisa", "Robert", "Jennifer", 
                   "William", "Karen", "James", "Nancy", "Christopher", "Betty", "Daniel", 
                   "Helen", "Matthew", "Sandra", "Anthony", "Donna", "Mark", "Carol", "Donald", 
                   "Ruth", "Steven", "Sharon", "Paul", "Michelle", "Andrew", "Laura", "Joshua", 
                   "Sarah", "Kenneth", "Kimberly", "Kevin", "Deborah", "Brian", "Dorothy", 
                   "George", "Lisa", "Edward", "Nancy", "Ronald", "Karen", "Timothy", "Betty"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
                  "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", 
                  "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", 
                  "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"]
    
    # Create all possible subject-class combinations
    all_assignments = []
    classes = generate_classes()
    
    for class_info in classes:
        # Each class gets 7 subjects (randomly selected from available subjects)
        selected_subjects = random.sample(SUBJECTS, SUBJECTS_PER_CLASS)
        for subject in selected_subjects:
            all_assignments.append({
                "class_id": class_info["class_id"],
                "class_name": class_info["name"],
                "subject_code": subject["code"],
                "subject_name": subject["name"],
                "periods_per_week": subject["periods_per_week"],
                "needs_lab": subject["needs_lab"]
            })
    
    # Shuffle assignments for random distribution
    random.shuffle(all_assignments)
    
    # Generate base teachers (each gets exactly 2 assignments)
    teacher_id = 1
    assignment_id = 1
    
    # Base teachers - each gets exactly 2 subject-class assignments
    for i in range(BASE_TEACHERS):
        if len(all_assignments) < 2:
            break
            
        # Generate teacher info
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        teacher = {
            "teacher_id": f"TEACHER_{teacher_id:03d}",
            "name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@school.edu",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "max_periods_per_day": 6,
            "max_periods_per_week": 30,
            "subjects_qualified": []
        }
        
        # Assign exactly 2 subject-class combinations to this teacher
        for _ in range(2):
            if all_assignments:
                assignment = all_assignments.pop(0)
                
                # Add to teacher's qualified subjects (max 2 subjects)
                if assignment["subject_code"] not in teacher["subjects_qualified"]:
                    teacher["subjects_qualified"].append(assignment["subject_code"])
                
                # Create assignment record
                assignments.append({
                    "assignment_id": f"ASSIGN_{assignment_id:03d}",
                    "teacher_id": teacher["teacher_id"],
                    "teacher_name": teacher["name"],
                    "class_id": assignment["class_id"],
                    "class_name": assignment["class_name"],
                    "subject_code": assignment["subject_code"],
                    "subject_name": assignment["subject_name"],
                    "periods_per_week": assignment["periods_per_week"],
                    "needs_lab": assignment["needs_lab"]
                })
                assignment_id += 1
        
        teachers.append(teacher)
        teacher_id += 1
    
    # Handle any remaining assignments with additional teachers (1 assignment each)
    while all_assignments:
        assignment = all_assignments.pop(0)
        
        # Generate new teacher for remaining assignment
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        teacher = {
            "teacher_id": f"TEACHER_{teacher_id:03d}",
            "name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@school.edu",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "max_periods_per_day": 6,
            "max_periods_per_week": 30,
            "subjects_qualified": [assignment["subject_code"]]
        }
        
        # Create assignment record
        assignments.append({
            "assignment_id": f"ASSIGN_{assignment_id:03d}",
            "teacher_id": teacher["teacher_id"],
            "teacher_name": teacher["name"],
            "class_id": assignment["class_id"],
            "class_name": assignment["class_name"],
            "subject_code": assignment["subject_code"],
            "subject_name": assignment["subject_name"],
            "periods_per_week": assignment["periods_per_week"],
            "needs_lab": assignment["needs_lab"]
        })
        
        teachers.append(teacher)
        teacher_id += 1
        assignment_id += 1
    
    # Generate substitute teachers (qualified for 2 subjects but no fixed assignments)
    for i in range(SUBSTITUTE_TEACHERS):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Select 2 random subjects for qualification
        available_subjects = [s["code"] for s in SUBJECTS]
        qualified_subjects = random.sample(available_subjects, 2)
        
        teacher = {
            "teacher_id": f"TEACHER_{teacher_id:03d}",
            "name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@school.edu",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "max_periods_per_day": 6,
            "max_periods_per_week": 30,
            "subjects_qualified": qualified_subjects
        }
        
        teachers.append(teacher)
        teacher_id += 1
    
    return teachers, assignments

def save_to_csv():
    """Generate all data and save to CSV files"""
    print("Generating test data for 30-class timetable scenario...")
    print(f"Classes: {NUM_CLASSES}")
    print(f"Teachers: {TOTAL_TEACHERS}")
    print(f"Rooms: {NUM_ROOMS}")
    print(f"Total periods to schedule: {NUM_CLASSES * DAYS_PER_WEEK * PERIODS_PER_DAY}")
    
    # Generate data
    classes = generate_classes()
    rooms = generate_rooms()
    teachers, assignments = generate_teachers_and_assignments()
    
    # Save classes
    with open('test_data_classes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['class_id', 'name', 'grade', 'section', 'capacity'])
        writer.writeheader()
        writer.writerows(classes)
    
    # Save rooms
    with open('test_data_rooms.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['room_id', 'name', 'type', 'capacity', 'has_projector']
        # Add specialization for labs
        for room in rooms:
            if 'specialization' not in room:
                room['specialization'] = ''
        
        writer = csv.DictWriter(f, fieldnames=fieldnames + ['specialization'])
        writer.writeheader()
        writer.writerows(rooms)
    
    # Save teachers
    with open('test_data_teachers.csv', 'w', newline='', encoding='utf-8') as f:
        # Convert subjects_qualified list to string
        for teacher in teachers:
            teacher['subjects_qualified'] = ','.join(teacher['subjects_qualified'])
        
        fieldnames = ['teacher_id', 'name', 'email', 'phone', 'max_periods_per_day', 
                     'max_periods_per_week', 'subjects_qualified']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(teachers)
    
    # Save assignments
    with open('test_data_assignments.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['assignment_id', 'teacher_id', 'teacher_name', 'class_id', 'class_name',
                     'subject_code', 'subject_name', 'periods_per_week', 'needs_lab']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(assignments)
    
    # Save subjects reference
    with open('test_data_subjects.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['code', 'name', 'needs_lab', 'periods_per_week']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{
            'code': s['code'],
            'name': s['name'], 
            'needs_lab': s['needs_lab'],
            'periods_per_week': s['periods_per_week']
        } for s in SUBJECTS])
    
    # Generate summary statistics
    total_periods_needed = sum([a['periods_per_week'] for a in assignments])
    total_periods_available = NUM_CLASSES * DAYS_PER_WEEK * PERIODS_PER_DAY
    
    print(f"\n=== DATA GENERATION COMPLETE ===")
    print(f"Classes generated: {len(classes)}")
    print(f"Teachers generated: {len(teachers)}")
    print(f"Rooms generated: {len(rooms)}")
    print(f"Subject assignments: {len(assignments)}")
    print(f"Total periods needed: {total_periods_needed}")
    print(f"Total periods available: {total_periods_available}")
    print(f"Utilization: {(total_periods_needed/total_periods_available)*100:.1f}%")
    
    print(f"\nFiles generated:")
    print(f"- test_data_classes.csv")
    print(f"- test_data_rooms.csv") 
    print(f"- test_data_teachers.csv")
    print(f"- test_data_assignments.csv")
    print(f"- test_data_subjects.csv")
    
    return {
        'classes': classes,
        'rooms': rooms,
        'teachers': teachers,
        'assignments': assignments,
        'subjects': SUBJECTS
    }

if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    data = save_to_csv()