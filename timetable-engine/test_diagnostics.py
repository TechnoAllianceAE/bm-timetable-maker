#!/usr/bin/env python3
"""
Test the Diagnostic Intelligence System
Demonstrates both feasible and infeasible scenarios with detailed feedback
"""

import requests
import json
from datetime import datetime

def test_infeasible_scenario():
    """Test with deliberately infeasible constraints to see diagnostic feedback"""

    print("\n" + "="*60)
    print("TEST 1: INFEASIBLE SCENARIO")
    print("Testing with insufficient Math teachers")
    print("="*60)

    # Deliberately create shortage: 2 classes need 10 Math periods total, but only 1 teacher
    test_data = {
        "school_id": "school-001",
        "academic_year_id": "2024",
        "classes": [
            {"id": "class-1", "school_id": "school-001", "name": "Class 10A", "grade": 10, "section": "A", "student_count": 30},
            {"id": "class-2", "school_id": "school-001", "name": "Class 10B", "grade": 10, "section": "B", "student_count": 30}
        ],
        "subjects": [
            {"id": "math", "school_id": "school-001", "name": "Mathematics", "code": "MATH", "periods_per_week": 5, "requires_lab": False},
            {"id": "sci", "school_id": "school-001", "name": "Science", "code": "SCI", "periods_per_week": 3, "requires_lab": True}
        ],
        "teachers": [
            # Only 1 Math teacher who can handle max 8 periods (insufficient for 10 needed)
            {
                "id": "t1",
                "user_id": "user-1",
                "name": "Ms. Smith",
                "subjects": ["Mathematics"],
                "max_periods_per_day": 4,
                "max_periods_per_week": 8  # Can only teach 8, but need 10
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
            {"id": "mon-1", "school_id": "school-001", "day_of_week": "MONDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
            {"id": "mon-2", "school_id": "school-001", "day_of_week": "MONDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False},
            {"id": "tue-1", "school_id": "school-001", "day_of_week": "TUESDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
            {"id": "tue-2", "school_id": "school-001", "day_of_week": "TUESDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False},
            {"id": "wed-1", "school_id": "school-001", "day_of_week": "WEDNESDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
            {"id": "wed-2", "school_id": "school-001", "day_of_week": "WEDNESDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False}
        ],
        "rooms": [
            {"id": "room-1", "school_id": "school-001", "name": "Room 101", "capacity": 40, "type": "CLASSROOM"},
            {"id": "room-2", "school_id": "school-001", "name": "Room 102", "capacity": 40, "type": "CLASSROOM"}
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

    # Test with new diagnostic endpoint
    url = "http://localhost:8001/generate"

    try:
        response = requests.post(url, json=test_data, timeout=30)
        result = response.json()

        print("\n📊 DIAGNOSTIC RESULTS:")
        print("-" * 40)

        if result.get("status") == "infeasible":
            print("❌ Status: INFEASIBLE (as expected)")

            if "diagnostics" in result:
                diag = result["diagnostics"]

                # Show critical issues
                if diag.get("critical_issues"):
                    print("\n🔴 Critical Issues:")
                    for issue in diag["critical_issues"]:
                        print(f"  • {issue['message']}")
                        if issue.get("suggestions"):
                            print("    Suggestions:")
                            for sugg in issue["suggestions"][:2]:
                                print(f"      → {sugg}")

                # Show recommendations
                if diag.get("recommendations"):
                    print("\n💡 Recommendations:")
                    for rec in diag["recommendations"][:3]:
                        print(f"  {rec}")

                # Show bottlenecks
                if diag.get("bottleneck_resources"):
                    print("\n📈 Resource Bottlenecks:")
                    for resource, score in list(diag["bottleneck_resources"].items())[:3]:
                        print(f"  • {resource}: {score:.0f}% utilized")
        else:
            print(f"Status: {result.get('status')}")

    except Exception as e:
        print(f"Error: {e}")

def test_feasible_scenario():
    """Test with feasible constraints to see success diagnostics"""

    print("\n" + "="*60)
    print("TEST 2: FEASIBLE SCENARIO")
    print("Testing with adequate resources")
    print("="*60)

    test_data = {
        "school_id": "school-001",
        "academic_year_id": "2024",
        "classes": [
            {"id": "class-1", "school_id": "school-001", "name": "Class 10A", "grade": 10, "section": "A", "student_count": 30}
        ],
        "subjects": [
            {"id": "math", "school_id": "school-001", "name": "Mathematics", "code": "MATH", "periods_per_week": 3, "requires_lab": False},
            {"id": "eng", "school_id": "school-001", "name": "English", "code": "ENG", "periods_per_week": 2, "requires_lab": False}
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
                "subjects": ["English"],
                "max_periods_per_day": 5,
                "max_periods_per_week": 20
            }
        ],
        "time_slots": [
            {"id": "mon-1", "school_id": "school-001", "day_of_week": "MONDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
            {"id": "mon-2", "school_id": "school-001", "day_of_week": "MONDAY", "period_number": 2, "start_time": "09:45", "end_time": "10:30", "is_break": False},
            {"id": "tue-1", "school_id": "school-001", "day_of_week": "TUESDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
            {"id": "wed-1", "school_id": "school-001", "day_of_week": "WEDNESDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
            {"id": "thu-1", "school_id": "school-001", "day_of_week": "THURSDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False},
            {"id": "fri-1", "school_id": "school-001", "day_of_week": "FRIDAY", "period_number": 1, "start_time": "09:00", "end_time": "09:45", "is_break": False}
        ],
        "rooms": [
            {"id": "room-1", "school_id": "school-001", "name": "Room 101", "capacity": 40, "type": "CLASSROOM"}
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

    url = "http://localhost:8001/generate"

    try:
        response = requests.post(url, json=test_data, timeout=30)
        result = response.json()

        print("\n📊 DIAGNOSTIC RESULTS:")
        print("-" * 40)

        print(f"Status: {result.get('status')}")

        if result.get("status") == "success":
            print("✅ Generation SUCCESSFUL")

            if "diagnostics" in result:
                diag = result["diagnostics"]

                # Show optimization summary
                if diag.get("optimization_summary"):
                    opt = diag["optimization_summary"]
                    print(f"\n⚡ Performance:")
                    print(f"  • CSP Time: {opt.get('csp_time', 0)}s")
                    print(f"  • Total Iterations: {opt.get('total_iterations', 0)}")
                    print(f"  • Final Score: {opt.get('final_fitness', 0):.1f}")

                # Show resource utilization
                if diag.get("resource_utilization"):
                    print("\n📊 Resource Utilization:")
                    for resource, util in list(diag["resource_utilization"].items())[:3]:
                        print(f"  • {resource}: {util:.0f}%")

                # Show warnings if any
                if diag.get("warnings"):
                    print("\n⚠️  Warnings:")
                    for warning in diag["warnings"][:2]:
                        print(f"  • {warning}")

            # Show solution summary
            if result.get("solutions"):
                print(f"\n📋 Generated {len(result['solutions'])} solution(s)")
                sol = result["solutions"][0]
                if sol.get("timetable", {}).get("entries"):
                    print(f"  • Entries: {len(sol['timetable']['entries'])}")
                    print(f"  • Score: {sol.get('total_score', 0):.1f}")

    except Exception as e:
        print(f"Error: {e}")

def test_validation_endpoint():
    """Test the validation endpoint for quick feasibility check"""

    print("\n" + "="*60)
    print("TEST 3: VALIDATION ENDPOINT")
    print("Quick feasibility check without full generation")
    print("="*60)

    test_data = {
        "entities": {
            "classes": [
                {"id": "c1", "student_count": 30},
                {"id": "c2", "student_count": 30},
                {"id": "c3", "student_count": 30}
            ],
            "subjects": [
                {"id": "math", "name": "Mathematics", "periods_per_week": 5, "requires_lab": False}
            ],
            "teachers": [
                {"id": "t1", "subjects": ["Mathematics"], "max_periods_per_week": 10}
            ],
            "time_slots": [{"id": f"slot-{i}", "is_break": False} for i in range(20)],
            "rooms": [{"id": "r1", "capacity": 40, "type": "CLASSROOM"}]
        },
        "constraints": []
    }

    url = "http://localhost:8001/validate"

    try:
        response = requests.post(url, json=test_data, timeout=10)
        result = response.json()

        print("\n📊 VALIDATION RESULTS:")
        print("-" * 40)
        print(f"Feasible: {result.get('feasible')}")

        if result.get("critical_issues"):
            print("\n🔴 Critical Issues:")
            for issue in result["critical_issues"]:
                print(f"  • {issue['message']}")

        if result.get("recommendations"):
            print("\n💡 Recommendations:")
            for rec in result["recommendations"][:3]:
                print(f"  • {rec}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DIAGNOSTIC INTELLIGENCE SYSTEM TEST")
    print("="*60)
    print("\nMake sure the diagnostic service is running on port 8001:")
    print("  python3 main_diagnostic.py")
    print("\nStarting tests in 3 seconds...")

    import time
    time.sleep(3)

    # Run all tests
    test_infeasible_scenario()
    test_feasible_scenario()
    test_validation_endpoint()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)