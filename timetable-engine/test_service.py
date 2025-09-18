#!/usr/bin/env python3
"""
Test script for the timetable generation service
Tests the FastAPI endpoints with sample data
"""

import requests
import json
from datetime import datetime, time

# Base URL for the service
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def create_sample_request():
    """Create a sample timetable generation request"""
    return {
        "school_id": "school-001",
        "academic_year_id": "year-2024",
        "classes": [
            {
                "id": "class-10a",
                "school_id": "school-001",
                "name": "10-A",
                "grade": 10,
                "section": "A",
                "student_count": 30
            },
            {
                "id": "class-10b",
                "school_id": "school-001",
                "name": "10-B",
                "grade": 10,
                "section": "B",
                "student_count": 32
            }
        ],
        "subjects": [
            {
                "id": "sub-math",
                "school_id": "school-001",
                "name": "Mathematics",
                "code": "MATH",
                "periods_per_week": 5,
                "requires_lab": False,
                "is_elective": False
            },
            {
                "id": "sub-sci",
                "school_id": "school-001",
                "name": "Science",
                "code": "SCI",
                "periods_per_week": 4,
                "requires_lab": True,
                "is_elective": False
            },
            {
                "id": "sub-eng",
                "school_id": "school-001",
                "name": "English",
                "code": "ENG",
                "periods_per_week": 4,
                "requires_lab": False,
                "is_elective": False
            }
        ],
        "teachers": [
            {
                "id": "teacher-001",
                "user_id": "user-001",
                "subjects": ["Mathematics"],
                "max_periods_per_day": 6,
                "max_periods_per_week": 25,
                "max_consecutive_periods": 3
            },
            {
                "id": "teacher-002",
                "user_id": "user-002",
                "subjects": ["Science"],
                "max_periods_per_day": 5,
                "max_periods_per_week": 24,
                "max_consecutive_periods": 2
            },
            {
                "id": "teacher-003",
                "user_id": "user-003",
                "subjects": ["English"],
                "max_periods_per_day": 6,
                "max_periods_per_week": 26,
                "max_consecutive_periods": 3
            }
        ],
        "time_slots": [],  # Will be generated
        "rooms": [
            {
                "id": "room-101",
                "school_id": "school-001",
                "name": "Room 101",
                "capacity": 35,
                "type": "CLASSROOM"
            },
            {
                "id": "room-102",
                "school_id": "school-001",
                "name": "Room 102",
                "capacity": 35,
                "type": "CLASSROOM"
            },
            {
                "id": "room-lab",
                "school_id": "school-001",
                "name": "Science Lab",
                "capacity": 40,
                "type": "LAB",
                "facilities": ["lab_equipment", "projector"]
            }
        ],
        "constraints": [
            {
                "id": "const-001",
                "school_id": "school-001",
                "type": "MAX_PERIODS_PER_WEEK",
                "priority": "MANDATORY",
                "description": "Maximum periods per week for subjects",
                "parameters": {}
            },
            {
                "id": "const-002",
                "school_id": "school-001",
                "type": "LUNCH_BREAK",
                "priority": "MANDATORY",
                "description": "Lunch break between 12:00 and 13:00",
                "parameters": {
                    "start_time": "12:00",
                    "end_time": "13:00"
                }
            }
        ],
        "options": 3,  # Generate 3 solutions
        "timeout": 60,
        "weights": {
            "academic_requirements": 0.4,
            "resource_utilization": 0.25,
            "gap_minimization": 0.2,
            "teacher_preferences": 0.15
        }
    }

def generate_time_slots():
    """Generate time slots for a 5-day week"""
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    slots = []

    # 8 periods per day with breaks
    period_times = [
        ("08:00", "08:45", 1),
        ("08:45", "09:30", 2),
        ("09:30", "10:15", 3),
        ("10:15", "10:30", 0),  # Break
        ("10:30", "11:15", 4),
        ("11:15", "12:00", 5),
        ("12:00", "13:00", 0),  # Lunch
        ("13:00", "13:45", 6),
        ("13:45", "14:30", 7),
        ("14:30", "15:15", 8),
    ]

    slot_id = 1
    for day in days:
        period_count = 1
        for start, end, period_num in period_times:
            is_break = period_num == 0
            if not is_break:  # Only add non-break slots
                slots.append({
                    "id": f"slot-{slot_id:03d}",
                    "school_id": "school-001",
                    "day_of_week": day,
                    "period_number": period_count,
                    "start_time": start,
                    "end_time": end,
                    "is_break": is_break
                })
                slot_id += 1
                period_count += 1

    return slots

def test_generate():
    """Test timetable generation endpoint"""
    request_data = create_sample_request()
    request_data["time_slots"] = generate_time_slots()

    print("\n" + "="*50)
    print("Testing /generate endpoint")
    print("="*50)

    print(f"\nSending request with:")
    print(f"  - Classes: {len(request_data['classes'])}")
    print(f"  - Subjects: {len(request_data['subjects'])}")
    print(f"  - Teachers: {len(request_data['teachers'])}")
    print(f"  - Time Slots: {len(request_data['time_slots'])}")
    print(f"  - Rooms: {len(request_data['rooms'])}")
    print(f"  - Constraints: {len(request_data['constraints'])}")

    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            json=request_data,
            timeout=70
        )

        print(f"\nResponse status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Generation time: {result.get('generation_time', 'N/A')} seconds")
            print(f"Solutions generated: {len(result.get('solutions', []))}")

            for i, solution in enumerate(result.get('solutions', []), 1):
                print(f"\nSolution {i}:")
                print(f"  - Score: {solution.get('total_score', 'N/A')}")
                print(f"  - Feasible: {solution.get('feasible', 'N/A')}")
                print(f"  - Conflicts: {len(solution.get('conflicts', []))}")
                if solution.get('metrics'):
                    print(f"  - Metrics: {solution['metrics']}")
        else:
            print(f"Error response: {response.text}")

        return response.status_code == 200

    except requests.exceptions.Timeout:
        print("Request timed out!")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_validate():
    """Test constraint validation endpoint"""
    request_data = {
        "entities": {
            "classes": [{"id": "class-001", "name": "10-A"}],
            "teachers": [{"id": "teacher-001", "subjects": ["Math"]}],
            "time_slots": generate_time_slots()[:10]  # Just a few slots
        },
        "constraints": [
            {
                "id": "const-001",
                "school_id": "school-001",
                "type": "MAX_PERIODS_PER_WEEK",
                "priority": "MANDATORY",
                "description": "Test constraint",
                "parameters": {}
            }
        ]
    }

    print("\n" + "="*50)
    print("Testing /validate endpoint")
    print("="*50)

    try:
        response = requests.post(
            f"{BASE_URL}/validate",
            json=request_data
        )

        print(f"\nResponse status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Feasible: {result.get('feasible', 'N/A')}")
            print(f"Conflicts: {result.get('conflicts', [])}")
            print(f"Suggestions: {result.get('suggestions', [])}")
        else:
            print(f"Error response: {response.text}")

        return response.status_code == 200

    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Timetable Service Tests")
    print("="*50)

    # Check if service is running
    try:
        if not test_health():
            print("\n❌ Service is not running. Please start it with:")
            print("   cd timetable-engine && python3 main.py")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to service at http://localhost:8000")
        print("   Please start the service with:")
        print("   cd timetable-engine && python3 main.py")
        return

    print("\n✅ Service is healthy")

    # Test validation
    if test_validate():
        print("\n✅ Validation endpoint working")
    else:
        print("\n❌ Validation endpoint failed")

    # Test generation
    if test_generate():
        print("\n✅ Generation endpoint working")
    else:
        print("\n❌ Generation endpoint failed")

    print("\n" + "="*50)
    print("Tests completed!")

if __name__ == "__main__":
    main()