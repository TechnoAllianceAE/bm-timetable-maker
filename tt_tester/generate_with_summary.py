#!/usr/bin/env python3
"""
Timetable Generator with Comprehensive Summary Report
Shows variations, pros/cons, teacher workload analysis
"""
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

BASE_PATH = Path(__file__).parent

class TimetableGeneratorWithSummary:
    def __init__(self, tt_id, version="v25", port=8002):
        self.tt_id = tt_id
        self.version = version
        self.port = port
        self.base_path = BASE_PATH

    def load_data(self):
        """Load test data"""
        print(f"Loading data for {self.tt_id}...")

        # Load subjects
        subject_code_to_name = {}
        subjects = []
        with open(self.base_path / f"data_subjects_{self.tt_id}.csv", 'r') as f:
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
        with open(self.base_path / f"data_classes_{self.tt_id}.csv", 'r') as f:
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
        with open(self.base_path / f"data_teachers_{self.tt_id}.csv", 'r') as f:
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
                    "max_periods_per_week": int(row['max_periods_per_week']),
                    "max_periods_per_day": int(row['max_periods_per_day']),
                    "subjects": subject_codes,
                    "email": row['email']
                }

        # Load rooms
        rooms = []
        with open(self.base_path / f"data_rooms_{self.tt_id}.csv", 'r') as f:
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
        with open(self.base_path / f"data_assignments_{self.tt_id}.csv", 'r') as f:
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
            "tt_generation_id": self.tt_id,
            "classes": classes,
            "teachers": teachers,
            "subjects": subjects,
            "rooms": rooms,
            "time_slots": time_slots,
            "assignments": assignments,
            "constraints": [],
            "options": 3,  # Request 3 variations
            "timeout": 180
        }

        return request_data, teacher_info, class_info

    def generate_timetable(self, data):
        """Generate timetable"""
        print(f"\nGenerating timetable using {self.version} on port {self.port}...")

        url = f"http://localhost:{self.port}/generate"

        start_time = time.time()
        response = requests.post(url, json=data, timeout=300)
        end_time = time.time()

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return None

        result = response.json()
        result['generation_time'] = end_time - start_time

        return result

    def analyze_solution(self, solution, teacher_info):
        """Analyze a single solution"""
        timetable = solution.get('timetable', {})
        entries = timetable.get('entries', [])

        # Teacher workload analysis
        teacher_periods = defaultdict(int)
        teacher_daily_periods = defaultdict(lambda: defaultdict(int))
        teacher_consecutive = defaultdict(lambda: defaultdict(list))

        # Conflict tracking
        teacher_schedule = defaultdict(lambda: defaultdict(set))
        room_schedule = defaultdict(lambda: defaultdict(set))
        class_schedule = defaultdict(lambda: defaultdict(set))

        violations = {
            'teacher_conflicts': [],
            'room_conflicts': [],
            'class_conflicts': [],
            'teacher_overload': [],
            'consecutive_violations': []
        }

        for entry in entries:
            teacher_id = entry.get('teacher_id')
            room_id = entry.get('room_id')
            class_id = entry.get('class_id')
            day = entry.get('day_of_week')
            period = entry.get('period_number')

            if not all([teacher_id, day, period, class_id]):
                continue

            # Count periods
            teacher_periods[teacher_id] += 1
            teacher_daily_periods[teacher_id][day] += 1
            teacher_consecutive[teacher_id][day].append(period)

            # Check conflicts
            if period in teacher_schedule[teacher_id][day]:
                violations['teacher_conflicts'].append(f"{teacher_id} @ {day} P{period}")
            teacher_schedule[teacher_id][day].add(period)

            if room_id and period in room_schedule[room_id][day]:
                violations['room_conflicts'].append(f"{room_id} @ {day} P{period}")
            if room_id:
                room_schedule[room_id][day].add(period)

            if period in class_schedule[class_id][day]:
                violations['class_conflicts'].append(f"{class_id} @ {day} P{period}")
            class_schedule[class_id][day].add(period)

        # Check overload
        for teacher_id, days in teacher_daily_periods.items():
            max_per_day = teacher_info.get(teacher_id, {}).get('max_periods_per_day', 8)
            for day, count in days.items():
                if count > max_per_day:
                    violations['teacher_overload'].append(f"{teacher_id} on {day}: {count}/{max_per_day}")

        # Check consecutive
        for teacher_id, days in teacher_consecutive.items():
            for day, periods in days.items():
                sorted_periods = sorted(periods)
                consecutive = 1
                for i in range(1, len(sorted_periods)):
                    if sorted_periods[i] == sorted_periods[i-1] + 1:
                        consecutive += 1
                        if consecutive > 3:
                            violations['consecutive_violations'].append(f"{teacher_id} on {day}: {consecutive}+ consecutive")
                            break
                    else:
                        consecutive = 1

        # Calculate teacher utilization
        overworked = []  # >90% of max
        optimal = []  # 60-90% of max
        underutilized = []  # <15% of max

        for teacher_id, periods in teacher_periods.items():
            max_periods = teacher_info.get(teacher_id, {}).get('max_periods_per_week', 40)
            utilization = (periods / max_periods) * 100
            teacher_name = teacher_info.get(teacher_id, {}).get('name', teacher_id)

            if utilization > 90:
                overworked.append({
                    'id': teacher_id,
                    'name': teacher_name,
                    'periods': periods,
                    'max': max_periods,
                    'utilization': utilization
                })
            elif utilization >= 60:
                optimal.append({
                    'id': teacher_id,
                    'name': teacher_name,
                    'periods': periods,
                    'max': max_periods,
                    'utilization': utilization
                })
            elif utilization < 15:
                underutilized.append({
                    'id': teacher_id,
                    'name': teacher_name,
                    'periods': periods,
                    'max': max_periods,
                    'utilization': utilization
                })

        # Sort by periods
        overworked.sort(key=lambda x: x['periods'], reverse=True)
        underutilized.sort(key=lambda x: x['utilization'])

        return {
            'total_entries': len(entries),
            'violations': violations,
            'total_violations': sum(len(v) for v in violations.values()),
            'teacher_workload': {
                'overworked': overworked,
                'optimal': optimal,
                'underutilized': underutilized
            }
        }

    def create_summary_html(self, result, teacher_info, class_info):
        """Create comprehensive summary HTML"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        solutions = result.get('solutions', [])
        generation_time = result.get('generation_time', 0)

        # Analyze all solutions
        analyses = []
        for idx, solution in enumerate(solutions):
            analysis = self.analyze_solution(solution, teacher_info)
            analysis['index'] = idx + 1
            analyses.append(analysis)

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timetable Generation Summary</title>
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
        .header h1 {{ font-size: 42px; color: #2d3748; margin-bottom: 10px; }}
        .subtitle {{ font-size: 16px; color: #718096; margin: 5px 0; }}
        .section {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .section h2 {{
            font-size: 28px;
            color: #2d3748;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f7fafc;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            text-align: center;
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: 800;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 14px;
            color: #718096;
            font-weight: 600;
        }}
        .variation-card {{
            background: #f7fafc;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
        }}
        .variation-card.best {{
            border-left-color: #48bb78;
            background: #f0fff4;
        }}
        .variation-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .variation-title {{
            font-size: 24px;
            font-weight: 700;
            color: #2d3748;
        }}
        .variation-badge {{
            background: #48bb78;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 700;
        }}
        .pros-cons {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .pros, .cons {{
            background: white;
            padding: 20px;
            border-radius: 12px;
        }}
        .pros {{
            border-left: 4px solid #48bb78;
        }}
        .cons {{
            border-left: 4px solid #f56565;
        }}
        .pros h4, .cons h4 {{
            font-size: 16px;
            margin-bottom: 10px;
            color: #2d3748;
        }}
        .pros ul, .cons ul {{
            list-style: none;
            padding: 0;
        }}
        .pros li, .cons li {{
            padding: 5px 0;
            font-size: 14px;
        }}
        .pros li:before {{
            content: "✓ ";
            color: #48bb78;
            font-weight: 700;
        }}
        .cons li:before {{
            content: "✗ ";
            color: #f56565;
            font-weight: 700;
        }}
        .teacher-list {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-top: 15px;
        }}
        .teacher-list h4 {{
            font-size: 16px;
            margin-bottom: 15px;
            color: #2d3748;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: #f7fafc;
            font-weight: 700;
            color: #4a5568;
            font-size: 14px;
        }}
        td {{
            font-size: 14px;
        }}
        .success {{ color: #48bb78; }}
        .warning {{ color: #ed8936; }}
        .error {{ color: #f56565; }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-success {{ background: #c6f6d5; color: #22543d; }}
        .badge-warning {{ background: #feebc8; color: #7c2d12; }}
        .badge-error {{ background: #fed7d7; color: #742a2a; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Timetable Generation Summary</h1>
            <div class="subtitle">Generated using {self.version.upper()} Engine</div>
            <div class="subtitle">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
            <div class="subtitle">TT ID: {self.tt_id}</div>
        </div>

        <div class="section">
            <h2>Overview</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(solutions)}</div>
                    <div class="stat-label">Variations Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{generation_time:.2f}s</div>
                    <div class="stat-label">Generation Time</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(class_info)}</div>
                    <div class="stat-label">Classes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(teacher_info)}</div>
                    <div class="stat-label">Teachers</div>
                </div>
            </div>
        </div>
'''

        # Best solution
        best_idx = min(range(len(analyses)), key=lambda i: analyses[i]['total_violations'])

        for idx, analysis in enumerate(analyses):
            is_best = idx == best_idx
            violations = analysis['violations']
            workload = analysis['teacher_workload']

            html += f'''
        <div class="section">
            <div class="variation-card{'  best' if is_best else ''}">
                <div class="variation-header">
                    <div class="variation-title">Variation #{analysis['index']}</div>
                    {f'<div class="variation-badge">RECOMMENDED</div>' if is_best else ''}
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{analysis['total_entries']}</div>
                        <div class="stat-label">Periods Scheduled</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value {'success' if analysis['total_violations'] == 0 else 'error'}">{analysis['total_violations']}</div>
                        <div class="stat-label">Total Violations</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value {'error' if len(workload['overworked']) > 0 else 'success'}">{len(workload['overworked'])}</div>
                        <div class="stat-label">Overworked Teachers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value {'warning' if len(workload['underutilized']) > 0 else 'success'}">{len(workload['underutilized'])}</div>
                        <div class="stat-label">Underutilized Teachers</div>
                    </div>
                </div>

                <div class="pros-cons">
                    <div class="pros">
                        <h4>Pros</h4>
                        <ul>
'''

            # Generate pros
            if len(violations['teacher_conflicts']) == 0:
                html += '<li>No teacher scheduling conflicts</li>\n'
            if len(violations['room_conflicts']) == 0:
                html += '<li>No room double-booking</li>\n'
            if len(violations['class_conflicts']) == 0:
                html += '<li>No class conflicts</li>\n'
            if len(workload['overworked']) == 0:
                html += '<li>No overworked teachers (>90% capacity)</li>\n'
            if len(workload['optimal']) > len(teacher_info) * 0.7:
                html += f'<li>Most teachers optimally utilized (60-90%)</li>\n'
            if analysis['total_violations'] == 0:
                html += '<li>Perfect constraint compliance</li>\n'

            html += '''
                        </ul>
                    </div>
                    <div class="cons">
                        <h4>Cons</h4>
                        <ul>
'''

            # Generate cons
            if len(violations['teacher_conflicts']) > 0:
                html += f'<li>{len(violations["teacher_conflicts"])} teacher conflicts</li>\n'
            if len(violations['room_conflicts']) > 0:
                html += f'<li>{len(violations["room_conflicts"])} room conflicts</li>\n'
            if len(violations['consecutive_violations']) > 0:
                html += f'<li>{len(violations["consecutive_violations"])} consecutive period violations</li>\n'
            if len(workload['overworked']) > 0:
                html += f'<li>{len(workload["overworked"])} teachers overworked</li>\n'
            if len(workload['underutilized']) > 0:
                html += f'<li>{len(workload["underutilized"])} teachers underutilized (<15%)</li>\n'
            if analysis['total_violations'] == 0 and len(workload['underutilized']) == 0 and len(workload['overworked']) == 0:
                html += '<li>None - excellent solution!</li>\n'

            html += '''
                        </ul>
                    </div>
                </div>
'''

            # Overworked teachers
            if workload['overworked']:
                html += '''
                <div class="teacher-list">
                    <h4>Most Loaded Teachers (>90% capacity)</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>Teacher</th>
                                <th>Periods Assigned</th>
                                <th>Max Capacity</th>
                                <th>Utilization</th>
                            </tr>
                        </thead>
                        <tbody>
'''
                for teacher in workload['overworked'][:10]:  # Top 10
                    html += f'''
                            <tr>
                                <td>{teacher['name']}</td>
                                <td>{teacher['periods']}</td>
                                <td>{teacher['max']}</td>
                                <td><span class="badge badge-error">{teacher['utilization']:.1f}%</span></td>
                            </tr>
'''
                html += '''
                        </tbody>
                    </table>
                </div>
'''

            # Underutilized teachers
            if workload['underutilized']:
                html += '''
                <div class="teacher-list">
                    <h4>Underutilized Teachers (<15% capacity)</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>Teacher</th>
                                <th>Periods Assigned</th>
                                <th>Max Capacity</th>
                                <th>Utilization</th>
                            </tr>
                        </thead>
                        <tbody>
'''
                for teacher in workload['underutilized']:
                    html += f'''
                            <tr>
                                <td>{teacher['name']}</td>
                                <td>{teacher['periods']}</td>
                                <td>{teacher['max']}</td>
                                <td><span class="badge badge-warning">{teacher['utilization']:.1f}%</span></td>
                            </tr>
'''
                html += '''
                        </tbody>
                    </table>
                </div>
'''

            html += '''
            </div>
        </div>
'''

        html += '''
    </div>
</body>
</html>
'''

        output_file = self.base_path / f"summary_{self.tt_id}_{timestamp}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_file

    def run(self):
        """Run complete generation with summary"""
        data, teacher_info, class_info = self.load_data()
        result = self.generate_timetable(data)

        if not result:
            print("Failed to generate timetable")
            return None

        solutions = result.get('solutions', [])
        print(f"\nGenerated {len(solutions)} variations")
        print(f"Generation time: {result.get('generation_time', 0):.2f}s")

        report_file = self.create_summary_html(result, teacher_info, class_info)

        print(f"\nSummary report created: {report_file}")

        # Open in browser
        import webbrowser
        webbrowser.open(str(report_file))

        return report_file

if __name__ == "__main__":
    import sys

    # Default to large dataset
    tt_id = "TT_20251004_121258_40b399a6"
    version = "v25"
    port = 8002

    if len(sys.argv) > 1:
        tt_id = sys.argv[1]
    if len(sys.argv) > 2:
        version = sys.argv[2]
    if len(sys.argv) > 3:
        port = int(sys.argv[3])

    generator = TimetableGeneratorWithSummary(tt_id, version, port)
    generator.run()
