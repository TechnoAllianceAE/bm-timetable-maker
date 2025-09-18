#!/usr/bin/env python3
"""
Generate timetable for 14 classes with 6 subjects using working test format.
Creates an HTML report with visualization.
"""

import requests
import json
from datetime import datetime
import os

# Calculate optimal teacher allocation
def get_teacher_allocation():
    """Calculate optimal teacher counts for 14 classes."""
    return {
        "Mathematics": 4,      # 14 classes * 5 periods = 70 periods / ~18 per teacher
        "Science": 3,          # 14 classes * 4 periods = 56 periods / ~19 per teacher
        "English": 3,          # 14 classes * 4 periods = 56 periods / ~19 per teacher
        "Social Studies": 3,   # 14 classes * 3 periods = 42 periods / ~14 per teacher
        "Computer Science": 2, # 14 classes * 2 periods = 28 periods / ~14 per teacher
        "Physical Education": 2 # 14 classes * 2 periods = 28 periods / ~14 per teacher
    }

def create_test_request():
    """Create working test request for 14 classes."""

    # Create 14 classes - using working format
    classes = []
    grade_sections = [
        ("6", "A"), ("6", "B"),
        ("7", "A"), ("7", "B"),
        ("8", "A"), ("8", "B"),
        ("9", "A"), ("9", "B"),
        ("10", "A"), ("10", "B"),
        ("11", "A"), ("11", "B"),
        ("12", "A"), ("12", "B")
    ]

    for grade, section in grade_sections:
        classes.append({
            "id": f"class-{grade}{section}",
            "school_id": "school-001",
            "name": f"{grade}-{section}",
            "grade": int(grade),
            "section": section,
            "student_count": 30 + (int(grade) % 3) * 2
        })

    # Create 6 subjects
    subjects = [
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
        },
        {
            "id": "sub-soc",
            "school_id": "school-001",
            "name": "Social Studies",
            "code": "SOC",
            "periods_per_week": 3,
            "requires_lab": False,
            "is_elective": False
        },
        {
            "id": "sub-cs",
            "school_id": "school-001",
            "name": "Computer Science",
            "code": "CS",
            "periods_per_week": 2,
            "requires_lab": True,
            "is_elective": False
        },
        {
            "id": "sub-pe",
            "school_id": "school-001",
            "name": "Physical Education",
            "code": "PE",
            "periods_per_week": 2,
            "requires_lab": False,
            "is_elective": False
        }
    ]

    # Create optimal teachers
    teachers = []
    teacher_allocation = get_teacher_allocation()
    teacher_id = 1

    for subject, count in teacher_allocation.items():
        for i in range(count):
            teachers.append({
                "id": f"teacher-{teacher_id:03d}",
                "user_id": f"user-{teacher_id:03d}",
                "subjects": [subject],
                "max_periods_per_day": 6,
                "max_periods_per_week": 25,
                "max_consecutive_periods": 3
            })
            teacher_id += 1

    # Create time slots (40 per week)
    time_slots = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    for day_idx, day in enumerate(days):
        for period in range(1, 9):
            time_slots.append({
                "id": f"slot-{day_idx * 8 + period - 1}",
                "school_id": "school-001",
                "day_of_week": day,
                "period_number": period,
                "start_time": f"{7 + period}:00",
                "end_time": f"{8 + period}:00",
                "is_break": False
            })

    # Create rooms (including labs)
    rooms = []

    # Regular classrooms
    for i in range(14):
        rooms.append({
            "id": f"room-{i+1:02d}",
            "school_id": "school-001",
            "name": f"Classroom {i+1}",
            "building": "Main",
            "floor": 1 + (i // 7),  # Distribute across floors
            "capacity": 40,
            "type": "CLASSROOM",
            "facilities": ["projector", "whiteboard"]
        })

    # Science labs
    for i in range(3):
        rooms.append({
            "id": f"room-sci-lab-{i+1}",
            "school_id": "school-001",
            "name": f"Science Lab {i+1}",
            "building": "Science Block",
            "floor": 1,
            "capacity": 35,
            "type": "LAB",
            "facilities": ["lab_equipment", "sink", "gas"]
        })

    # Computer labs
    for i in range(2):
        rooms.append({
            "id": f"room-comp-lab-{i+1}",
            "school_id": "school-001",
            "name": f"Computer Lab {i+1}",
            "building": "Tech Block",
            "floor": 2,
            "capacity": 35,
            "type": "LAB",
            "facilities": ["computers", "projector", "internet"]
        })

    # Sports area
    rooms.append({
        "id": "room-sports",
        "school_id": "school-001",
        "name": "Sports Ground",
        "building": "Outdoor",
        "floor": 0,
        "capacity": 100,
        "type": "SPORTS",
        "facilities": ["field", "track"]
    })

    # Simple constraints - just two basic ones
    constraints = [
        {
            "id": "const-1",
            "school_id": "school-001",
            "type": "MIN_PERIODS_PER_WEEK",
            "entity_type": "SUBJECT",
            "entity_id": "sub-math",
            "priority": "HIGH",
            "description": "Math minimum periods",
            "parameters": {"min_periods": 5}
        },
        {
            "id": "const-2",
            "school_id": "school-001",
            "type": "ROOM_CAPACITY",
            "entity_type": "ROOM",
            "entity_id": "room-01",
            "priority": "MEDIUM",
            "description": "Room capacity",
            "parameters": {"max_students": 40}
        }
    ]

    return {
        "school_id": "school-001",
        "academic_year_id": "year-2024",
        "classes": classes,
        "subjects": subjects,
        "teachers": teachers,
        "time_slots": time_slots,
        "rooms": rooms,
        "constraints": constraints,
        "weights": {
            "academic_requirements": 0.4,
            "teacher_preferences": 0.2,
            "resource_utilization": 0.2,
            "gap_minimization": 0.2
        },
        "options": 3
    }

def generate_html_report(request, response):
    """Generate HTML visualization report."""

    classes_count = len(request['classes'])
    subjects_count = len(request['subjects'])
    teachers_count = len(request['teachers'])

    # Calculate total periods needed
    total_periods = sum(s['periods_per_week'] for s in request['subjects']) * classes_count

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timetable Report - {classes_count} Classes × {subjects_count} Subjects</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }}

        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .stat-card .value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }}

        .stat-card .label {{
            font-size: 0.9rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-size: 1.8rem;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }}

        td {{
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .success {{
            color: #28a745;
            font-weight: bold;
        }}

        .error {{
            color: #dc3545;
            font-weight: bold;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .teacher-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .teacher-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .teacher-card h4 {{
            margin-bottom: 10px;
            color: #495057;
        }}

        .result-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}

        .result-success {{
            border-left: 4px solid #28a745;
        }}

        .result-error {{
            border-left: 4px solid #dc3545;
        }}

        .timetable-preview {{
            overflow-x: auto;
            margin-top: 20px;
        }}

        .timetable-grid {{
            display: grid;
            grid-template-columns: 80px repeat(8, 1fr);
            gap: 1px;
            background: #dee2e6;
            min-width: 800px;
        }}

        .timetable-cell {{
            background: white;
            padding: 8px;
            min-height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
        }}

        .timetable-header {{
            background: #667eea;
            color: white;
            font-weight: bold;
        }}

        .timetable-day {{
            background: #f8f9fa;
            font-weight: 600;
        }}

        .period-entry {{
            text-align: center;
            font-size: 0.75rem;
        }}

        .period-subject {{
            font-weight: bold;
            color: #667eea;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Timetable Generation Report</h1>
            <div class="subtitle">{classes_count} Classes × {subjects_count} Subjects</div>
            <div style="margin-top: 15px; font-size: 0.9rem;">
                Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </div>
        </div>

        <div class="content">
            <!-- Statistics Overview -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="label">Classes</div>
                    <div class="value">{classes_count}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Subjects</div>
                    <div class="value">{subjects_count}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Teachers</div>
                    <div class="value">{teachers_count}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Total Periods</div>
                    <div class="value">{total_periods}</div>
                </div>
            </div>

            <!-- Teacher Allocation Section -->
            <div class="section">
                <h2 class="section-title">👥 Teacher Allocation</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>Periods/Week per Class</th>
                            <th>Total Periods ({classes_count} classes)</th>
                            <th>Teachers Allocated</th>
                            <th>Avg Load per Teacher</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    # Add teacher allocation details
    teacher_allocation = get_teacher_allocation()
    subject_periods = {
        "Mathematics": 5,
        "Science": 4,
        "English": 4,
        "Social Studies": 3,
        "Computer Science": 2,
        "Physical Education": 2
    }

    for subject, periods in subject_periods.items():
        total = periods * classes_count
        teachers = teacher_allocation[subject]
        avg_load = total / teachers
        html += f"""
                        <tr>
                            <td><strong>{subject}</strong></td>
                            <td>{periods}</td>
                            <td>{total}</td>
                            <td>{teachers}</td>
                            <td>{avg_load:.1f}</td>
                        </tr>
"""

    html += """
                    </tbody>
                </table>
            </div>

            <!-- Generation Results -->
            <div class="section">
                <h2 class="section-title">📊 Generation Results</h2>
"""

    if response and response.get('status') == 'success':
        result = response['data']
        html += f"""
                <div class="result-box result-success">
                    <h3 class="success">✅ Timetable Generated Successfully!</h3>
                    <p style="margin-top: 10px;">
                        <strong>Generation Time:</strong> {result.get('generation_time', 0):.2f} seconds<br>
                        <strong>Solutions Generated:</strong> {len(result.get('solutions', []))}<br>
                    </p>
                </div>
"""

        # Show solution details
        if result.get('solutions'):
            html += """
                <h3 style="margin-top: 20px;">Generated Solutions:</h3>
                <table style="margin-top: 10px;">
                    <thead>
                        <tr>
                            <th>Solution #</th>
                            <th>Score</th>
                            <th>Feasible</th>
                            <th>Entries</th>
                            <th>Conflicts</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for i, sol in enumerate(result['solutions'][:3], 1):
                feasible = "✅ Yes" if sol['feasible'] else "❌ No"
                html += f"""
                        <tr>
                            <td>Solution {i}</td>
                            <td>{sol['total_score']:.2f}</td>
                            <td>{feasible}</td>
                            <td>{len(sol['timetable']['entries'])}</td>
                            <td>{len(sol.get('conflicts', []))}</td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
"""

            # Sample timetable preview
            if result['solutions'][0]['timetable']['entries']:
                html += """
                <h3 style="margin-top: 30px;">Sample Timetable (Class 6-A)</h3>
                <div class="timetable-preview">
                    <div class="timetable-grid">
                        <div class="timetable-cell timetable-header">Time</div>
"""
                for p in range(1, 9):
                    html += f'<div class="timetable-cell timetable-header">Period {p}</div>'

                days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
                sample_entries = [e for e in result['solutions'][0]['timetable']['entries'] if e.get('class_id') == 'class-6A']

                for day in days[:3]:  # Show first 3 days
                    html += f'<div class="timetable-cell timetable-day">{day}</div>'
                    for period in range(1, 9):
                        entry = next((e for e in sample_entries if e.get('day_of_week') == day and e.get('period_number') == period), None)
                        if entry:
                            subject = entry.get('subject_id', '').replace('sub-', '').upper()
                            html += f'<div class="timetable-cell"><div class="period-entry"><span class="period-subject">{subject}</span></div></div>'
                        else:
                            html += '<div class="timetable-cell">-</div>'

                html += """
                    </div>
                </div>
"""

    else:
        error_msg = response.get('error', 'Unknown error') if response else 'No response from service'
        html += f"""
                <div class="result-box result-error">
                    <h3 class="error">❌ Generation Failed</h3>
                    <p style="margin-top: 10px;">
                        <strong>Error:</strong> {error_msg}
                    </p>
                </div>
"""

    html += """
            </div>

            <!-- Summary -->
            <div class="section">
                <h2 class="section-title">📝 Summary</h2>
                <p>
                    This report shows the timetable generation attempt for <strong>{classes_count} classes</strong> across
                    <strong>{subjects_count} subjects</strong> with <strong>{teachers_count} teachers</strong>.
                    The system uses Constraint Satisfaction Problem (CSP) solver with Genetic Algorithm (GA) optimization
                    to generate conflict-free timetables.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
""".format(
        classes_count=classes_count,
        subjects_count=subjects_count,
        teachers_count=teachers_count
    )

    return html

def main():
    print("=" * 70)
    print("GENERATING TIMETABLE FOR 14 CLASSES × 6 SUBJECTS")
    print("=" * 70)
    print()

    # Create request
    print("📋 Preparing request data...")
    request_data = create_test_request()

    print(f"✓ Classes: {len(request_data['classes'])}")
    print(f"✓ Subjects: {len(request_data['subjects'])}")
    print(f"✓ Teachers: {len(request_data['teachers'])}")
    print(f"✓ Time Slots: {len(request_data['time_slots'])}")
    print(f"✓ Rooms: {len(request_data['rooms'])}")
    print()

    # Show teacher allocation
    print("👥 Teacher Allocation:")
    teacher_alloc = get_teacher_allocation()
    for subject, count in teacher_alloc.items():
        print(f"  {subject}: {count} teachers")
    print()

    # Call service
    print("🚀 Calling timetable generation service...")
    try:
        response = requests.post(
            'http://localhost:8000/generate',
            json=request_data,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS! Generated in {result['generation_time']:.2f} seconds")
            print(f"   Solutions: {len(result['solutions'])}")

            response_data = {
                'status': 'success',
                'data': result
            }
        else:
            print(f"❌ Error {response.status_code}")
            print(f"   {response.text[:200]}")

            response_data = {
                'status': 'error',
                'error': response.text
            }

    except Exception as e:
        print(f"❌ Request failed: {e}")
        response_data = {
            'status': 'error',
            'error': str(e)
        }

    print()

    # Generate HTML report
    print("📝 Generating HTML report...")
    html_content = generate_html_report(request_data, response_data)

    # Save report
    report_file = "timetable_14classes_report.html"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Report saved to: {report_file}")
    print()
    print("🎉 Done! Open the HTML file to view the results.")
    print("=" * 70)

if __name__ == "__main__":
    main()