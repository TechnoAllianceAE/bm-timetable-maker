"""
Test script to verify CSP solver correctly uses grade-specific subject requirements
"""
import requests
import json

# Test data: Simple school with 2 classes in different grades
test_request = {
    "school_id": "test-school-1",
    "academic_year_id": "test-year-1",
    "classes": [
        {
            "id": "class-6a",
            "school_id": "test-school-1",
            "name": "Grade 6A",
            "grade": 6,
            "section": "A",
            "stream": None,
            "student_count": 30
        },
        {
            "id": "class-7a",
            "school_id": "test-school-1",
            "name": "Grade 7A",
            "grade": 7,
            "section": "A",
            "stream": None,
            "student_count": 30
        }
    ],
    "subjects": [
        {
            "id": "math",
            "school_id": "test-school-1",
            "name": "Mathematics",
            "code": "MATH",
            "periods_per_week": 5,  # Default if no requirement specified
            "requires_lab": False,
            "is_elective": False,
            "prefer_morning": False,
            "preferred_periods": None,
            "avoid_periods": None
        },
        {
            "id": "english",
            "school_id": "test-school-1",
            "name": "English",
            "code": "ENG",
            "periods_per_week": 4,
            "requires_lab": False,
            "is_elective": False,
            "prefer_morning": False,
            "preferred_periods": None,
            "avoid_periods": None
        }
    ],
    "teachers": [
        {
            "id": "teacher-1",
            "user_id": "user-1",
            "subjects": ["Mathematics"],
            "availability": {},
            "max_periods_per_day": 20,
            "max_periods_per_week": 40,
            "max_consecutive_periods": 5
        },
        {
            "id": "teacher-2",
            "user_id": "user-2",
            "subjects": ["English"],
            "availability": {},
            "max_periods_per_day": 20,
            "max_periods_per_week": 40,
            "max_consecutive_periods": 5
        }
    ],
    "time_slots": [
        {"id": f"slot-{day}-{period}", "school_id": "test-school-1", "day_of_week": day,
         "period_number": period, "start_time": f"{8+period}:00",
         "end_time": f"{9+period}:00", "is_break": False}
        for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        for period in range(1, 3)  # 2 periods per day = 10 slots total
    ],
    "rooms": [
        {
            "id": "room-1",
            "school_id": "test-school-1",
            "name": "Room 1",
            "building": "Main",
            "floor": 1,
            "capacity": 40,
            "type": "CLASSROOM",
            "facilities": []
        }
    ],
    "constraints": [],
    # GRADE-SPECIFIC REQUIREMENTS - This is what we're testing!
    "subject_requirements": [
        # Grade 6: Math gets 6 periods, English gets 4 periods
        {"grade": 6, "subject_id": "math", "periods_per_week": 6},
        {"grade": 6, "subject_id": "english", "periods_per_week": 4},
        # Grade 7: Math gets 8 periods, English gets 2 periods
        {"grade": 7, "subject_id": "math", "periods_per_week": 8},
        {"grade": 7, "subject_id": "english", "periods_per_week": 2}
    ],
    "options": 1,
    "timeout": 30
}

print("=" * 80)
print("Testing CSP Solver with Grade-Specific Subject Requirements")
print("=" * 80)
print("\nTest Scenario:")
print("- Grade 6A: Math should get 6 periods, English should get 4 periods")
print("- Grade 7A: Math should get 8 periods, English should get 2 periods")
print("\nSending request to Python service...")

try:
    response = requests.post(
        "http://localhost:8000/generate",
        json=test_request,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print("\n[SUCCESS] Generation successful!")
        print(f"Generated {len(result.get('solutions', []))} solution(s)")

        # Analyze the first solution
        if result.get('solutions'):
            solution = result['solutions'][0]
            timetable = solution['timetable']
            entries = timetable.get('entries', [])

            # Count periods per class per subject
            class_subject_counts = {}
            for entry in entries:
                class_id = entry['class_id']
                subject_id = entry['subject_id']
                key = (class_id, subject_id)
                class_subject_counts[key] = class_subject_counts.get(key, 0) + 1

            print("\n[ACTUAL] Period Counts:")
            print("-" * 80)
            for (class_id, subject_id), count in sorted(class_subject_counts.items()):
                class_name = "Grade 6A" if class_id == "class-6a" else "Grade 7A"
                subject_name = "Math" if subject_id == "math" else "English"
                print(f"{class_name} - {subject_name}: {count} periods")

            print("\n[EXPECTED] Period Counts:")
            print("-" * 80)
            print("Grade 6A - Math: 6 periods")
            print("Grade 6A - English: 4 periods")
            print("Grade 7A - Math: 8 periods")
            print("Grade 7A - English: 2 periods")

            # Verify the counts match expectations
            print("\n[VERIFICATION]")
            print("-" * 80)
            grade6_math = class_subject_counts.get(("class-6a", "math"), 0)
            grade6_english = class_subject_counts.get(("class-6a", "english"), 0)
            grade7_math = class_subject_counts.get(("class-7a", "math"), 0)
            grade7_english = class_subject_counts.get(("class-7a", "english"), 0)

            checks = [
                (grade6_math == 6, f"Grade 6A Math: {grade6_math} == 6"),
                (grade6_english == 4, f"Grade 6A English: {grade6_english} == 4"),
                (grade7_math == 8, f"Grade 7A Math: {grade7_math} == 8"),
                (grade7_english == 2, f"Grade 7A English: {grade7_english} == 2")
            ]

            all_passed = all(check[0] for check in checks)
            for passed, message in checks:
                status = "[PASS]" if passed else "[FAIL]"
                print(f"{status} {message}")

            print("\n" + "=" * 80)
            if all_passed:
                print("*** TEST PASSED: Grade-specific requirements are correctly enforced! ***")
            else:
                print("*** TEST FAILED: Some requirements were not met ***")
            print("=" * 80)
    else:
        print(f"\n[ERROR] Request failed with status {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n[ERROR] {e}")
