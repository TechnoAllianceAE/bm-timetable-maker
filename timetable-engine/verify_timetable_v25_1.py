#!/usr/bin/env python3
"""
Verification Script for v2.5.1 Fixes

Tests:
1. Teacher consistency per subject per class (CRITICAL)
2. Home room usage optimization (LOW PRIORITY)

Run this after generating a timetable to verify fixes work correctly.
"""

from collections import defaultdict
from typing import Dict, List


def verify_teacher_consistency(timetable) -> bool:
    """
    FIX 1 VERIFICATION: Check that each subject-class pair has only ONE teacher.

    Returns:
        True if all subject-class pairs have consistent teachers
    """
    print("\n" + "=" * 70)
    print("FIX 1 VERIFICATION: Teacher Consistency")
    print("=" * 70)

    # Map: (class_id, subject_id) -> set of teacher_ids
    class_subject_teachers = defaultdict(set)

    # Collect all teachers for each subject-class combination
    for entry in timetable.entries:
        key = (entry.class_id, entry.subject_id)
        class_subject_teachers[key].add(entry.teacher_id)

    # Check for violations
    violations = []
    consistent_pairs = 0

    for (class_id, subject_id), teachers in class_subject_teachers.items():
        if len(teachers) > 1:
            violations.append({
                'class': class_id,
                'subject': subject_id,
                'teacher_count': len(teachers),
                'teachers': list(teachers)
            })
        else:
            consistent_pairs += 1

    # Report results
    total_pairs = len(class_subject_teachers)

    if violations:
        print(f"\n[FAILED] Teacher consistency violations found:")
        print(f"  Total subject-class pairs: {total_pairs}")
        print(f"  Consistent pairs: {consistent_pairs}")
        print(f"  Violations: {len(violations)}\n")

        for v in violations[:10]:  # Show first 10
            print(f"  - Class {v['class']}, Subject {v['subject']}: "
                  f"{v['teacher_count']} different teachers")
            print(f"    Teachers: {', '.join(v['teachers'])}")

        if len(violations) > 10:
            print(f"  ... and {len(violations) - 10} more violations")

        return False
    else:
        print(f"\n[OK] Teacher consistency verified:")
        print(f"  Total subject-class pairs: {total_pairs}")
        print(f"  Consistent pairs: {consistent_pairs} (100%)")
        print(f"  Violations: 0")
        print(f"\n  ✓ Each class has ONE consistent teacher per subject")
        return True


def verify_home_room_usage(timetable, expected_home_rooms=None) -> bool:
    """
    FIX 2 VERIFICATION: Check home room usage patterns.

    Args:
        timetable: Timetable object with entries
        expected_home_rooms: Optional dict of class_id -> room_id

    Returns:
        True if home room usage is reasonable
    """
    print("\n" + "=" * 70)
    print("FIX 2 VERIFICATION: Home Room Usage")
    print("=" * 70)

    # Map: class_id -> {room_id: count}
    class_room_usage = defaultdict(lambda: defaultdict(int))

    # Count room usage per class
    for entry in timetable.entries:
        class_room_usage[entry.class_id][entry.room_id] += 1

    # Analyze usage patterns
    print(f"\nRoom usage analysis:")

    all_good = True

    for class_id, room_counts in sorted(class_room_usage.items()):
        total_periods = sum(room_counts.values())

        # Find most-used room (likely the home room)
        most_used_room = max(room_counts.items(), key=lambda x: x[1])
        most_used_room_id, most_used_count = most_used_room
        most_used_percentage = (most_used_count / total_periods) * 100

        # Count how many different rooms used
        room_count = len(room_counts)

        # Status indicator
        if most_used_percentage >= 70:
            status = "[EXCELLENT]"
        elif most_used_percentage >= 50:
            status = "[GOOD]"
        elif most_used_percentage >= 30:
            status = "[OK]"
        else:
            status = "[POOR]"
            all_good = False

        print(f"\n  Class {class_id}: {status}")
        print(f"    Primary room: {most_used_room_id} ({most_used_count}/{total_periods} = {most_used_percentage:.1f}%)")
        print(f"    Total rooms used: {room_count}")

        if room_count > 1:
            # Show other rooms
            other_rooms = [(rid, cnt) for rid, cnt in room_counts.items()
                          if rid != most_used_room_id]
            if other_rooms:
                print(f"    Other rooms:")
                for rid, cnt in sorted(other_rooms, key=lambda x: x[1], reverse=True)[:3]:
                    percentage = (cnt / total_periods) * 100
                    print(f"      - {rid}: {cnt} periods ({percentage:.1f}%)")

        # Compare with expected if provided
        if expected_home_rooms and class_id in expected_home_rooms:
            expected_room = expected_home_rooms[class_id]
            if most_used_room_id == expected_room:
                print(f"    ✓ Using assigned home room")
            else:
                actual_usage = room_counts.get(expected_room, 0)
                percentage = (actual_usage / total_periods) * 100
                print(f"    ⚠️ Expected home room {expected_room} only used {percentage:.1f}%")

    print(f"\n{'='*70}")
    if all_good:
        print("[OK] Home room usage is optimal")
        print("  ✓ All classes primarily use one main room")
    else:
        print("[WARNING] Some classes have poor home room usage")
        print("  Consider reviewing room assignments or subject requirements")

    return all_good


def analyze_teacher_workload(timetable) -> Dict:
    """
    Additional analysis: Teacher workload distribution.
    """
    print("\n" + "=" * 70)
    print("ADDITIONAL ANALYSIS: Teacher Workload")
    print("=" * 70)

    # Count periods per teacher
    teacher_periods = defaultdict(int)
    teacher_subjects = defaultdict(set)
    teacher_classes = defaultdict(set)

    for entry in timetable.entries:
        teacher_periods[entry.teacher_id] += 1
        teacher_subjects[entry.teacher_id].add(entry.subject_id)
        teacher_classes[entry.teacher_id].add(entry.class_id)

    # Sort by workload
    sorted_teachers = sorted(teacher_periods.items(), key=lambda x: x[1], reverse=True)

    print(f"\nTeacher workload summary:")
    print(f"  Total teachers: {len(sorted_teachers)}")

    if sorted_teachers:
        avg_load = sum(teacher_periods.values()) / len(teacher_periods)
        print(f"  Average periods per teacher: {avg_load:.1f}")

        print(f"\n  Top 5 teachers by workload:")
        for teacher_id, periods in sorted_teachers[:5]:
            subjects = len(teacher_subjects[teacher_id])
            classes = len(teacher_classes[teacher_id])
            print(f"    {teacher_id}: {periods} periods, {subjects} subjects, {classes} classes")

    return {
        'teacher_periods': dict(teacher_periods),
        'teacher_subjects': {k: list(v) for k, v in teacher_subjects.items()},
        'teacher_classes': {k: list(v) for k, v in teacher_classes.items()}
    }


def run_full_verification(timetable, expected_home_rooms=None):
    """
    Run all verification checks.

    Args:
        timetable: Generated timetable to verify
        expected_home_rooms: Optional dict of class -> home room assignments
    """
    print("\n" + "=" * 70)
    print("TIMETABLE VERIFICATION SUITE v2.5.1")
    print("=" * 70)
    print(f"\nTimetable: {timetable.id}")
    print(f"Total entries: {len(timetable.entries)}")

    # Run verifications
    teacher_ok = verify_teacher_consistency(timetable)
    room_ok = verify_home_room_usage(timetable, expected_home_rooms)

    # Additional analysis
    analyze_teacher_workload(timetable)

    # Final summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    results = {
        'Teacher Consistency (CRITICAL)': teacher_ok,
        'Home Room Usage (LOW PRIORITY)': room_ok
    }

    all_passed = all(results.values())

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {check}: {status}")

    print("=" * 70)

    if all_passed:
        print("\n✅ ALL CHECKS PASSED - Timetable is valid!")
    else:
        print("\n⚠️ SOME CHECKS FAILED - Review issues above")

    print()

    return all_passed


# Example usage
if __name__ == "__main__":
    print("""
    Timetable Verification Script v2.5.1
    =====================================

    Usage:

    1. Generate timetable:
       from src.csp_solver_complete_v25_1 import CSPSolverCompleteV25
       solver = CSPSolverCompleteV25(debug=True)
       timetables, _, _, _ = solver.solve(...)
       timetable = timetables[0]

    2. Run verification:
       from verify_timetable_v25_1 import run_full_verification
       run_full_verification(timetable)

    3. With expected home rooms:
       expected = {"10A": "R201", "10B": "R202"}
       run_full_verification(timetable, expected)

    This will verify:
    - Fix 1: Teacher consistency (CRITICAL)
    - Fix 2: Home room usage (LOW PRIORITY)
    - Bonus: Teacher workload analysis
    """)
