#!/usr/bin/env python3
"""
3-Way A/B Testing: v2.5 vs v3.0 vs v3.0.1 Timetable Engine

Tests all 3 versions on identical data across all 5 configurations:
- v2.5: Metadata-driven optimization with teacher consistency (baseline)
- v3.0: Simplified room allocation
- v3.0.1: Simplified room allocation + performance optimizations

Generates comprehensive HTML comparison report.
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'timetable-engine'))

# Import all 3 versions
from src.models_phase1_v25 import Class as ClassV25, Subject as SubjectV25, Teacher as TeacherV25, TimeSlot as TimeSlotV25, Room as RoomV25, RoomType as RoomTypeV25
from src.csp_solver_complete_v25 import CSPSolverCompleteV25

from src.models_phase1_v30 import Class as ClassV30, Subject as SubjectV30, Teacher as TeacherV30, TimeSlot as TimeSlotV30, Room as RoomV30, RoomType as RoomTypeV30
from src.csp_solver_complete_v30 import CSPSolverCompleteV30

from src.models_phase1_v30 import Class as ClassV301, Subject as SubjectV301, Teacher as TeacherV301, TimeSlot as TimeSlotV301, Room as RoomV301, RoomType as RoomTypeV301
from src.csp_solver_complete_v301 import CSPSolverCompleteV301


# Test configurations
CONFIGS = {
    "small": {
        "classes": 5, "teachers": 10, "subjects": 5, "days": 5, "periods": 5,
        "home_rooms": 5, "shared_rooms": 2
    },
    "medium": {
        "classes": 15, "teachers": 25, "subjects": 8, "days": 5, "periods": 7,
        "home_rooms": 15, "shared_rooms": 5
    },
    "large": {
        "classes": 30, "teachers": 50, "subjects": 10, "days": 5, "periods": 7,
        "home_rooms": 30, "shared_rooms": 6
    },
    "big": {
        "classes": 46, "teachers": 85, "subjects": 12, "days": 5, "periods": 8,
        "home_rooms": 50, "shared_rooms": 6
    },
    "huge": {
        "classes": 78, "teachers": 140, "subjects": 15, "days": 6, "periods": 8,
        "home_rooms": 80, "shared_rooms": 6
    }
}


def generate_test_data_v30(config: Dict[str, int]):
    """Generate test data for v3.0 (WITH home_room_id)."""
    school_id = "test_school_v30"
    classes, subjects, teachers, time_slots, rooms = [], [], [], [], []

    # Subjects
    subject_names = ["English", "Math", "Hindi", "Science", "Social", "Computer", "Art", "Music",
                    "PE", "Library", "EVS", "Sanskrit", "French", "Drama", "Dance"]
    subject_codes = ["ENG", "MATH", "HIN", "SCI", "SOC", "CS", "ART", "MUS",
                    "PE", "LIB", "EVS", "SAN", "FR", "DRA", "DAN"]
    for i in range(config["subjects"]):
        requires_lab = i in [5, 6]  # Computer, Art
        subjects.append(SubjectV30(
            id=f"subj_{i:02d}",
            school_id=school_id,
            name=subject_names[i],
            code=subject_codes[i],
            periods_per_week=5 if i < 3 else 3,
            prefer_morning=i < 4,
            requires_lab=requires_lab
        ))

    # Teachers
    for i in range(1, config["teachers"] + 1):
        teacher_subjects = [subjects[j % len(subjects)].id for j in range(i-1, i+2)]
        teachers.append(TeacherV30(
            id=f"teacher_{i:03d}",
            school_id=school_id,
            user_id=f"user_{i:03d}",
            name=f"Teacher-{i}",
            subjects=teacher_subjects,
            max_consecutive_periods=3
        ))

    # Rooms - Home classrooms first
    for i in range(1, config["home_rooms"] + 1):
        rooms.append(RoomV30(
            id=f"room_home_{i:03d}",
            school_id=school_id,
            name=f"Room-{i}",
            type=RoomTypeV30.CLASSROOM,
            capacity=40
        ))

    # Rooms - Shared amenities
    shared_types = [RoomTypeV30.LAB, RoomTypeV30.SPORTS, RoomTypeV30.LIBRARY]
    for i in range(1, config["shared_rooms"] + 1):
        room_type = shared_types[i % len(shared_types)]
        rooms.append(RoomV30(
            id=f"room_shared_{i:03d}",
            school_id=school_id,
            name=f"Lab-{i}",
            type=room_type,
            capacity=35
        ))

    # Classes (WITH home_room_id in v3.0)
    for i in range(1, config["classes"] + 1):
        home_room_id = f"room_home_{min(i, config['home_rooms']):03d}"
        classes.append(ClassV30(
            id=f"class_{i:03d}",
            school_id=school_id,
            name=f"Class-{i}",
            grade=min(((i - 1) // 6) + 1, 12),
            section=chr(65 + ((i - 1) % 6)),
            student_count=35,
            home_room_id=home_room_id  # Pre-assigned
        ))

    # Time slots
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"][:config["days"]]
    for day in days:
        for period in range(1, config["periods"] + 1):
            time_slots.append(TimeSlotV30(
                id=f"slot_{day}_{period}",
                school_id=school_id,
                day_of_week=day,
                period_number=period,
                start_time=f"{8 + period - 1}:00",
                end_time=f"{8 + period}:00"
            ))

    return classes, subjects, teachers, time_slots, rooms


def generate_test_data_v25(config: Dict[str, int]):
    """Generate test data for v2.5 (no home_room_id)."""
    school_id = "test_school_v25"
    classes, subjects, teachers, time_slots, rooms = [], [], [], [], []

    # Subjects
    subject_names = ["English", "Math", "Hindi", "Science", "Social", "Computer", "Art", "Music",
                    "PE", "Library", "EVS", "Sanskrit", "French", "Drama", "Dance"]
    subject_codes = ["ENG", "MATH", "HIN", "SCI", "SOC", "CS", "ART", "MUS",
                    "PE", "LIB", "EVS", "SAN", "FR", "DRA", "DAN"]
    for i in range(config["subjects"]):
        subjects.append(SubjectV25(
            id=f"subj_{i:02d}",
            school_id=school_id,
            name=subject_names[i],
            code=subject_codes[i],
            periods_per_week=5 if i < 3 else 3,
            prefer_morning=i < 4  # Metadata
        ))

    # Teachers
    for i in range(1, config["teachers"] + 1):
        teacher_subjects = [subjects[j % len(subjects)].id for j in range(i-1, i+2)]
        teachers.append(TeacherV25(
            id=f"teacher_{i:03d}",
            school_id=school_id,
            user_id=f"user_{i:03d}",
            name=f"Teacher-{i}",
            subjects=teacher_subjects,
            max_consecutive_periods=3  # Metadata
        ))

    # Classes (no home_room_id in v2.5)
    for i in range(1, config["classes"] + 1):
        classes.append(ClassV25(
            id=f"class_{i:03d}",
            school_id=school_id,
            name=f"Class-{i}",
            grade=min(((i - 1) // 6) + 1, 12),
            section=chr(65 + ((i - 1) % 6)),
            student_count=35
        ))

    # Time slots
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"][:config["days"]]
    for day in days:
        for period in range(1, config["periods"] + 1):
            time_slots.append(TimeSlotV25(
                id=f"slot_{day}_{period}",
                school_id=school_id,
                day_of_week=day,
                period_number=period,
                start_time=f"{8 + period - 1}:00",
                end_time=f"{8 + period}:00"
            ))

    # Rooms (all treated equally in v2.5)
    total_rooms = config["home_rooms"] + config["shared_rooms"]
    for i in range(1, total_rooms + 1):
        rooms.append(RoomV25(
            id=f"room_{i:03d}",
            school_id=school_id,
            name=f"Room-{i}",
            type=RoomTypeV25.CLASSROOM,
            capacity=40
        ))

    return classes, subjects, teachers, time_slots, rooms


def generate_test_data_v301(config: Dict[str, int]):
    """Generate test data for v3.0.1 (WITH home_room_id)."""
    school_id = "test_school_v301"
    classes, subjects, teachers, time_slots, rooms = [], [], [], [], []

    # Subjects
    subject_names = ["English", "Math", "Hindi", "Science", "Social", "Computer", "Art", "Music",
                    "PE", "Library", "EVS", "Sanskrit", "French", "Drama", "Dance"]
    subject_codes = ["ENG", "MATH", "HIN", "SCI", "SOC", "CS", "ART", "MUS",
                    "PE", "LIB", "EVS", "SAN", "FR", "DRA", "DAN"]
    for i in range(config["subjects"]):
        requires_lab = i in [5, 6]  # Computer, Art
        subjects.append(SubjectV301(
            id=f"subj_{i:02d}",
            school_id=school_id,
            name=subject_names[i],
            code=subject_codes[i],
            periods_per_week=5 if i < 3 else 3,
            prefer_morning=i < 4,
            requires_lab=requires_lab
        ))

    # Teachers
    for i in range(1, config["teachers"] + 1):
        teacher_subjects = [subjects[j % len(subjects)].id for j in range(i-1, i+2)]
        teachers.append(TeacherV301(
            id=f"teacher_{i:03d}",
            school_id=school_id,
            user_id=f"user_{i:03d}",
            name=f"Teacher-{i}",
            subjects=teacher_subjects,
            max_consecutive_periods=3
        ))

    # Rooms - Home classrooms first
    for i in range(1, config["home_rooms"] + 1):
        rooms.append(RoomV301(
            id=f"room_home_{i:03d}",
            school_id=school_id,
            name=f"Room-{i}",
            type=RoomTypeV301.CLASSROOM,
            capacity=40
        ))

    # Rooms - Shared amenities
    shared_types = [RoomTypeV301.LAB, RoomTypeV301.SPORTS, RoomTypeV301.LIBRARY]
    for i in range(1, config["shared_rooms"] + 1):
        room_type = shared_types[i % len(shared_types)]
        rooms.append(RoomV301(
            id=f"room_shared_{i:03d}",
            school_id=school_id,
            name=f"Lab-{i}",
            type=room_type,
            capacity=35
        ))

    # Classes (WITH home_room_id in v3.0.1)
    for i in range(1, config["classes"] + 1):
        home_room_id = f"room_home_{min(i, config['home_rooms']):03d}"
        classes.append(ClassV301(
            id=f"class_{i:03d}",
            school_id=school_id,
            name=f"Class-{i}",
            grade=min(((i - 1) // 6) + 1, 12),
            section=chr(65 + ((i - 1) % 6)),
            student_count=35,
            home_room_id=home_room_id  # Pre-assigned
        ))

    # Time slots
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"][:config["days"]]
    for day in days:
        for period in range(1, config["periods"] + 1):
            time_slots.append(TimeSlotV301(
                id=f"slot_{day}_{period}",
                school_id=school_id,
                day_of_week=day,
                period_number=period,
                start_time=f"{8 + period - 1}:00",
                end_time=f"{8 + period}:00"
            ))

    return classes, subjects, teachers, time_slots, rooms


def run_test(version: str, config_name: str, config: Dict[str, int]) -> Dict[str, Any]:
    """Run test for a specific version and configuration."""
    print(f"\n[*] Running {version} on {config_name.upper()} configuration...")

    result = {
        "version": version,
        "config": config_name,
        "success": False,
        "time": 0.0,
        "assignments": 0,
        "timetables": 0,
        "errors": 0,
        "warnings": 0,
        "conflict_checks": 0
    }

    try:
        # Generate test data
        if version == "v2.5":
            classes, subjects, teachers, time_slots, rooms = generate_test_data_v25(config)
            solver = CSPSolverCompleteV25(debug=False)
        elif version == "v3.0":
            classes, subjects, teachers, time_slots, rooms = generate_test_data_v30(config)
            solver = CSPSolverCompleteV30(debug=False)
        elif version == "v3.0.1":
            classes, subjects, teachers, time_slots, rooms = generate_test_data_v301(config)
            solver = CSPSolverCompleteV301(debug=False)
        else:
            raise ValueError(f"Unknown version: {version}")

        print(f"  ✓ Generated data: {len(classes)} classes, {len(subjects)} subjects, {len(teachers)} teachers")
        print(f"  ✓ Time slots: {len(time_slots)}, Rooms: {len(rooms)}")

        # Run solver (all versions have same signature)
        start_time = time.time()
        timetables, quality_score, errors, warnings = solver.solve(
            classes=classes,
            subjects=subjects,
            teachers=teachers,
            time_slots=time_slots,
            rooms=rooms,
            constraints=[],
            num_solutions=3,
            enforce_teacher_consistency=True
        )
        end_time = time.time()

        # Collect results
        result["success"] = len(timetables) > 0
        result["time"] = end_time - start_time
        result["timetables"] = len(timetables)
        result["errors"] = len(errors)
        result["warnings"] = len(warnings)

        # Count assignments
        total_assignments = 0
        for tt in timetables:
            total_assignments += len(tt.entries)
        result["assignments"] = total_assignments

        # Estimate conflict checks (rooms tracked)
        if version == "v3.0.1":
            result["conflict_checks"] = config["shared_rooms"] * config["days"] * config["periods"]
        else:
            total_rooms = config["home_rooms"] + config["shared_rooms"]
            result["conflict_checks"] = total_rooms * config["days"] * config["periods"]

        print(f"  ✓ {version} completed in {result['time']:.2f}s")
        print(f"    - Timetables: {result['timetables']}")
        print(f"    - Assignments: {result['assignments']:,}")
        print(f"    - Errors: {result['errors']}, Warnings: {result['warnings']}")

    except Exception as e:
        print(f"  ✗ {version} failed: {str(e)}")
        result["error"] = str(e)

    return result


def generate_html_report(results: List[Dict[str, Any]], output_file: str):
    """Generate comprehensive 3-way HTML comparison report."""

    # Group results by configuration
    configs_results = {}
    for result in results:
        config_name = result["config"]
        if config_name not in configs_results:
            configs_results[config_name] = {}
        configs_results[config_name][result["version"]] = result

    total_tests = len(results)
    total_assignments = sum(r.get("assignments", 0) for r in results)

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>3-Way A/B Test: v2.5 vs v3.0 vs v3.0.1</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }}
        h1 {{ color: #667eea; text-align: center; font-size: 2.5em; margin-bottom: 10px; }}
        h2 {{ color: #764ba2; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-top: 40px; }}
        h3 {{ color: #667eea; margin-top: 30px; }}
        .subtitle {{ text-align: center; color: #666; font-size: 1.2em; margin-bottom: 40px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ font-size: 1.1em; opacity: 0.9; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        th {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background-color: #f8f9ff; }}
        .winner {{ background-color: #d4edda; font-weight: bold; }}
        .loser {{ background-color: #f8d7da; }}
        .badge {{ display: inline-block; padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; margin-left: 10px; }}
        .badge-success {{ background: #28a745; color: white; }}
        .badge-warning {{ background: #ffc107; color: black; }}
        .badge-danger {{ background: #dc3545; color: white; }}
        .config-section {{ background: #f8f9ff; padding: 25px; border-radius: 10px; margin: 25px 0; border-left: 5px solid #667eea; }}
        .chart {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 3-Way Engine Battle: v2.5 vs v3.0 vs v3.0.1</h1>
        <p class="subtitle">Comprehensive performance comparison across 5 configurations</p>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Tests</div>
                <div class="stat-value">{total_tests}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Assignments</div>
                <div class="stat-value">{total_assignments:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Configurations</div>
                <div class="stat-value">5</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Versions Tested</div>
                <div class="stat-value">3</div>
            </div>
        </div>
"""

    # Add configuration comparisons
    for config_name in ["small", "medium", "large", "big", "huge"]:
        if config_name not in configs_results:
            continue

        config_data = configs_results[config_name]
        v25 = config_data.get("v2.5", {})
        v30 = config_data.get("v3.0", {})
        v301 = config_data.get("v3.0.1", {})

        config = CONFIGS[config_name]

        html += f"""
        <div class="config-section">
            <h2>📊 {config_name.upper()} Configuration</h2>
            <p><strong>Scale:</strong> {config['classes']} classes, {config['teachers']} teachers,
            {config['subjects']} subjects, {config['days']}×{config['periods']} time slots</p>

            <table>
                <tr>
                    <th>Metric</th>
                    <th>v2.5 (Baseline)</th>
                    <th>v3.0 (Simplified)</th>
                    <th>v3.0.1 (Optimized)</th>
                </tr>
                <tr>
                    <td><strong>Generation Time</strong></td>
                    <td>{v25.get('time', 0):.2f}s</td>
                    <td>{v30.get('time', 0):.2f}s</td>
                    <td>{v301.get('time', 0):.2f}s</td>
                </tr>
                <tr>
                    <td><strong>Assignments Created</strong></td>
                    <td>{v25.get('assignments', 0):,}</td>
                    <td>{v30.get('assignments', 0):,}</td>
                    <td>{v301.get('assignments', 0):,}</td>
                </tr>
                <tr>
                    <td><strong>Conflict Checks</strong></td>
                    <td>{v25.get('conflict_checks', 0):,}</td>
                    <td>{v30.get('conflict_checks', 0):,}</td>
                    <td>{v301.get('conflict_checks', 0):,}</td>
                </tr>
                <tr>
                    <td><strong>Throughput</strong></td>
                    <td>{v25.get('assignments', 0) / max(v25.get('time', 1), 0.001):.0f} assignments/sec</td>
                    <td>{v30.get('assignments', 0) / max(v30.get('time', 1), 0.001):.0f} assignments/sec</td>
                    <td>{v301.get('assignments', 0) / max(v301.get('time', 1), 0.001):.0f} assignments/sec</td>
                </tr>
            </table>
        </div>
"""

    html += """
        <h2>🎯 Key Findings</h2>
        <div class="config-section">
            <h3>Performance Summary</h3>
            <ul>
                <li><strong>v2.5:</strong> Metadata-driven baseline with teacher consistency (all rooms tracked)</li>
                <li><strong>v3.0:</strong> Simplified room allocation (only shared amenities tracked)</li>
                <li><strong>v3.0.1:</strong> v3.0 + performance optimizations (cached lookups, reduced redundancy)</li>
            </ul>

            <h3>Architectural Differences</h3>
            <ul>
                <li><strong>v2.5:</strong> All rooms tracked for conflicts (baseline overhead)</li>
                <li><strong>v3.0 & v3.0.1:</strong> Only shared amenities tracked (71-93% reduction in checks)</li>
                <li><strong>v3.0.1 specific:</strong> Pre-computed metadata, cached values, optimized searches</li>
            </ul>
        </div>

        <p style="text-align: center; margin-top: 40px; color: #666; font-size: 0.9em;">
            Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
        </p>
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✓ HTML report saved to: {output_file}")


def main():
    """Main execution function."""
    print("=" * 80)
    print("3-WAY A/B TESTING: v2.5 vs v3.0 vs v3.0.1")
    print("=" * 80)
    print("\nTesting on all 5 configurations: Small, Medium, Large, Big, Huge\n")

    all_results = []

    for config_name in ["small", "medium", "large", "big", "huge"]:
        print("\n" + "=" * 80)
        print(f"A/B TEST: {config_name.upper()} CONFIGURATION")
        print("=" * 80)

        config = CONFIGS[config_name]

        # Test v2.5
        result_v25 = run_test("v2.5", config_name, config)
        all_results.append(result_v25)

        # Test v3.0
        result_v30 = run_test("v3.0", config_name, config)
        all_results.append(result_v30)

        # Test v3.0.1
        result_v301 = run_test("v3.0.1", config_name, config)
        all_results.append(result_v301)

        # Print comparison
        if all([r["success"] for r in [result_v25, result_v30, result_v301]]):
            print(f"\n  Performance Comparison ({config_name}):")
            fastest = min([result_v25, result_v30, result_v301], key=lambda x: x["time"])
            print(f"    - Fastest: {fastest['version']} at {fastest['time']:.2f}s")
            print(f"    - v2.5: {result_v25['time']:.2f}s")
            print(f"    - v3.0: {result_v30['time']:.2f}s")
            print(f"    - v3.0.1: {result_v301['time']:.2f}s")

    # Generate HTML report
    print("\n" + "=" * 80)
    print("GENERATING HTML REPORT")
    print("=" * 80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = f"ab_test_3way_{timestamp}.html"
    generate_html_report(all_results, html_file)

    print("\n" + "=" * 80)
    print("✓ 3-WAY A/B TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
