#!/usr/bin/env python3
"""
A/B Testing Framework for Timetable Generators
Compares main_v20.py vs main_v25.py performance and quality
"""

import json
import time
import requests
import subprocess
import threading
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics

class TimetableEngineManager:
    """Manages starting and stopping timetable engine servers"""
    
    def __init__(self):
        self.processes = {}
        self.ports = {'v20': 8020, 'v25': 8025}
        
    def start_engine(self, version, script_path):
        """Start a timetable engine on specified port"""
        port = self.ports[version]
        print(f"🚀 Starting {version} engine on port {port}...")
        
        try:
            # Use our custom launcher
            launcher_path = Path(__file__).parent / "engine_launcher.py"
            process = subprocess.Popen([
                'python', str(launcher_path),
                version, str(port)
            ], stdout=subprocess.PIPE,
               stderr=subprocess.PIPE,
               text=True)
            
            self.processes[version] = process
            
            # Wait a bit for startup
            time.sleep(5)
            
            # Test if server is responding
            test_url = f"http://localhost:{port}/docs"
            try:
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {version} engine started successfully on port {port}")
                    return True
            except:
                pass
                
            print(f"⚠️  {version} engine may not be ready, continuing anyway...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {version} engine: {e}")
            return False
    
    def stop_engine(self, version):
        """Stop a timetable engine"""
        if version in self.processes:
            print(f"🛑 Stopping {version} engine...")
            self.processes[version].terminate()
            self.processes[version].wait()
            del self.processes[version]
    
    def stop_all(self):
        """Stop all engines"""
        for version in list(self.processes.keys()):
            self.stop_engine(version)

class ABTestRunner:
    """Main A/B testing class"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.engine_path = self.base_path.parent / "timetable-engine"
        self.manager = TimetableEngineManager()
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

    def test_engine(self, version, test_data, runs=3):
        """Test a specific engine version multiple times"""
        port = self.manager.ports[version]
        url = f"http://localhost:{port}/generate"
        
        print(f"\n🧪 Testing {version} engine ({runs} runs)...")
        
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
                    error_msg = f"HTTP {response.status_code}: {response.text}"
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

    def run_ab_test(self, tt_id, runs=3):
        """Run complete A/B test"""
        print(f"\n{'='*80}")
        print(f"🔬 Starting A/B Test: main_v20 vs main_v25")
        print(f"📊 Test Data: {tt_id}")
        print(f"🔄 Runs per version: {runs}")
        print(f"{'='*80}")
        
        # Load test data
        test_data = self.load_test_data(tt_id)
        print(f"📋 Loaded data: {len(test_data['classes'])} classes, {len(test_data['teachers'])} teachers, {len(test_data['assignments'])} assignments")
        
        # Start both engines
        v20_started = self.manager.start_engine('v20', self.engine_path / 'main_v20.py')
        v25_started = self.manager.start_engine('v25', self.engine_path / 'main_v25.py')
        
        if not v20_started or not v25_started:
            print("❌ Failed to start one or both engines. Aborting test.")
            self.manager.stop_all()
            return None
        
        try:
            # Test both versions
            self.results['v20'] = self.test_engine('v20', test_data, runs)
            self.results['v25'] = self.test_engine('v25', test_data, runs)
            
            # Generate comparison report
            report_file = self.generate_html_report(tt_id)
            
            print(f"\n{'='*80}")
            print(f"✅ A/B Test Complete!")
            print(f"📄 Report generated: {report_file}")
            print(f"🌐 Open the HTML file to view detailed comparison")
            print(f"{'='*80}")
            
            return self.results
            
        finally:
            # Clean up
            self.manager.stop_all()
    
    def determine_winner(self):
        """Determine which version performed better"""
        v20 = self.results.get('v20', {})
        v25 = self.results.get('v25', {})
        
        # Success rate comparison
        v20_success_rate = (v20.get('success_count', 0) / len(v20.get('runs', []))) * 100 if v20.get('runs') else 0
        v25_success_rate = (v25.get('success_count', 0) / len(v25.get('runs', []))) * 100 if v25.get('runs') else 0
        
        # Performance comparison
        v20_time = v20.get('avg_time', float('inf'))
        v25_time = v25.get('avg_time', float('inf'))
        
        # Quality comparison
        v20_coverage = v20.get('avg_coverage', 0)
        v25_coverage = v25.get('avg_coverage', 0)
        
        # Scoring system
        v20_score = 0
        v25_score = 0
        
        # Success rate (40 points)
        if v20_success_rate > v25_success_rate:
            v20_score += 40
        elif v25_success_rate > v20_success_rate:
            v25_score += 40
        else:
            v20_score += 20
            v25_score += 20
        
        # Speed (30 points) - lower time is better
        if v20_time < v25_time:
            v20_score += 30
        elif v25_time < v20_time:
            v25_score += 30
        else:
            v20_score += 15
            v25_score += 15
        
        # Coverage/Quality (30 points)
        if v20_coverage > v25_coverage:
            v20_score += 30
        elif v25_coverage > v20_coverage:
            v25_score += 30
        else:
            v20_score += 15
            v25_score += 15
        
        winner = 'v20' if v20_score > v25_score else ('v25' if v25_score > v20_score else 'tie')
        
        return {
            'winner': winner,
            'v20_score': v20_score,
            'v25_score': v25_score,
            'v20_success_rate': v20_success_rate,
            'v25_success_rate': v25_success_rate,
            'speed_winner': 'v20' if v20_time < v25_time else 'v25',
            'quality_winner': 'v20' if v20_coverage > v25_coverage else 'v25'
        }

    def generate_html_report(self, tt_id):
        """Generate comprehensive HTML comparison report"""
        winner_analysis = self.determine_winner()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
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

        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #edf2f7;
        }}

        .metric:last-child {{
            border-bottom: none;
        }}

        .metric-label {{
            font-weight: 600;
            color: #4a5568;
        }}

        .metric-value {{
            font-size: 18px;
            font-weight: 700;
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

        .detailed-results {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .detailed-results h3 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #2d3748;
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

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

        .winner-badge {{
            background: #48bb78;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .v20-winner {{
            background: #3182ce;
        }}

        .v25-winner {{
            background: #38a169;
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
        if winner_analysis['winner'] != 'tie':
            winner_name = f"main_{winner_analysis['winner']}.py"
            winner_score = winner_analysis[f"{winner_analysis['winner']}_score"]
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
        for version in ['v20', 'v25']:
            data = self.results.get(version, {})
            runs = data.get('runs', [])
            total_runs = len(runs)
            success_count = data.get('success_count', 0)
            success_rate = (success_count / total_runs * 100) if total_runs > 0 else 0
            
            is_speed_winner = winner_analysis['speed_winner'] == version
            is_quality_winner = winner_analysis['quality_winner'] == version
            is_overall_winner = winner_analysis['winner'] == version
            
            html_content += f'''
            <div class="version-card">
                <h3>
                    main_{version}.py 
                    {f'<span class="winner-badge {version}-winner">Overall Winner</span>' if is_overall_winner else ''}
                </h3>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value {'success' if success_rate == 100 else 'warning' if success_rate > 0 else 'error'}">{success_rate:.0f}%</div>
                        <div class="stat-label">Success Rate {'🏆' if success_rate > winner_analysis[f"{'v25' if version == 'v20' else 'v20'}_success_rate"] else ''}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{data.get('avg_time', 0):.2f}s</div>
                        <div class="stat-label">Avg Time {'⚡' if is_speed_winner else ''}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{data.get('avg_coverage', 0):.1f}%</div>
                        <div class="stat-label">Avg Coverage {'🎯' if is_quality_winner else ''}</div>
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
'''

        # Detailed analysis
        html_content += f'''
        <div class="detailed-results">
            <h3>📊 Detailed Analysis</h3>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{winner_analysis['winner'].upper()}</div>
                    <div class="stat-label">Overall Winner</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{winner_analysis['speed_winner'].upper()}</div>
                    <div class="stat-label">Faster Engine</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{winner_analysis['quality_winner'].upper()}</div>
                    <div class="stat-label">Better Quality</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(self.results['v20']['runs']) + len(self.results['v25']['runs'])}</div>
                    <div class="stat-label">Total Test Runs</div>
                </div>
            </div>
            
            <h4>Scoring Breakdown (100 points total):</h4>
            <ul style="margin: 20px 0; padding-left: 30px;">
                <li><strong>Success Rate</strong>: 40 points - Reliability and ability to generate valid timetables</li>
                <li><strong>Speed</strong>: 30 points - Average generation time across all runs</li>
                <li><strong>Quality</strong>: 30 points - Coverage percentage and solution quality</li>
            </ul>
            
            <h4>Final Scores:</h4>
            <div style="margin: 20px 0; font-size: 18px;">
                <div>📈 main_v20.py: <strong>{winner_analysis['v20_score']}/100 points</strong></div>
                <div>📈 main_v25.py: <strong>{winner_analysis['v25_score']}/100 points</strong></div>
            </div>
        </div>
'''

        html_content += '''
    </div>
</body>
</html>
'''

        # Save report
        report_file = self.base_path / f"ab_test_report_{tt_id}_{timestamp}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_file

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
    
    # Run A/B test
    runner = ABTestRunner()
    results = runner.run_ab_test(tt_id, runs=3)
    
    if results:
        print(f"\n🎯 Quick Summary:")
        print(f"   v20 Success: {results['v20']['success_count']}/{len(results['v20']['runs'])} ({(results['v20']['success_count']/len(results['v20']['runs'])*100):.0f}%)")
        print(f"   v25 Success: {results['v25']['success_count']}/{len(results['v25']['runs'])} ({(results['v25']['success_count']/len(results['v25']['runs'])*100):.0f}%)")
        print(f"   v20 Avg Time: {results['v20']['avg_time']:.2f}s")
        print(f"   v25 Avg Time: {results['v25']['avg_time']:.2f}s")
        print(f"   v20 Avg Coverage: {results['v20']['avg_coverage']:.1f}%")
        print(f"   v25 Avg Coverage: {results['v25']['avg_coverage']:.1f}%")