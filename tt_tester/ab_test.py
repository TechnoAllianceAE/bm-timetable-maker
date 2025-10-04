#!/usr/bin/env python3
"""
A/B Testing Script for Timetable Generator Versions
Compares main_v20.py vs main_v25.py performance
Direct function calls instead of HTTP services
"""

import json
import time
import sys
import csv
from pathlib import Path

# Add timetable-engine to path
sys.path.insert(0, str(Path(__file__).parent.parent / "timetable-engine"))

# Global subject lookup for data loading
subject_code_to_name = {}

def load_test_data(tt_id):
    """Load CSV data for testing"""
    base_path = Path(__file__).parent

    # Load subjects
    subjects = []
    with open(base_path / f"data_subjects_{tt_id}.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            subjects.append({
                "id": f"sub-{row['code'].lower()}",
                "school_id": "test-school",
                "name": row['name'],
                "code": row['code'],
                "periods_per_week": int(row['periods_per_week']),
                "requires_lab": row['needs_lab'] == 'True',
                "is_elective": False,
                # v2.5 fields (defaults for compatibility)
                "prefer_morning": False,
                "preferred_periods": None,
                "avoid_periods": None
            })

    # Load classes
    classes = []
    with open(base_path / f"data_classes_{tt_id}.csv", 'r') as f:
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

    # Load teachers
    teachers = []
    with open(base_path / f"data_teachers_{tt_id}.csv", 'r') as f:
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

    # Load rooms
    rooms = []
    with open(base_path / f"data_rooms_{tt_id}.csv", 'r') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            room_type = row['type'].upper() if row['type'].upper() in ['CLASSROOM', 'LAB', 'AUDITORIUM'] else 'CLASSROOM'
            facilities = []
            if row.get('has_projector') == 'True':
                facilities.append('projector')
            if row.get('specialization'):
                facilities.append(row['specialization'])

            rooms.append({
                "id": row['room_id'],
                "school_id": "test-school",
                "name": row['name'],
                "building": "Main Building",
                "floor": (idx // 10) + 1,
                "capacity": int(row['capacity']),
                "type": room_type,
                "facilities": facilities
            })

    # Create time slots
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

    # Create constraints
    constraints = [
        {
            "id": "constraint-1",
            "school_id": "test-school",
            "type": "NO_GAPS",
            "priority": "MANDATORY",
            "entity_type": "CLASS",
            "entity_id": None,
            "parameters": {},
            "description": "Classes must have no gaps in their schedules"
        }
    ]

    return {
        "school_id": "test-school",
        "academic_year_id": "2025-2026",
        "tt_generation_id": tt_id,
        "classes": classes,
        "teachers": teachers,
        "subjects": subjects,
        "rooms": rooms,
        "time_slots": time_slots,
        "assignments": [],  # Will be generated
        "constraints": constraints,
        "options": 3,
        "timeout": 120,
        "weights": {
            "workload_balance": 50.0,
            "gap_minimization": 20.0,
            "time_preferences": 30.0,
            "consecutive_periods": 15.0,
            "morning_period_cutoff": 4
        }
    }

def run_direct_test(version, tt_id):
    """Run direct function test for a version"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING VERSION {version} (Direct Function Call)")
    print(f"{'='*80}")

    try:
        # Load test data
        print("📂 Loading test data...")
        test_data = load_test_data(tt_id)

        # Import the appropriate modules
        if version == "v20":
            from src.models_phase1 import (
                GenerateRequest, GenerateResponse, OptimizationWeights,
                Class, Subject, Teacher, TimeSlot, Room
            )
            from src.csp_solver_complete import CSPSolverComplete
            from src.ga_optimizer_fixed import GAOptimizerFixed

            # Convert data to v2.0 format
            request = GenerateRequest(
                school_id=test_data["school_id"],
                academic_year_id=test_data["academic_year_id"],
                classes=[Class(**c) for c in test_data["classes"]],
                subjects=[Subject(**s) for s in test_data["subjects"]],
                teachers=[Teacher(**t) for t in test_data["teachers"]],
                time_slots=[TimeSlot(**ts) for ts in test_data["time_slots"]],
                rooms=[Room(**r) for r in test_data["rooms"]],
                constraints=[],  # Simplified
                weights=OptimizationWeights(**test_data["weights"]),
                options=test_data["options"],
                timeout=test_data["timeout"]
            )

            # Initialize solvers
            csp_solver = CSPSolverComplete(debug=True)
            ga_optimizer = GAOptimizerFixed()

        elif version == "v25":
            from src.models_phase1_v25 import (
                GenerateRequest, GenerateResponse, OptimizationWeights,
                Class, Subject, Teacher, TimeSlot, Room
            )
            from src.csp_solver_complete_v25 import CSPSolverCompleteV25
            from src.algorithms.core.ga_optimizer_v25 import GAOptimizerV25

            # Convert data to v2.5 format
            request = GenerateRequest(
                school_id=test_data["school_id"],
                academic_year_id=test_data["academic_year_id"],
                classes=[Class(**c) for c in test_data["classes"]],
                subjects=[Subject(**s) for s in test_data["subjects"]],
                teachers=[Teacher(**t) for t in test_data["teachers"]],
                time_slots=[TimeSlot(**ts) for ts in test_data["time_slots"]],
                rooms=[Room(**r) for r in test_data["rooms"]],
                constraints=[],  # Simplified
                weights=OptimizationWeights(**test_data["weights"]),
                options=test_data["options"],
                timeout=test_data["timeout"]
            )

            # Initialize solvers
            csp_solver = CSPSolverCompleteV25(debug=True)
            ga_optimizer = GAOptimizerV25()

        print("✅ Data loaded and converted")

        # Run generation
        print("🚀 Running timetable generation...")
        start_time = time.time()

        # CSP Phase
        print("🧩 Phase 1: CSP Solver...")
        base_solutions, csp_time, conflicts, suggestions = csp_solver.solve(
            classes=request.classes,
            subjects=request.subjects,
            teachers=request.teachers,
            time_slots=request.time_slots,
            rooms=request.rooms,
            constraints=request.constraints,
            num_solutions=request.options
        )

        if not base_solutions:
            print("❌ CSP solver failed to generate solutions")
            return None

        print(f"✅ CSP generated {len(base_solutions)} solutions in {csp_time:.2f}s")

        # GA Phase
        print("🧬 Phase 2: GA Optimizer...")
        ga_start = time.time()
        optimized_solutions = ga_optimizer.evolve(
            population=base_solutions,
            generations=30,
            mutation_rate=0.15,
            crossover_rate=0.7,
            elitism_count=2,
            weights=request.weights
        )
        ga_time = time.time() - ga_start

        print(f"✅ GA optimization completed in {ga_time:.2f}s")

        total_time = time.time() - start_time

        # Create response
        response = GenerateResponse(
            solutions=optimized_solutions,
            generation_time=total_time,
            conflicts=None,
            suggestions=None
        )

        print(f"🎉 Generation complete in {total_time:.2f}s")
        print(f"   Best score: {optimized_solutions[0].total_score:.1f}")

        return {
            "status": "success",
            "message": f"Generated {len(optimized_solutions)} timetables",
            "generation_time": total_time,
            "solutions": [
                {
                    "total_score": sol.total_score,
                    "feasible": sol.feasible,
                    "metrics": sol.metrics
                } for sol in optimized_solutions[:3]  # Top 3
            ]
        }

    except Exception as e:
        print(f"❌ Error in {version} test: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python ab_test.py <TT_ID>")
        sys.exit(1)

    tt_id = sys.argv[1]

    print("🧪 Starting A/B Test between v2.0 and v2.5")
    print(f"📊 Test Data: {tt_id}")

    # Test v2.0
    v20_result = run_direct_test("v20", tt_id)

    # Test v2.5
    v25_result = run_direct_test("v25", tt_id)

    # Generate comparison
    if v20_result or v25_result:
        html_file = generate_comparison_html(v20_result, v25_result, tt_id)
        print(f"\n🎉 A/B Test complete! Open {html_file} in your browser to view results.")
    else:
        print("\n❌ Both versions failed - no results to compare")

if __name__ == "__main__":
    main()

def generate_comparison_html(v20_result, v25_result, tt_id):
    """Generate HTML comparison page"""
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A/B Test Results: v2.0 vs v2.5</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .comparison {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .version {{
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .version.v20 {{ border-left: 5px solid #ff6b6b; }}
        .version.v25 {{ border-left: 5px solid #4ecdc4; }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .metric:last-child {{ border-bottom: none; }}
        .metric.winner {{ background: #e8f5e8; }}
        .metric.loser {{ background: #ffeaea; }}
        .value {{
            font-weight: bold;
        }}
        .badge {{
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge.winner {{ background: #4ecdc4; color: white; }}
        .badge.better {{ background: #45b7d1; color: white; }}
        .badge.worse {{ background: #ff6b6b; color: white; }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-top: 20px;
        }}
        .chart {{
            display: flex;
            align-items: end;
            height: 200px;
            margin: 20px 0;
            gap: 10px;
        }}
        .bar {{
            flex: 1;
            background: #ddd;
            position: relative;
            border-radius: 5px 5px 0 0;
            display: flex;
            align-items: end;
            justify-content: center;
            color: white;
            font-weight: bold;
            min-height: 20px;
        }}
        .bar.v20 {{ background: #ff6b6b; }}
        .bar.v25 {{ background: #4ecdc4; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 A/B Test Results</h1>
            <h2>Timetable Generator: v2.0 vs v2.5</h2>
            <p>Test Data: {tt_id}</p>
        </div>

        <div class="comparison">
"""

    # Version 2.0 results
    v20_time = v20_result.get('generation_time', 0) if v20_result else 0
    v20_solutions = len(v20_result.get('solutions', [])) if v20_result else 0
    v20_score = v20_result['solutions'][0]['total_score'] if v20_result and v20_result['solutions'] else 0

    # Version 2.5 results
    v25_time = v25_result.get('generation_time', 0) if v25_result else 0
    v25_solutions = len(v25_result.get('solutions', [])) if v25_result else 0
    v25_score = v25_result['solutions'][0]['total_score'] if v25_result and v25_result['solutions'] else 0

    # Determine winners
    time_winner = "v20" if v20_time < v25_time and v20_time > 0 else "v25"
    score_winner = "v20" if v20_score > v25_score else "v25"

    html += f"""
            <div class="version v20">
                <h2>🚀 Version 2.0</h2>
                <div class="metric {'winner' if time_winner == 'v20' else 'loser' if v20_time > 0 else ''}">
                    <span>Generation Time</span>
                    <span class="value">{v20_time:.2f}s {'🏆' if time_winner == 'v20' else ''}</span>
                </div>
                <div class="metric {'winner' if score_winner == 'v20' else 'loser'}">
                    <span>Best Score</span>
                    <span class="value">{v20_score:.1f} {'🏆' if score_winner == 'v20' else ''}</span>
                </div>
                <div class="metric">
                    <span>Solutions Generated</span>
                    <span class="value">{v20_solutions}</span>
                </div>
                <div class="metric">
                    <span>Status</span>
                    <span class="value">{'✅ Success' if v20_result else '❌ Failed'}</span>
                </div>
            </div>

            <div class="version v25">
                <h2>🧠 Version 2.5 (Metadata-Driven)</h2>
                <div class="metric {'winner' if time_winner == 'v25' else 'loser' if v25_time > 0 else ''}">
                    <span>Generation Time</span>
                    <span class="value">{v25_time:.2f}s {'🏆' if time_winner == 'v25' else ''}</span>
                </div>
                <div class="metric {'winner' if score_winner == 'v25' else 'loser'}">
                    <span>Best Score</span>
                    <span class="value">{v25_score:.1f} {'🏆' if score_winner == 'v25' else ''}</span>
                </div>
                <div class="metric">
                    <span>Solutions Generated</span>
                    <span class="value">{v25_solutions}</span>
                </div>
                <div class="metric">
                    <span>Status</span>
                    <span class="value">{'✅ Success' if v25_result else '❌ Failed'}</span>
                </div>
            </div>
        </div>

        <div class="summary">
            <h2>📊 Performance Comparison</h2>

            <h3>Generation Time</h3>
            <div class="chart">
                <div class="bar v20" style="height: {min(200, v20_time * 20)}px">{v20_time:.1f}s</div>
                <div class="bar v25" style="height: {min(200, v25_time * 20)}px">{v25_time:.1f}s</div>
            </div>
            <p>
                <span class="badge {'winner' if time_winner == 'v20' else 'better' if v20_time < v25_time else 'worse'}">v2.0: {v20_time:.2f}s</span>
                <span class="badge {'winner' if time_winner == 'v25' else 'better' if v25_time < v20_time else 'worse'}">v2.5: {v25_time:.2f}s</span>
            </p>

            <h3>Solution Quality</h3>
            <p>
                <span class="badge {'winner' if score_winner == 'v20' else 'better'}">v2.0: {v20_score:.1f}</span>
                <span class="badge {'winner' if score_winner == 'v25' else 'better'}">v2.5: {v25_score:.1f}</span>
            </p>

            <h3>Analysis</h3>
            <ul>
"""

    if v20_result and v25_result:
        time_diff = abs(v20_time - v25_time)
        score_diff = abs(v20_score - v25_score)

        if time_winner == score_winner:
            html += f"<li>🏆 <strong>Clear winner:</strong> Version {time_winner[1:]}.0 performs better in both speed and quality</li>"
        else:
            html += f"<li>⚖️ <strong>Trade-off:</strong> Version {time_winner[1:]}.0 is faster, but version {score_winner[1:]}.0 produces better quality solutions</li>"

        html += f"""
                <li>⏱️ <strong>Time difference:</strong> {time_diff:.2f}s ({'faster' if time_diff < 1 else 'slower'})</li>
                <li>🎯 <strong>Quality difference:</strong> {score_diff:.1f} points</li>
                <li>🔧 <strong>v2.5 features:</strong> Metadata-driven optimization, language-agnostic preferences, school-customizable structures</li>
"""
    else:
        html += "<li>❌ One or both versions failed to generate results</li>"

    html += """
            </ul>
        </div>
    </div>
</body>
</html>
"""

    # Save HTML file
    output_file = Path(__file__).parent / f"ab_test_results_{tt_id}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n📄 HTML comparison saved to: {output_file}")
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python ab_test.py <TT_ID>")
        sys.exit(1)

    tt_id = sys.argv[1]

    print("🧪 Starting A/B Test between v2.0 and v2.5")
    print(f"📊 Test Data: {tt_id}")

    # Test v2.0 on port 8000
    v20_result = run_version_test("v20", 8000, tt_id)

    # Test v2.5 on port 8001
    v25_result = run_version_test("v25", 8001, tt_id)

    # Generate comparison
    if v20_result or v25_result:
        html_file = generate_comparison_html(v20_result, v25_result, tt_id)
        print(f"\n🎉 A/B Test complete! Open {html_file} in your browser to view results.")
    else:
        print("\n❌ Both versions failed - no results to compare")

if __name__ == "__main__":
    main()