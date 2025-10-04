#!/usr/bin/env python3
"""
Simple A/B Testing - Manual Version
Tests one engine at a time to avoid subprocess complexity
"""

import json
import time
import requests
import csv
from pathlib import Path
from datetime import datetime
import statistics

class SimpleABTester:
    """Simple A/B testing that requires manual engine startup"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {}
    
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
        with open(self.base_path / f"data_classes_{tt_id}.csv", 'r') as f:
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

        # Load teachers
        teachers = []
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

        # Load rooms
        rooms = []
        with open(self.base_path / f"data_rooms_{tt_id}.csv", 'r') as f:
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

        return {
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
            "timeout": 120
        }

    def test_engine(self, version, test_data, port, runs=3):
        """Test a specific engine version"""
        url = f"http://localhost:{port}/generate"
        
        print(f"\n🧪 Testing {version} engine on port {port} ({runs} runs)...")
        
        # First, check if the engine is running
        try:
            health_check = requests.get(f"http://localhost:{port}/docs", timeout=5)
            if health_check.status_code != 200:
                print(f"❌ Engine not responding on port {port}. Please start the engine first.")
                return None
        except Exception as e:
            print(f"❌ Engine not accessible on port {port}: {str(e)}")
            print(f"   Please start the engine first:")
            print(f"   cd ../timetable-engine")
            if version == "v20":
                print(f"   python main_v20.py")
            else:
                print(f"   python main_v25.py")
            return None
        
        print(f"✅ Engine is running on port {port}")
        
        results = {
            'version': version,
            'runs': [],
            'success_count': 0,
            'avg_time': 0,
            'avg_score': 0,
            'avg_coverage': 0,
            'errors': []
        }
        
        for run in range(runs):
            print(f"   Run {run + 1}/{runs}...", end=" ")
            
            try:
                start_time = time.time()
                response = requests.post(url, json=test_data, timeout=150)
                end_time = time.time()
                
                generation_time = end_time - start_time
                
                if response.status_code == 200:
                    result_data = response.json()
                    
                    # Extract metrics
                    diagnostics = result_data.get('diagnostics', {})
                    schedules = result_data.get('schedules', [])
                    
                    run_result = {
                        'success': True,
                        'time': generation_time,
                        'status': result_data.get('status', 'unknown'),
                        'message': result_data.get('message', ''),
                        'schedules_count': len(schedules),
                        'total_assignments': diagnostics.get('total_assignments', 0),
                        'scheduled_assignments': diagnostics.get('scheduled_assignments', 0),
                        'coverage': diagnostics.get('coverage_percentage', 0),
                        'score': diagnostics.get('best_fitness', 0)
                    }
                    
                    results['runs'].append(run_result)
                    results['success_count'] += 1
                    
                    print(f"✅ Success ({generation_time:.2f}s, {run_result['coverage']:.1f}% coverage)")
                    
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:100]}..."
                    results['errors'].append(error_msg)
                    results['runs'].append({
                        'success': False,
                        'time': generation_time,
                        'error': error_msg
                    })
                    print(f"❌ Failed ({error_msg})")
                    
            except Exception as e:
                error_msg = str(e)
                results['errors'].append(error_msg)
                results['runs'].append({
                    'success': False,
                    'time': 0,
                    'error': error_msg
                })
                print(f"💥 Error ({error_msg})")
        
        # Calculate averages
        successful_runs = [r for r in results['runs'] if r.get('success', False)]
        if successful_runs:
            results['avg_time'] = statistics.mean([r['time'] for r in successful_runs])
            results['avg_score'] = statistics.mean([r.get('score', 0) for r in successful_runs])
            results['avg_coverage'] = statistics.mean([r.get('coverage', 0) for r in successful_runs])
        
        return results

    def generate_comparison_report(self, tt_id, v20_results, v25_results):
        """Generate HTML comparison report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Determine winner
        v20_success_rate = (v20_results.get('success_count', 0) / len(v20_results.get('runs', []))) * 100 if v20_results and v20_results.get('runs') else 0
        v25_success_rate = (v25_results.get('success_count', 0) / len(v25_results.get('runs', []))) * 100 if v25_results and v25_results.get('runs') else 0
        
        v20_time = v20_results.get('avg_time', float('inf')) if v20_results else float('inf')
        v25_time = v25_results.get('avg_time', float('inf')) if v25_results else float('inf')
        
        v20_coverage = v20_results.get('avg_coverage', 0) if v20_results else 0
        v25_coverage = v25_results.get('avg_coverage', 0) if v25_results else 0
        
        # Simple winner determination
        v20_score = 0
        v25_score = 0
        
        if v20_success_rate > v25_success_rate:
            v20_score += 40
        elif v25_success_rate > v20_success_rate:
            v25_score += 40
        else:
            v20_score += 20
            v25_score += 20
        
        if v20_time < v25_time:
            v20_score += 30
        elif v25_time < v20_time:
            v25_score += 30
        else:
            v20_score += 15
            v25_score += 15
        
        if v20_coverage > v25_coverage:
            v20_score += 30
        elif v25_coverage > v20_coverage:
            v25_score += 30
        else:
            v20_score += 15
            v25_score += 15
        
        winner = 'v20' if v20_score > v25_score else ('v25' if v25_score > v20_score else 'tie')
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A/B Test Results: main_v20 vs main_v25</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
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
            font-size: 36px;
            color: #2d3748;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 16px;
            color: #718096;
        }}

        .winner-banner {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .winner-banner h2 {{
            font-size: 28px;
            margin-bottom: 10px;
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

        .version-card h3 {{
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .stat-card {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
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

        .success {{
            color: #48bb78;
        }}

        .error {{
            color: #f56565;
        }}

        .warning {{
            color: #ed8936;
        }}

        .winner-badge {{
            background: #48bb78;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #edf2f7;
        }}

        th {{
            background: #f7fafc;
            font-weight: 600;
            color: #4a5568;
        }}

        .run-success {{
            color: #48bb78;
            font-weight: 600;
        }}

        .run-error {{
            color: #f56565;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 A/B Test Results: Timetable Generators</h1>
            <div class="subtitle">main_v20.py vs main_v25.py</div>
            <div class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
            <div class="subtitle">Test Data: {tt_id}</div>
        </div>
'''

        # Winner banner
        if winner != 'tie':
            winner_name = f"main_{winner}.py"
            winner_score = v20_score if winner == 'v20' else v25_score
            html_content += f'''
        <div class="winner-banner">
            <h2>🏆 Winner: {winner_name}</h2>
            <p>Overall Score: {winner_score}/100 points</p>
        </div>
'''
        else:
            html_content += '''
        <div class="winner-banner">
            <h2>🤝 It's a Tie!</h2>
            <p>Both versions performed equally well</p>
        </div>
'''

        # Comparison grid
        html_content += '''
        <div class="comparison-grid">
'''

        # Version cards
        for version, results in [('v20', v20_results), ('v25', v25_results)]:
            if not results:
                html_content += f'''
            <div class="version-card">
                <h3>main_{version}.py</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value error">N/A</div>
                        <div class="stat-label">No Data</div>
                    </div>
                </div>
                <p style="color: #f56565; text-align: center; margin: 20px;">Engine was not tested</p>
            </div>
'''
                continue
                
            runs = results.get('runs', [])
            total_runs = len(runs)
            success_count = results.get('success_count', 0)
            success_rate = (success_count / total_runs * 100) if total_runs > 0 else 0
            
            is_overall_winner = winner == version
            
            html_content += f'''
            <div class="version-card">
                <h3>
                    main_{version}.py 
                    {f'<span class="winner-badge">Overall Winner</span>' if is_overall_winner else ''}
                </h3>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value {'success' if success_rate == 100 else 'warning' if success_rate > 0 else 'error'}">{success_rate:.0f}%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{results.get('avg_time', 0):.2f}s</div>
                        <div class="stat-label">Avg Time</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{results.get('avg_coverage', 0):.1f}%</div>
                        <div class="stat-label">Avg Coverage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{success_count}/{total_runs}</div>
                        <div class="stat-label">Successful Runs</div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Run</th>
                            <th>Status</th>
                            <th>Time</th>
                            <th>Coverage</th>
                        </tr>
                    </thead>
                    <tbody>
'''
            
            for i, run in enumerate(runs, 1):
                if run.get('success', False):
                    html_content += f'''
                        <tr>
                            <td>Run {i}</td>
                            <td class="run-success">✅ Success</td>
                            <td>{run.get('time', 0):.2f}s</td>
                            <td>{run.get('coverage', 0):.1f}%</td>
                        </tr>
'''
                else:
                    html_content += f'''
                        <tr>
                            <td>Run {i}</td>
                            <td class="run-error">❌ Failed</td>
                            <td>{run.get('time', 0):.2f}s</td>
                            <td>-</td>
                        </tr>
'''
            
            html_content += '''
                    </tbody>
                </table>
            </div>
'''

        html_content += '''
        </div>
    </div>
</body>
</html>
'''

        # Save report
        report_file = self.base_path / f"simple_ab_test_report_{tt_id}_{timestamp}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_file

    def run_test_sequence(self, tt_id):
        """Run the test sequence with user prompts"""
        print(f"\n{'='*80}")
        print(f"🔬 Simple A/B Test: main_v20 vs main_v25")
        print(f"📊 Test Data: {tt_id}")
        print(f"{'='*80}")
        
        # Load test data
        test_data = self.load_test_data(tt_id)
        print(f"📋 Loaded data: {len(test_data['classes'])} classes, {len(test_data['teachers'])} teachers, {len(test_data['assignments'])} assignments")
        
        # Test v20
        print(f"\n🧪 Step 1: Testing main_v20.py")
        print(f"📝 Instructions:")
        print(f"   1. Open a new terminal/command prompt")
        print(f"   2. Navigate to: cd ../timetable-engine")
        print(f"   3. Start the engine: python main_v20.py")
        print(f"   4. Wait for 'Application startup complete' message")
        print(f"   5. Press Enter here to continue...")
        
        input("\n⏸️  Press Enter when main_v20.py is running on http://localhost:8000...")
        
        v20_results = self.test_engine('v20', test_data, 8000, 3)
        
        print(f"\n✅ v20 testing complete!")
        print(f"📝 Instructions:")
        print(f"   1. Stop the main_v20.py server (Ctrl+C)")
        print(f"   2. Start main_v25.py: python main_v25.py")
        print(f"   3. Wait for 'Application startup complete' message")
        print(f"   4. Press Enter here to continue...")
        
        input("\n⏸️  Press Enter when main_v25.py is running on http://localhost:8000...")
        
        v25_results = self.test_engine('v25', test_data, 8000, 3)
        
        print(f"\n✅ v25 testing complete!")
        
        # Generate report
        report_file = self.generate_comparison_report(tt_id, v20_results, v25_results)
        
        print(f"\n{'='*80}")
        print(f"✅ A/B Test Complete!")
        print(f"📄 Report generated: {report_file}")
        print(f"🌐 Opening report in browser...")
        print(f"{'='*80}")
        
        # Try to open the report
        import webbrowser
        try:
            webbrowser.open(str(report_file))
        except:
            print(f"Could not auto-open browser. Please manually open: {report_file}")
        
        # Print summary
        if v20_results and v25_results:
            print(f"\n🎯 Quick Summary:")
            print(f"   v20 Success: {v20_results['success_count']}/{len(v20_results['runs'])} ({(v20_results['success_count']/len(v20_results['runs'])*100):.0f}%)")
            print(f"   v25 Success: {v25_results['success_count']}/{len(v25_results['runs'])} ({(v25_results['success_count']/len(v25_results['runs'])*100):.0f}%)")
            print(f"   v20 Avg Time: {v20_results['avg_time']:.2f}s")
            print(f"   v25 Avg Time: {v25_results['avg_time']:.2f}s")
            print(f"   v20 Avg Coverage: {v20_results['avg_coverage']:.1f}%")
            print(f"   v25 Avg Coverage: {v25_results['avg_coverage']:.1f}%")

if __name__ == "__main__":
    import sys
    
    # Get TT ID from command line or use default
    if len(sys.argv) > 1:
        tt_id = sys.argv[1]
    else:
        # Use the most recent TT ID available
        import glob
        csv_files = glob.glob(str(Path(__file__).parent / "data_classes_TT*.csv"))
        if csv_files:
            latest_file = max(csv_files, key=lambda x: Path(x).stat().st_mtime)
            tt_id = Path(latest_file).name.replace('data_classes_', '').replace('.csv', '')
        else:
            print("❌ No test data found. Please generate test data first:")
            print("   python data_generator.py --config medium")
            sys.exit(1)
    
    # Run simple A/B test
    tester = SimpleABTester()
    tester.run_test_sequence(tt_id)