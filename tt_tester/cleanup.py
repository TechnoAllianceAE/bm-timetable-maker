#!/usr/bin/env python3
"""
Cleanup script for tt_tester directory
Removes old files and keeps only essential tools
"""

import os
import glob
import argparse

# Files to remove - organized by category (shared between functions)
old_patterns = [
    # [TEMPORARY] Temporary launcher files
    "temp_launcher_*.py",
    "temp_v25_launcher.py",
    "temp_*.py",

    # [TEST DATA] Old test data files (timestamped versions)
    "data_assignments_TT_*.csv",
    "data_classes_TT_*.csv",
    "data_rooms_TT_*.csv",
    "data_subjects_TT_*.csv",
    "data_teachers_TT_*.csv",
    "data_teachers_reduced.csv",

    # [HTML REPORTS] Old HTML report files
    "ab_test_report_TT_*.html",
    "automated_ab_test_report_TT_*.html",
    "complete_timetable_TT_*.html",
    "demo_ab_test_report.html",
    "simple_ab_test_report_TT_*.html",
    "timetable_3grade_6subject_results.html",
    "timetable_test_report.html",
    "timetable_verification_TT_*.html",
    "timetable_viewer_LEGACY_DATA_*.html",
    "timetable_viewer_TT_*.html",
    "v25_timetable_TT_*.html",

    # [METADATA] Old metadata and result files
    "metadata_TT_*.json",
    "result_TT_*.json",

    # [LEGACY SCRIPTS] Legacy test scripts
    "engine_launcher.py",
    "run_ab_test_v20_v25.py",
    "start_v25.py",
    "generate_3grade_6subject_test.py",
    "generate_14_classes.py",
    "generate_30class_test.py",
    "generate_and_display_timetable.py",
    "generate_large_school_timetable.py",
    "generate_v25_html.py",
    "run_3grade_test.py",
    "run_timetable_test.py",
    "simple_ab_test.py",
    "test_output.txt",
    "view_timetable.py",

    # [OLD DOCS] Old documentation files
    "ALGORITHM_ARCHITECTURE.md",
    "AUDIT_REPORT.md",
    "CONSOLIDATION_SUMMARY.md",
    "MEMORY_SEPTEMBER_19_2025.md",
    "TERMINOLOGY_CLEANUP_SUMMARY.md",
    "VIEWER_ENHANCEMENTS_SUMMARY.md",
    "test_data_generator_guide.md",
    "openapi-phase1.yaml",
    "openapi.yaml",

    # [OLD CSV] Old CSV files (keeping base test_data files)
    "gapfree_timetable_TT_*.csv",
    "test_3grade_6subject_*.csv",

    # [LEGACY] Legacy files
    "node_remover.sh",

    # [VERY OLD] Very old specific files (keeping these for backward compatibility)
    # "*_20250918_*.csv",
    # "*_20250919_111*.csv",
    # "*_20250919_113*.csv"
]

def cleanup_old_files():
    """Remove old and redundant files"""

    print("[CLEANUP] Starting comprehensive cleanup...")
    print("[WARNING] This will remove obsolete files while keeping essential tools.")
    print("[INFO] Files to be removed are organized by category.\n")
    
    removed_count = 0
    category_count = 0

    for pattern in old_patterns:
        files = glob.glob(pattern)
        if files:
            print(f"[PATTERN] Processing pattern: {pattern}")
            category_count += 1

            for file in files:
                try:
                    # Safety check: don't remove essential files
                    essential_files = ["test_data_", "comprehensive_tt_generator.py", "data_generator.py",
                                     "timetable_viewer.py", "tt_generation_tracker.py", "analyze_teacher_subjects.py",
                                     "ab_test.py", "cleanup.py", "README.md"]

                    if any(essential in file for essential in essential_files):
                        print(f"   [SKIP] Skipped essential file: {file}")
                        continue

                    os.remove(file)
                    print(f"   [REMOVED] Removed: {file}")
                    removed_count += 1
                except Exception as e:
                    print(f"   [ERROR] Error removing {file}: {e}")

    print(f"\n[SUCCESS] Cleanup complete!")
    print(f"   [STATS] Categories processed: {category_count}")
    print(f"   [STATS] Files removed: {removed_count}")
    print(f"   [STATS] Essential files preserved")

def dry_run_cleanup():
    """Show what would be removed without actually removing files"""
    print("[DRY RUN] DRY RUN MODE - No files will be actually removed\n")

    removed_count = 0
    category_count = 0

    for pattern in old_patterns:
        files = glob.glob(pattern)
        if files:
            print(f"[PATTERN] Pattern: {pattern}")
            category_count += 1

            for file in files:
                # Safety check: don't remove essential files
                essential_files = ["test_data_", "comprehensive_tt_generator.py", "data_generator.py",
                                 "timetable_viewer.py", "tt_generation_tracker.py", "analyze_teacher_subjects.py",
                                 "ab_test.py", "cleanup.py", "README.md"]

                if any(essential in file for essential in essential_files):
                    print(f"   [SKIP] Would skip essential file: {file}")
                else:
                    print(f"   [WOULD REMOVE] Would remove: {file}")
                    removed_count += 1

    print(f"\n[DRY RUN SUMMARY]")
    print(f"   [STATS] Categories that would be processed: {category_count}")
    print(f"   [STATS] Files that would be removed: {removed_count}")
    print(f"   [STATS] Essential files that would be preserved")
    print(f"\n[TIP] Run 'python cleanup.py --clean' to actually remove these files.")

def list_current_files():
    """List current files in directory"""

    print("[INFO] Current files in tt_tester:")
    print("-" * 40)

    # Core tools (essential files to keep)
    core_files = [
        "comprehensive_tt_generator.py",    # Main generation tool
        "data_generator.py",                # Universal data generator
        "timetable_viewer.py",              # Universal timetable viewer
        "tt_generation_tracker.py",         # Generation management
        "analyze_teacher_subjects.py",      # Teacher constraint analysis
        "ab_test.py",                       # Current A/B testing framework
        "cleanup.py",                       # This cleanup script itself
        "README.md"                         # Documentation
    ]

    print("[CORE TOOLS]")
    for file in core_files:
        if os.path.exists(file):
            print(f"   [OK] {file}")
        else:
            print(f"   [MISSING] {file} (missing)")

    # Data files
    print("\n[DATA FILES]")
    csv_files = glob.glob("*.csv")
    for file in sorted(csv_files):
        print(f"   [CSV] {file}")

    # Generated files
    print("\n[GENERATED FILES]")
    metadata_files = glob.glob("metadata_*.json")
    for file in sorted(metadata_files):
        print(f"   [METADATA] {file}")

    html_files = glob.glob("*.html")
    for file in sorted(html_files):
        print(f"   [HTML] {file}")

    # Documentation
    print("\n[DOCUMENTATION]")
    doc_files = ["README.md"]
    for file in doc_files:
        if os.path.exists(file):
            print(f"   [DOC] {file}")

    # Essential data files (base test data to keep)
    print("\n[ESSENTIAL DATA] Essential Data Files (KEPT):")
    essential_data = [
        "test_data_classes.csv",
        "test_data_teachers.csv",
        "test_data_rooms.csv",
        "test_data_subjects.csv",
        "test_data_assignments.csv"
    ]
    for file in essential_data:
        if os.path.exists(file):
            print(f"   [OK] {file}")
        else:
            print(f"   [WARNING] {file} (missing)")

    # Tests directory
    print("\n[TESTS]")
    if os.path.exists("tests"):
        test_files = os.listdir("tests")
        print(f"   [DIR] tests/ ({len(test_files)} files)")
    else:
        print("   [MISSING] tests/ (missing)")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Comprehensive cleanup tool for tt_tester directory')
    parser.add_argument('--clean', action='store_true', help='Remove obsolete files (comprehensive cleanup)')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt (for automated scripts)')
    parser.add_argument('--list', action='store_true', help='List current files and their status')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed without actually removing')

    args = parser.parse_args()

    # Determine the action to take
    if args.clean or args.force:
        print("[CLEANUP] TT Tester Comprehensive Cleanup Tool")
        print("=" * 50)
        print("[WARNING] WARNING: This will permanently remove obsolete files!")
        print("[TIP] Pro tip: Run --list first to see what will be kept.")
        print("")

        # Safety confirmation (skip if --force is used)
        if args.force:
            print("[FORCE] Skipping confirmation (forced cleanup)")
            cleanup_old_files()
        else:
            confirm = input("Are you sure you want to proceed? (type 'yes' to confirm): ")
            if confirm.lower() == 'yes':
                cleanup_old_files()
            else:
                print("[CANCELLED] Cleanup cancelled.")

    elif args.dry_run:
        print("[DRY RUN] DRY RUN: Showing what would be removed...")
        print("=" * 50)
        dry_run_cleanup()

    elif args.list:
        list_current_files()
    else:
        print("[CLEANUP] TT Tester Comprehensive Cleanup Tool")
        print("=" * 50)
        print("Usage:")
        print("  python cleanup.py --clean     # Remove obsolete files")
        print("  python cleanup.py --force     # Remove files without confirmation")
        print("  python cleanup.py --dry-run   # Show what would be removed")
        print("  python cleanup.py --list      # List current files")
        print("")
        print("Examples:")
        print("  python cleanup.py --list      # Check what exists")
        print("  python cleanup.py --dry-run   # Preview cleanup")
        print("  python cleanup.py --clean     # Interactive cleanup (asks for confirmation)")
        print("  python cleanup.py --force     # Automated cleanup (no confirmation)")

if __name__ == "__main__":
    main()