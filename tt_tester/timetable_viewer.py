#!/usr/bin/env python3
"""
Universal Timetable Viewer - Reusable viewer for any timetable data
Supports multiple data sources and formats
"""

import csv
import json
import sys
import glob
from datetime import datetime
from collections import defaultdict

class TimetableViewer:
    """Universal timetable viewer with multiple data source support"""
    
    def __init__(self, tt_id=None):
        self.tt_id = tt_id
        self.data = {}
        
    def load_data_by_tt_id(self, tt_id):
        """Load data using TT generation ID"""
        self.tt_id = tt_id
        
        # Find data files with various patterns
        data_files = {
            'classes': glob.glob(f"*classes*{tt_id}*.csv"),
            'teachers': glob.glob(f"*teachers*{tt_id}*.csv"),
            'rooms': glob.glob(f"*rooms*{tt_id}*.csv"),
            'assignments': glob.glob(f"*assignments*{tt_id}*.csv"),
            'subjects': glob.glob(f"*subjects*{tt_id}*.csv"),
            'timetable': glob.glob(f"*timetable*{tt_id}*.csv")
        }
        
        # Load each data type
        for data_type, files in data_files.items():
            if files:
                self.data[data_type] = self.load_csv(files[0])
                print(f"✅ Loaded {data_type}: {len(self.data[data_type])} records from {files[0]}")
            else:
                self.data[data_type] = []
                print(f"⚠️  No {data_type} file found for TT ID: {tt_id}")
        
        # Load metadata if available
        metadata_files = glob.glob(f"metadata*{tt_id}*.json")
        if metadata_files:
            with open(metadata_files[0], 'r', encoding='utf-8') as f:
                self.data['metadata'] = json.load(f)
                print(f"✅ Loaded metadata from {metadata_files[0]}")
        
        return len(self.data['classes']) > 0
    
    def load_legacy_data(self):
        """Load legacy test data files"""
        legacy_files = {
            'classes': 'test_data_classes.csv',
            'teachers': 'test_data_teachers.csv',
            'rooms': 'test_data_rooms.csv',
            'assignments': 'test_data_assignments.csv',
            'subjects': 'test_data_subjects.csv'
        }
        
        for data_type, filename in legacy_files.items():
            try:
                self.data[data_type] = self.load_csv(filename)
                print(f"✅ Loaded legacy {data_type}: {len(self.data[data_type])} records")
            except FileNotFoundError:
                self.data[data_type] = []
                print(f"⚠️  Legacy file not found: {filename}")
        
        # Initialize timetable as empty for legacy data
        self.data['timetable'] = []
        self.data['metadata'] = {}
        
        self.tt_id = "LEGACY_DATA"
        return len(self.data['classes']) > 0
    
    def load_csv(self, filename):
        """Load CSV file"""
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def generate_mock_timetable(self):
        """Generate mock timetable from assignments if not provided"""
        if self.data['timetable']:
            return self.data['timetable']
        
        print("📝 Generating mock timetable from assignments...")
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        periods = list(range(1, 9))
        
        # Create class-assignment mapping
        class_assignments = defaultdict(list)
        for assignment in self.data['assignments']:
            class_assignments[assignment['class_id']].append(assignment)
        
        timetable_data = []
        assignment_id = 1
        
        for class_info in self.data['classes']:
            class_id = class_info['class_id']
            class_name = class_info['name']
            
            # Get assignments for this class
            class_subjects = class_assignments.get(class_id, [])
            
            # Create period pool
            period_pool = []
            total_assigned_periods = 0
            
            for assignment in class_subjects:
                periods_needed = int(assignment['periods_per_week'])
                total_assigned_periods += periods_needed
                
                for _ in range(periods_needed):
                    period_pool.append(assignment)
            
            # Fill remaining slots to complete schedule
            total_periods = len(days) * len(periods)
            remaining_periods = total_periods - total_assigned_periods
            
            if remaining_periods > 0:
                for i in range(remaining_periods):
                    assignment = class_subjects[i % len(class_subjects)] if class_subjects else None
                    if assignment:
                        period_pool.append(assignment)
            
            # Shuffle and assign
            import random
            random.shuffle(period_pool)
            
            period_index = 0
            for day in days:
                for period in periods:
                    if period_index < len(period_pool):
                        assignment = period_pool[period_index]
                        
                        # Find appropriate room
                        room = self.find_room(assignment.get('needs_lab', 'false') == 'true')
                        
                        entry = {
                            'tt_generation_id': self.tt_id,
                            'assignment_id': f"MOCK_{assignment_id:04d}",
                            'class_id': class_id,
                            'class_name': class_name,
                            'subject_code': assignment['subject_code'],
                            'subject_name': assignment['subject_name'],
                            'teacher_id': assignment['teacher_id'],
                            'teacher_name': assignment['teacher_name'],
                            'room_id': room['room_id'],
                            'room_name': room['name'],
                            'day': day,
                            'period': period,
                            'start_time': f"{8 + period}:00",
                            'end_time': f"{9 + period}:00"
                        }
                        
                        timetable_data.append(entry)
                        assignment_id += 1
                        period_index += 1
        
        self.data['timetable'] = timetable_data
        return timetable_data
    
    def find_room(self, needs_lab=False):
        """Find appropriate room"""
        if needs_lab:
            lab_rooms = [r for r in self.data['rooms'] if r['type'] == 'lab']
            if lab_rooms:
                import random
                return random.choice(lab_rooms)
        
        regular_rooms = [r for r in self.data['rooms'] if r['type'] == 'classroom']
        if regular_rooms:
            import random
            return random.choice(regular_rooms)
        
        # Fallback
        return {'room_id': 'ROOM_001', 'name': 'Default Room'}
    
    def validate_schedule(self):
        """Validate complete schedule"""
        timetable = self.data['timetable']
        if not timetable:
            return False, []
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        periods = list(range(1, 9))
        
        # Group by class
        class_schedules = defaultdict(list)
        for entry in timetable:
            class_schedules[entry['class_id']].append(entry)
        
        total_missing = 0
        incomplete_details = []
        
        for class_id, entries in class_schedules.items():
            class_name = entries[0]['class_name'] if entries else class_id
            
            # Create schedule grid
            schedule_grid = {}
            for entry in entries:
                key = (entry['day'], int(entry['period']))
                schedule_grid[key] = entry
            
            # Check for missing periods
            missing_periods = 0
            missing_slots = []
            
            for day in days:
                for period in periods:
                    key = (day, period)
                    if key not in schedule_grid:
                        missing_periods += 1
                        total_missing += 1
                        missing_slots.append(f"{day} P{period}")
            
            if missing_periods > 0:
                incomplete_details.append({
                    'class_id': class_id,
                    'class_name': class_name,
                    'gaps': missing_periods,
                    'missing_slots': missing_slots
                })
        
        return total_missing == 0, incomplete_details
    
    def create_viewer(self):
        """Create interactive HTML viewer"""
        if not self.data['classes']:
            print("❌ No data loaded")
            return None
        
        # Generate or load timetable
        timetable = self.generate_mock_timetable()
        
        # Validate schedule
        is_complete, incomplete_details = self.validate_schedule()
        
        # Prepare data for viewer
        classes = sorted(list(set(entry['class_id'] for entry in timetable)))
        teachers = sorted(list(set(entry['teacher_id'] for entry in timetable if entry['teacher_id'])))
        
        # Create teacher-subject mapping with period counts
        teacher_subjects = defaultdict(set)
        teacher_workload = defaultdict(lambda: defaultdict(int))
        for entry in timetable:
            if entry['teacher_id'] and entry['subject_code']:
                teacher_subjects[entry['teacher_id']].add(entry['subject_code'])
                teacher_workload[entry['teacher_id']][entry['subject_code']] += 1
        
        # Create class-teacher mapping with period counts
        class_teachers = defaultdict(list)
        class_subject_periods = defaultdict(lambda: defaultdict(int))
        
        for assignment in self.data['assignments']:
            class_teachers[assignment['class_id']].append({
                'teacher_id': assignment['teacher_id'],
                'teacher_name': assignment['teacher_name'],
                'subject_code': assignment['subject_code'],
                'subject_name': assignment['subject_name'],
                'periods_per_week': int(assignment['periods_per_week'])
            })
        
        # Count actual periods in timetable for each class-subject combination
        for entry in timetable:
            if entry['class_id'] and entry['subject_code']:
                class_subject_periods[entry['class_id']][entry['subject_code']] += 1
        
        # Generate HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"timetable_viewer_{self.tt_id}_{timestamp}.html"
        
        # Get metadata info
        metadata = self.data.get('metadata', {})
        config_name = metadata.get('config_name', 'Unknown')
        
        # Validation status
        status_class = "constraint-success" if is_complete else "constraint-error"
        status_text = "✅ Complete Schedule - All periods assigned!" if is_complete else f"❌ {len(incomplete_details)} classes have missing periods"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timetable Viewer - {self.tt_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .tt-id {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 10px;
            font-family: monospace;
            background: rgba(255,255,255,0.1);
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
        }}
        
        .config-info {{
            font-size: 1em;
            opacity: 0.8;
        }}
        
        .validation-status {{
            padding: 15px 20px;
            margin: 20px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 1.1em;
            text-align: center;
        }}
        
        .constraint-success {{
            background: #d4edda;
            color: #155724;
            border: 2px solid #c3e6cb;
        }}
        
        .constraint-error {{
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #f5c6cb;
        }}
        
        .stats-bar {{
            background: #f8f9fa;
            padding: 20px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .stat-item {{
            text-align: center;
            margin: 10px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .controls {{
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .control-group {{
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .control-group label {{
            font-weight: 600;
            color: #2c3e50;
            min-width: 100px;
        }}
        
        .control-group select {{
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            background: white;
            min-width: 200px;
            transition: border-color 0.3s;
        }}
        
        .control-group select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .info-panels {{
            display: flex;
            gap: 20px;
            padding: 20px 30px;
            background: #f8f9fa;
            flex-wrap: wrap;
        }}
        
        .info-panel {{
            flex: 1;
            min-width: 300px;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .panel-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .teacher-details {{
            margin-bottom: 15px;
        }}
        
        .teacher-name {{
            font-size: 1.1em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .teacher-meta {{
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 10px;
        }}
        
        .subjects-list {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .subject-badge {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        
        .class-teachers-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        
        .class-teachers-table th {{
            background: #f8f9fa;
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid #e9ecef;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .class-teachers-table td {{
            padding: 8px 10px;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.9em;
        }}
        
        .class-teachers-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .workload-section {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .workload-section h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1em;
        }}
        
        .workload-summary {{
            margin-bottom: 15px;
        }}
        
        .workload-bar, .utilization-bar {{
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            margin: 8px 0;
            overflow: hidden;
        }}
        
        .workload-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #ffc107 70%, #dc3545 90%);
            transition: width 0.3s ease;
        }}
        
        .utilization-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }}
        
        .workload-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        
        .workload-table th {{
            background: #e9ecef;
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
            font-weight: 600;
            color: #495057;
        }}
        
        .workload-table td {{
            padding: 6px 8px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .workload-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .class-summary {{
            margin-bottom: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
        }}
        
        .class-summary h4 {{
            color: #1976d2;
            margin-bottom: 10px;
            font-size: 1em;
        }}
        
        .subjects-list h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1em;
        }}
        
        .timetable-container {{
            padding: 30px;
            overflow-x: auto;
        }}
        
        .timetable {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .timetable th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 10px;
            text-align: center;
            font-weight: 600;
            font-size: 0.9em;
        }}
        
        .timetable td {{
            padding: 12px 8px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
            vertical-align: middle;
            font-size: 0.85em;
        }}
        
        .timetable tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .subject-cell {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .teacher-cell {{
            color: #495057;
            font-size: 0.8em;
        }}
        
        .room-cell {{
            color: #6c757d;
            font-size: 0.75em;
        }}
        
        .time-cell {{
            background: #f8f9fa !important;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .missing-cell {{
            background-color: #f8d7da !important;
            color: #721c24;
            font-weight: bold;
        }}
        
        .hidden {{
            display: none;
        }}
        
        @media (max-width: 768px) {{
            .info-panels {{
                flex-direction: column;
            }}
            
            .control-group {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .control-group select {{
                min-width: 100%;
            }}
            
            .stats-bar {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Universal Timetable Viewer</h1>
            <div class="tt-id">TT ID: {self.tt_id}</div>
            <div class="config-info">{config_name} Configuration</div>
        </div>
        
        <div class="validation-status {status_class}">
            {status_text}
        </div>
        
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-number">{len(classes)}</div>
                <div class="stat-label">Classes</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(teachers)}</div>
                <div class="stat-label">Teachers</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(timetable)}</div>
                <div class="stat-label">Total Periods</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(classes) * 40}</div>
                <div class="stat-label">Expected Periods</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="viewType">View Type:</label>
                <select id="viewType" onchange="switchView()">
                    <option value="class">Class Timetable</option>
                    <option value="teacher">Teacher Schedule</option>
                </select>
                
                <label for="entitySelect">Select:</label>
                <select id="entitySelect" onchange="updateDisplay()">
                </select>
            </div>
        </div>
        
        <div class="info-panels">
            <div class="info-panel" id="teacherInfoPanel">
                <div class="panel-title">👨‍🏫 Teacher Information</div>
                <div id="teacherDetails">
                    <p>Select a teacher to view details</p>
                </div>
            </div>
            
            <div class="info-panel" id="classTeachersPanel">
                <div class="panel-title">📚 Class Teachers & Subjects</div>
                <div id="classTeachersContent">
                    <p>Select a class to view teachers</p>
                </div>
            </div>
        </div>
        
        <div class="timetable-container">
            <table class="timetable">
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
                <tbody id="timetableBody">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Data from Python
        const timetableData = {json.dumps(timetable, indent=8)};
        const teachersData = {json.dumps({t['teacher_id']: t for t in self.data['teachers']}, indent=8)};
        const classTeachersData = {json.dumps(dict(class_teachers), indent=8)};
        const classList = {json.dumps(classes)};
        const teacherList = {json.dumps(teachers)};
        const teacherSubjects = {json.dumps({k: list(v) for k, v in teacher_subjects.items()})};
        const teacherWorkload = {json.dumps(dict(teacher_workload), indent=8)};
        const classSubjectPeriods = {json.dumps(dict(class_subject_periods), indent=8)};
        
        let currentView = 'class';
        
        function switchView() {{
            currentView = document.getElementById('viewType').value;
            populateEntitySelect();
            updateDisplay();
        }}
        
        function populateEntitySelect() {{
            const select = document.getElementById('entitySelect');
            select.innerHTML = '';
            
            const entities = currentView === 'class' ? classList : teacherList;
            entities.forEach(entity => {{
                const option = document.createElement('option');
                option.value = entity;
                option.textContent = entity;
                select.appendChild(option);
            }});
        }}
        
        function updateDisplay() {{
            const selectedEntity = document.getElementById('entitySelect').value;
            
            if (currentView === 'teacher') {{
                showTeacherInfo(selectedEntity);
                hideClassTeachers();
            }} else {{
                showClassTeachers(selectedEntity);
                hideTeacherInfo();
            }}
            
            updateTimetable(selectedEntity);
        }}
        
        function showTeacherInfo(teacherId) {{
            const panel = document.getElementById('teacherInfoPanel');
            const details = document.getElementById('teacherDetails');
            const teacher = teachersData[teacherId];
            
            if (teacher) {{
                const subjects = teacher.subjects_qualified ? teacher.subjects_qualified.split(',') : [];
                const workload = teacherWorkload[teacherId] || {{}};
                
                // Calculate total workload
                let totalPeriods = 0;
                Object.values(workload).forEach(periods => totalPeriods += periods);
                
                // Create workload breakdown
                let workloadHTML = '';
                if (Object.keys(workload).length > 0) {{
                    workloadHTML = `
                        <div class="workload-section">
                            <h4>📊 Current Workload</h4>
                            <div class="workload-summary">
                                <strong>Total: ${{totalPeriods}} / ${{teacher.max_periods_per_week}} periods per week</strong>
                                <div class="workload-bar">
                                    <div class="workload-fill" style="width: ${{(totalPeriods / teacher.max_periods_per_week) * 100}}%"></div>
                                </div>
                            </div>
                            <table class="workload-table">
                                <thead>
                                    <tr>
                                        <th>Subject</th>
                                        <th>Periods/Week</th>
                                        <th>% of Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{Object.entries(workload).map(([subject, periods]) => `
                                        <tr>
                                            <td><span class="subject-badge">${{subject}}</span></td>
                                            <td>${{periods}} periods</td>
                                            <td>${{((periods / totalPeriods) * 100).toFixed(1)}}%</td>
                                        </tr>
                                    `).join('')}}
                                </tbody>
                            </table>
                        </div>
                    `;
                }}
                
                details.innerHTML = `
                    <div class="teacher-details">
                        <div class="teacher-name">${{teacher.name}}</div>
                        <div class="teacher-meta">
                            📧 ${{teacher.email}}<br>
                            📞 ${{teacher.phone}}<br>
                            ⏰ Max: ${{teacher.max_periods_per_day}} periods/day, ${{teacher.max_periods_per_week}} periods/week
                        </div>
                        <div class="subjects-list">
                            <h4>🎓 Qualified Subjects</h4>
                            ${{subjects.map(subject => `<span class="subject-badge">${{subject}}</span>`).join('')}}
                        </div>
                        ${{workloadHTML}}
                    </div>
                `;
            }}
            
            panel.classList.remove('hidden');
        }}
        
        function hideTeacherInfo() {{
            document.getElementById('teacherInfoPanel').classList.add('hidden');
        }}
        
        function showClassTeachers(classId) {{
            const panel = document.getElementById('classTeachersPanel');
            const content = document.getElementById('classTeachersContent');
            const classTeachers = classTeachersData[classId] || [];
            const subjectPeriods = classSubjectPeriods[classId] || {{}};
            
            if (classTeachers.length > 0) {{
                // Calculate total periods for this class
                let totalPeriods = 0;
                Object.values(subjectPeriods).forEach(periods => totalPeriods += periods);
                
                let tableHTML = `
                    <div class="class-summary">
                        <h4>📊 Class Schedule Summary</h4>
                        <p><strong>Total Periods Assigned: ${{totalPeriods}} / 40 per week</strong></p>
                        <div class="utilization-bar">
                            <div class="utilization-fill" style="width: ${{(totalPeriods / 40) * 100}}%"></div>
                        </div>
                    </div>
                    <table class="class-teachers-table">
                        <thead>
                            <tr>
                                <th>Teacher</th>
                                <th>Subject</th>
                                <th>Assigned Periods</th>
                                <th>Actual Periods</th>
                                <th>Teacher ID</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                classTeachers.forEach(teacher => {{
                    const actualPeriods = subjectPeriods[teacher.subject_code] || 0;
                    const assignedPeriods = teacher.periods_per_week || 0;
                    const statusIcon = actualPeriods === assignedPeriods ? '✅' : 
                                     actualPeriods > assignedPeriods ? '⚠️' : '❌';
                    
                    tableHTML += `
                        <tr>
                            <td>${{teacher.teacher_name}}</td>
                            <td><span class="subject-badge">${{teacher.subject_name}}</span></td>
                            <td>${{assignedPeriods}} periods</td>
                            <td>${{statusIcon}} ${{actualPeriods}} periods</td>
                            <td>${{teacher.teacher_id}}</td>
                        </tr>
                    `;
                }});
                
                tableHTML += `
                        </tbody>
                    </table>
                `;
                
                content.innerHTML = tableHTML;
            }} else {{
                content.innerHTML = '<p>No teachers assigned to this class</p>';
            }}
            
            panel.classList.remove('hidden');
        }}
        
        function hideClassTeachers() {{
            document.getElementById('classTeachersPanel').classList.add('hidden');
        }}
        
        function updateTimetable(selectedEntity) {{
            const tbody = document.getElementById('timetableBody');
            
            // Filter data for selected entity
            const filteredData = timetableData.filter(entry => {{
                if (currentView === 'class') {{
                    return entry.class_id === selectedEntity;
                }} else {{
                    return entry.teacher_id === selectedEntity;
                }}
            }});
            
            // Create timetable grid
            const periods = [1, 2, 3, 4, 5, 6, 7, 8];
            const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
            
            tbody.innerHTML = '';
            
            periods.forEach(period => {{
                const row = document.createElement('tr');
                
                // Time column
                const timeCell = document.createElement('td');
                timeCell.innerHTML = `<strong>Period ${{period}}</strong><br>${{8 + period}}:00 - ${{9 + period}}:00`;
                timeCell.classList.add('time-cell');
                row.appendChild(timeCell);
                
                // Day columns
                days.forEach(day => {{
                    const cell = document.createElement('td');
                    const entry = filteredData.find(e => e.day === day && parseInt(e.period) === period);
                    
                    if (entry) {{
                        cell.innerHTML = `
                            <div class="subject-cell">${{entry.subject_name}}</div>
                            <div class="teacher-cell">${{entry.teacher_name}}</div>
                            <div class="room-cell">${{entry.room_name}}</div>
                        `;
                    }} else {{
                        cell.innerHTML = '<div class="missing-cell">MISSING!</div>';
                        cell.classList.add('missing-cell');
                    }}
                    
                    row.appendChild(cell);
                }});
                
                tbody.appendChild(row);
            }});
        }}
        
        // Initialize
        populateEntitySelect();
        updateDisplay();
    </script>
</body>
</html>"""
        
        # Save HTML file
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ Universal Viewer Created: {html_filename}")
        print(f"🆔 TT Generation ID: {self.tt_id}")
        print(f"🔍 Schedule status: {'✅ COMPLETE' if is_complete else '❌ INCOMPLETE'}")
        
        if not is_complete:
            print(f"⚠️  Classes with missing periods: {len(incomplete_details)}")
            for incomplete in incomplete_details[:3]:  # Show first 3
                print(f"   - {incomplete['class_name']}: {incomplete['gaps']} missing periods")
        
        return html_filename

def main():
    """Main function with command-line interface"""
    if len(sys.argv) < 2:
        print("🎓 Universal Timetable Viewer")
        print("Usage:")
        print("  python3 timetable_viewer.py <TT_ID>     # View by TT generation ID")
        print("  python3 timetable_viewer.py legacy      # View legacy test data")
        print("  python3 timetable_viewer.py latest      # View latest generation")
        return
    
    arg = sys.argv[1]
    viewer = TimetableViewer()
    
    if arg.lower() == "legacy":
        if viewer.load_legacy_data():
            viewer_file = viewer.create_viewer()
            if viewer_file:
                print(f"\n🎉 Open {viewer_file} in your browser!")
        else:
            print("❌ Failed to load legacy data")
    
    elif arg.lower() == "latest":
        # Find latest generation
        metadata_files = glob.glob("metadata_TT_*.json")
        if not metadata_files:
            print("❌ No generations found")
            return
        
        # Sort by timestamp (newest first)
        metadata_files.sort(reverse=True)
        
        with open(metadata_files[0], 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            tt_id = metadata['tt_generation_id']
        
        if viewer.load_data_by_tt_id(tt_id):
            viewer_file = viewer.create_viewer()
            if viewer_file:
                print(f"\n🎉 Open {viewer_file} in your browser!")
        else:
            print(f"❌ Failed to load data for TT ID: {tt_id}")
    
    else:
        # Treat as TT ID
        tt_id = arg
        if viewer.load_data_by_tt_id(tt_id):
            viewer_file = viewer.create_viewer()
            if viewer_file:
                print(f"\n🎉 Open {viewer_file} in your browser!")
        else:
            print(f"❌ Failed to load data for TT ID: {tt_id}")

if __name__ == "__main__":
    main()