#!/usr/bin/env python3
"""
View and validate timetable generation results with gap detection
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def load_metadata(tt_id):
    """Load metadata and CSV data for subject/class/teacher names"""
    base_path = Path(__file__).parent

    with open(base_path / f"metadata_{tt_id}.json", 'r') as f:
        metadata = json.load(f)

    # Load subject names
    import csv
    subjects = {}
    with open(base_path / f"data_subjects_{tt_id}.csv", 'r') as f:
        for row in csv.DictReader(f):
            subjects[f"sub-{row['code'].lower()}"] = row['name']

    # Load class names
    classes = {}
    with open(base_path / f"data_classes_{tt_id}.csv", 'r') as f:
        for row in csv.DictReader(f):
            classes[row['class_id']] = row['name']

    # Load teacher names
    teachers = {}
    with open(base_path / f"data_teachers_{tt_id}.csv", 'r') as f:
        for row in csv.DictReader(f):
            teachers[row['teacher_id']] = row['name']

    return metadata, subjects, classes, teachers

def analyze_timetable(tt_id):
    """Analyze timetable for completeness and gaps"""
    base_path = Path(__file__).parent
    result_file = base_path / f"result_{tt_id}.json"

    if not result_file.exists():
        print(f"❌ Result file not found: {result_file}")
        return

    with open(result_file, 'r') as f:
        result = json.load(f)

    if result['status'] != 'success':
        print(f"❌ Generation failed: {result.get('status')}")
        return

    metadata, subjects, classes, teachers = load_metadata(tt_id)

    # Analyze first solution
    solution = result['solutions'][0]
    timetable = solution['timetable']
    entries = timetable['entries']

    print("\n" + "=" * 80)
    print(f"TIMETABLE ANALYSIS - {tt_id}")
    print("=" * 80)
    print(f"\nMetadata:")
    print(f"  Classes: {metadata['classes_count']}")
    print(f"  Teachers: {metadata['teachers_count']}")
    print(f"  Subjects: {metadata['subjects_count']}")
    print(f"  Total periods per class: 40 (5 days × 8 periods)")
    print(f"  Expected entries: {metadata['classes_count'] * 40}")
    print(f"\nResults:")
    print(f"  Total entries generated: {len(entries)}")
    print(f"  Solutions provided: {len(result['solutions'])}")
    print(f"  Status: {result['status']}")

    # Group by class to check for gaps
    class_schedules = defaultdict(list)
    for entry in entries:
        class_schedules[entry['class_id']].append(entry)

    # Days and periods
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
    periods_per_day = 8

    # Check each class for completeness
    print(f"\n{'=' * 80}")
    print("GAP ANALYSIS BY CLASS")
    print("=" * 80)

    total_gaps = 0
    for class_id in sorted(classes.keys()):
        class_name = classes[class_id]
        schedule = class_schedules[class_id]

        # Create a grid to check coverage
        coverage = {}
        for day in days:
            for period in range(1, periods_per_day + 1):
                coverage[(day, period)] = None

        # Fill in the schedule
        for entry in schedule:
            key = (entry['day_of_week'], entry['period_number'])
            coverage[key] = entry

        # Count gaps
        gaps = sum(1 for v in coverage.values() if v is None)
        total_gaps += gaps

        status = "✅ COMPLETE" if gaps == 0 else f"❌ {gaps} GAPS"
        print(f"{class_name:15} : {len(schedule):3}/40 periods | {status}")

    print(f"\n{'=' * 80}")
    if total_gaps == 0:
        print("🎉 SUCCESS: All classes have ZERO gaps - 100% coverage achieved!")
    else:
        print(f"❌ FAILURE: Total gaps across all classes: {total_gaps}")
    print("=" * 80)

    return total_gaps == 0

def generate_html_report(tt_id):
    """Generate HTML report showing all class timetables"""
    base_path = Path(__file__).parent
    result_file = base_path / f"result_{tt_id}.json"

    with open(result_file, 'r') as f:
        result = json.load(f)

    metadata, subjects, classes, teachers = load_metadata(tt_id)

    solution = result['solutions'][0]
    entries = solution['timetable']['entries']

    # Group by class
    class_schedules = defaultdict(list)
    for entry in entries:
        class_schedules[entry['class_id']].append(entry)

    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
    periods_per_day = 8

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Complete Timetable - {tt_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }}
        h1 {{ color: #2c3e50; text-align: center; margin: 20px 0; }}

        /* Tab Navigation */
        .tabs {{ background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .tab-buttons {{ display: flex; border-bottom: 2px solid #ddd; }}
        .tab-button {{ padding: 15px 30px; cursor: pointer; border: none; background: none; font-size: 16px; font-weight: bold; color: #7f8c8d; transition: all 0.3s; }}
        .tab-button:hover {{ background: #ecf0f1; }}
        .tab-button.active {{ color: #3498db; border-bottom: 3px solid #3498db; }}
        .tab-content {{ display: none; padding: 20px; }}
        .tab-content.active {{ display: block; }}

        .summary {{ background: #fff; padding: 20px; border-radius: 8px; margin: 0 20px 30px 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .summary h2 {{ margin-top: 0; color: #27ae60; }}
        .summary .stat {{ display: inline-block; margin-right: 30px; }}
        .class-timetable {{ background: white; margin: 30px 20px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .class-timetable h3 {{ margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background: #3498db; color: white; padding: 12px; text-align: left; font-weight: bold; }}
        td {{ padding: 10px; border: 1px solid #ddd; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .subject {{ font-weight: bold; color: #2c3e50; }}
        .teacher {{ color: #7f8c8d; font-size: 0.9em; }}
        .class-info {{ color: #16a085; font-size: 0.9em; }}
        .gap {{ background: #ffebee !important; color: #c62828; font-weight: bold; }}
        .free {{ background: #e8f5e9 !important; color: #2e7d32; }}
        .complete-badge {{ display: inline-block; background: #27ae60; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.85em; margin-left: 10px; }}
        .gap-badge {{ display: inline-block; background: #e74c3c; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.85em; margin-left: 10px; }}
        .workload-badge {{ display: inline-block; background: #9b59b6; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.85em; margin-left: 10px; }}
    </style>
    <script>
        function switchTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            document.querySelector(`[onclick="switchTab('${{tabName}}')"]`).classList.add('active');
        }}
    </script>
</head>
<body>
    <h1>🎓 Complete School Timetable</h1>

    <div class="tabs">
        <div class="tab-buttons">
            <button class="tab-button active" onclick="switchTab('classes')">📚 Class Timetables</button>
            <button class="tab-button" onclick="switchTab('teachers')">👨‍🏫 Teacher Timetables</button>
        </div>
    </div>

    <div class="summary">
        <h2>✅ Generation Summary</h2>
        <div class="stat"><strong>TT ID:</strong> {tt_id}</div>
        <div class="stat"><strong>Classes:</strong> {metadata['classes_count']}</div>
        <div class="stat"><strong>Teachers:</strong> {metadata['teachers_count']}</div>
        <div class="stat"><strong>Total Entries:</strong> {len(entries)}/{metadata['classes_count'] * 40}</div>
        <div class="stat"><strong>Coverage:</strong> {(len(entries) / (metadata['classes_count'] * 40) * 100):.1f}%</div>
    </div>

    <div id="classes" class="tab-content active">
"""

    # Generate tables for each class
    for class_id in sorted(classes.keys()):
        class_name = classes[class_id]
        schedule = class_schedules[class_id]

        # Create coverage grid
        coverage = {}
        for day in days:
            for period in range(1, periods_per_day + 1):
                coverage[(day, period)] = None

        for entry in schedule:
            key = (entry['day_of_week'], entry['period_number'])
            coverage[key] = entry

        gaps = sum(1 for v in coverage.values() if v is None)
        badge = '<span class="complete-badge">✅ NO GAPS</span>' if gaps == 0 else f'<span class="gap-badge">❌ {gaps} GAPS</span>'

        html += f"""
    <div class="class-timetable">
        <h3>{class_name} {badge}</h3>
        <table>
            <tr>
                <th>Period</th>
                <th>Monday</th>
                <th>Tuesday</th>
                <th>Wednesday</th>
                <th>Thursday</th>
                <th>Friday</th>
            </tr>
"""

        for period in range(1, periods_per_day + 1):
            html += f"            <tr><td><strong>P{period}</strong></td>"

            for day in days:
                entry = coverage.get((day, period))
                if entry:
                    subject_name = subjects.get(entry['subject_id'], entry['subject_id'])
                    teacher_name = teachers.get(entry['teacher_id'], entry['teacher_id'])
                    html += f'<td><div class="subject">{subject_name}</div><div class="teacher">{teacher_name}</div></td>'
                else:
                    html += '<td class="gap">FREE PERIOD (GAP)</td>'

            html += "</tr>\n"

        html += "        </table>\n    </div>\n"

    html += "    </div>\n\n"  # Close classes tab

    # Generate Teacher Timetables Tab
    html += '    <div id="teachers" class="tab-content">\n'

    # Group by teacher
    teacher_schedules = defaultdict(list)
    for entry in entries:
        teacher_schedules[entry['teacher_id']].append(entry)

    for teacher_id in sorted(teachers.keys()):
        teacher_name = teachers[teacher_id]
        schedule = teacher_schedules.get(teacher_id, [])

        # Create coverage grid
        coverage = {}
        for day in days:
            for period in range(1, periods_per_day + 1):
                coverage[(day, period)] = None

        for entry in schedule:
            key = (entry['day_of_week'], entry['period_number'])
            coverage[key] = entry

        # Count periods and free periods
        periods_assigned = len(schedule)
        free_periods = 40 - periods_assigned

        workload_color = "#27ae60" if periods_assigned <= 30 else "#e67e22" if periods_assigned <= 35 else "#e74c3c"
        workload_badge = f'<span class="workload-badge" style="background: {workload_color};">{periods_assigned}/40 periods</span>'

        html += f"""
    <div class="class-timetable">
        <h3>{teacher_name} {workload_badge}</h3>
        <table>
            <tr>
                <th>Period</th>
                <th>Monday</th>
                <th>Tuesday</th>
                <th>Wednesday</th>
                <th>Thursday</th>
                <th>Friday</th>
            </tr>
"""

        for period in range(1, periods_per_day + 1):
            html += f"            <tr><td><strong>P{period}</strong></td>"

            for day in days:
                entry = coverage.get((day, period))
                if entry:
                    subject_name = subjects.get(entry['subject_id'], entry['subject_id'])
                    class_name = classes.get(entry['class_id'], entry['class_id'])
                    html += f'<td><div class="subject">{subject_name}</div><div class="class-info">{class_name}</div></td>'
                else:
                    html += '<td class="free">Free Period</td>'

            html += "</tr>\n"

        html += "        </table>\n    </div>\n"

    html += "    </div>\n\n"  # Close teachers tab

    html += """
</body>
</html>
"""

    output_file = base_path / f"timetable_verification_{tt_id}.html"
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"\n✅ HTML report generated: {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 view_timetable.py <TT_ID>")
        print("Example: python3 view_timetable.py TT_20250930_155334_8fd6ea32")
        sys.exit(1)

    tt_id = sys.argv[1]

    # Analyze for gaps
    success = analyze_timetable(tt_id)

    # Generate HTML report
    html_file = generate_html_report(tt_id)

    # Open in browser
    import subprocess
    subprocess.run(['open', str(html_file)])

    sys.exit(0 if success else 1)