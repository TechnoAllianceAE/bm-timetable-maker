"""
Simple test to verify CSP solver uses grade-specific subject requirements
Tests one class at a time to avoid resource conflicts
"""
import requests
import json

def test_grade(grade_num, math_periods, english_periods):
    """Test a single grade with specific requirements"""

    test_request = {
        "school_id": "test-school-1",
        "academic_year_id": "test-year-1",
        "classes": [
            {
                "id": f"class-{grade_num}a",
                "school_id": "test-school-1",
                "name": f"Grade {grade_num}A",
                "grade": grade_num,
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
                "periods_per_week": 5,  # Default (should be overridden)
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
                "periods_per_week": 4,  # Default (should be overridden)
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
                "max_consecutive_periods": 10
            },
            {
                "id": "teacher-2",
                "user_id": "user-2",
                "subjects": ["English"],
                "availability": {},
                "max_periods_per_day": 20,
                "max_periods_per_week": 40,
                "max_consecutive_periods": 10
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
        # GRADE-SPECIFIC REQUIREMENTS
        "subject_requirements": [
            {"grade": grade_num, "subject_id": "math", "periods_per_week": math_periods},
            {"grade": grade_num, "subject_id": "english", "periods_per_week": english_periods}
        ],
        "options": 1,
        "timeout": 30
    }

    try:
        response = requests.post(
            "http://localhost:8000/generate",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('solutions'):
                solution = result['solutions'][0]
                entries = solution['timetable'].get('entries', [])

                # Count periods per subject
                counts = {}
                for entry in entries:
                    subject_id = entry['subject_id']
                    counts[subject_id] = counts.get(subject_id, 0) + 1

                return counts.get("math", 0), counts.get("english", 0)

        return 0, 0

    except Exception as e:
        print(f"[ERROR] {e}")
        return 0, 0


print("=" * 80)
print("Testing CSP Solver with Grade-Specific Subject Requirements")
print("=" * 80)

# Test 1: Grade 6 with 6 math, 4 english
print("\n[TEST 1] Grade 6: Math=6, English=4")
print("-" * 80)
math_actual, english_actual = test_grade(6, 6, 4)
test1_pass = (math_actual == 6 and english_actual == 4)
print(f"Expected: Math=6, English=4")
print(f"Actual:   Math={math_actual}, English={english_actual}")
print(f"Result: {'[PASS]' if test1_pass else '[FAIL]'}")

# Test 2: Grade 7 with 8 math, 2 english
print("\n[TEST 2] Grade 7: Math=8, English=2")
print("-" * 80)
math_actual, english_actual = test_grade(7, 8, 2)
test2_pass = (math_actual == 8 and english_actual == 2)
print(f"Expected: Math=8, English=2")
print(f"Actual:   Math={math_actual}, English={english_actual}")
print(f"Result: {'[PASS]' if test2_pass else '[FAIL]'}")

# Test 3: Grade 9 with 3 math, 7 english (flipped)
print("\n[TEST 3] Grade 9: Math=3, English=7")
print("-" * 80)
math_actual, english_actual = test_grade(9, 3, 7)
test3_pass = (math_actual == 3 and english_actual == 7)
print(f"Expected: Math=3, English=7")
print(f"Actual:   Math={math_actual}, English={english_actual}")
print(f"Result: {'[PASS]' if test3_pass else '[FAIL]'}")

# Summary
print("\n" + "=" * 80)
all_pass = test1_pass and test2_pass and test3_pass
if all_pass:
    print("*** ALL TESTS PASSED ***")
    print("Grade-specific requirements are correctly enforced!")
else:
    print("*** SOME TESTS FAILED ***")
    failed = []
    if not test1_pass: failed.append("Test 1 (Grade 6)")
    if not test2_pass: failed.append("Test 2 (Grade 7)")
    if not test3_pass: failed.append("Test 3 (Grade 9)")
    print(f"Failed: {', '.join(failed)}")
print("=" * 80)
