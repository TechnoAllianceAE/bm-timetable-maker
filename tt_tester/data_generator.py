#!/usr/bin/env python3
"""
Consolidated Data Generator - Single tool for all timetable data generation
Supports multiple school sizes with complete schedule generation
"""

import csv
import json
import uuid
import random
import argparse
from datetime import datetime
from collections import defaultdict

class TimetableDataGenerator:
    """Consolidated timetable data generator with multiple configurations"""
    
    def __init__(self, config_name="medium"):
        self.config = self.get_config(config_name)
        self.tt_id = self.generate_tt_id()
        
    def generate_tt_id(self):
        """Generate unique timetable generation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"TT_{timestamp}_{unique_id}"
    
    def get_config(self, config_name):
        """Get configuration for different school sizes"""
        configs = {
            "small": {
                "name": "Small School",
                "classes": 14,
                "subjects_per_class": 6,
                "base_teachers_ratio": 2.0,  # subjects per teacher
                "substitute_buffer": 0.15,
                "grades": ["6", "7", "8", "9", "10"],
                "rooms": 20,
                "lab_rooms": 5
            },
            "medium": {
                "name": "Medium School", 
                "classes": 30,
                "subjects_per_class": 7,
                "base_teachers_ratio": 2.0,
                "substitute_buffer": 0.15,
                "grades": ["6", "7", "8", "9", "10", "11", "12"],
                "rooms": 35,
                "lab_rooms": 10
            },
            "large": {
                "name": "Large School",
                "classes": 50,
                "subjects_per_class": 8,
                "base_teachers_ratio": 2.0,
                "substitute_buffer": 0.15,
                "grades": ["6", "7", "8", "9", "10", "11", "12"],
                "rooms": 60,
                "lab_rooms": 15
            }
        }
        
        if config_name not in configs:
            raise ValueError(f"Unknown config: {config_name}. Available: {list(configs.keys())}")
        
        return configs[config_name]
    
    def get_subjects(self):
        """Get subject definitions"""
        return [
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
    
    def generate_classes(self):
        """Generate classes based on configuration"""
        classes = []
        class_id = 1
        
        classes_per_grade = self.config["classes"] // len(self.config["grades"])
        remaining = self.config["classes"] % len(self.config["grades"])
        
        for i, grade in enumerate(self.config["grades"]):
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
    
    def generate_rooms(self):
        """Generate rooms based on configuration"""
        rooms = []
        
        # Regular classrooms
        regular_rooms = self.config["rooms"] - self.config["lab_rooms"]
        for i in range(1, regular_rooms + 1):
            rooms.append({
                "room_id": f"ROOM_{i:03d}",
                "name": f"Classroom {i}",
                "type": "classroom",
                "capacity": random.randint(30, 40),
                "has_projector": random.choice([True, False]),
                "specialization": ""
            })
        
        # Specialized labs
        lab_types = ["Science Lab", "Computer Lab", "Physics Lab", "Chemistry Lab", 
                     "Biology Lab", "Language Lab", "Art Studio", "Music Room", 
                     "PE Hall", "Library", "Math Lab", "Geography Lab", 
                     "History Room", "Auditorium", "Conference Room"]
        
        for i in range(self.config["lab_rooms"]):
            lab_type = lab_types[i % len(lab_types)]
            rooms.append({
                "room_id": f"LAB_{i+1:03d}",
                "name": f"{lab_type} {i+1}",
                "type": "lab",
                "capacity": random.randint(20, 35),
                "has_projector": True,
                "specialization": lab_type.lower().replace(" ", "_")
            })
        
        return rooms
    
    def generate_teachers_and_assignments(self, classes):
        """Generate optimized teachers with 2-subject constraint"""
        subjects = self.get_subjects()
        
        # Calculate teacher requirements
        total_assignments = len(classes) * self.config["subjects_per_class"]
        base_teachers = int(total_assignments / self.config["base_teachers_ratio"])
        substitute_teachers = int(base_teachers * self.config["substitute_buffer"])
        total_teachers = base_teachers + substitute_teachers
        
        print(f"📊 Teacher calculation:")
        print(f"   Total assignments needed: {total_assignments}")
        print(f"   Base teachers (2 subjects each): {base_teachers}")
        print(f"   Substitute teachers ({self.config['substitute_buffer']*100:.0f}% buffer): {substitute_teachers}")
        print(f"   Total teachers: {total_teachers}")
        
        # Generate teacher names
        first_names = ["John", "Mary", "David", "Sarah", "Michael", "Lisa", "Robert", "Jennifer", 
                       "William", "Karen", "James", "Nancy", "Christopher", "Betty", "Daniel", 
                       "Helen", "Matthew", "Sandra", "Anthony", "Donna", "Mark", "Carol", "Donald", 
                       "Ruth", "Steven", "Sharon", "Paul", "Michelle", "Andrew", "Laura", "Joshua", 
                       "Kenneth", "Kimberly", "Kevin", "Deborah", "Brian", "Dorothy", "George", 
                       "Edward", "Ronald", "Timothy", "Betty", "Lisa", "Nancy", "Karen"]
        
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
                      "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
                      "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", 
                      "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", 
                      "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"]
        
        # Create all assignments
        all_assignments = []
        for class_info in classes:
            selected_subjects = random.sample(subjects, self.config["subjects_per_class"])
            for subject in selected_subjects:
                all_assignments.append({
                    "class_id": class_info["class_id"],
                    "class_name": class_info["name"],
                    "subject_code": subject["code"],
                    "subject_name": subject["name"],
                    "periods_per_week": subject["periods_per_week"],
                    "needs_lab": subject["needs_lab"]
                })
        
        random.shuffle(all_assignments)
        
        # Generate teachers and assignments
        teachers = []
        assignments = []
        teacher_id = 1
        assignment_id = 1
        
        # Base teachers (each gets exactly 2 assignments)
        for i in range(base_teachers):
            if len(all_assignments) < 2:
                break
                
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
            
            # Assign exactly 2 assignments
            for _ in range(2):
                if all_assignments:
                    assignment = all_assignments.pop(0)
                    
                    if assignment["subject_code"] not in teacher["subjects_qualified"]:
                        teacher["subjects_qualified"].append(assignment["subject_code"])
                    
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
        
        # Handle remaining assignments (1 each)
        while all_assignments:
            assignment = all_assignments.pop(0)
            
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
        
        # Generate substitute teachers
        for i in range(substitute_teachers):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            available_subjects = [s["code"] for s in subjects]
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
    
    def generate_all_data(self):
        """Generate complete dataset"""
        print(f"🚀 Generating {self.config['name']} Data")
        print(f"🆔 Generation ID: {self.tt_id}")
        print("=" * 60)
        
        # Generate all components
        classes = self.generate_classes()
        rooms = self.generate_rooms()
        teachers, assignments = self.generate_teachers_and_assignments(classes)
        subjects = self.get_subjects()
        
        print(f"\n📊 Generated data:")
        print(f"   Classes: {len(classes)}")
        print(f"   Teachers: {len(teachers)}")
        print(f"   Rooms: {len(rooms)}")
        print(f"   Assignments: {len(assignments)}")
        print(f"   Subjects: {len(subjects)}")
        
        return {
            'tt_id': self.tt_id,
            'config': self.config,
            'classes': classes,
            'teachers': teachers,
            'rooms': rooms,
            'assignments': assignments,
            'subjects': subjects
        }
    
    def save_data(self, data, prefix="data"):
        """Save all data to CSV files"""
        tt_id = data['tt_id']
        
        # Save classes
        filename = f"{prefix}_classes_{tt_id}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['class_id', 'name', 'grade', 'section', 'capacity']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data['classes'])
        
        # Save teachers
        filename = f"{prefix}_teachers_{tt_id}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            teachers_for_csv = []
            for teacher in data['teachers']:
                teacher_copy = teacher.copy()
                teacher_copy['subjects_qualified'] = ','.join(teacher['subjects_qualified'])
                teachers_for_csv.append(teacher_copy)
            
            fieldnames = ['teacher_id', 'name', 'email', 'phone', 'max_periods_per_day', 
                         'max_periods_per_week', 'subjects_qualified']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(teachers_for_csv)
        
        # Save rooms
        filename = f"{prefix}_rooms_{tt_id}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['room_id', 'name', 'type', 'capacity', 'has_projector', 'specialization']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data['rooms'])
        
        # Save assignments
        filename = f"{prefix}_assignments_{tt_id}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['assignment_id', 'teacher_id', 'teacher_name', 'class_id', 'class_name',
                         'subject_code', 'subject_name', 'periods_per_week', 'needs_lab']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data['assignments'])
        
        # Save subjects
        filename = f"{prefix}_subjects_{tt_id}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['code', 'name', 'needs_lab', 'periods_per_week']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([{
                'code': s['code'],
                'name': s['name'], 
                'needs_lab': s['needs_lab'],
                'periods_per_week': s['periods_per_week']
            } for s in data['subjects']])
        
        # Save metadata
        metadata = {
            'tt_generation_id': tt_id,
            'generation_timestamp': datetime.now().isoformat(),
            'config_name': data['config']['name'],
            'classes_count': len(data['classes']),
            'teachers_count': len(data['teachers']),
            'rooms_count': len(data['rooms']),
            'assignments_count': len(data['assignments']),
            'subjects_count': len(data['subjects'])
        }
        
        metadata_filename = f"metadata_{tt_id}.json"
        with open(metadata_filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Data saved with TT ID: {tt_id}")
        print(f"📄 Files: {prefix}_*_{tt_id}.csv")
        print(f"📋 Metadata: {metadata_filename}")
        
        return tt_id

def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(description='Generate timetable test data')
    parser.add_argument('--config', choices=['small', 'medium', 'large'], 
                       default='medium', help='School size configuration')
    parser.add_argument('--prefix', default='data', 
                       help='File prefix for generated files')
    
    args = parser.parse_args()
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Generate data
    generator = TimetableDataGenerator(args.config)
    data = generator.generate_all_data()
    tt_id = generator.save_data(data, args.prefix)
    
    print(f"\n🎉 {data['config']['name']} data generation complete!")
    print(f"🆔 TT ID: {tt_id}")
    print(f"📊 Use: python3 timetable_viewer.py {tt_id}")

if __name__ == "__main__":
    main()