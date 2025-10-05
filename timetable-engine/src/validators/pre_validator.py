"""
Pre-Validator: Validates request constraints before timetable generation

This module checks:
1. Whether requested constraints are supported by the compiler
2. Resource feasibility (enough teachers, rooms, time slots)
3. Constraint parameter validity
4. Mathematical feasibility checks

Returns error/warning messages if validation fails.
"""

from typing import List, Dict, Any, Tuple
from src.models_phase1_v25 import (
    GenerateRequest, Constraint, ConstraintType,
    Class, Subject, Teacher, TimeSlot, Room,
    GradeSubjectRequirement
)


# =============================================================================
# SUPPORTED FEATURES REGISTRY
# =============================================================================

SUPPORTED_CONSTRAINT_TYPES = {
    ConstraintType.TEACHER_AVAILABILITY,
    ConstraintType.ROOM_CAPACITY,
    ConstraintType.CONSECUTIVE_PERIODS,
    ConstraintType.MIN_PERIODS_PER_WEEK,
    ConstraintType.MAX_PERIODS_PER_WEEK,
    ConstraintType.PREFERRED_TIME_SLOT,
    ConstraintType.NO_GAPS,
    ConstraintType.LUNCH_BREAK,
    ConstraintType.ONE_TEACHER_PER_SUBJECT,
}

SUPPORTED_FEATURES = {
    "teacher_consistency": True,  # One teacher per subject per class
    "home_classroom": True,       # Dedicated home classroom usage
    "lab_requirements": True,     # Lab subjects use LAB rooms
    "grade_subject_requirements": True,  # Grade-specific period allocations
    "teacher_availability": True,
    "room_capacity": True,
    "consecutive_period_limits": True,
    "preferred_time_slots": True,
    "subject_time_preferences": True,  # prefer_morning, etc.
}


# =============================================================================
# PRE-VALIDATION FUNCTIONS
# =============================================================================

def validate_constraints(constraints: List[Constraint]) -> Tuple[bool, List[str], List[str]]:
    """
    Validate that all requested constraints are supported.

    Returns:
        (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    for constraint in constraints:
        if constraint.type not in SUPPORTED_CONSTRAINT_TYPES:
            errors.append(
                f"Unsupported constraint type: '{constraint.type}'. "
                f"Supported types: {[ct.value for ct in SUPPORTED_CONSTRAINT_TYPES]}"
            )

    return len(errors) == 0, errors, warnings


def validate_resource_feasibility(
    classes: List[Class],
    subjects: List[Subject],
    teachers: List[Teacher],
    time_slots: List[TimeSlot],
    rooms: List[Room],
    subject_requirements: List[GradeSubjectRequirement] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Check if resources are mathematically sufficient for timetable generation.

    Returns:
        (is_feasible, errors, warnings)
    """
    errors = []
    warnings = []

    # Count active time slots (non-break periods)
    active_slots = [slot for slot in time_slots if not slot.is_break]
    total_slots_per_class = len(active_slots)

    # 1. Check if total subject periods fit in available time slots
    if subject_requirements:
        # Use grade-specific requirements
        for class_obj in classes:
            required_periods = 0
            for req in subject_requirements:
                if req.grade == class_obj.grade:
                    required_periods += req.periods_per_week

            if required_periods > total_slots_per_class:
                errors.append(
                    f"Class {class_obj.name} (Grade {class_obj.grade}): "
                    f"Required {required_periods} periods/week but only {total_slots_per_class} slots available"
                )
    else:
        # Use default subject periods_per_week
        total_periods_needed = sum(s.periods_per_week for s in subjects)
        if total_periods_needed > total_slots_per_class:
            errors.append(
                f"Total subject periods ({total_periods_needed}) exceed available time slots ({total_slots_per_class})"
            )

    # 2. Check teacher availability
    subject_teacher_map = {}
    for teacher in teachers:
        for subject_id in teacher.subjects:
            if subject_id not in subject_teacher_map:
                subject_teacher_map[subject_id] = []
            subject_teacher_map[subject_id].append(teacher)

    for subject in subjects:
        if subject.id not in subject_teacher_map and subject.code not in subject_teacher_map:
            errors.append(
                f"No teacher qualified to teach subject '{subject.name}' (ID: {subject.id}, Code: {subject.code})"
            )

    # 3. Check room capacity
    total_classrooms = sum(1 for r in rooms if r.type.value == "CLASSROOM")
    total_labs = sum(1 for r in rooms if r.type.value == "LAB")

    lab_subjects = [s for s in subjects if s.requires_lab]
    if lab_subjects and total_labs == 0:
        errors.append(
            f"Lab subjects present ({len(lab_subjects)}) but no LAB rooms available"
        )

    if total_classrooms == 0:
        errors.append("No CLASSROOM type rooms available")

    # 4. Check home classroom assignments
    home_room_ids = {c.home_room_id for c in classes if c.home_room_id}
    available_room_ids = {r.id for r in rooms}

    invalid_home_rooms = home_room_ids - available_room_ids
    if invalid_home_rooms:
        errors.append(
            f"Invalid home room IDs assigned: {list(invalid_home_rooms)}"
        )

    # 5. Warnings for potential issues
    if len(classes) > len(active_slots):
        warnings.append(
            f"Number of classes ({len(classes)}) exceeds available periods ({len(active_slots)}). "
            "This may require shared room usage."
        )

    total_teacher_capacity = sum(t.max_periods_per_week for t in teachers)
    total_required_periods = len(classes) * total_slots_per_class

    if total_teacher_capacity < total_required_periods * 1.5:  # 1.5x safety margin
        warnings.append(
            f"Teacher capacity ({total_teacher_capacity} periods/week) may be insufficient for "
            f"{len(classes)} classes × {total_slots_per_class} slots = {total_required_periods} total periods. "
            "Consider adding more teachers or reducing class count."
        )

    return len(errors) == 0, errors, warnings


def validate_request(request: GenerateRequest) -> Tuple[bool, Dict[str, Any]]:
    """
    Complete pre-validation of generation request.

    Returns:
        (is_valid, validation_result)

    validation_result contains:
        - status: "valid" | "error" | "warning"
        - errors: List of error messages
        - warnings: List of warning messages
        - suggestions: List of specific actionable recommendations
        - details: Additional validation details
    """
    all_errors = []
    all_warnings = []
    suggestions = []

    # 1. Validate constraints
    constraints_valid, constraint_errors, constraint_warnings = validate_constraints(
        request.constraints
    )
    all_errors.extend(constraint_errors)
    all_warnings.extend(constraint_warnings)

    # 2. Validate resource feasibility
    feasible, feasibility_errors, feasibility_warnings = validate_resource_feasibility(
        classes=request.classes,
        subjects=request.subjects,
        teachers=request.teachers,
        time_slots=request.time_slots,
        rooms=request.rooms,
        subject_requirements=request.subject_requirements
    )
    all_errors.extend(feasibility_errors)
    all_warnings.extend(feasibility_warnings)

    # 3. Check for empty data
    if not request.classes:
        all_errors.append("No classes provided")
    if not request.subjects:
        all_errors.append("No subjects provided")
    if not request.teachers:
        all_errors.append("No teachers provided")
    if not request.time_slots:
        all_errors.append("No time slots provided")
    if not request.rooms:
        all_errors.append("No rooms provided")

    # ==================================================================
    # Generate Specific Suggestions Based on Errors/Warnings
    # ==================================================================

    # Find subjects without qualified teachers
    subject_teacher_map = {}
    for teacher in request.teachers:
        for subject_id in teacher.subjects:
            if subject_id not in subject_teacher_map:
                subject_teacher_map[subject_id] = []
            subject_teacher_map[subject_id].append(teacher)

    subjects_without_teachers = []
    for subject in request.subjects:
        if subject.id not in subject_teacher_map and subject.code not in subject_teacher_map:
            subjects_without_teachers.append(subject.name)

    if subjects_without_teachers:
        suggestions.append(f"Add qualified teachers for: {', '.join(subjects_without_teachers)}")

    # Find lab subjects without lab rooms
    lab_subjects = [s for s in request.subjects if s.requires_lab]
    total_labs = sum(1 for r in request.rooms if r.type.value == "LAB")

    if lab_subjects and total_labs == 0:
        lab_names = [s.name for s in lab_subjects]
        suggestions.append(f"Add LAB rooms for subjects: {', '.join(lab_names)}")
    elif lab_subjects and total_labs < len(lab_subjects):
        suggestions.append(f"Consider adding more LAB rooms (currently {total_labs}, recommended: at least {len(lab_subjects)})")

    # Check grade-specific period overflow
    active_slots = [ts for ts in request.time_slots if not ts.is_break]
    total_slots_per_class = len(active_slots)

    if request.subject_requirements:
        grades_with_overflow = []
        for class_obj in request.classes:
            required_periods = sum(
                req.periods_per_week
                for req in request.subject_requirements
                if req.grade == class_obj.grade
            )
            if required_periods > total_slots_per_class:
                grades_with_overflow.append((class_obj.grade, required_periods, total_slots_per_class))

        # Group by grade
        grade_dict = {}
        for grade, required, available in grades_with_overflow:
            if grade not in grade_dict:
                grade_dict[grade] = (required, available)

        for grade, (required, available) in sorted(grade_dict.items()):
            overflow = required - available
            suggestions.append(f"Grade {grade}: Reduce subject periods by {overflow} (currently {required}/{available} slots)")

    # Check home room assignments
    home_room_ids = {c.home_room_id for c in request.classes if c.home_room_id}
    available_room_ids = {r.id for r in request.rooms}
    invalid_home_rooms = home_room_ids - available_room_ids

    if invalid_home_rooms:
        affected_classes = [c.name for c in request.classes if c.home_room_id in invalid_home_rooms]
        suggestions.append(f"Assign valid home rooms for classes: {', '.join(affected_classes)}")

    # Determine overall status
    is_valid = len(all_errors) == 0
    status = "valid" if is_valid else "error"
    if is_valid and all_warnings:
        status = "warning"

    result = {
        "status": status,
        "is_valid": is_valid,
        "errors": all_errors,
        "warnings": all_warnings,
        "suggestions": suggestions,
        "details": {
            "total_classes": len(request.classes),
            "total_subjects": len(request.subjects),
            "total_teachers": len(request.teachers),
            "total_rooms": len(request.rooms),
            "total_time_slots": len(request.time_slots),
            "active_time_slots": len([ts for ts in request.time_slots if not ts.is_break]),
            "constraints_count": len(request.constraints),
            "supported_features": SUPPORTED_FEATURES
        }
    }

    return is_valid, result
