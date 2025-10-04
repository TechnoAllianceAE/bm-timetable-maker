#!/usr/bin/env python3
"""
Comprehensive Timetable Generator with Full Visualization
Generates complete timetables using v25 engine and creates beautiful HTML reports
"""

import json
import time
import requests
import subprocess
import csv
import os
import signal
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import webbrowser

class ComprehensiveTimetableGenerator:
    """Complete timetable generation and visualization system"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.engine_path = self.base_path.parent / "timetable-engine"
        self.engine_process = None
        self.port = 8000
        
    def start_v25_engine(self):
        """Start the v25 engine"""
        print("🚀 Starting main_v25.py engine...")
        
        try:
            # Create launcher script for v25
            launcher_script = f'''
import sys
import os
sys.path.append(r"{self.engine_path}")
os.chdir(r"{self.engine_path}")

import uvicorn
from main_v25 import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={self.port}, log_level="warning")
'''
            
            # Write temporary launcher
            temp_launcher = self.base_path / "temp_v25_launcher.py"
            with open(temp_launcher, 'w') as f:
                f.write(launcher_script)
            
            # Start the process
            self.engine_process = subprocess.Popen([
                'python', str(temp_launcher)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
            
            # Wait for startup
            max_wait = 30
            wait_time = 0
            while wait_time < max_wait:
                try:
                    response = requests.get(f"http://localhost:{self.port}/docs", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ v25 engine started successfully on port {self.port}")
                        return True
                except:
                    pass
                
                time.sleep(2)
                wait_time += 2
                print(f"   Waiting for v25 engine... ({wait_time}s)")
            
            print("⚠️ Engine startup timeout, but continuing...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start v25 engine: {e}")
            return False
    
    def stop_engine(self):
        """Stop the engine"""
        if self.engine_process:
            print("🛑 Stopping v25 engine...")
            try:
                if os.name == 'nt':
                    self.engine_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    self.engine_process.terminate()
                
                try:
                    self.engine_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.engine_process.kill()
                    self.engine_process.wait()
                
                # Clean up temp file
                temp_file = self.base_path / "temp_v25_launcher.py"
                if temp_file.exists():
                    temp_file.unlink()
                    
            except Exception as e:
                print(f"Warning: Error stopping engine: {e}")
            
            self.engine_process = None
    
    def load_test_data(self, tt_id):
        """Load CSV test data for given TT ID"""
        print(f"📂 Loading test data for {tt_id}...")
        
        # Load subjects first for code->name mapping
        subject_code_to_name = {}
        subjects = []
        with open(self.base_path / f"data_subjects_{tt_id}.csv", 'r') as f:
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
        with open(self.base_path / f"data_classes_{tt_id}.csv", 'r') as f:
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
                class_info[row['class_id']] = {
                    "name": row['name'],
                    "grade": int(row['grade']),
                    "section": row['section'],
                    "capacity": int(row['capacity'])
                }

        # Load teachers
        teachers = []
        teacher_info = {}
        with open(self.base_path / f"data_teachers_{tt_id}.csv", 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                subject_codes = row['subjects_qualified'].split(',')
                subject_names = [subject_code_to_name.get(code.strip(), code.strip()) 
                               for code in subject_codes]
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
                    "subjects": subject_codes,
                    "email": row['email'],
                    "phone": row['phone']
                }

        # Load rooms
        rooms = []
        room_info = {}
        with open(self.base_path / f"data_rooms_{tt_id}.csv", 'r') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                room_type = row['type'].upper() if row['type'].upper() in ['CLASSROOM', 'LAB', 'AUDITORIUM'] else 'CLASSROOM'
                facilities = []
                if row.get('has_projector') == 'True':
                    facilities.append('projector')
                if row.get('specialization'):
                    facilities.append(row['specialization'])

                room_data = {
                    "id": row['room_id'],
                    "school_id": "test-school",
                    "name": row['name'],
                    "building": "Main Building",
                    "floor": (idx // 10) + 1,
                    "capacity": int(row['capacity']),
                    "type": room_type,
                    "facilities": facilities
                }
                rooms.append(room_data)
                room_info[row['room_id']] = {
                    "name": row['name'],
                    "type": room_type,
                    "capacity": int(row['capacity']),
                    "has_projector": row.get('has_projector') == 'True',
                    "specialization": row.get('specialization', '')
                }

        # Load assignments
        assignments = []
        assignment_map = {}
        with open(self.base_path / f"data_assignments_{tt_id}.csv", 'r') as f:
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

        request_data = {
            "school_id": "test-school",
            "academic_year_id": "2025-2026",
            "tt_generation_id": tt_id,
            "classes": classes,
            "teachers": teachers,
            "subjects": subjects,
            "rooms": rooms,
            "time_slots": time_slots,
            "assignments": assignments,
            "constraints": constraints,
            "options": 3,
            "timeout": 180
        }

        return request_data, teacher_info, class_info, room_info, assignment_map, subject_code_to_name

    def generate_timetable(self, test_data):
        """Generate timetable using v25 engine"""
        url = f"http://localhost:{self.port}/generate"
        
        print(f"\n🧮 Generating timetable using main_v25.py...")
        print(f"📊 Data: {len(test_data['classes'])} classes, {len(test_data['teachers'])} teachers, {len(test_data['assignments'])} assignments")
        
        try:
            start_time = time.time()
            response = requests.post(url, json=test_data, timeout=300)  # 5 minute timeout
            end_time = time.time()
            
            generation_time = end_time - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                
                print(f"✅ Timetable generated successfully!")
                print(f"⏱️ Generation time: {generation_time:.2f}s")
                print(f"📈 Status: {result_data.get('status', 'unknown')}")
                
                # Extract diagnostics
                diagnostics = result_data.get('diagnostics', {})
                print(f"📊 Coverage: {diagnostics.get('coverage_percentage', 0):.1f}%")
                print(f"📝 Schedules: {len(result_data.get('schedules', []))}")
                
                return result_data
            else:
                print(f"❌ Failed to generate timetable: HTTP {response.status_code}")
                print(f"📄 Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"💥 Error generating timetable: {e}")
            return None

    def create_comprehensive_html_report(self, tt_id, result_data, teacher_info, class_info, room_info, assignment_map, subject_code_to_name):
        """Create comprehensive HTML report with all timetables"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Parse the timetable result
        schedules = result_data.get('schedules', [])
        diagnostics = result_data.get('diagnostics', {})
        
        if not schedules:
            print("❌ No schedules found in result data")
            return None
        
        # Use the first (best) schedule
        best_schedule = schedules[0] if schedules else {"entries": []}
        entries = best_schedule.get('entries', [])
        
        # Organize entries by class and teacher
        class_schedules = defaultdict(lambda: defaultdict(list))
        teacher_schedules = defaultdict(lambda: defaultdict(list))
        room_utilization = defaultdict(lambda: defaultdict(list))
        
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        
        for entry in entries:
            class_id = entry.get('class_id')
            teacher_id = entry.get('teacher_id')
            room_id = entry.get('room_id')
            subject_code = entry.get('subject_code')
            day = entry.get('day_of_week')
            period = entry.get('period_number')
            
            if all([class_id, teacher_id, day, period, subject_code]):
                subject_name = subject_code_to_name.get(subject_code, subject_code)
                teacher_name = teacher_info.get(teacher_id, {}).get('name', teacher_id)
                class_name = class_info.get(class_id, {}).get('name', class_id)
                room_name = room_info.get(room_id, {}).get('name', room_id) if room_id else 'TBA'
                
                # Class schedule
                class_schedules[class_id][day].append({
                    'period': period,
                    'subject': subject_name,
                    'subject_code': subject_code,
                    'teacher': teacher_name,
                    'teacher_id': teacher_id,
                    'room': room_name
                })
                
                # Teacher schedule
                teacher_schedules[teacher_id][day].append({
                    'period': period,
                    'subject': subject_name,
                    'class': class_name,
                    'class_id': class_id,
                    'room': room_name
                })
                
                # Room utilization
                if room_id:
                    room_utilization[room_id][day].append({
                        'period': period,
                        'class': class_name,
                        'subject': subject_name,
                        'teacher': teacher_name
                    })

        # Sort schedules by period for each day
        for class_id in class_schedules:
            for day in class_schedules[class_id]:
                class_schedules[class_id][day].sort(key=lambda x: x['period'])
        
        for teacher_id in teacher_schedules:
            for day in teacher_schedules[teacher_id]:
                teacher_schedules[teacher_id][day].sort(key=lambda x: x['period'])

        # Generate HTML
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete School Timetable - {tt_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
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
            margin: 5px 0;
        }}

        .nav-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }}

        .nav-tab {{
            padding: 15px 30px;
            background: white;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-weight: 700;
            font-size: 16px;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .nav-tab:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }}

        .nav-tab.active {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
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
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: #f7fafc;
            padding: 25px;
            border-radius: 15px;
            border-left: 4px solid #667eea;
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
        }}

        .timetable-grid {{
            overflow-x: auto;
            margin-bottom: 30px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 10px;
            text-align: center;
            font-weight: 700;
            font-size: 14px;
        }}

        td {{
            padding: 12px 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
            font-size: 13px;
            vertical-align: top;
        }}

        tr:nth-child(even) {{
            background: #f8fafc;
        }}

        .period-cell {{
            background: #edf2f7;
            font-weight: 700;
            color: #4a5568;
        }}

        .subject {{
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 4px;
        }}

        .teacher {{
            font-size: 11px;
            color: #718096;
            margin-bottom: 2px;
        }}

        .room {{
            font-size: 10px;
            color: #a0aec0;
        }}

        .free-period {{
            color: #cbd5e0;
            font-style: italic;
        }}

        .entity-title {{
            background: #667eea;
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        }}

        .entity-title h3 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .entity-title .subtitle {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .entity-tabs {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }}

        .entity-tab {{
            padding: 12px 16px;
            background: #edf2f7;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            text-align: center;
            transition: all 0.3s;
        }}

        .entity-tab:hover {{
            background: #667eea;
            color: white;
        }}

        .entity-tab.active {{
            background: #667eea;
            color: white;
        }}

        .success {{
            color: #48bb78;
        }}

        .warning {{
            color: #ed8936;
        }}

        .error {{
            color: #f56565;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 28px;
            }}
            
            .nav-tab {{
                padding: 10px 20px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Complete School Timetable</h1>
            <div class="subtitle">Generated using main_v25.py</div>
            <div class="subtitle">Created on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
            <div class="subtitle">TT ID: {tt_id}</div>
        </div>

        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showMainTab('overview')">📊 Overview</button>
            <button class="nav-tab" onclick="showMainTab('classes')">📚 Class Timetables</button>
            <button class="nav-tab" onclick="showMainTab('teachers')">👨‍🏫 Teacher Timetables</button>
            <button class="nav-tab" onclick="showMainTab('rooms')">🏢 Room Utilization</button>
        </div>

        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="section">
                <h2>📊 Generation Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value success">{len(class_schedules)}</div>
                        <div class="stat-label">Classes with Schedules</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value success">{len(teacher_schedules)}</div>
                        <div class="stat-label">Teachers Assigned</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(entries)}</div>
                        <div class="stat-label">Total Scheduled Periods</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value success">{diagnostics.get('coverage_percentage', 0):.1f}%</div>
                        <div class="stat-label">Schedule Coverage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(room_utilization)}</div>
                        <div class="stat-label">Rooms Utilized</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{diagnostics.get('total_assignments', 0)}</div>
                        <div class="stat-label">Total Assignments</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Classes Tab -->
        <div id="classes" class="tab-content">
            <div class="section">
                <h2>📚 Class Timetables</h2>
                <div class="entity-tabs" id="classTabs">
'''

        # Add class tabs
        for idx, (class_id, _) in enumerate(sorted(class_schedules.items())):
            class_name = class_info.get(class_id, {}).get('name', class_id)
            active = "active" if idx == 0 else ""
            html_content += f'<button class="entity-tab {active}" onclick="showEntityTab(\'class\', \'{class_id}\')">{class_name}</button>\n'

        html_content += '''
                </div>
'''

        # Add class timetables
        for idx, (class_id, schedule) in enumerate(sorted(class_schedules.items())):
            class_data = class_info.get(class_id, {})
            class_name = class_data.get('name', class_id)
            active = "active" if idx == 0 else ""
            
            html_content += f'''
                <div id="class-{class_id}" class="tab-content {active}">
                    <div class="entity-title">
                        <h3>{class_name}</h3>
                        <div class="subtitle">Grade {class_data.get('grade', 'N/A')} • Section {class_data.get('section', 'N/A')} • {class_data.get('capacity', 'N/A')} students</div>
                    </div>
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
'''
            
            for period in range(1, 9):
                time_start = 7 + period
                time_end = 8 + period
                html_content += f'<tr><td class="period-cell">Period {period}<br>{time_start:02d}:00-{time_end:02d}:00</td>'
                
                for day in days:
                    period_data = [p for p in schedule[day] if p['period'] == period]
                    if period_data:
                        pd = period_data[0]
                        html_content += f'''<td>
                            <div class="subject">{pd['subject']}</div>
                            <div class="teacher">{pd['teacher']}</div>
                            <div class="room">{pd['room']}</div>
                        </td>'''
                    else:
                        html_content += '<td class="free-period">Free Period</td>'
                
                html_content += '</tr>\n'
            
            html_content += '''
                            </tbody>
                        </table>
                    </div>
                </div>
'''

        html_content += '''
            </div>
        </div>

        <!-- Teachers Tab -->
        <div id="teachers" class="tab-content">
            <div class="section">
                <h2>👨‍🏫 Teacher Timetables</h2>
                <div class="entity-tabs" id="teacherTabs">
'''

        # Add teacher tabs
        for idx, (teacher_id, _) in enumerate(sorted(teacher_schedules.items())):
            teacher_name = teacher_info.get(teacher_id, {}).get('name', teacher_id)
            active = "active" if idx == 0 else ""
            html_content += f'<button class="entity-tab {active}" onclick="showEntityTab(\'teacher\', \'{teacher_id}\')">{teacher_name}</button>\n'

        html_content += '''
                </div>
'''

        # Add teacher timetables
        for idx, (teacher_id, schedule) in enumerate(sorted(teacher_schedules.items())):
            teacher_data = teacher_info.get(teacher_id, {})
            teacher_name = teacher_data.get('name', teacher_id)
            subjects = ', '.join(teacher_data.get('subjects', []))
            active = "active" if idx == 0 else ""
            
            html_content += f'''
                <div id="teacher-{teacher_id}" class="tab-content {active}">
                    <div class="entity-title">
                        <h3>{teacher_name}</h3>
                        <div class="subtitle">Subjects: {subjects}</div>
                        <div class="subtitle">{teacher_data.get('email', '')} • {teacher_data.get('phone', '')}</div>
                    </div>
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
'''
            
            for period in range(1, 9):
                time_start = 7 + period
                time_end = 8 + period
                html_content += f'<tr><td class="period-cell">Period {period}<br>{time_start:02d}:00-{time_end:02d}:00</td>'
                
                for day in days:
                    period_data = [p for p in schedule[day] if p['period'] == period]
                    if period_data:
                        pd = period_data[0]
                        html_content += f'''<td>
                            <div class="subject">{pd['subject']}</div>
                            <div class="teacher">{pd['class']}</div>
                            <div class="room">{pd['room']}</div>
                        </td>'''
                    else:
                        html_content += '<td class="free-period">Free</td>'
                
                html_content += '</tr>\n'
            
            html_content += '''
                            </tbody>
                        </table>
                    </div>
                </div>
'''

        # Close teachers section and add rooms section
        html_content += '''
            </div>
        </div>

        <!-- Rooms Tab -->
        <div id="rooms" class="tab-content">
            <div class="section">
                <h2>🏢 Room Utilization</h2>
                <div class="stats-grid">
'''

        # Room utilization stats
        total_room_periods = len(room_utilization) * 40  # 40 periods per week per room
        used_periods = sum(len([p for day_schedule in room_schedule.values() for p in day_schedule]) 
                          for room_schedule in room_utilization.values())
        utilization_rate = (used_periods / total_room_periods * 100) if total_room_periods > 0 else 0

        html_content += f'''
                    <div class="stat-card">
                        <div class="stat-value">{len(room_utilization)}</div>
                        <div class="stat-label">Rooms in Use</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{used_periods}</div>
                        <div class="stat-label">Room-Periods Used</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{utilization_rate:.1f}%</div>
                        <div class="stat-label">Room Utilization Rate</div>
                    </div>
                </div>
                
                <div class="timetable-grid">
                    <table>
                        <thead>
                            <tr>
                                <th>Room</th>
                                <th>Type</th>
                                <th>Capacity</th>
                                <th>Periods Used</th>
                                <th>Utilization</th>
                            </tr>
                        </thead>
                        <tbody>
'''

        for room_id, schedule in sorted(room_utilization.items()):
            room_data = room_info.get(room_id, {})
            periods_used = sum(len(day_schedule) for day_schedule in schedule.values())
            room_utilization_pct = (periods_used / 40 * 100)
            
            html_content += f'''
                            <tr>
                                <td><strong>{room_data.get('name', room_id)}</strong></td>
                                <td>{room_data.get('type', 'N/A')}</td>
                                <td>{room_data.get('capacity', 'N/A')}</td>
                                <td>{periods_used}/40</td>
                                <td>{room_utilization_pct:.1f}%</td>
                            </tr>
'''

        html_content += '''
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showMainTab(tabName) {
            // Hide all main tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Remove active from all nav buttons
            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function showEntityTab(type, id) {
            // Hide all entity tabs of this type
            const tabs = document.querySelectorAll(`[id^="${type}-"]`);
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Remove active from all entity buttons
            const buttons = document.querySelectorAll(`#${type}Tabs .entity-tab`);
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(`${type}-${id}`).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
'''

        # Save the HTML report
        report_file = self.base_path / f"comprehensive_timetable_{tt_id}_{timestamp}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_file

    def run_complete_generation(self, tt_id):
        """Run the complete timetable generation process"""
        print(f"\n{'='*80}")
        print(f"🎓 Comprehensive Timetable Generation")
        print(f"📊 TT ID: {tt_id}")
        print(f"🚀 Engine: main_v25.py")
        print(f"{'='*80}")
        
        try:
            # Start engine
            if not self.start_v25_engine():
                print("❌ Failed to start engine. Aborting.")
                return None
            
            # Load test data
            test_data, teacher_info, class_info, room_info, assignment_map, subject_code_to_name = self.load_test_data(tt_id)
            
            # Generate timetable
            result_data = self.generate_timetable(test_data)
            if not result_data:
                print("❌ Failed to generate timetable")
                return None
            
            # Create HTML report
            print(f"\n🎨 Creating comprehensive HTML report...")
            report_file = self.create_comprehensive_html_report(
                tt_id, result_data, teacher_info, class_info, room_info, assignment_map, subject_code_to_name
            )
            
            if report_file:
                print(f"\n{'='*80}")
                print(f"✅ Comprehensive Timetable Generation Complete!")
                print(f"📄 Report: {report_file}")
                print(f"🌐 Opening in browser...")
                print(f"{'='*80}")
                
                # Open in browser
                try:
                    webbrowser.open(str(report_file))
                    print("🌐 Report opened in your default browser!")
                except:
                    print(f"Could not auto-open browser. Please open: {report_file}")
                
                return report_file
            
        except Exception as e:
            print(f"💥 Error during generation: {e}")
            return None
            
        finally:
            # Clean up
            print(f"\n🧹 Cleaning up...")
            self.stop_engine()
            print(f"✅ Cleanup complete!")

if __name__ == "__main__":
    import sys
    
    # Get TT ID from command line or use the most recent
    if len(sys.argv) > 1:
        tt_id = sys.argv[1]
    else:
        import glob
        csv_files = glob.glob(str(Path(__file__).parent / "data_classes_TT*.csv"))
        if csv_files:
            latest_file = max(csv_files, key=lambda x: Path(x).stat().st_mtime)
            tt_id = Path(latest_file).name.replace('data_classes_', '').replace('.csv', '')
        else:
            print("❌ No test data found. Please generate test data first:")
            print("   python data_generator.py --config medium")
            sys.exit(1)
    
    # Run comprehensive generation
    generator = ComprehensiveTimetableGenerator()
    result = generator.run_complete_generation(tt_id)