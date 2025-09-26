#!/usr/bin/env python3
"""
Run timetable engine with 3-grade 6-subject test data
"""

import requests
import json
from datetime import datetime

def create_3grade_6subject_request():
    """Create test request for 3 grades with 6 subjects"""

    # Create 6 classes (2 per grade for grades 8, 9, 10)
    classes = []
    grade_sections = [
        ("8", "A"), ("8", "B"),
        ("9", "A"), ("9", "B"),
        ("10", "A"), ("10", "B")
    ]

    for grade, section in grade_sections:
        classes.append({
            "id": f"class-{grade}{section}",
            "school_id": "school-001",
            "name": f"{grade}-{section}",
            "grade": int(grade),
            "section": section,
            "student_count": 30
        })

    # Create 6 subjects
    subjects = [
        {
            "id": "sub-math",
            "school_id": "school-001",
            "name": "Mathematics",
            "code": "MATH",
            "periods_per_week": 6,
            "requires_lab": False,
            "is_elective": False
        },
        {
            "id": "sub-eng",
            "school_id": "school-001",
            "name": "English",
            "code": "ENG",
            "periods_per_week": 5,
            "requires_lab": False,
            "is_elective": False
        },
        {
            "id": "sub-sci",
            "school_id": "school-001",
            "name": "Science",
            "code": "SCI",
            "periods_per_week": 6,
            "requires_lab": True,
            "is_elective": False
        },
        {
            "id": "sub-ss",
            "school_id": "school-001",
            "name": "Social Studies",
            "code": "SS",
            "periods_per_week": 4,
            "requires_lab": False,
            "is_elective": False
        },
        {
            "id": "sub-cs",
            "school_id": "school-001",
            "name": "Computer Science",
            "code": "CS",
            "periods_per_week": 4,
            "requires_lab": True,
            "is_elective": False
        },
        {
            "id": "sub-pe",
            "school_id": "school-001",
            "name": "Physical Education",
            "code": "PE",
            "periods_per_week": 3,
            "requires_lab": False,
            "is_elective": False
        }
    ]

    # Calculate teachers needed: 6 subjects × 2 teachers each = 12 teachers
    teachers = []
    teacher_allocation = {
        "Mathematics": 2,
        "English": 2,
        "Science": 2,
        "Social Studies": 2,
        "Computer Science": 2,
        "Physical Education": 2
    }

    teacher_id = 1
    for subject, count in teacher_allocation.items():
        for i in range(count):
            teachers.append({
                "id": f"teacher-{teacher_id:03d}",
                "user_id": f"user-{teacher_id:03d}",
                "subjects": [subject],
                "max_periods_per_day": 6,
                "max_periods_per_week": 30,
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

    # Create rooms
    rooms = []
    # Regular classrooms
    for i in range(6):
        rooms.append({
            "id": f"room-{i+1:02d}",
            "school_id": "school-001",
            "name": f"Classroom {i+1}",
            "building": "Main",
            "floor": 1,
            "capacity": 35,
            "type": "CLASSROOM",
            "facilities": ["projector", "whiteboard"]
        })

    # Science and Computer labs
    rooms.extend([
        {
            "id": "room-sci-lab",
            "school_id": "school-001",
            "name": "Science Lab",
            "building": "Science Block",
            "floor": 1,
            "capacity": 30,
            "type": "LAB",
            "facilities": ["lab_equipment", "sink"]
        },
        {
            "id": "room-comp-lab",
            "school_id": "school-001",
            "name": "Computer Lab",
            "building": "Tech Block",
            "floor": 2,
            "capacity": 30,
            "type": "LAB",
            "facilities": ["computers", "projector"]
        },
        {
            "id": "room-sports",
            "school_id": "school-001",
            "name": "Sports Ground",
            "building": "Outdoor",
            "floor": 0,
            "capacity": 60,
            "type": "SPORTS",
            "facilities": ["field"]
        }
    ])

    # Simple constraints
    constraints = []

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

def generate_html_output(request, response):
    """Generate HTML output showing the timetable"""

    classes_count = len(request['classes'])
    subjects_count = len(request['subjects'])
    teachers_count = len(request['teachers'])

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3-Grade 6-Subject Timetable Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
        }}
        .stat {{
            text-align: center;
            padding: 20px;
            background: #e3f2fd;
            border-radius: 8px;
        }}
        .stat .number {{
            font-size: 2em;
            font-weight: bold;
            color: #1976d2;
        }}
        .timetable {{
            margin-top: 30px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        th {{
            background: #1976d2;
            color: white;
        }}
        .success {{
            color: #4caf50;
            font-weight: bold;
        }}
        .error {{
            color: #f44336;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 3-Grade 6-Subject Timetable Test Results</h1>
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="number">{classes_count}</div>
                <div>Classes</div>
            </div>
            <div class="stat">
                <div class="number">{subjects_count}</div>
                <div>Subjects</div>
            </div>
            <div class="stat">
                <div class="number">{teachers_count}</div>
                <div>Teachers</div>
            </div>
            <div class="stat">
                <div class="number">{classes_count * 40}</div>
                <div>Total Periods</div>
            </div>
        </div>
"""

    if response and response.get('status') == 'success':
        result = response['data']
        html += f"""
        <div style="text-align: center; margin: 20px 0;">
            <h2 class="success">✅ Timetable Generated Successfully!</h2>
            <p>Generation Time: {result.get('generation_time', 0):.2f} seconds</p>
            <p>Solutions Generated: {len(result.get('solutions', []))}</p>
        </div>

        <h3>📋 Teacher Allocation</h3>
        <table>
            <tr>
                <th>Subject</th>
                <th>Periods per Class</th>
                <th>Total Periods</th>
                <th>Teachers</th>
            </tr>
"""

        subject_periods = {
            "Mathematics": 6,
            "English": 5,
            "Science": 6,
            "Social Studies": 4,
            "Computer Science": 4,
            "Physical Education": 3
        }

        for subject, periods in subject_periods.items():
            total = periods * classes_count
            teachers = 2  # 2 teachers per subject
            html += f"""
            <tr>
                <td>{subject}</td>
                <td>{periods}</td>
                <td>{total}</td>
                <td>{teachers}</td>
            </tr>
"""

        html += """
        </table>

        <h3>📅 Sample Timetable (Grade 8-A)</h3>
        <div class="timetable">
            <table>
                <tr>
                    <th>Time</th>
                    <th>Monday</th>
                    <th>Tuesday</th>
                    <th>Wednesday</th>
                    <th>Thursday</th>
                    <th>Friday</th>
                </tr>
"""

        # Show sample timetable for first class
        if result.get('solutions') and result['solutions'][0]['timetable']['entries']:
            sample_entries = [e for e in result['solutions'][0]['timetable']['entries']
                            if e.get('class_id') == 'class-8A']

            for period in range(1, 9):
                html += f"<tr><td><strong>Period {period}</strong><br>9:{period+8:02d}-10:{period+8:02d}</td>"

                for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                    entry = next((e for e in sample_entries
                                if e.get('day_of_week') == day and e.get('period_number') == period), None)
                    if entry:
                        subject = entry.get('subject_id', '').replace('sub-', '').upper()
                        teacher = entry.get('teacher_id', '').replace('teacher-', 'T')
                        room = entry.get('room_id', '').replace('room-', 'R')
                        html += f"<td><strong>{subject}</strong><br>{teacher}<br>{room}</td>"
                    else:
                        html += "<td>-</td>"

                html += "</tr>"

        html += """
            </table>
        </div>
"""

    else:
        error_msg = response.get('error', 'Unknown error') if response else 'No response from service'
        html += f"""
        <div style="text-align: center; margin: 20px 0;">
            <h2 class="error">❌ Generation Failed</h2>
            <p>Error: {error_msg}</p>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    return html

def main():
    print("🚀 Running 3-Grade 6-Subject Timetable Test")
    print("=" * 50)

    # Create request
    print("📋 Preparing request data...")
    request_data = create_3grade_6subject_request()

    print(f"✓ Classes: {len(request_data['classes'])}")
    print(f"✓ Subjects: {len(request_data['subjects'])}")
    print(f"✓ Teachers: {len(request_data['teachers'])}")
    print(f"✓ Time Slots: {len(request_data['time_slots'])}")
    print(f"✓ Rooms: {len(request_data['rooms'])}")
    print()

    # Check if service is running
    try:
        health_response = requests.get('http://localhost:8000/health', timeout=5)
        if health_response.status_code != 200:
            print("❌ Timetable service is not running on localhost:8000")
            print("💡 Please start the service with: cd timetable-engine && python main.py")
            return
    except:
        print("❌ Cannot connect to timetable service on localhost:8000")
        print("💡 Please start the service with: cd timetable-engine && python main.py")
        return

    # Call service
    print("🔧 Calling timetable generation service...")
    try:
        response = requests.post(
            'http://localhost:8000/generate',
            json=request_data,
            timeout=120
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
    html_content = generate_html_output(request_data, response_data)

    # Save report
    report_file = "timetable_3grade_6subject_results.html"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Report saved to: {report_file}")
    print()

    if response_data.get('status') == 'success':
        print("🎉 Done! Open the HTML file to view the timetable results.")
    else:
        print("❌ Generation failed. Check the HTML report for details.")

    print("=" * 50)

if __name__ == "__main__":
    main()