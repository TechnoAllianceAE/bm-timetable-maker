#!/usr/bin/env python3
"""
Generate and display a working timetable with HTML visualization
"""

import requests
import json
from datetime import datetime
import webbrowser
import os

def generate_timetable_html():
    """Generate timetable and create interactive HTML report."""

    print("=" * 70)
    print("GENERATING DEMONSTRATION TIMETABLE")
    print("=" * 70)
    print()

    # Create request for 6 classes with 5 subjects
    request_data = {
        "school_id": "school-001",
        "academic_year_id": "2024-2025",
        "classes": [
            {"id": f"class-{grade}{section}", "school_id": "school-001", "name": f"{grade}-{section}",
             "grade": grade, "section": section, "student_count": 30}
            for grade, section in [(9, 'A'), (9, 'B'), (10, 'A'), (10, 'B'), (11, 'A'), (11, 'B')]
        ],
        "subjects": [
            {"id": "sub-math", "school_id": "school-001", "name": "Mathematics", "code": "MATH",
             "periods_per_week": 5, "requires_lab": False, "is_elective": False},
            {"id": "sub-sci", "school_id": "school-001", "name": "Science", "code": "SCI",
             "periods_per_week": 4, "requires_lab": True, "is_elective": False},
            {"id": "sub-eng", "school_id": "school-001", "name": "English", "code": "ENG",
             "periods_per_week": 4, "requires_lab": False, "is_elective": False},
            {"id": "sub-soc", "school_id": "school-001", "name": "Social Studies", "code": "SOC",
             "periods_per_week": 3, "requires_lab": False, "is_elective": False},
            {"id": "sub-pe", "school_id": "school-001", "name": "Physical Education", "code": "PE",
             "periods_per_week": 2, "requires_lab": False, "is_elective": False}
        ],
        "teachers": [
            {"id": "t-math-1", "user_id": "u1", "subjects": ["Mathematics"], "max_periods_per_day": 6, "max_periods_per_week": 28, "max_consecutive_periods": 3},
            {"id": "t-math-2", "user_id": "u2", "subjects": ["Mathematics"], "max_periods_per_day": 6, "max_periods_per_week": 28, "max_consecutive_periods": 3},
            {"id": "t-sci-1", "user_id": "u3", "subjects": ["Science"], "max_periods_per_day": 5, "max_periods_per_week": 25, "max_consecutive_periods": 2},
            {"id": "t-sci-2", "user_id": "u4", "subjects": ["Science"], "max_periods_per_day": 5, "max_periods_per_week": 25, "max_consecutive_periods": 2},
            {"id": "t-eng-1", "user_id": "u5", "subjects": ["English"], "max_periods_per_day": 6, "max_periods_per_week": 28, "max_consecutive_periods": 3},
            {"id": "t-eng-2", "user_id": "u6", "subjects": ["English"], "max_periods_per_day": 6, "max_periods_per_week": 28, "max_consecutive_periods": 3},
            {"id": "t-soc-1", "user_id": "u7", "subjects": ["Social Studies"], "max_periods_per_day": 6, "max_periods_per_week": 28, "max_consecutive_periods": 3},
            {"id": "t-pe-1", "user_id": "u8", "subjects": ["Physical Education"], "max_periods_per_day": 6, "max_periods_per_week": 30, "max_consecutive_periods": 4}
        ],
        "time_slots": [
            {"id": f"slot-{d}-{p}", "school_id": "school-001", "day_of_week": day, "period_number": p,
             "start_time": f"{7+p}:00", "end_time": f"{8+p}:00", "is_break": False}
            for d, day in enumerate(['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'])
            for p in range(1, 8)
        ],
        "rooms": [
            {"id": f"room-{i}", "school_id": "school-001", "name": f"Classroom {i}",
             "building": "Main", "floor": 1, "capacity": 40, "type": "CLASSROOM", "facilities": []}
            for i in range(1, 7)
        ] + [
            {"id": "lab-1", "school_id": "school-001", "name": "Science Lab 1",
             "building": "Science", "floor": 1, "capacity": 35, "type": "LAB", "facilities": []},
            {"id": "lab-2", "school_id": "school-001", "name": "Science Lab 2",
             "building": "Science", "floor": 1, "capacity": 35, "type": "LAB", "facilities": []},
            {"id": "ground", "school_id": "school-001", "name": "Sports Ground",
             "building": "Outdoor", "floor": 0, "capacity": 100, "type": "SPORTS", "facilities": []}
        ],
        "constraints": [],
        "weights": {
            "academic_requirements": 0.4,
            "teacher_preferences": 0.2,
            "resource_utilization": 0.2,
            "gap_minimization": 0.2
        },
        "options": 1
    }

    print(f"📚 Classes: {len(request_data['classes'])}")
    print(f"📖 Subjects: {len(request_data['subjects'])}")
    print(f"👩‍🏫 Teachers: {len(request_data['teachers'])}")
    print(f"🕐 Time Slots: {len(request_data['time_slots'])}")
    print(f"🏫 Rooms: {len(request_data['rooms'])}")
    print()

    # Call the service
    print("🚀 Generating timetable...")
    try:
        response = requests.post('http://localhost:8000/generate', json=request_data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Generated in {result['generation_time']:.2f} seconds")

            if result['solutions']:
                solution = result['solutions'][0]
                entries = solution['timetable']['entries']
                print(f"📋 Total entries: {len(entries)}")

                # Generate HTML
                html = generate_html_report(request_data, result)

                # Save HTML
                filename = "demo_timetable.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)

                print(f"\n✅ HTML report saved as: {filename}")
                print("📂 Opening in browser...")

                # Open in browser
                file_path = os.path.abspath(filename)
                webbrowser.open(f"file://{file_path}")

                return True

        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def generate_html_report(request, result):
    """Generate interactive HTML timetable visualization."""

    solution = result['solutions'][0] if result['solutions'] else None
    entries = solution['timetable']['entries'] if solution else []

    # Organize entries by class
    timetables_by_class = {}
    for entry in entries:
        class_id = entry['class_id']
        if class_id not in timetables_by_class:
            timetables_by_class[class_id] = {}

        # Use string key for JSON serialization
        key = f"{entry['day_of_week']},{entry['period_number']}"
        timetables_by_class[class_id][key] = entry

    # Calculate statistics
    total_entries = len(entries)
    expected_total = sum(s['periods_per_week'] for s in request['subjects']) * len(request['classes'])

    # Check for conflicts
    conflicts = check_conflicts(entries)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>School Timetable - Interactive View</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}

        .header .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat .value {{
            font-size: 2rem;
            font-weight: bold;
        }}

        .stat .label {{
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 5px;
        }}

        .content {{
            padding: 30px;
        }}

        .status-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .status-card {{
            padding: 20px;
            border-radius: 10px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
        }}

        .status-card.success {{
            border-left-color: #28a745;
            background: #d4edda;
        }}

        .status-card.error {{
            border-left-color: #dc3545;
            background: #f8d7da;
        }}

        .status-card h3 {{
            margin-bottom: 10px;
            color: #333;
        }}

        .class-selector {{
            margin: 30px 0;
            text-align: center;
        }}

        .class-selector select {{
            padding: 10px 20px;
            font-size: 1.1rem;
            border: 2px solid #667eea;
            border-radius: 8px;
            background: white;
            cursor: pointer;
        }}

        .timetable {{
            overflow-x: auto;
            margin-top: 20px;
        }}

        .timetable table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
        }}

        .timetable th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: 600;
        }}

        .timetable td {{
            border: 1px solid #dee2e6;
            padding: 10px;
            text-align: center;
            min-height: 80px;
            position: relative;
        }}

        .timetable tr:first-child th:first-child {{
            background: #764ba2;
        }}

        .period-cell {{
            min-height: 60px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 5px;
        }}

        .subject-name {{
            font-weight: bold;
            color: #667eea;
            font-size: 0.95rem;
        }}

        .teacher-name {{
            font-size: 0.85rem;
            color: #666;
        }}

        .room-name {{
            font-size: 0.8rem;
            color: #999;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 3px;
        }}

        .empty-cell {{
            background: #f8f9fa;
            color: #aaa;
            font-style: italic;
        }}

        .conflict-indicator {{
            position: absolute;
            top: 5px;
            right: 5px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #dc3545;
        }}

        .legend {{
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}

        .legend h3 {{
            margin-bottom: 15px;
            color: #333;
        }}

        .legend-items {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
            .class-selector {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 School Timetable</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <div class="stats">
                <div class="stat">
                    <div class="value">{len(request['classes'])}</div>
                    <div class="label">Classes</div>
                </div>
                <div class="stat">
                    <div class="value">{len(request['subjects'])}</div>
                    <div class="label">Subjects</div>
                </div>
                <div class="stat">
                    <div class="value">{len(request['teachers'])}</div>
                    <div class="label">Teachers</div>
                </div>
                <div class="stat">
                    <div class="value">{total_entries}</div>
                    <div class="label">Total Periods</div>
                </div>
            </div>
        </div>

        <div class="content">
            <div class="status-section">
                <div class="status-card {'success' if total_entries == expected_total else 'error'}">
                    <h3>📊 Generation Status</h3>
                    <p>Generated: {total_entries} periods</p>
                    <p>Expected: {expected_total} periods</p>
                    <p>Status: {'✅ Complete' if total_entries == expected_total else f'⚠️ {abs(total_entries - expected_total)} periods difference'}</p>
                </div>
                <div class="status-card {'success' if not conflicts['teacher'] else 'error'}">
                    <h3>👩‍🏫 Teacher Conflicts</h3>
                    <p>{'✅ No conflicts' if not conflicts['teacher'] else f"❌ {len(conflicts['teacher'])} conflicts found"}</p>
                </div>
                <div class="status-card {'success' if not conflicts['room'] else 'error'}">
                    <h3>🏫 Room Conflicts</h3>
                    <p>{'✅ No conflicts' if not conflicts['room'] else f"❌ {len(conflicts['room'])} conflicts found"}</p>
                </div>
                <div class="status-card success">
                    <h3>⏱️ Generation Time</h3>
                    <p>{result.get('generation_time', 0):.2f} seconds</p>
                </div>
            </div>

            <div class="class-selector">
                <label for="classSelect">Select Class: </label>
                <select id="classSelect" onchange="showTimetable(this.value)">
                    {''.join([f'<option value="{c["id"]}">{c["name"]}</option>' for c in request['classes']])}
                </select>
            </div>

            <div id="timetableContainer">
                <!-- Timetables will be inserted here by JavaScript -->
            </div>

            <div class="legend">
                <h3>📝 Legend</h3>
                <div class="legend-items">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #667eea;"></div>
                        <span>Subject Name</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #666;"></div>
                        <span>Teacher</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #f0f0f0;"></div>
                        <span>Room</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const timetableData = {json.dumps(timetables_by_class)};
        const subjects = {json.dumps({s['id']: s for s in request['subjects']})};
        const teachers = {json.dumps({t['id']: t for t in request['teachers']})};
        const rooms = {json.dumps({r['id']: r for r in request['rooms']})};

        function showTimetable(classId) {{
            const container = document.getElementById('timetableContainer');
            const classTimetable = timetableData[classId] || {{}};

            let html = '<div class="timetable"><table>';

            // Header
            html += '<tr><th>Day/Period</th>';
            for (let p = 1; p <= 7; p++) {{
                html += `<th>Period ${{p}}<br><small>${{7+p}}:00-${{8+p}}:00</small></th>`;
            }}
            html += '</tr>';

            // Days
            const days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'];
            for (const day of days) {{
                html += `<tr><th>${{day}}</th>`;

                for (let p = 1; p <= 7; p++) {{
                    const key = `${{day}},${{p}}`;
                    const entry = classTimetable[key];

                    if (entry) {{
                        const subject = subjects[entry.subject_id];
                        const teacher = teachers[entry.teacher_id];
                        const room = rooms[entry.room_id];

                        html += '<td><div class="period-cell">';
                        html += `<div class="subject-name">${{subject ? subject.name : entry.subject_id}}</div>`;
                        html += `<div class="teacher-name">${{teacher ? 'T: ' + teacher.id : ''}}</div>`;
                        html += `<div class="room-name">${{room ? room.name : entry.room_id}}</div>`;
                        html += '</div></td>';
                    }} else {{
                        html += '<td class="empty-cell">Free</td>';
                    }}
                }}
                html += '</tr>';
            }}

            html += '</table></div>';
            container.innerHTML = html;
        }}

        // Show first class by default
        showTimetable('{request['classes'][0]['id'] if request['classes'] else ''}');
    </script>
</body>
</html>"""

    return html


def check_conflicts(entries):
    """Check for scheduling conflicts."""
    conflicts = {'teacher': [], 'room': []}

    # Check teacher conflicts
    teacher_schedule = {}
    for entry in entries:
        key = f"{entry['day_of_week']}-{entry['period_number']}-{entry['teacher_id']}"
        if key in teacher_schedule:
            conflicts['teacher'].append(key)
        teacher_schedule[key] = entry

    # Check room conflicts
    room_schedule = {}
    for entry in entries:
        key = f"{entry['day_of_week']}-{entry['period_number']}-{entry['room_id']}"
        if key in room_schedule:
            conflicts['room'].append(key)
        room_schedule[key] = entry

    return conflicts


if __name__ == "__main__":
    success = generate_timetable_html()
    if success:
        print("\n🎉 Timetable generated and displayed successfully!")
    else:
        print("\n❌ Failed to generate timetable")