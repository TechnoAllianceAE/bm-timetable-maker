#!/usr/bin/env python3
"""
Generate a realistic school timetable for 14 classes with diagnostic intelligence
Creates an HTML report showing the process and results
"""

import requests
import json
from datetime import datetime
import random

def generate_school_data():
    """Generate realistic school data for 14 classes"""

    # 14 classes across grades 6-10
    classes = []
    class_id = 1
    for grade in [6, 7, 8, 9, 10]:
        sections = ['A', 'B', 'C'] if grade in [8, 9] else ['A', 'B']
        for section in sections:
            classes.append({
                "id": f"class-{class_id}",
                "school_id": "school-001",
                "name": f"Grade {grade}{section}",
                "grade": grade,
                "section": section,
                "student_count": random.randint(25, 35)
            })
            class_id += 1

    # 6 core subjects per grade level
    subjects = [
        {"id": "math", "school_id": "school-001", "name": "Mathematics", "code": "MATH",
         "periods_per_week": 6, "requires_lab": False},
        {"id": "eng", "school_id": "school-001", "name": "English", "code": "ENG",
         "periods_per_week": 5, "requires_lab": False},
        {"id": "sci", "school_id": "school-001", "name": "Science", "code": "SCI",
         "periods_per_week": 5, "requires_lab": True},
        {"id": "soc", "school_id": "school-001", "name": "Social Studies", "code": "SOC",
         "periods_per_week": 4, "requires_lab": False},
        {"id": "lang", "school_id": "school-001", "name": "Second Language", "code": "LANG",
         "periods_per_week": 4, "requires_lab": False},
        {"id": "comp", "school_id": "school-001", "name": "Computer Science", "code": "COMP",
         "periods_per_week": 3, "requires_lab": True},
        {"id": "pe", "school_id": "school-001", "name": "Physical Education", "code": "PE",
         "periods_per_week": 2, "requires_lab": False},
        {"id": "art", "school_id": "school-001", "name": "Art & Craft", "code": "ART",
         "periods_per_week": 2, "requires_lab": False}
    ]

    # 30 teachers with subject specializations
    teachers = []
    teacher_configs = [
        # Math specialists (5 teachers)
        ("Mr. Anderson", ["Mathematics", "Computer Science"], 60, 40),
        ("Ms. Brown", ["Mathematics", "Science"], 70, 30),
        ("Mr. Chen", ["Mathematics"], 100, 0),
        ("Ms. Davis", ["Mathematics", "Computer Science"], 60, 40),
        ("Mr. Evans", ["Mathematics"], 100, 0),

        # English specialists (4 teachers)
        ("Ms. Fisher", ["English", "Second Language"], 60, 40),
        ("Mr. Garcia", ["English"], 100, 0),
        ("Ms. Harris", ["English", "Art & Craft"], 80, 20),
        ("Mr. Ibrahim", ["English", "Second Language"], 70, 30),

        # Science specialists (5 teachers)
        ("Ms. Jackson", ["Science"], 100, 0),
        ("Mr. Kim", ["Science", "Mathematics"], 70, 30),
        ("Ms. Lee", ["Science"], 100, 0),
        ("Mr. Martinez", ["Science", "Computer Science"], 60, 40),
        ("Ms. Nelson", ["Science"], 100, 0),

        # Social Studies specialists (3 teachers)
        ("Mr. O'Brien", ["Social Studies", "Second Language"], 70, 30),
        ("Ms. Patel", ["Social Studies"], 100, 0),
        ("Mr. Quinn", ["Social Studies", "English"], 60, 40),

        # Language specialists (4 teachers)
        ("Ms. Rodriguez", ["Second Language"], 100, 0),
        ("Mr. Smith", ["Second Language", "English"], 50, 50),
        ("Ms. Taylor", ["Second Language", "Social Studies"], 60, 40),
        ("Mr. Umar", ["Second Language"], 100, 0),

        # Computer Science specialists (3 teachers)
        ("Ms. Valdez", ["Computer Science"], 100, 0),
        ("Mr. Wang", ["Computer Science", "Mathematics"], 40, 60),
        ("Ms. Xavier", ["Computer Science", "Science"], 50, 50),

        # PE specialists (3 teachers)
        ("Mr. Young", ["Physical Education"], 100, 0),
        ("Ms. Zhang", ["Physical Education"], 100, 0),
        ("Mr. Adams", ["Physical Education", "Art & Craft"], 80, 20),

        # Art specialists (3 teachers)
        ("Ms. Bailey", ["Art & Craft"], 100, 0),
        ("Mr. Cooper", ["Art & Craft", "Physical Education"], 70, 30),
        ("Ms. Diaz", ["Art & Craft", "English"], 60, 40)
    ]

    for i, (name, subjects_taught, _, _) in enumerate(teacher_configs, 1):
        teachers.append({
            "id": f"teacher-{i}",
            "user_id": f"user-{i}",
            "name": name,
            "subjects": subjects_taught,
            "max_periods_per_day": 6,
            "max_periods_per_week": 28
        })

    # 5 days, 8 periods each
    time_slots = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    for day in days:
        for period in range(1, 9):
            # Add break after period 4
            if period == 5:
                time_slots.append({
                    "id": f"{day[:3].lower()}-break",
                    "school_id": "school-001",
                    "day_of_week": day,
                    "period_number": period,
                    "start_time": "12:00",
                    "end_time": "12:30",
                    "is_break": True
                })

            start_hour = 8 + (period if period <= 4 else period - 1)
            start_min = 0 if period <= 4 else 30

            time_slots.append({
                "id": f"{day[:3].lower()}-{period}",
                "school_id": "school-001",
                "day_of_week": day,
                "period_number": period,
                "start_time": f"{start_hour:02d}:{start_min:02d}",
                "end_time": f"{start_hour + (1 if period != 4 else 0):02d}:{start_min + (45 if period != 4 else 0):02d}",
                "is_break": False
            })

    # Rooms: 14 regular classrooms + 3 labs + 1 computer lab + 1 PE ground + 1 art room
    rooms = []

    # Regular classrooms
    for i in range(1, 15):
        rooms.append({
            "id": f"room-{i}",
            "school_id": "school-001",
            "name": f"Room {100 + i}",
            "capacity": 40,
            "type": "CLASSROOM"
        })

    # Science labs
    for i in range(1, 4):
        rooms.append({
            "id": f"lab-{i}",
            "school_id": "school-001",
            "name": f"Science Lab {i}",
            "capacity": 35,
            "type": "LAB"
        })

    # Computer lab
    rooms.append({
        "id": "comp-lab",
        "school_id": "school-001",
        "name": "Computer Lab",
        "capacity": 35,
        "type": "LAB"
    })

    # Other facilities
    rooms.append({
        "id": "playground",
        "school_id": "school-001",
        "name": "Playground",
        "capacity": 100,
        "type": "CLASSROOM"  # Using CLASSROOM type for simplicity
    })

    rooms.append({
        "id": "art-room",
        "school_id": "school-001",
        "name": "Art Room",
        "capacity": 35,
        "type": "CLASSROOM"
    })

    return {
        "school_id": "school-001",
        "academic_year_id": "2024-25",
        "classes": classes,
        "subjects": subjects,
        "teachers": teachers,
        "time_slots": time_slots,
        "rooms": rooms,
        "constraints": [],
        "options": 1,
        "weights": {
            "constraint_satisfaction": 0.4,
            "teacher_preferences": 0.2,
            "room_utilization": 0.2,
            "gap_minimization": 0.2
        }
    }

def generate_timetable():
    """Generate timetable using the diagnostic service"""

    print("Generating school data...")
    school_data = generate_school_data()

    print(f"School Configuration:")
    print(f"  - Classes: {len(school_data['classes'])}")
    print(f"  - Subjects: {len(school_data['subjects'])}")
    print(f"  - Teachers: {len(school_data['teachers'])}")
    print(f"  - Time Slots: {len([s for s in school_data['time_slots'] if not s['is_break']])}")
    print(f"  - Rooms: {len(school_data['rooms'])}")

    # Call the diagnostic service
    print("\nCalling timetable generation service...")
    url = "http://localhost:8001/generate"

    try:
        response = requests.post(url, json=school_data, timeout=60)
        result = response.json()
        return result, school_data
    except Exception as e:
        print(f"Error: {e}")
        return None, school_data

def create_html_report(result, school_data):
    """Create an HTML report with the diagnostic process and timetables"""

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>School Timetable Generation Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        h2 {
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .info-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .info-card h3 {
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 1.2em;
        }
        .info-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .status-box {
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .status-success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .status-warning {
            background: #fff3cd;
            border: 1px solid #ffeeba;
            color: #856404;
        }
        .status-error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .diagnostic-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .timetable {
            overflow-x: auto;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            position: sticky;
            top: 0;
        }
        td {
            padding: 10px;
            border: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background: #f8f9fa;
        }
        .class-entry {
            background: #e3f2fd;
            border-radius: 4px;
            padding: 5px;
            margin: 2px 0;
            font-size: 0.85em;
        }
        .subject { font-weight: bold; color: #1976d2; }
        .teacher { color: #388e3c; }
        .room { color: #7b1fa2; }
        .break-slot {
            background: #ffeb3b;
            text-align: center;
            font-weight: bold;
        }
        .resource-bar {
            display: inline-block;
            width: 200px;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-left: 10px;
        }
        .resource-fill {
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #8bc34a);
            transition: width 0.3s;
        }
        .warning-list {
            list-style: none;
            padding: 0;
        }
        .warning-list li {
            padding: 10px;
            margin: 5px 0;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 School Timetable Generation Report</h1>
        <p style="text-align: center; color: #666;">Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>

        <h2>📊 School Configuration</h2>
        <div class="info-grid">
            <div class="info-card">
                <h3>Classes</h3>
                <div class="value">""" + str(len(school_data['classes'])) + """</div>
            </div>
            <div class="info-card">
                <h3>Subjects</h3>
                <div class="value">""" + str(len(school_data['subjects'])) + """</div>
            </div>
            <div class="info-card">
                <h3>Teachers</h3>
                <div class="value">""" + str(len(school_data['teachers'])) + """</div>
            </div>
            <div class="info-card">
                <h3>Rooms</h3>
                <div class="value">""" + str(len(school_data['rooms'])) + """</div>
            </div>
            <div class="info-card">
                <h3>Weekly Periods</h3>
                <div class="value">40</div>
            </div>
        </div>
    """

    # Add generation status
    if result:
        status = result.get('status', 'unknown')
        if status == 'success':
            html += """
        <div class="status-box status-success">
            <h3>✅ Generation Successful!</h3>
            <p>Timetable generated in """ + str(result.get('generation_time', 0)) + """ seconds</p>
        </div>
            """
        elif status == 'infeasible':
            html += """
        <div class="status-box status-error">
            <h3>❌ Generation Failed - Infeasible</h3>
            <p>The constraints cannot be satisfied with current resources.</p>
        </div>
            """
        else:
            html += """
        <div class="status-box status-warning">
            <h3>⚠️ Generation Status: """ + status + """</h3>
        </div>
            """

    # Add diagnostics section
    if result and 'diagnostics' in result:
        diag = result['diagnostics']
        html += """
        <h2>🔍 Diagnostic Intelligence</h2>
        <div class="diagnostic-section">
        """

        # Resource utilization
        if diag.get('resource_utilization'):
            html += "<h3>Resource Utilization</h3>"
            for resource, util in diag['resource_utilization'].items():
                if isinstance(util, (int, float)):
                    color = '#4caf50' if util < 70 else '#ff9800' if util < 90 else '#f44336'
                    html += f"""
            <div style="margin: 10px 0;">
                <span>{resource}:</span>
                <div class="resource-bar">
                    <div class="resource-fill" style="width: {min(util, 100)}%; background: {color};"></div>
                </div>
                <span style="margin-left: 10px;">{util:.1f}%</span>
            </div>
                    """

        # Warnings
        if diag.get('warnings'):
            html += """
            <h3>⚠️ Warnings</h3>
            <ul class="warning-list">
            """
            for warning in diag['warnings']:
                html += f"<li>{warning}</li>"
            html += "</ul>"

        # Critical issues
        if diag.get('critical_issues'):
            html += """
            <h3>🔴 Critical Issues</h3>
            <ul style="color: #d32f2f;">
            """
            for issue in diag['critical_issues']:
                html += f"<li><strong>{issue['message']}</strong>"
                if issue.get('suggestions'):
                    html += "<ul>"
                    for sugg in issue['suggestions']:
                        html += f"<li>→ {sugg}</li>"
                    html += "</ul>"
                html += "</li>"
            html += "</ul>"

        # Recommendations
        if diag.get('recommendations'):
            html += """
            <h3>💡 Recommendations</h3>
            <ul style="color: #1976d2;">
            """
            for rec in diag['recommendations']:
                html += f"<li>{rec}</li>"
            html += "</ul>"

        html += "</div>"

    # Add timetables if successful
    if result and result.get('status') == 'success' and result.get('solutions'):
        solution = result['solutions'][0]
        timetable = solution.get('timetable', {})
        entries = timetable.get('entries', [])

        html += """
        <h2>📅 Generated Timetables</h2>
        """

        # Create timetable view for each class
        for class_obj in school_data['classes'][:3]:  # Show first 3 classes as example
            class_id = class_obj['id']
            class_name = class_obj['name']

            html += f"""
        <h3>Timetable for {class_name}</h3>
        <div class="timetable">
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Monday</th>
                        <th>Tuesday</th>
                        <th>Wednesday</th>
                        <th>Thursday</th>
                        <th>Friday</th>
                    </tr>
                </thead>
                <tbody>
            """

            # Build timetable grid
            for period in range(1, 9):
                html += "<tr>"

                # Time column
                if period <= 4:
                    time = f"{7 + period}:00 - {8 + period}:00"
                elif period == 5:
                    time = "12:00 - 12:30"
                    html += f'<td>{time}</td>'
                    html += '<td colspan="5" class="break-slot">BREAK</td>'
                    html += "</tr>"
                    continue
                else:
                    time = f"{7 + period}:30 - {8 + period}:30"

                html += f"<td><strong>{time}</strong><br>Period {period}</td>"

                # Each day
                for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                    # Find entry for this slot
                    entry = None
                    for e in entries:
                        if (e['class_id'] == class_id and
                            e['day_of_week'] == day and
                            e['period_number'] == period):
                            entry = e
                            break

                    if entry:
                        # Get subject name
                        subject_name = next((s['name'] for s in school_data['subjects']
                                           if s['id'] == entry['subject_id']), 'Unknown')
                        # Get teacher name
                        teacher_name = next((t['name'] for t in school_data['teachers']
                                           if t['id'] == entry['teacher_id']), 'Unknown')
                        # Get room name
                        room_name = next((r['name'] for r in school_data['rooms']
                                        if r['id'] == entry['room_id']), 'Unknown')

                        html += f"""
                        <td>
                            <div class="class-entry">
                                <div class="subject">{subject_name}</div>
                                <div class="teacher">👨‍🏫 {teacher_name}</div>
                                <div class="room">📍 {room_name}</div>
                            </div>
                        </td>
                        """
                    else:
                        html += "<td>-</td>"

                html += "</tr>"

            html += """
                </tbody>
            </table>
        </div>
            """

        # Summary statistics
        html += f"""
        <h2>📊 Summary Statistics</h2>
        <div class="info-grid">
            <div class="info-card">
                <h3>Total Entries</h3>
                <div class="value">{len(entries)}</div>
            </div>
            <div class="info-card">
                <h3>Success Score</h3>
                <div class="value">{solution.get('total_score', 0):.1f}</div>
            </div>
            <div class="info-card">
                <h3>Conflicts</h3>
                <div class="value">{len(solution.get('conflicts', []))}</div>
            </div>
        </div>
        """

    html += """
    </div>
</body>
</html>
    """

    return html

def main():
    print("\n" + "="*60)
    print("SCHOOL TIMETABLE GENERATION")
    print("14 Classes | 30 Teachers | 6 Subjects per Class")
    print("="*60 + "\n")

    # Generate timetable
    result, school_data = generate_timetable()

    if result:
        # Create HTML report
        html = create_html_report(result, school_data)

        # Save to file
        filename = f"school_timetable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w') as f:
            f.write(html)

        print(f"\n✅ HTML report saved to: {filename}")
        print(f"Open the file in a browser to view the timetables and diagnostics.")

        # Print summary
        if result.get('status') == 'success':
            solutions = result.get('solutions', [])
            if solutions:
                solution = solutions[0]
                timetable = solution.get('timetable', {})
                entries = timetable.get('entries', [])
                print(f"\n📊 Generation Summary:")
                print(f"  - Status: SUCCESS")
                print(f"  - Time: {result.get('generation_time', 0):.2f} seconds")
                print(f"  - Entries Generated: {len(entries)}")
                print(f"  - Score: {solution.get('total_score', 0):.1f}")
        else:
            print(f"\n⚠️  Generation Status: {result.get('status', 'unknown')}")

            if 'diagnostics' in result:
                diag = result['diagnostics']
                if diag.get('recommendations'):
                    print("\n💡 Recommendations:")
                    for rec in diag['recommendations'][:3]:
                        print(f"  • {rec}")
    else:
        print("\n❌ Failed to generate timetable")

if __name__ == "__main__":
    main()