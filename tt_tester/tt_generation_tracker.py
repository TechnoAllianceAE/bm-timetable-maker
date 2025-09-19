#!/usr/bin/env python3
"""
Timetable Generation Tracker - Manage multiple TT generations with unique IDs
"""

import json
import os
import glob
from datetime import datetime
from collections import defaultdict

def load_all_generations():
    """Load all TT generation metadata files"""
    
    metadata_files = glob.glob("metadata_TT_*.json")
    generations = []
    
    for file in metadata_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                metadata['metadata_file'] = file
                
                # Check for associated files
                tt_id = metadata.get('tt_generation_id', '')
                if tt_id:
                    # Look for data files
                    data_files = glob.glob(f"*{tt_id}*.csv")
                    viewer_files = glob.glob(f"*viewer*{tt_id}*.html")
                    
                    metadata['data_files'] = data_files
                    metadata['viewer_files'] = viewer_files
                
                generations.append(metadata)
        except Exception as e:
            print(f"⚠️  Error loading {file}: {e}")
    
    # Sort by generation timestamp (newest first)
    generations.sort(key=lambda x: x.get('generation_timestamp', ''), reverse=True)
    
    return generations

def display_generation_summary():
    """Display summary of all TT generations"""
    
    generations = load_all_generations()
    
    if not generations:
        print("📭 No TT generations found")
        print("💡 Run 'python3 data_generator.py' to create your first generation")
        return
    
    print("🗂️  TIMETABLE GENERATION TRACKER")
    print("=" * 60)
    print(f"📊 Total generations: {len(generations)}")
    
    # Statistics
    valid_generations = sum(1 for g in generations if g.get('is_complete', g.get('is_gapfree', False)))
    invalid_generations = len(generations) - valid_generations
    
    print(f"✅ Complete schedules: {valid_generations}")
    print(f"❌ Incomplete schedules: {invalid_generations}")
    
    print("\n📋 GENERATION HISTORY:")
    print("-" * 60)
    
    for i, gen in enumerate(generations):
        tt_id = gen.get('tt_generation_id', 'UNKNOWN')
        timestamp = gen.get('generation_timestamp', 'UNKNOWN')
        is_valid = gen.get('is_gapfree', False)
        coverage = gen.get('coverage_percentage', 0)
        classes = gen.get('classes_count', 0)
        entries = gen.get('total_entries', 0)
        
        # Parse timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp
        
        status_icon = "✅" if is_valid else "❌"
        status_text = "COMPLETE" if is_valid else "INCOMPLETE"
        
        print(f"{i+1:2d}. {status_icon} {tt_id}")
        print(f"    📅 Generated: {time_str}")
        print(f"    📊 Status: {status_text} | Coverage: {coverage:.1f}%")
        print(f"    🏫 Classes: {classes} | Entries: {entries}")
        
        # Show files
        csv_file = gen.get('filename', 'N/A')
        metadata_file = gen.get('metadata_file', 'N/A')
        
        print(f"    📄 CSV: {csv_file}")
        print(f"    📋 Metadata: {metadata_file}")
        
        # Check for viewer files
        viewer_files = glob.glob(f"*viewer*{tt_id}*.html")
        if viewer_files:
            print(f"    🌐 Viewers: {', '.join(viewer_files)}")
        
        print()

def get_latest_valid_generation():
    """Get the latest valid (complete) generation"""
    
    generations = load_all_generations()
    
    for gen in generations:
        if gen.get('is_complete', gen.get('is_gapfree', False)):
            return gen
    
    return None

def get_generation_by_id(tt_id):
    """Get specific generation by TT ID"""
    
    generations = load_all_generations()
    
    for gen in generations:
        if gen.get('tt_generation_id') == tt_id:
            return gen
    
    return None

def cleanup_old_generations(keep_count=5):
    """Clean up old generation files, keeping only the most recent ones"""
    
    generations = load_all_generations()
    
    if len(generations) <= keep_count:
        print(f"📦 Only {len(generations)} generations found, no cleanup needed")
        return
    
    # Keep the most recent ones
    to_keep = generations[:keep_count]
    to_remove = generations[keep_count:]
    
    print(f"🧹 CLEANUP: Keeping {keep_count} most recent generations")
    print(f"🗑️  Removing {len(to_remove)} old generations:")
    
    for gen in to_remove:
        tt_id = gen.get('tt_generation_id', 'UNKNOWN')
        print(f"   Removing: {tt_id}")
        
        # Remove associated files
        files_to_remove = []
        
        # CSV file
        csv_file = gen.get('filename')
        if csv_file and os.path.exists(csv_file):
            files_to_remove.append(csv_file)
        
        # Metadata file
        metadata_file = gen.get('metadata_file')
        if metadata_file and os.path.exists(metadata_file):
            files_to_remove.append(metadata_file)
        
        # Viewer files
        viewer_files = glob.glob(f"*viewer*{tt_id}*.html")
        files_to_remove.extend(viewer_files)
        
        # Remove files
        for file in files_to_remove:
            try:
                os.remove(file)
                print(f"     ✅ Removed: {file}")
            except Exception as e:
                print(f"     ❌ Error removing {file}: {e}")
    
    print(f"✅ Cleanup complete!")

def create_generation_report():
    """Create HTML report of all generations"""
    
    generations = load_all_generations()
    
    if not generations:
        print("📭 No generations to report")
        return
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"tt_generation_report_{timestamp}.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TT Generation Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-label {{
            color: #6c757d;
            margin-top: 5px;
        }}
        .generation-card {{
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: white;
        }}
        .generation-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .tt-id {{
            font-family: monospace;
            font-size: 1.1em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .status-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .status-valid {{
            background: #d4edda;
            color: #155724;
        }}
        .status-invalid {{
            background: #f8d7da;
            color: #721c24;
        }}
        .generation-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        .detail-item {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }}
        .detail-label {{
            font-weight: bold;
            color: #495057;
            font-size: 0.9em;
        }}
        .detail-value {{
            color: #2c3e50;
            margin-top: 5px;
        }}
        .files-list {{
            margin-top: 15px;
        }}
        .file-link {{
            display: inline-block;
            margin: 5px 10px 5px 0;
            padding: 5px 10px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.9em;
        }}
        .file-link:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗂️ Timetable Generation Report</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(generations)}</div>
                <div class="stat-label">Total Generations</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{sum(1 for g in generations if g.get('is_complete', g.get('is_gapfree', False)))}</div>
                <div class="stat-label">Complete Schedules</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{sum(1 for g in generations if not g.get('is_complete', g.get('is_gapfree', False)))}</div>
                <div class="stat-label">Incomplete Schedules</div>
            </div>
        </div>
"""
    
    for gen in generations:
        tt_id = gen.get('tt_generation_id', 'UNKNOWN')
        timestamp = gen.get('generation_timestamp', 'UNKNOWN')
        is_valid = gen.get('is_gapfree', False)
        coverage = gen.get('coverage_percentage', 0)
        classes = gen.get('classes_count', 0)
        entries = gen.get('total_entries', 0)
        expected = gen.get('expected_entries', 0)
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp
        
        status_class = "status-valid" if is_valid else "status-invalid"
        status_text = "✅ COMPLETE" if is_valid else "❌ INCOMPLETE"
        
        html_content += f"""
        <div class="generation-card">
            <div class="generation-header">
                <div class="tt-id">{tt_id}</div>
                <div class="status-badge {status_class}">{status_text}</div>
            </div>
            
            <div class="generation-details">
                <div class="detail-item">
                    <div class="detail-label">Generated</div>
                    <div class="detail-value">{time_str}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Classes</div>
                    <div class="detail-value">{classes}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Total Entries</div>
                    <div class="detail-value">{entries} / {expected}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Coverage</div>
                    <div class="detail-value">{coverage:.1f}%</div>
                </div>
            </div>
            
            <div class="files-list">
                <strong>Files:</strong>
"""
        
        # Add file links
        csv_file = gen.get('filename')
        if csv_file and os.path.exists(csv_file):
            html_content += f'<a href="{csv_file}" class="file-link">📄 CSV Data</a>'
        
        metadata_file = gen.get('metadata_file')
        if metadata_file and os.path.exists(metadata_file):
            html_content += f'<a href="{metadata_file}" class="file-link">📋 Metadata</a>'
        
        # Viewer files
        viewer_files = glob.glob(f"*viewer*{tt_id}*.html")
        for viewer_file in viewer_files:
            html_content += f'<a href="{viewer_file}" class="file-link">🌐 Viewer</a>'
        
        html_content += """
            </div>
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>"""
    
    # Save report
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📊 Generation report created: {report_filename}")
    return report_filename

def main():
    """Main function with command-line interface"""
    
    import sys
    
    if len(sys.argv) < 2:
        print("🗂️  TT Generation Tracker")
        print("Usage:")
        print("  python3 tt_generation_tracker.py list          # List all generations")
        print("  python3 tt_generation_tracker.py latest        # Show latest valid generation")
        print("  python3 tt_generation_tracker.py cleanup [N]   # Keep only N most recent (default: 5)")
        print("  python3 tt_generation_tracker.py report        # Create HTML report")
        print("  python3 tt_generation_tracker.py get <TT_ID>   # Get specific generation")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        display_generation_summary()
    
    elif command == "latest":
        latest = get_latest_valid_generation()
        if latest:
            tt_id = latest.get('tt_generation_id')
            timestamp = latest.get('generation_timestamp')
            print(f"🆔 Latest valid generation: {tt_id}")
            print(f"📅 Generated: {timestamp}")
            print(f"📄 CSV: {latest.get('filename')}")
            
            # Check for viewer
            viewer_files = glob.glob(f"*viewer*{tt_id}*.html")
            if viewer_files:
                print(f"🌐 Viewer: {viewer_files[0]}")
        else:
            print("❌ No valid generations found")
    
    elif command == "cleanup":
        keep_count = 5
        if len(sys.argv) > 2:
            try:
                keep_count = int(sys.argv[2])
            except ValueError:
                print("❌ Invalid number for keep count")
                return
        cleanup_old_generations(keep_count)
    
    elif command == "report":
        create_generation_report()
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("❌ Please provide TT ID")
            return
        
        tt_id = sys.argv[2]
        gen = get_generation_by_id(tt_id)
        
        if gen:
            print(f"🆔 Generation: {tt_id}")
            print(f"📅 Generated: {gen.get('generation_timestamp')}")
            print(f"✅ Complete: {'Yes' if gen.get('is_complete', gen.get('is_gapfree', False)) else 'No'}")
            print(f"📊 Coverage: {gen.get('coverage_percentage', 0):.1f}%")
            print(f"📄 CSV: {gen.get('filename')}")
            print(f"📋 Metadata: {gen.get('metadata_file')}")
        else:
            print(f"❌ Generation {tt_id} not found")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()