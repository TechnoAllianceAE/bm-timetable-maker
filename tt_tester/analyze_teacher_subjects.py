#!/usr/bin/env python3
"""
Analyze teacher subject distribution to verify 2-subject maximum constraint
"""

import csv
from collections import Counter

def analyze_teachers():
    """Analyze teacher subject distribution"""
    
    # Read teacher data
    teachers = []
    with open('test_data_teachers.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        teachers = list(reader)
    
    # Analyze subject distribution
    subject_counts = []
    subject_distribution = Counter()
    
    for teacher in teachers:
        subjects = teacher['subjects_qualified'].split(',') if teacher['subjects_qualified'] else []
        num_subjects = len(subjects)
        subject_counts.append(num_subjects)
        subject_distribution[num_subjects] += 1
    
    print("=== TEACHER SUBJECT ANALYSIS ===")
    print(f"Total teachers: {len(teachers)}")
    print(f"Average subjects per teacher: {sum(subject_counts)/len(subject_counts):.2f}")
    print(f"Max subjects per teacher: {max(subject_counts)}")
    print(f"Min subjects per teacher: {min(subject_counts)}")
    
    print("\n=== SUBJECT COUNT DISTRIBUTION ===")
    for num_subjects in sorted(subject_distribution.keys()):
        count = subject_distribution[num_subjects]
        percentage = (count / len(teachers)) * 100
        print(f"{num_subjects} subjects: {count} teachers ({percentage:.1f}%)")
    
    # Verify constraint
    violation_count = sum(1 for count in subject_counts if count > 2)
    print(f"\n=== CONSTRAINT VERIFICATION ===")
    print(f"Teachers with >2 subjects: {violation_count}")
    print(f"Constraint satisfied: {'✓ YES' if violation_count == 0 else '✗ NO'}")
    
    # Show some examples
    print(f"\n=== EXAMPLES ===")
    examples_shown = 0
    for teacher in teachers[:10]:
        subjects = teacher['subjects_qualified'].split(',') if teacher['subjects_qualified'] else []
        print(f"{teacher['teacher_id']}: {teacher['name']} -> {len(subjects)} subjects: {', '.join(subjects)}")
        examples_shown += 1
        if examples_shown >= 10:
            break

if __name__ == "__main__":
    analyze_teachers()