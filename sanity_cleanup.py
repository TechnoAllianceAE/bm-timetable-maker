"""
Comprehensive Sanity Cleanup Script

Removes unwanted temporary, test, debug files from the entire project
while keeping necessary scripts and configuration files.
"""

import os
import glob
from datetime import datetime

PROJECT_ROOT = "."

def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def sanity_cleanup():
    """Perform comprehensive project cleanup"""

    print("="*80)
    print("PROJECT SANITY CLEANUP")
    print("="*80)
    print(f"Project Root: {os.path.abspath(PROJECT_ROOT)}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Define cleanup categories
    cleanup_patterns = {
        "Temporary Test CSVs": [
            "temp_test_*.csv",
            "timetable-engine/temp_test_*.csv",
        ],
        "Log Files": [
            "*.log",
            "backend/*.log",
            "frontend/*.log",
            "timetable-engine/*.log",
            "logs/*.log",
        ],
        "Debug Scripts": [
            "debug_*.py",
            "debug_*.js",
            "timetable-engine/debug_*.py",
            "diagnose_*.sh",
        ],
        "Test JSON/Request Files": [
            "test_*.json",
            "timetable-engine/test_*.json",
        ],
        "Temporary Databases": [
            "backend/dev.db",  # Empty duplicate
        ],
        "Cleanup Scripts (used once)": [
            "analyze_timetable.py",
            "clear_school_data.py",
            "clear_non_admin_users.py",
            "clean_tt_tester.py",
            "test_backend_validation.js",
        ],
        "Backend Seed Scripts": [
            "backend/add-teachers.js",
            "backend/add-more-teachers.js",
        ],
        "Old Test Scripts in timetable-engine": [
            "timetable-engine/test_teacher_consistency.py",
            "timetable-engine/test_api_with_free_periods.py",
            "timetable-engine/test_free_period_tolerance.py",
            "timetable-engine/test_and_verify_comprehensive.py",
            "timetable-engine/test_3_sizes_teacher_consistency.py",
            "timetable-engine/test_v25_1_teacher_consistency.py",
        ],
    }

    # Files to ALWAYS keep (whitelist)
    files_to_keep = {
        # Documentation
        "README.md", "CLAUDE.md", "COMMUNICATION_SETUP.md",
        "SERVICE_SCRIPTS.md", "AGENTS.md", "GEMINI.md",
        "WORK_TO_BE_DONE.md", "WIP_TEACHER_CONSISTENCY_FIX.md",
        "WARP.md",

        # Service scripts
        "START_ALL_SERVICES.sh", "STOP_ALL_SERVICES.sh",
        "START_ALL_SERVICES.bat", "STOP_ALL_SERVICES.bat",

        # Current working scripts in tt_tester
        "test_data_generator_guide.md",

        # Production test files
        "timetable-engine/test_v25_metadata_flow.py",
        "timetable-engine/test_subject_requirements.py",
        "timetable-engine/test_subject_requirements_simple.py",
    }

    print("🔍 Scanning project for unwanted files...")
    print()

    all_files_to_delete = {}

    for category, patterns in cleanup_patterns.items():
        category_files = []

        for pattern in patterns:
            matches = glob.glob(os.path.join(PROJECT_ROOT, pattern))

            for file_path in matches:
                file_name = os.path.basename(file_path)

                # Skip if in whitelist
                if file_name in files_to_keep:
                    continue

                # Skip if doesn't exist
                if not os.path.exists(file_path):
                    continue

                # Skip directories
                if os.path.isdir(file_path):
                    continue

                category_files.append(file_path)

        if category_files:
            all_files_to_delete[category] = list(set(category_files))

    # Count total files
    total_files = sum(len(files) for files in all_files_to_delete.values())
    total_size = sum(
        get_file_size(f)
        for files in all_files_to_delete.values()
        for f in files
    )

    if total_files == 0:
        print("✅ No unwanted files found. Project is already clean!")
        print()
        return

    print(f"📋 Found {total_files} unwanted files to delete:")
    print("-"*80)

    # Show files by category
    for category, files in all_files_to_delete.items():
        if files:
            print(f"\n📁 {category} ({len(files)} files):")
            category_size = sum(get_file_size(f) for f in files)

            # Show first 10 files in each category
            for f in sorted(files)[:10]:
                size = get_file_size(f)
                rel_path = os.path.relpath(f, PROJECT_ROOT)
                print(f"  • {rel_path} ({size:,} bytes)")

            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")

            print(f"  Category total: {category_size:,} bytes ({category_size/1024:.2f} KB)")

    print()
    print("-"*80)
    print(f"Total files to delete: {total_files}")
    print(f"Total size to free: {total_size:,} bytes ({total_size/1024:.2f} KB)")
    print()

    # Show what will be kept
    print("✅ WILL BE KEPT:")
    print("-"*80)
    print("  ✓ All documentation (README.md, CLAUDE.md, etc.)")
    print("  ✓ Service start/stop scripts")
    print("  ✓ Production test files")
    print("  ✓ Essential configuration files")
    print("  ✓ Source code (backend, frontend, timetable-engine)")
    print("  ✓ Node modules and dependencies")
    print("  ✓ Git repository")
    print()

    # Confirm
    print("="*80)
    response = input("⚠️  Proceed with cleanup? This cannot be undone! (yes/no): ")
    print()

    if response.lower() != 'yes':
        print("❌ Cleanup cancelled.")
        return

    print("🔄 Deleting files...")
    print()

    deleted_by_category = {}
    total_deleted = 0
    total_failed = 0

    for category, files in all_files_to_delete.items():
        deleted_count = 0

        for file_path in files:
            try:
                os.remove(file_path)
                deleted_count += 1
                total_deleted += 1
            except Exception as e:
                print(f"  ⚠️  Failed to delete {os.path.basename(file_path)}: {e}")
                total_failed += 1

        if deleted_count > 0:
            deleted_by_category[category] = deleted_count

    print()
    print("📊 Deletion Summary by Category:")
    print("-"*80)
    for category, count in deleted_by_category.items():
        print(f"  ✓ {category}: {count} files deleted")

    print()
    print(f"✅ Successfully deleted {total_deleted} files")
    if total_failed > 0:
        print(f"⚠️  Failed to delete {total_failed} files")
    print(f"💾 Disk space freed: {total_size:,} bytes ({total_size/1024:.2f} KB)")
    print()

    print("="*80)
    print("🎉 PROJECT SANITY CLEANUP COMPLETE!")
    print("="*80)
    print()
    print("Summary:")
    print(f"  • Total files removed: {total_deleted}")
    print(f"  • Space freed: {total_size/1024:.2f} KB")
    print(f"  • Project is now clean and organized")
    print()
    print("Next steps:")
    print("  • All essential files and scripts are preserved")
    print("  • Project is ready for development")
    print("  • Consider committing these changes")
    print()

if __name__ == "__main__":
    sanity_cleanup()
