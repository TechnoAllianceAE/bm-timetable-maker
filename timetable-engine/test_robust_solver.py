#!/usr/bin/env python3
"""
Test the robust CSP solver to verify it properly distributes periods
"""

import requests
import json
from datetime import datetime

# Test data - small example with all required fields
test_data = {
    "school_id": "school-001",
    "academic_year_id": "2024",
    "classes": [
        {"id": "class-1", "school_id": "school-001", "name": "Class 10A", "grade": 10, "section": "A", "student_count": 30}
    ],
    "subjects": [
        {"id": "math", "school_id": "school-001", "name": "Mathematics", "code": "MATH", "periods_per_week": 5, "requires_lab": False},
        {"id": "sci", "school_id": "school-001", "name": "Science", "code": "SCI", "periods_per_week": 4, "requires_lab": True}
    ],
    "teachers": [
        {
            "id": "t1",
            "user_id": "user-1",
            "name": "Ms. Smith",
            "subjects": ["Mathematics"],
            "max_periods_per_day": 6,
            "max_periods_per_week": 25
        },
        {
            "id": "t2",
            "user_id": "user-2",
            "name": "Mr. Johnson",
            "subjects": ["Science"],
            "max_periods_per_day": 5,
            "max_periods_per_week": 20
        }
    ],
    "time_slots": [
        # Monday
        {"id": "mon-1", "school_id": "school-001", "day_of_week": "MONDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
        {"id": "mon-2", "school_id": "school-001", "day_of_week": "MONDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False},
        {"id": "mon-3", "school_id": "school-001", "day_of_week": "MONDAY", "period_number": 3, "start_time": "10:45", "end_time": "11:30", "is_break": False},
        {"id": "mon-4", "school_id": "school-001", "day_of_week": "MONDAY", "period_number": 4, "start_time": "11:30", "end_time": "12:15", "is_break": False},

        # Tuesday
        {"id": "tue-1", "school_id": "school-001", "day_of_week": "TUESDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
        {"id": "tue-2", "school_id": "school-001", "day_of_week": "TUESDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False},
        {"id": "tue-3", "school_id": "school-001", "day_of_week": "TUESDAY", "period_number": 3, "start_time": "10:45", "end_time": "11:30", "is_break": False},
        {"id": "tue-4", "school_id": "school-001", "day_of_week": "TUESDAY", "period_number": 4, "start_time": "11:30", "end_time": "12:15", "is_break": False},

        # Wednesday
        {"id": "wed-1", "school_id": "school-001", "day_of_week": "WEDNESDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
        {"id": "wed-2", "school_id": "school-001", "day_of_week": "WEDNESDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False},
        {"id": "wed-3", "school_id": "school-001", "day_of_week": "WEDNESDAY", "period_number": 3, "start_time": "10:45", "end_time": "11:30", "is_break": False},
        {"id": "wed-4", "school_id": "school-001", "day_of_week": "WEDNESDAY", "period_number": 4, "start_time": "11:30", "end_time": "12:15", "is_break": False},

        # Thursday
        {"id": "thu-1", "school_id": "school-001", "day_of_week": "THURSDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
        {"id": "thu-2", "school_id": "school-001", "day_of_week": "THURSDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False},
        {"id": "thu-3", "school_id": "school-001", "day_of_week": "THURSDAY", "period_number": 3, "start_time": "10:45", "end_time": "11:30", "is_break": False},
        {"id": "thu-4", "school_id": "school-001", "day_of_week": "THURSDAY", "period_number": 4, "start_time": "11:30", "end_time": "12:15", "is_break": False},

        # Friday
        {"id": "fri-1", "school_id": "school-001", "day_of_week": "FRIDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
        {"id": "fri-2", "school_id": "school-001", "day_of_week": "FRIDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False},
        {"id": "fri-3", "school_id": "school-001", "day_of_week": "FRIDAY", "period_number": 3, "start_time": "10:45", "end_time": "11:30", "is_break": False}
    ],
    "rooms": [
        {"id": "room-1", "school_id": "school-001", "name": "Room 101", "capacity": 40, "type": "CLASSROOM"},
        {"id": "lab-1", "school_id": "school-001", "name": "Science Lab", "capacity": 35, "type": "LAB"}
    ],
    "constraints": [],
    "options": 1,
    "weights": {
        "constraint_satisfaction": 0.4,
        "teacher_preferences": 0.2,
        "room_utilization": 0.2,
        "gap_minimization": 0.2
    }
}

def test_generate_endpoint():
    """Test the /generate endpoint with the robust solver."""

    print("=" * 60)
    print("Testing Robust CSP Solver")
    print("=" * 60)

    url = "http://localhost:8000/generate"

    try:
        response = requests.post(url, json=test_data, timeout=30)

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ Generation successful!")
            print(f"Generation time: {result['generation_time']} seconds")
            print(f"Number of solutions: {len(result['solutions'])}")

            # Analyze the solution
            for i, solution in enumerate(result['solutions']):
                print(f"\n📊 Solution {i+1} Analysis:")
                print(f"Total score: {solution['total_score']}")
                print(f"Feasible: {solution['feasible']}")
                print(f"Number of entries: {len(solution['timetable']['entries'])}")

                # Check period distribution
                day_distribution = {}
                subject_day_distribution = {}

                for entry in solution['timetable']['entries']:
                    day = entry['day_of_week']
                    subject = entry['subject_id']

                    # Overall day distribution
                    day_distribution[day] = day_distribution.get(day, 0) + 1

                    # Subject-specific day distribution
                    if subject not in subject_day_distribution:
                        subject_day_distribution[subject] = {}
                    subject_day_distribution[subject][day] = \
                        subject_day_distribution[subject].get(day, 0) + 1

                print("\n📅 Day Distribution:")
                for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
                    count = day_distribution.get(day, 0)
                    bar = "█" * count
                    print(f"  {day:10}: {bar} ({count} periods)")

                print("\n📚 Subject Distribution by Day:")
                for subject, days in subject_day_distribution.items():
                    print(f"  {subject}:")
                    for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
                        count = days.get(day, 0)
                        if count > 0:
                            print(f"    {day}: {count} period(s)")

                # Check for Monday P1 bug
                monday_p1_count = sum(1 for e in solution['timetable']['entries']
                                    if e['day_of_week'] == 'MONDAY' and e['period_number'] == 1)

                if monday_p1_count > 1:
                    print(f"\n⚠️  WARNING: Multiple assignments at Monday Period 1: {monday_p1_count}")
                else:
                    print(f"\n✅ No Monday P1 bug detected! (Monday P1 has {monday_p1_count} assignment)")

                # Show first few entries
                print("\n📝 Sample Entries:")
                for j, entry in enumerate(solution['timetable']['entries'][:5]):
                    print(f"  {j+1}. {entry['day_of_week']} P{entry['period_number']}: "
                          f"{entry['subject_id']} in {entry['room_id']} with {entry['teacher_id']}")

        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        print("\n⚠️  Make sure the service is running:")
        print("  cd timetable-engine")
        print("  python3 main.py")

if __name__ == "__main__":
    test_generate_endpoint()