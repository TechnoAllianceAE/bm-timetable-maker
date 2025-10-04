#!/usr/bin/env python3
"""Simple A/B Test - assumes engines are already running"""
import sys
import os
import io
import json
import csv
import time
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

TT_ID = "TT_20251004_121258_40b399a6"  # Large school: 50 classes, 230 teachers, 400 assignments, 2000 periods
BASE_PATH = Path(__file__).parent

def load_data():
    """Load test data"""
    print(f"Loading test data: {TT_ID}")

    # Load subjects
    subject_code_to_name = {}
    subjects = []
    with open(BASE_PATH / f"data_subjects_{TT_ID}.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            subject_code_to_name[row['code']] = row['name']
            subjects.append({
                "id": f"sub-{row['code'].lower()}",
                "school_id": "test-school",
                "name": row['name'],
                "code": row['code'],
                "periods_per_week": int(row['periods_per_week']),
                "requires_lab": row['needs_lab'] == 'True',
                "is_elective": False
            })

    # Load classes
    classes = []
    class_info = {}
    with open(BASE_PATH / f"data_classes_{TT_ID}.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            class_data = {
                "id": row['class_id'],
                "school_id": "test-school",
                "name": row['name'],
                "grade": int(row['grade']),
                "section": row['section'],
                "student_count": int(row['capacity'])
            }
            classes.append(class_data)
            class_info[row['class_id']] = class_data

    # Load teachers
    teachers = []
    teacher_info = {}
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
            teacher_info[row['teacher_id']] = {
                "name": row['name'],
                "max_periods_per_day": int(row['max_periods_per_day']),
                "max_consecutive_periods": 3
            }

    # Load rooms
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

    # Load assignments
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

    # Time slots
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

    print(f"  {len(classes)} classes, {len(teachers)} teachers, {len(assignments)} assignments")
    return request_data, teacher_info, class_info

def test_engine(version, port, data):
    """Test an engine"""
    print(f"\nTesting {version.upper()} on port {port}...")

    url = f"http://localhost:{port}/generate"

    start_time = time.time()
    try:
        response = requests.post(url, json=data, timeout=300)
        end_time = time.time()

        if response.status_code != 200:
            print(f"  FAILED: HTTP {response.status_code}")
            return None

        result = response.json()
        generation_time = end_time - start_time

        # Both v2.0 and v2.5 now use the same format: {'status', 'solutions', 'generation_time', 'diagnostics'}
        status = result.get('status', '')
        solutions = result.get('solutions', [])

        if solutions:
            timetable = solutions[0].get('timetable', {})
            entries = timetable.get('entries', [])
            # Consider success if we have entries, regardless of status field
            success = len(entries) > 0
        else:
            success = False
            entries = []

        print(f"  Response status: {status}")
        print(f"  Generation status: {'SUCCESS' if success else 'FAILED'}")
        print(f"  Time: {generation_time:.2f}s")
        print(f"  Entries: {len(entries)}")

        return {
            'version': version,
            'success': success,
            'generation_time': generation_time,
            'entries': entries
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def validate_constraints(result, teacher_info):
    """Validate constraints"""
    entries = result['entries']
    violations = {
        'teacher_conflicts': [],
        'room_conflicts': [],
        'class_conflicts': [],
        'teacher_overload': [],
        'consecutive_violations': []
    }

    teacher_schedule = defaultdict(lambda: defaultdict(set))
    room_schedule = defaultdict(lambda: defaultdict(set))
    class_schedule = defaultdict(lambda: defaultdict(set))
    teacher_daily_counts = defaultdict(lambda: defaultdict(int))
    teacher_consecutive = defaultdict(lambda: defaultdict(list))

    for entry in entries:
        teacher_id = entry.get('teacher_id')
        room_id = entry.get('room_id')
        class_id = entry.get('class_id')
        day = entry.get('day_of_week')
        period = entry.get('period_number')

        if not all([teacher_id, day, period, class_id]):
            continue

        # Teacher conflicts
        if period in teacher_schedule[teacher_id][day]:
            violations['teacher_conflicts'].append(f"{teacher_id} @ {day} P{period}")
        teacher_schedule[teacher_id][day].add(period)
        teacher_daily_counts[teacher_id][day] += 1
        teacher_consecutive[teacher_id][day].append(period)

        # Room conflicts
        if room_id and period in room_schedule[room_id][day]:
            violations['room_conflicts'].append(f"{room_id} @ {day} P{period}")
        if room_id:
            room_schedule[room_id][day].add(period)

        # Class conflicts
        if period in class_schedule[class_id][day]:
            violations['class_conflicts'].append(f"{class_id} @ {day} P{period}")
        class_schedule[class_id][day].add(period)

    # Teacher overload
    for teacher_id, days in teacher_daily_counts.items():
        max_periods = teacher_info.get(teacher_id, {}).get('max_periods_per_day', 8)
        for day, count in days.items():
            if count > max_periods:
                violations['teacher_overload'].append(f"{teacher_id} on {day}: {count}/{max_periods}")

    # Consecutive periods
    for teacher_id, days in teacher_consecutive.items():
        max_consecutive = teacher_info.get(teacher_id, {}).get('max_consecutive_periods', 3)
        for day, periods in days.items():
            sorted_periods = sorted(periods)
            consecutive = 1
            for i in range(1, len(sorted_periods)):
                if sorted_periods[i] == sorted_periods[i-1] + 1:
                    consecutive += 1
                    if consecutive > max_consecutive:
                        violations['consecutive_violations'].append(f"{teacher_id} on {day}: {consecutive}+ consecutive")
                        break
                else:
                    consecutive = 1

    total = sum(len(v) for v in violations.values())

    print(f"\n  Constraint Validation for {result['version']}:")
    print(f"    Teacher conflicts: {len(violations['teacher_conflicts'])}")
    print(f"    Room conflicts: {len(violations['room_conflicts'])}")
    print(f"    Class conflicts: {len(violations['class_conflicts'])}")
    print(f"    Teacher overload: {len(violations['teacher_overload'])}")
    print(f"    Consecutive violations: {len(violations['consecutive_violations'])}")
    print(f"    TOTAL: {total}")

    return violations, total

def create_html_report(v20_result, v25_result, v20_violations, v25_violations):
    """Create HTML report"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Determine winner
    v20_score = v20_violations[1]
    v25_score = v25_violations[1]

    if not v20_result['success']:
        winner = 'v25'
    elif not v25_result['success']:
        winner = 'v20'
    elif v20_score < v25_score:
        winner = 'v20'
    elif v25_score < v20_score:
        winner = 'v25'
    else:
        winner = 'tie'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A/B Test: v2.0 vs v2.5</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 48px; color: #2d3748; margin-bottom: 10px; }}
        .subtitle {{ font-size: 18px; color: #718096; margin: 5px 0; }}
        .winner-banner {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
            font-size: 32px;
            font-weight: 800;
            box-shadow: 0 10px 30px rgba(72, 187, 120, 0.4);
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        .version-card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .version-card.winner {{
            border: 5px solid #48bb78;
            box-shadow: 0 15px 40px rgba(72, 187, 120, 0.4);
        }}
        .version-card h2 {{
            font-size: 32px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 4px solid #667eea;
            color: #2d3748;
        }}
        .version-card.winner h2 {{
            color: #48bb78;
            border-bottom-color: #48bb78;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 25px;
        }}
        .stat {{
            background: #f7fafc;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            text-align: center;
        }}
        .stat-value {{
            font-size: 42px;
            font-weight: 900;
            color: #2d3748;
            margin-bottom: 8px;
        }}
        .stat-label {{
            font-size: 14px;
            color: #718096;
            font-weight: 600;
        }}
        .success {{ color: #48bb78; }}
        .error {{ color: #f56565; }}
        .warning {{ color: #ed8936; }}
        .violations {{
            background: #fff5f5;
            border-left: 5px solid #f56565;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }}
        .violations h3 {{
            color: #f56565;
            font-size: 18px;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        .violations ul {{
            list-style: none;
            padding-left: 0;
        }}
        .violations li {{
            padding: 8px 0;
            color: #742a2a;
            font-size: 15px;
            font-weight: 500;
        }}
        .violations li strong {{ color: #c53030; }}
        .summary {{
            background: white;
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .summary h2 {{
            font-size: 32px;
            color: #2d3748;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 4px solid #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 2px solid #e2e8f0;
            font-size: 16px;
        }}
        th {{
            background: #f7fafc;
            font-weight: 700;
            color: #4a5568;
        }}
        td.winner-cell {{
            background: #f0fff4;
            font-weight: 700;
            color: #48bb78;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>A/B Test Report</h1>
            <div class="subtitle">Version 2.0 vs Version 2.5</div>
            <div class="subtitle">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
            <div class="subtitle">Test ID: {TT_ID}</div>
        </div>

        <div class="winner-banner">
            {'🏆 WINNER: VERSION 2.0' if winner == 'v20' else '🏆 WINNER: VERSION 2.5' if winner == 'v25' else '🤝 TIE - Both versions performed equally'}
        </div>

        <div class="comparison-grid">
            <div class="version-card{' winner' if winner == 'v20' else ''}">
                <h2>{'🏆 ' if winner == 'v20' else ''}Version 2.0</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value {'success' if v20_result['success'] else 'error'}">
                            {'✓' if v20_result['success'] else '✗'}
                        </div>
                        <div class="stat-label">Status</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{v20_result['generation_time']:.2f}s</div>
                        <div class="stat-label">Generation Time</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{len(v20_result['entries'])}</div>
                        <div class="stat-label">Periods Scheduled</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value {'success' if v20_violations[1] == 0 else 'error'}">{v20_violations[1]}</div>
                        <div class="stat-label">Total Violations</div>
                    </div>
                </div>
                <div class="violations">
                    <h3>Constraint Violations</h3>
                    <ul>
                        <li><strong>{len(v20_violations[0]['teacher_conflicts'])}</strong> Teacher Conflicts</li>
                        <li><strong>{len(v20_violations[0]['room_conflicts'])}</strong> Room Conflicts</li>
                        <li><strong>{len(v20_violations[0]['class_conflicts'])}</strong> Class Conflicts</li>
                        <li><strong>{len(v20_violations[0]['teacher_overload'])}</strong> Teacher Overload</li>
                        <li><strong>{len(v20_violations[0]['consecutive_violations'])}</strong> Consecutive Period Violations</li>
                    </ul>
                </div>
            </div>

            <div class="version-card{' winner' if winner == 'v25' else ''}">
                <h2>{'🏆 ' if winner == 'v25' else ''}Version 2.5</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value {'success' if v25_result['success'] else 'error'}">
                            {'✓' if v25_result['success'] else '✗'}
                        </div>
                        <div class="stat-label">Status</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{v25_result['generation_time']:.2f}s</div>
                        <div class="stat-label">Generation Time</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{len(v25_result['entries'])}</div>
                        <div class="stat-label">Periods Scheduled</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value {'success' if v25_violations[1] == 0 else 'error'}">{v25_violations[1]}</div>
                        <div class="stat-label">Total Violations</div>
                    </div>
                </div>
                <div class="violations">
                    <h3>Constraint Violations</h3>
                    <ul>
                        <li><strong>{len(v25_violations[0]['teacher_conflicts'])}</strong> Teacher Conflicts</li>
                        <li><strong>{len(v25_violations[0]['room_conflicts'])}</strong> Room Conflicts</li>
                        <li><strong>{len(v25_violations[0]['class_conflicts'])}</strong> Class Conflicts</li>
                        <li><strong>{len(v25_violations[0]['teacher_overload'])}</strong> Teacher Overload</li>
                        <li><strong>{len(v25_violations[0]['consecutive_violations'])}</strong> Consecutive Period Violations</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="summary">
            <h2>Detailed Comparison</h2>
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Version 2.0</th>
                        <th>Version 2.5</th>
                        <th>Better</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Generation Time</strong></td>
                        <td>{v20_result['generation_time']:.2f}s</td>
                        <td>{v25_result['generation_time']:.2f}s</td>
                        <td class="{'winner-cell' if v20_result['generation_time'] < v25_result['generation_time'] else ''}">{
                            'v2.0 (' + str(round((1 - v20_result['generation_time']/v25_result['generation_time'])*100, 1)) + '% faster)'
                            if v20_result['generation_time'] < v25_result['generation_time']
                            else 'v2.5 (' + str(round((1 - v25_result['generation_time']/v20_result['generation_time'])*100, 1)) + '% faster)'
                        }</td>
                    </tr>
                    <tr>
                        <td><strong>Periods Scheduled</strong></td>
                        <td>{len(v20_result['entries'])}</td>
                        <td>{len(v25_result['entries'])}</td>
                        <td class="{'winner-cell' if len(v20_result['entries']) >= len(v25_result['entries']) else ''}">{
                            'v2.0' if len(v20_result['entries']) >= len(v25_result['entries']) else 'v2.5'
                        }</td>
                    </tr>
                    <tr>
                        <td><strong>Total Violations</strong></td>
                        <td class="{'error' if v20_violations[1] > 0 else 'success'}">{v20_violations[1]}</td>
                        <td class="{'error' if v25_violations[1] > 0 else 'success'}">{v25_violations[1]}</td>
                        <td class="winner-cell">{
                            'v2.0' if v20_violations[1] < v25_violations[1]
                            else 'v2.5' if v25_violations[1] < v20_violations[1]
                            else 'Tie'
                        }</td>
                    </tr>
                    <tr>
                        <td><strong>Teacher Conflicts</strong></td>
                        <td>{len(v20_violations[0]['teacher_conflicts'])}</td>
                        <td>{len(v25_violations[0]['teacher_conflicts'])}</td>
                        <td class="{'winner-cell' if len(v20_violations[0]['teacher_conflicts']) <= len(v25_violations[0]['teacher_conflicts']) else ''}">{
                            'v2.0' if len(v20_violations[0]['teacher_conflicts']) <= len(v25_violations[0]['teacher_conflicts']) else 'v2.5'
                        }</td>
                    </tr>
                    <tr>
                        <td><strong>Room Conflicts</strong></td>
                        <td>{len(v20_violations[0]['room_conflicts'])}</td>
                        <td>{len(v25_violations[0]['room_conflicts'])}</td>
                        <td class="{'winner-cell' if len(v20_violations[0]['room_conflicts']) <= len(v25_violations[0]['room_conflicts']) else ''}">{
                            'v2.0' if len(v20_violations[0]['room_conflicts']) <= len(v25_violations[0]['room_conflicts']) else 'v2.5'
                        }</td>
                    </tr>
                    <tr>
                        <td><strong>Class Conflicts</strong></td>
                        <td>{len(v20_violations[0]['class_conflicts'])}</td>
                        <td>{len(v25_violations[0]['class_conflicts'])}</td>
                        <td class="{'winner-cell' if len(v20_violations[0]['class_conflicts']) <= len(v25_violations[0]['class_conflicts']) else ''}">{
                            'v2.0' if len(v20_violations[0]['class_conflicts']) <= len(v25_violations[0]['class_conflicts']) else 'v2.5'
                        }</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
'''

    output_file = BASE_PATH / f"ab_comparison_{TT_ID}_{timestamp}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_file

if __name__ == "__main__":
    print("="*60)
    print("A/B TEST: v2.0 vs v2.5")
    print("="*60)

    # Load data
    data, teacher_info, class_info = load_data()

    # Test v2.0 on port 8001
    v20_result = test_engine('v20', 8001, data)
    if not v20_result:
        print("\nv2.0 test failed!")
        sys.exit(1)

    # Test v2.5 on port 8002
    v25_result = test_engine('v25', 8002, data)
    if not v25_result:
        print("\nv2.5 test failed!")
        sys.exit(1)

    # Validate constraints
    v20_violations = validate_constraints(v20_result, teacher_info)
    v25_violations = validate_constraints(v25_result, teacher_info)

    # Create report
    report_file = create_html_report(v20_result, v25_result, v20_violations, v25_violations)

    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"v2.0: {v20_result['generation_time']:.2f}s, {len(v20_result['entries'])} entries, {v20_violations[1]} violations")
    print(f"v2.5: {v25_result['generation_time']:.2f}s, {len(v25_result['entries'])} entries, {v25_violations[1]} violations")
    print(f"\nReport: {report_file}")

    # Open report
    import webbrowser
    webbrowser.open(str(report_file))
