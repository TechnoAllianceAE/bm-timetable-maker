#!/usr/bin/env python3
"""Check v2.0 response format"""
import sys
import os
import io
import json
import csv
import requests
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

TT_ID = "TT_20251004_112839_d317628b"
BASE_PATH = Path(__file__).parent

# Load minimal data
subjects = []
with open(BASE_PATH / f"data_subjects_{TT_ID}.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        subjects.append({
            "id": f"sub-{row['code'].lower()}",
            "school_id": "test-school",
            "name": row['name'],
            "code": row['code'],
            "periods_per_week": int(row['periods_per_week']),
            "requires_lab": row['needs_lab'] == 'True',
            "is_elective": False
        })

classes = []
with open(BASE_PATH / f"data_classes_{TT_ID}.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        classes.append({
            "id": row['class_id'],
            "school_id": "test-school",
            "name": row['name'],
            "grade": int(row['grade']),
            "section": row['section'],
            "student_count": int(row['capacity'])
        })

teachers = []
subject_code_to_name = {}
for s in subjects:
    subject_code_to_name[s['code']] = s['name']

with open(BASE_PATH / f"data_teachers_{TT_ID}.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        subject_codes = row['subjects_qualified'].split(',')
        subject_names = [subject_code_to_name.get(code.strip(), code.strip()) for code in subject_codes]
        teachers.append({
            "id": row['teacher_id'],
            "user_id": row['teacher_id'],
            "subjects": subject_names,
            "max_periods_per_day": int(row['max_periods_per_day']),
            "max_periods_per_week": int(row['max_periods_per_week']),
            "max_consecutive_periods": 3
        })

rooms = []
with open(BASE_PATH / f"data_rooms_{TT_ID}.csv", 'r') as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader):
        room_type = row['type'].upper() if row['type'].upper() in ['CLASSROOM', 'LAB', 'AUDITORIUM'] else 'CLASSROOM'
        rooms.append({
            "id": row['room_id'],
            "school_id": "test-school",
            "name": row['name'],
            "building": "Main Building",
            "floor": (idx // 10) + 1,
            "capacity": int(row['capacity']),
            "type": room_type,
            "facilities": []
        })

assignments = []
with open(BASE_PATH / f"data_assignments_{TT_ID}.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        assignments.append({
            "id": row['assignment_id'],
            "teacher_id": row['teacher_id'],
            "class_id": row['class_id'],
            "subject_code": row['subject_code'],
            "periods_per_week": int(row['periods_per_week'])
        })

time_slots = []
days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
for day_idx, day in enumerate(days):
    for period in range(1, 9):
        time_slots.append({
            "id": f"slot-{day_idx * 8 + period}",
            "school_id": "test-school",
            "day_of_week": day,
            "period_number": period,
            "start_time": f"{7 + period}:00",
            "end_time": f"{8 + period}:00",
            "is_break": False
        })

request_data = {
    "school_id": "test-school",
    "academic_year_id": "2025-2026",
    "tt_generation_id": TT_ID,
    "classes": classes,
    "teachers": teachers,
    "subjects": subjects,
    "rooms": rooms,
    "time_slots": time_slots,
    "assignments": assignments,
    "constraints": [],
    "options": 3,
    "timeout": 180
}

print("Testing v2.0 on port 8001...")
response = requests.post("http://localhost:8001/generate", json=request_data, timeout=300)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\nResponse keys: {list(result.keys())}")

    for key in result.keys():
        if key == 'timetable':
            print(f"\n  {key}: (dict with {len(result[key])} keys)")
            print(f"    Keys: {list(result[key].keys())}")
            if 'entries' in result[key]:
                print(f"    Entries: {len(result[key]['entries'])}")
        elif key == 'diagnostics':
            print(f"\n  {key}: {result[key]}")
        else:
            print(f"\n  {key}: {result[key]}")
else:
    print(f"Error: {response.text[:500]}")
