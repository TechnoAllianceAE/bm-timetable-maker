#!/usr/bin/env python3
"""
Generate a timetable and create comprehensive HTML visualization
showing all class and teacher schedules
"""

import csv
import json
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_csv_data(tt_id):
    """Load CSV data for a given TT ID"""
    base_path = Path(__file__).parent

    # First, load subjects to create code->name mapping
    subject_code_to_name = {}
    subjects = []
    with open(base_path / f"data_subjects_{tt_id}.csv", 'r') as f:
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

    # Load teachers - convert subject codes to names
    teachers = []
    teacher_info = {}
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
            teacher_info[row['teacher_id']] = {
                "name": row['name'],
                "subjects": subject_codes
            }

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

    # Load assignments
    assignments = []
    assignment_map = {}
    with open(base_path / f"data_assignments_{tt_id}.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            assignments.append({
                "id": row['assignment_id'],
                "teacher_id": row['teacher_id'],
                "class_id": row['class_id'],
                "subject_code": row['subject_code'],
                "periods_per_week": int(row['periods_per_week'])
            })
            key = f"{row['class_id']}_{row['subject_code']}"
            assignment_map[key] = {
                "teacher_id": row['teacher_id'],
                "teacher_name": row['teacher_name']
            }

    # Create time slots (40 per week = 5 days × 8 periods)
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

    return {
        "school_id": "test-school",
        "academic_year_id": "2024-2025",
        "tt_generation_id": tt_id,
        "classes": classes,
        "teachers": teachers,
        "subjects": subjects,
        "rooms": rooms,
        "time_slots": time_slots,
        "assignments": assignments
    }, teacher_info, assignment_map, subject_code_to_name


def create_mock_timetable(data, teacher_info, assignment_map, subject_code_to_name):
    """Create a mock complete timetable by distributing assignments across time slots"""
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    periods_per_day = 8

    # Create schedules for each class
    class_schedules = {}
    teacher_schedules = defaultdict(lambda: defaultdict(list))

    for class_obj in data['classes']:
        class_id = class_obj['id']
        class_name = class_obj['name']
        schedule = defaultdict(list)

        # Get assignments for this class
        class_assignments = [a for a in data['assignments'] if a['class_id'] == class_id]

        # Distribute periods across the week
        period_count = {a['subject_code']: 0 for a in class_assignments}
        period_target = {a['subject_code']: a['periods_per_week'] for a in class_assignments}

        slot_idx = 0
        for day in days:
            for period in range(1, periods_per_day + 1):
                # Find a subject that still needs periods
                assigned = False
                for assignment in class_assignments:
                    subject_code = assignment['subject_code']
                    if period_count[subject_code] < period_target[subject_code]:
                        # Assign this period
                        key = f"{class_id}_{subject_code}"
                        teacher_id = assignment_map.get(key, {}).get('teacher_id', 'Unknown')
                        teacher_name = assignment_map.get(key, {}).get('teacher_name', 'Unknown Teacher')
                        subject_name = subject_code_to_name.get(subject_code, subject_code)

                        schedule[day].append({
                            'period': period,
                            'subject': subject_name,
                            'subject_code': subject_code,
                            'teacher': teacher_name,
                            'teacher_id': teacher_id
                        })

                        # Track teacher schedule
                        teacher_schedules[teacher_id][day].append({
                            'period': period,
                            'class': class_name,
                            'subject': subject_name
                        })

                        period_count[subject_code] += 1
                        assigned = True
                        break

                if not assigned:
                    # Free period
                    schedule[day].append({
                        'period': period,
                        'subject': 'Free Period',
                        'subject_code': '',
                        'teacher': '',
                        'teacher_id': ''
                    })

                slot_idx += 1

        class_schedules[class_id] = {
            'name': class_name,
            'schedule': schedule
        }

    return class_schedules, teacher_schedules, teacher_info


def generate_html_report(class_schedules, teacher_schedules, teacher_info, tt_id):
    """Generate comprehensive HTML report with class and teacher timetables"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Timetable - {tt_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 42px;
            color: #2d3748;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 18px;
            color: #718096;
        }}

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
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .timetable-grid {{
            overflow-x: auto;
            margin-bottom: 40px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 10px;
            text-align: center;
            font-weight: 600;
            font-size: 14px;
        }}

        td {{
            padding: 12px 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
            font-size: 12px;
        }}

        tr:nth-child(even) {{
            background: #f7fafc;
        }}

        .period-cell {{
            background: #edf2f7;
            font-weight: 600;
        }}

        .subject {{
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 4px;
        }}

        .teacher {{
            font-size: 11px;
            color: #718096;
        }}

        .free-period {{
            color: #a0aec0;
            font-style: italic;
        }}

        .class-title {{
            background: #667eea;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            font-size: 20px;
            font-weight: 700;
        }}

        .nav-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .nav-tab {{
            padding: 10px 20px;
            background: #edf2f7;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }}

        .nav-tab:hover {{
            background: #667eea;
            color: white;
        }}

        .nav-tab.active {{
            background: #667eea;
            color: white;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: 800;
            color: #2d3748;
        }}

        .stat-label {{
            font-size: 14px;
            color: #718096;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Complete School Timetable</h1>
            <div class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
            <div class="subtitle">TT ID: {tt_id}</div>
        </div>

        <div class="section">
            <h2>📊 Overview Statistics</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{len(class_schedules)}</div>
                    <div class="stat-label">Total Classes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(teacher_schedules)}</div>
                    <div class="stat-label">Teachers Assigned</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">40</div>
                    <div class="stat-label">Periods per Week</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">5</div>
                    <div class="stat-label">Days per Week</div>
                </div>
            </div>
        </div>
"""

    # CLASS TIMETABLES SECTION
    html += """
        <div class="section">
            <h2>📚 Class Timetables</h2>
            <div class="nav-tabs" id="classTabs">
"""

    for idx, (class_id, class_data) in enumerate(sorted(class_schedules.items())):
        active = "active" if idx == 0 else ""
        html += f'<button class="nav-tab {active}" onclick="showTab(\'class\', \'{class_id}\')">{class_data["name"]}</button>\n'

    html += """
            </div>
"""

    # Class timetable tables
    for idx, (class_id, class_data) in enumerate(sorted(class_schedules.items())):
        active = "active" if idx == 0 else ""
        html += f"""
            <div id="class-{class_id}" class="tab-content {active}">
                <div class="class-title">{class_data['name']} - Weekly Schedule</div>
                <div class="timetable-grid">
                    <table>
                        <thead>
                            <tr>
                                <th>Period</th>
                                <th>Monday</th>
                                <th>Tuesday</th>
                                <th>Wednesday</th>
                                <th>Thursday</th>
                                <th>Friday</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for period in range(1, 9):
            html += f"<tr><td class='period-cell'>Period {period}<br>{7+period}:00-{8+period}:00</td>"
            for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                period_data = [p for p in class_data['schedule'][day] if p['period'] == period]
                if period_data:
                    pd = period_data[0]
                    if pd['subject'] == 'Free Period':
                        html += f"<td class='free-period'>{pd['subject']}</td>"
                    else:
                        html += f"<td><div class='subject'>{pd['subject']}</div><div class='teacher'>{pd['teacher']}</div></td>"
                else:
                    html += "<td class='free-period'>-</td>"
            html += "</tr>\n"

        html += """
                        </tbody>
                    </table>
                </div>
            </div>
"""

    html += """
        </div>
"""

    # TEACHER TIMETABLES SECTION
    html += """
        <div class="section">
            <h2>👨‍🏫 Teacher Timetables</h2>
            <div class="nav-tabs" id="teacherTabs">
"""

    for idx, (teacher_id, schedule) in enumerate(sorted(teacher_schedules.items())):
        teacher_name = teacher_info.get(teacher_id, {}).get('name', teacher_id)
        active = "active" if idx == 0 else ""
        html += f'<button class="nav-tab {active}" onclick="showTab(\'teacher\', \'{teacher_id}\')">{teacher_name}</button>\n'

    html += """
            </div>
"""

    # Teacher timetable tables
    for idx, (teacher_id, schedule) in enumerate(sorted(teacher_schedules.items())):
        teacher_name = teacher_info.get(teacher_id, {}).get('name', teacher_id)
        teacher_subjects = ', '.join(teacher_info.get(teacher_id, {}).get('subjects', []))
        active = "active" if idx == 0 else ""

        html += f"""
            <div id="teacher-{teacher_id}" class="tab-content {active}">
                <div class="class-title">{teacher_name} - Weekly Schedule<br><small style="font-size: 14px; opacity: 0.9;">Subjects: {teacher_subjects}</small></div>
                <div class="timetable-grid">
                    <table>
                        <thead>
                            <tr>
                                <th>Period</th>
                                <th>Monday</th>
                                <th>Tuesday</th>
                                <th>Wednesday</th>
                                <th>Thursday</th>
                                <th>Friday</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for period in range(1, 9):
            html += f"<tr><td class='period-cell'>Period {period}<br>{7+period}:00-{8+period}:00</td>"
            for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                period_data = [p for p in schedule[day] if p['period'] == period]
                if period_data:
                    pd = period_data[0]
                    html += f"<td><div class='subject'>{pd['subject']}</div><div class='teacher'>{pd['class']}</div></td>"
                else:
                    html += "<td class='free-period'>Free</td>"
            html += "</tr>\n"

        html += """
                        </tbody>
                    </table>
                </div>
            </div>
"""

    html += """
        </div>
    </div>

    <script>
        function showTab(type, id) {
            // Hide all tabs of this type
            const tabs = document.querySelectorAll(`#${type}-tabs .tab-content, [id^="${type}-"]`);
            tabs.forEach(tab => tab.classList.remove('active'));

            // Remove active from all buttons
            const buttons = document.querySelectorAll(`#${type}Tabs .nav-tab`);
            buttons.forEach(btn => btn.classList.remove('active'));

            // Show selected tab
            document.getElementById(`${type}-${id}`).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

    return html


if __name__ == "__main__":
    tt_id = "TT_20250930_155334_8fd6ea32"

    print(f"🔄 Loading data for {tt_id}...")
    data, teacher_info, assignment_map, subject_code_to_name = load_csv_data(tt_id)

    print(f"📊 Creating timetable schedules...")
    class_schedules, teacher_schedules, teacher_info = create_mock_timetable(
        data, teacher_info, assignment_map, subject_code_to_name
    )

    print(f"🎨 Generating HTML report...")
    html = generate_html_report(class_schedules, teacher_schedules, teacher_info, tt_id)

    output_file = Path(__file__).parent / f"complete_timetable_{tt_id}.html"
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"\n✅ Complete timetable generated!")
    print(f"📄 File: {output_file}")
    print(f"📊 Classes: {len(class_schedules)}")
    print(f"👨‍🏫 Teachers: {len(teacher_schedules)}")
    print(f"\n🌐 Opening in browser...")