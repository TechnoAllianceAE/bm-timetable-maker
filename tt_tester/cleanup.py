#!/usr/bin/env python3
"""
Cleanup script for tt_tester directory
Removes old files and keeps only essential tools
"""

import os
import glob
import argparse

def cleanup_old_files():
    """Remove old and redundant files"""
    
    # Files to remove
    old_patterns = [
        "*.html",  # All old HTML files
        "demo_*.csv",
        "realistic_*.csv", 
        "school_*.csv",
        "large_*.csv",
        "timetable_*.csv",
        "*_20250918_*.csv",
        "*_20250919_111*.csv",
        "*_20250919_113*.csv"
    ]
    
    removed_count = 0
    
    for pattern in old_patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                print(f"🗑️  Removed: {file}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {file}: {e}")
    
    print(f"\n✅ Cleanup complete: {removed_count} files removed")

def list_current_files():
    """List current files in directory"""
    
    print("📁 Current files in tt_tester:")
    print("-" * 40)
    
    # Core tools
    core_files = [
        "data_generator.py",
        "timetable_viewer.py", 
        "tt_generation_tracker.py",
        "analyze_teacher_subjects.py"
    ]
    
    print("🔧 Core Tools:")
    for file in core_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
    
    # Data files
    print("\n📊 Data Files:")
    csv_files = glob.glob("*.csv")
    for file in sorted(csv_files):
        print(f"   📄 {file}")
    
    # Generated files
    print("\n🆔 Generated Files:")
    metadata_files = glob.glob("metadata_*.json")
    for file in sorted(metadata_files):
        print(f"   📋 {file}")
    
    html_files = glob.glob("*.html")
    for file in sorted(html_files):
        print(f"   🌐 {file}")
    
    # Documentation
    print("\n📚 Documentation:")
    doc_files = ["README.md", "test_data_generator_guide.md", "GAPFREE_SOLUTION_SUMMARY.md"]
    for file in doc_files:
        if os.path.exists(file):
            print(f"   📖 {file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Cleanup tt_tester directory')
    parser.add_argument('--clean', action='store_true', help='Remove old files')
    parser.add_argument('--list', action='store_true', help='List current files')
    
    args = parser.parse_args()
    
    if args.clean:
        cleanup_old_files()
    elif args.list:
        list_current_files()
    else:
        print("🧹 TT Tester Cleanup Tool")
        print("Usage:")
        print("  python3 cleanup.py --clean    # Remove old files")
        print("  python3 cleanup.py --list     # List current files")

if __name__ == "__main__":
    main()