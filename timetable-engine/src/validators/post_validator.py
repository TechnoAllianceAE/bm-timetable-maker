"""
Post-Validator: Validates generated timetable against mandatory criteria

This module performs MUST-PASS validation checks on the generated timetable:
1. 100% slot coverage (NO free periods in any class)
2. No teacher conflicts (teacher in only one place at a time)
3. No room conflicts (room hosts only one class at a time)
4. Teacher consistency (one teacher per subject per class)
5. Home classroom usage (classes use home rooms for regular subjects)
6. Lab requirements (lab subjects use LAB rooms)
7. Subject period requirements met

Returns success/failure with detailed diagnostics.
"""

from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict
from src.models_phase1_v25 import (
    Timetable, TimetableEntry, Class, Subject, Teacher,
    TimeSlot, Room, GradeSubjectRequirement
)


# =============================================================================
# MANDATORY VALIDATION CHECKS
# =============================================================================

def validate_slot_coverage(
    timetable: Timetable,
    classes: List[Class],
    time_slots: List[TimeSlot]
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    CRITICAL CHECK: Verify 100% slot coverage - NO free periods allowed.

    Returns:
        (is_valid, violations, metrics)
    """
    violations = []

    # Filter active slots (non-break periods)
    active_slots = [slot for slot in time_slots if not slot.is_break]
    expected_total = len(classes) * len(active_slots)
    actual_total = len(timetable.entries)

    coverage_percentage = (actual_total / expected_total * 100) if expected_total > 0 else 0

    if actual_total < expected_total:
        violations.append(
            f"CRITICAL: Incomplete slot coverage! Expected {expected_total} entries "
            f"but generated only {actual_total} ({coverage_percentage:.1f}% coverage). "
            f"Missing {expected_total - actual_total} slots."
        )

        # Find which classes have gaps
        class_entry_count = defaultdict(int)
        for entry in timetable.entries:
            class_entry_count[entry.class_id] += 1

        for class_obj in classes:
            expected_for_class = len(active_slots)
            actual_for_class = class_entry_count.get(class_obj.id, 0)

            if actual_for_class < expected_for_class:
                violations.append(
                    f"  Class {class_obj.name}: {actual_for_class}/{expected_for_class} slots filled "
                    f"({expected_for_class - actual_for_class} FREE PERIODS)"
                )

    metrics = {
        "expected_entries": expected_total,
        "actual_entries": actual_total,
        "coverage_percentage": coverage_percentage,
        "missing_entries": max(0, expected_total - actual_total)
    }

    return len(violations) == 0, violations, metrics


def validate_teacher_conflicts(
    timetable: Timetable,
    teachers: List[Teacher]
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Check that no teacher is assigned to multiple classes at the same time.

    Returns:
        (is_valid, violations, metrics)
    """
    violations = []

    # Track teacher assignments per time slot
    teacher_assignments = defaultdict(list)  # (teacher_id, time_slot_id) -> [entry_ids]

    for entry in timetable.entries:
        key = (entry.teacher_id, entry.time_slot_id)
        teacher_assignments[key].append(entry.id)

    # Find conflicts
    conflict_count = 0
    for (teacher_id, time_slot_id), entry_ids in teacher_assignments.items():
        if len(entry_ids) > 1:
            conflict_count += 1
            teacher_name = next((t.id for t in teachers if t.id == teacher_id), teacher_id)
            violations.append(
                f"Teacher conflict: {teacher_name} assigned to {len(entry_ids)} classes "
                f"at time slot {time_slot_id}"
            )

    metrics = {
        "total_assignments": len(timetable.entries),
        "unique_teacher_slots": len(teacher_assignments),
        "conflicts": conflict_count
    }

    return len(violations) == 0, violations, metrics


def validate_room_conflicts(
    timetable: Timetable,
    rooms: List[Room]
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Check that no room hosts multiple classes at the same time.

    Returns:
        (is_valid, violations, metrics)
    """
    violations = []

    # Track room assignments per time slot
    room_assignments = defaultdict(list)  # (room_id, time_slot_id) -> [entry_ids]

    for entry in timetable.entries:
        if entry.room_id:  # Some entries might not have rooms
            key = (entry.room_id, entry.time_slot_id)
            room_assignments[key].append(entry.id)

    # Find conflicts
    conflict_count = 0
    for (room_id, time_slot_id), entry_ids in room_assignments.items():
        if len(entry_ids) > 1:
            conflict_count += 1
            room_name = next((r.name for r in rooms if r.id == room_id), room_id)
            violations.append(
                f"Room conflict: {room_name} assigned to {len(entry_ids)} classes "
                f"at time slot {time_slot_id}"
            )

    metrics = {
        "total_room_assignments": sum(1 for e in timetable.entries if e.room_id),
        "unique_room_slots": len(room_assignments),
        "conflicts": conflict_count
    }

    return len(violations) == 0, violations, metrics


def validate_teacher_consistency(
    timetable: Timetable,
    classes: List[Class],
    subjects: List[Subject]
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Check that each subject in each class is taught by exactly ONE teacher.

    Returns:
        (is_valid, violations, metrics)
    """
    violations = []

    # Track teachers per (class, subject)
    class_subject_teachers = defaultdict(set)  # (class_id, subject_id) -> set of teacher_ids

    for entry in timetable.entries:
        key = (entry.class_id, entry.subject_id)
        class_subject_teachers[key].add(entry.teacher_id)

    # Find violations
    violation_count = 0
    for (class_id, subject_id), teacher_ids in class_subject_teachers.items():
        if len(teacher_ids) > 1:
            violation_count += 1
            class_name = next((c.name for c in classes if c.id == class_id), class_id)
            subject_name = next((s.name for s in subjects if s.id == subject_id), subject_id)

            violations.append(
                f"Teacher consistency violation: {class_name} - {subject_name} taught by "
                f"{len(teacher_ids)} different teachers: {list(teacher_ids)}"
            )

    metrics = {
        "total_class_subject_pairs": len(class_subject_teachers),
        "consistent_pairs": sum(1 for teachers in class_subject_teachers.values() if len(teachers) == 1),
        "violations": violation_count
    }

    return len(violations) == 0, violations, metrics


def validate_home_classroom_usage(
    timetable: Timetable,
    classes: List[Class],
    subjects: List[Subject],
    rooms: List[Room]
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Check that classes use their home classroom for regular (non-lab) subjects.

    Returns:
        (is_valid, violations, metrics)
    """
    violations = []
    home_used = 0
    home_violations = 0

    for entry in timetable.entries:
        class_obj = next((c for c in classes if c.id == entry.class_id), None)
        subject = next((s for s in subjects if s.id == entry.subject_id), None)

        if not class_obj or not subject or not class_obj.home_room_id:
            continue

        # Only check regular subjects (non-lab)
        if not subject.requires_lab:
            if entry.room_id == class_obj.home_room_id:
                home_used += 1
            else:
                home_violations += 1
                room_name = next((r.name for r in rooms if r.id == entry.room_id), entry.room_id)
                violations.append(
                    f"Home classroom violation: {class_obj.name} - {subject.name} "
                    f"using {room_name} instead of home classroom"
                )

    metrics = {
        "home_classroom_used": home_used,
        "home_classroom_violations": home_violations,
        "compliance_rate": (home_used / (home_used + home_violations) * 100) if (home_used + home_violations) > 0 else 100
    }

    return len(violations) == 0, violations, metrics


def validate_lab_requirements(
    timetable: Timetable,
    subjects: List[Subject],
    rooms: List[Room]
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Check that lab subjects are assigned to LAB rooms.

    Returns:
        (is_valid, violations, metrics)
    """
    violations = []
    lab_correct = 0
    lab_violations = 0

    for entry in timetable.entries:
        subject = next((s for s in subjects if s.id == entry.subject_id), None)
        room = next((r for r in rooms if r.id == entry.room_id), None)

        if not subject or not room:
            continue

        if subject.requires_lab:
            if room.type.value == "LAB":
                lab_correct += 1
            else:
                lab_violations += 1
                violations.append(
                    f"Lab requirement violation: {subject.name} (lab subject) "
                    f"assigned to {room.name} ({room.type.value} room)"
                )

    metrics = {
        "lab_assignments_correct": lab_correct,
        "lab_violations": lab_violations
    }

    return len(violations) == 0, violations, metrics


def validate_subject_requirements(
    timetable: Timetable,
    classes: List[Class],
    subjects: List[Subject],
    subject_requirements: List[GradeSubjectRequirement] = None
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Check that subject period requirements are met for each class.

    Returns:
        (is_valid, violations, metrics)
    """
    violations = []

    # Count actual periods per (class, subject)
    class_subject_count = defaultdict(int)
    for entry in timetable.entries:
        key = (entry.class_id, entry.subject_id)
        class_subject_count[key] += 1

    # Check against requirements
    if subject_requirements:
        # Use grade-specific requirements
        for class_obj in classes:
            for req in subject_requirements:
                if req.grade == class_obj.grade:
                    key = (class_obj.id, req.subject_id)
                    actual_periods = class_subject_count.get(key, 0)
                    required_periods = req.periods_per_week

                    if actual_periods != required_periods:
                        subject_name = next((s.name for s in subjects if s.id == req.subject_id), req.subject_id)
                        violations.append(
                            f"Period requirement mismatch: {class_obj.name} - {subject_name} "
                            f"has {actual_periods} periods but requires {required_periods}"
                        )
    else:
        # Use default subject periods_per_week
        for class_obj in classes:
            for subject in subjects:
                key = (class_obj.id, subject.id)
                actual_periods = class_subject_count.get(key, 0)
                required_periods = subject.periods_per_week

                if actual_periods < required_periods:
                    violations.append(
                        f"Period requirement not met: {class_obj.name} - {subject.name} "
                        f"has {actual_periods} periods but requires at least {required_periods}"
                    )

    metrics = {
        "total_class_subject_pairs": len(class_subject_count),
        "requirement_violations": len(violations)
    }

    return len(violations) == 0, violations, metrics


# =============================================================================
# MAIN POST-VALIDATION FUNCTION
# =============================================================================

def validate_timetable(
    timetable: Timetable,
    classes: List[Class],
    subjects: List[Subject],
    teachers: List[Teacher],
    time_slots: List[TimeSlot],
    rooms: List[Room],
    subject_requirements: List[GradeSubjectRequirement] = None
) -> Dict[str, Any]:
    """
    Complete post-validation of generated timetable.

    Performs all mandatory checks and returns comprehensive validation report.

    Returns:
        validation_result containing:
        - status: "success" | "failure"
        - is_valid: boolean
        - checks: Dict of individual check results
        - summary: Overall metrics
        - critical_violations: List of MUST-FIX issues
        - warnings: List of non-critical issues
        - suggestions: List of specific actionable recommendations
    """

    all_violations = []
    all_metrics = {}
    checks = {}
    suggestions = []  # Specific suggestions based on validation results

    # 1. CRITICAL: Slot coverage (100% required)
    coverage_valid, coverage_violations, coverage_metrics = validate_slot_coverage(
        timetable, classes, time_slots
    )
    checks["slot_coverage"] = {
        "passed": coverage_valid,
        "violations": coverage_violations,
        "metrics": coverage_metrics,
        "critical": True
    }
    all_violations.extend(coverage_violations)
    all_metrics.update(coverage_metrics)

    # 2. CRITICAL: No teacher conflicts
    teacher_valid, teacher_violations, teacher_metrics = validate_teacher_conflicts(
        timetable, teachers
    )
    checks["teacher_conflicts"] = {
        "passed": teacher_valid,
        "violations": teacher_violations,
        "metrics": teacher_metrics,
        "critical": True
    }
    all_violations.extend(teacher_violations)
    all_metrics.update(teacher_metrics)

    # 3. CRITICAL: No room conflicts
    room_valid, room_violations, room_metrics = validate_room_conflicts(
        timetable, rooms
    )
    checks["room_conflicts"] = {
        "passed": room_valid,
        "violations": room_violations,
        "metrics": room_metrics,
        "critical": True
    }
    all_violations.extend(room_violations)
    all_metrics.update(room_metrics)

    # 4. Teacher consistency (one teacher per subject per class)
    consistency_valid, consistency_violations, consistency_metrics = validate_teacher_consistency(
        timetable, classes, subjects
    )
    checks["teacher_consistency"] = {
        "passed": consistency_valid,
        "violations": consistency_violations,
        "metrics": consistency_metrics,
        "critical": False  # Warning only, not failure
    }
    if not consistency_valid:
        all_violations.extend(consistency_violations)
    all_metrics.update(consistency_metrics)

    # 5. Home classroom usage
    home_valid, home_violations, home_metrics = validate_home_classroom_usage(
        timetable, classes, subjects, rooms
    )
    checks["home_classroom"] = {
        "passed": home_valid,
        "violations": home_violations,
        "metrics": home_metrics,
        "critical": False  # Warning only
    }
    if not home_valid:
        all_violations.extend(home_violations)
    all_metrics.update(home_metrics)

    # 6. Lab requirements
    lab_valid, lab_violations, lab_metrics = validate_lab_requirements(
        timetable, subjects, rooms
    )
    checks["lab_requirements"] = {
        "passed": lab_valid,
        "violations": lab_violations,
        "metrics": lab_metrics,
        "critical": False
    }
    if not lab_valid:
        all_violations.extend(lab_violations)
    all_metrics.update(lab_metrics)

    # 7. Subject period requirements
    req_valid, req_violations, req_metrics = validate_subject_requirements(
        timetable, classes, subjects, subject_requirements
    )
    checks["subject_requirements"] = {
        "passed": req_valid,
        "violations": req_violations,
        "metrics": req_metrics,
        "critical": True
    }
    all_violations.extend(req_violations)
    all_metrics.update(req_metrics)

    # Determine overall validity (all CRITICAL checks must pass)
    critical_checks_passed = all(
        check["passed"] for check in checks.values() if check.get("critical", False)
    )

    # Separate critical violations from warnings
    critical_violations = []
    warnings = []

    for check_name, check_data in checks.items():
        if not check_data["passed"]:
            if check_data.get("critical", False):
                critical_violations.extend(check_data["violations"])
            else:
                warnings.extend(check_data["violations"])

    status = "success" if critical_checks_passed else "failure"

    # ==================================================================
    # Generate Specific Suggestions Based on Validation Results
    # ==================================================================

    # 1. Slot coverage suggestions
    if not coverage_valid:
        # Find classes with gaps grouped by grade
        class_entry_count = defaultdict(int)
        for entry in timetable.entries:
            class_entry_count[entry.class_id] += 1

        active_slots = [slot for slot in time_slots if not slot.is_break]
        expected_slots = len(active_slots)

        classes_with_gaps = []
        for class_obj in classes:
            actual = class_entry_count.get(class_obj.id, 0)
            if actual < expected_slots:
                classes_with_gaps.append((class_obj, expected_slots - actual))

        # Group by grade
        grade_gaps = defaultdict(list)
        for class_obj, gap_count in classes_with_gaps:
            grade_gaps[class_obj.grade].append((class_obj.name, gap_count))

        for grade, class_gaps in sorted(grade_gaps.items()):
            class_names = ", ".join([f"{name} ({gaps} gaps)" for name, gaps in class_gaps])
            suggestions.append(f"Grade {grade}: Fill {sum(g for _, g in class_gaps)} vacant periods across classes: {class_names}")

    # 2. Teacher consistency suggestions
    if not consistency_valid:
        # Find class-subject pairs with multiple teachers
        class_subject_teachers = defaultdict(set)
        for entry in timetable.entries:
            key = (entry.class_id, entry.subject_id)
            class_subject_teachers[key].add(entry.teacher_id)

        # Group by subject
        subject_issues = defaultdict(list)
        for (class_id, subject_id), teacher_ids in class_subject_teachers.items():
            if len(teacher_ids) > 1:
                class_name = next((c.name for c in classes if c.id == class_id), class_id)
                subject_name = next((s.name for s in subjects if s.id == subject_id), subject_id)
                subject_issues[subject_name].append(class_name)

        for subject_name, class_names in subject_issues.items():
            suggestions.append(f"{subject_name}: Assign one consistent teacher for classes: {', '.join(class_names)}")

    # 3. Home classroom suggestions
    if not home_valid and home_violations > 0:
        # Find classes with home classroom violations
        home_violations_by_class = defaultdict(int)
        for entry in timetable.entries:
            class_obj = next((c for c in classes if c.id == entry.class_id), None)
            subject = next((s for s in subjects if s.id == entry.subject_id), None)

            if class_obj and subject and class_obj.home_room_id:
                if not subject.requires_lab and entry.room_id != class_obj.home_room_id:
                    home_violations_by_class[class_obj.name] += 1

        if home_violations_by_class:
            class_list = ", ".join([f"{name} ({count} violations)" for name, count in sorted(home_violations_by_class.items())])
            suggestions.append(f"Home Classroom: Prioritize home room assignments for regular subjects in classes: {class_list}")

    # 4. Lab requirement suggestions
    if not lab_valid and lab_metrics.get('lab_violations', 0) > 0:
        # Find which lab subjects are affected
        lab_violations_by_subject = defaultdict(set)
        for entry in timetable.entries:
            subject = next((s for s in subjects if s.id == entry.subject_id), None)
            room = next((r for r in rooms if r.id == entry.room_id), None)

            if subject and room and subject.requires_lab:
                if room.type.value != "LAB":
                    class_obj = next((c for c in classes if c.id == entry.class_id), None)
                    if class_obj:
                        lab_violations_by_subject[subject.name].add(class_obj.name)

        for subject_name, class_names in lab_violations_by_subject.items():
            suggestions.append(f"{subject_name}: Need LAB room assignments for classes: {', '.join(sorted(class_names))}")

    # 5. Subject requirement suggestions
    if not req_valid:
        # Find which subjects/classes have period mismatches
        class_subject_count = defaultdict(int)
        for entry in timetable.entries:
            key = (entry.class_id, entry.subject_id)
            class_subject_count[key] += 1

        # Group mismatches by subject
        subject_mismatches = defaultdict(list)

        if subject_requirements:
            for class_obj in classes:
                for req in subject_requirements:
                    if req.grade == class_obj.grade:
                        key = (class_obj.id, req.subject_id)
                        actual = class_subject_count.get(key, 0)
                        required = req.periods_per_week

                        if actual != required:
                            subject_name = next((s.name for s in subjects if s.id == req.subject_id), req.subject_id)
                            subject_mismatches[subject_name].append(f"{class_obj.name} ({actual}/{required} periods)")
        else:
            for class_obj in classes:
                for subject in subjects:
                    key = (class_obj.id, subject.id)
                    actual = class_subject_count.get(key, 0)
                    required = subject.periods_per_week

                    if actual < required:
                        subject_mismatches[subject.name].append(f"{class_obj.name} ({actual}/{required} periods)")

        for subject_name, class_details in subject_mismatches.items():
            suggestions.append(f"{subject_name}: Adjust period allocation for {', '.join(class_details)}")

    result = {
        "status": status,
        "is_valid": critical_checks_passed,
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "checks_passed": sum(1 for c in checks.values() if c["passed"]),
            "checks_failed": sum(1 for c in checks.values() if not c["passed"]),
            "critical_failures": len(critical_violations),
            "warnings": len(warnings)
        },
        "critical_violations": critical_violations,
        "warnings": warnings,
        "suggestions": suggestions,  # Add specific suggestions
        "metrics": all_metrics
    }

    return result
