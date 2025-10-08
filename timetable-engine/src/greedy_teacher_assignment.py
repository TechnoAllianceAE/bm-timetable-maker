"""
Greedy Teacher Assignment Algorithm

PURPOSE:
Pre-assigns teachers to (class, subject) pairs BEFORE CSP scheduling begins.
This ensures optimal teacher utilization and prevents resource bottlenecks.

ALGORITHM:
1. Calculate total workload needed per subject across all classes
2. Sort (class, subject) pairs by subject demand (high demand first)
3. For each pair, assign the teacher with:
   - Qualification for the subject
   - Lowest current workload
   - Most available time slots
4. Track teacher workload to ensure fair distribution

VERSION: 1.0.0
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import random

from src.models_phase1_v25 import Class, Subject, Teacher, TimeSlot


class GreedyTeacherAssignment:
    """
    Greedy algorithm for optimal teacher-to-class-subject assignment.
    """

    def __init__(self, debug: bool = False):
        self.debug = debug

    def assign_teachers(
        self,
        classes: List[Class],
        subjects: List[Subject],
        teachers: List[Teacher],
        time_slots: List[TimeSlot],
        subject_requirements: Optional[Dict[str, int]] = None
    ) -> Dict[Tuple[str, str], str]:
        """
        Assign teachers to (class_id, subject_id) pairs using greedy algorithm.

        Args:
            classes: List of classes
            subjects: List of subjects
            teachers: List of teachers
            time_slots: List of time slots (to calculate availability)
            subject_requirements: Optional dict mapping subject_id to periods_per_week

        Returns:
            Dictionary mapping (class_id, subject_id) -> teacher_id
        """
        if self.debug:
            print("\n[GREEDY] Starting teacher assignment")
            print(f"  Classes: {len(classes)}")
            print(f"  Subjects: {len(subjects)}")
            print(f"  Teachers: {len(teachers)}")

        # Filter active slots
        active_slots = [ts for ts in time_slots if not ts.is_break]
        total_slots_per_week = len(active_slots)

        # Build teacher-subject qualification map
        teacher_qualifications = self._build_qualification_map(teachers, subjects)

        # Calculate subject requirements per class
        subject_demand = self._calculate_subject_demand(
            classes, subjects, subject_requirements
        )

        # Calculate total demand per subject across all classes
        total_subject_demand = defaultdict(int)
        for (class_id, subject_id), periods in subject_demand.items():
            total_subject_demand[subject_id] += periods

        if self.debug:
            print("\n[GREEDY] Subject demand analysis:")
            for subject in subjects:
                demand = total_subject_demand.get(subject.id, 0)
                qualified_count = len(teacher_qualifications.get(subject.id, []))
                print(f"  {subject.name}: {demand} periods/week, {qualified_count} teachers")

        # Sort (class, subject) pairs with intelligent prioritization
        # STRATEGY (mimics manual timetable creation):
        # 1. MANDATORY/CORE subjects first (Math, English, Science)
        # 2. High-demand subjects (most periods needed)
        # 3. Optional/elective subjects last
        pairs_to_assign = []

        # Define mandatory subjects (customize based on school)
        mandatory_keywords = ['math', 'english', 'science', 'language']

        for class_obj in classes:
            for subject in subjects:
                key = (class_obj.id, subject.id)
                periods_needed = subject_demand.get(key, subject.periods_per_week)

                # Calculate priority
                # 1. Is it mandatory? (highest priority)
                is_mandatory = any(kw in subject.name.lower() for kw in mandatory_keywords)
                mandatory_score = 1000 if is_mandatory else 0

                # 2. Subject demand across all classes
                demand_score = total_subject_demand[subject.id]

                # Combined priority
                priority = mandatory_score + demand_score

                pairs_to_assign.append((priority, is_mandatory, class_obj, subject, periods_needed))

        # Sort by priority (mandatory + high demand first)
        pairs_to_assign.sort(key=lambda x: x[0], reverse=True)

        if self.debug:
            print("\n[GREEDY] Assignment priority order (first 10):")
            for i, (priority, is_mandatory, class_obj, subject, periods) in enumerate(pairs_to_assign[:10]):
                status = "MANDATORY" if is_mandatory else "optional"
                print(f"  {i+1}. {class_obj.name} - {subject.name} ({status}, {periods}p, priority={priority})")

        # Track teacher workload
        teacher_workload = {t.id: 0 for t in teachers}
        teacher_max_workload = {t.id: t.max_periods_per_week for t in teachers}

        # Assignment result
        assignment_map = {}

        # Assign teachers greedily
        for priority, is_mandatory, class_obj, subject, periods_needed in pairs_to_assign:
            key = (class_obj.id, subject.id)

            # Get qualified teachers for this subject
            qualified_teachers = teacher_qualifications.get(subject.id, [])

            if not qualified_teachers:
                if self.debug:
                    print(f"  [WARNING] No qualified teachers for {subject.name}")
                # Try to find any teacher with capacity
                qualified_teachers = [t for t in teachers
                                    if teacher_workload[t.id] < teacher_max_workload[t.id]]

            if not qualified_teachers:
                if self.debug:
                    print(f"  [ERROR] Cannot assign teacher for {class_obj.name} - {subject.name}")
                continue

            # Select teacher with lowest current workload
            # This ensures fair distribution
            best_teacher = None
            best_score = float('-inf')

            for teacher in qualified_teachers:
                current_workload = teacher_workload[teacher.id]
                max_workload = teacher_max_workload[teacher.id]
                available_capacity = max_workload - current_workload

                # Skip if teacher doesn't have enough capacity
                if available_capacity < periods_needed:
                    continue

                # Score = available capacity (higher is better)
                # Prefer teachers with more availability
                score = available_capacity

                if score > best_score:
                    best_score = score
                    best_teacher = teacher

            # If no teacher has enough capacity, use the one with most availability
            if not best_teacher:
                qualified_teachers.sort(
                    key=lambda t: teacher_max_workload[t.id] - teacher_workload[t.id],
                    reverse=True
                )
                best_teacher = qualified_teachers[0] if qualified_teachers else None

            if best_teacher:
                assignment_map[key] = best_teacher.id
                teacher_workload[best_teacher.id] += periods_needed

                if self.debug:
                    workload_pct = (teacher_workload[best_teacher.id] / teacher_max_workload[best_teacher.id]) * 100
                    print(f"  [ASSIGN] {class_obj.name} - {subject.name} → "
                          f"Teacher {best_teacher.id[:8]} "
                          f"({periods_needed}p, {workload_pct:.0f}% capacity)")
            else:
                if self.debug:
                    print(f"  [ERROR] No available teacher for {class_obj.name} - {subject.name}")

        # Summary
        if self.debug:
            print("\n[GREEDY] Assignment complete")
            print(f"  Total assignments: {len(assignment_map)}")
            print(f"  Expected: {len(classes) * len(subjects)}")

            print("\n[GREEDY] Teacher utilization:")
            for teacher in teachers:
                workload = teacher_workload[teacher.id]
                max_workload = teacher_max_workload[teacher.id]
                if workload > 0:
                    pct = (workload / max_workload) * 100
                    print(f"  Teacher {teacher.id[:8]}: {workload}/{max_workload} periods ({pct:.0f}%)")

        return assignment_map

    def _build_qualification_map(
        self,
        teachers: List[Teacher],
        subjects: List[Subject]
    ) -> Dict[str, List[Teacher]]:
        """Build map of subject_id -> list of qualified teachers."""
        qualification_map = defaultdict(list)

        for subject in subjects:
            for teacher in teachers:
                # Check if teacher is qualified (by name or code)
                if subject.name in teacher.subjects or subject.code in teacher.subjects:
                    qualification_map[subject.id].append(teacher)

        return qualification_map

    def _calculate_subject_demand(
        self,
        classes: List[Class],
        subjects: List[Subject],
        subject_requirements: Optional[Dict[str, int]] = None
    ) -> Dict[Tuple[str, str], int]:
        """Calculate periods needed for each (class, subject) pair."""
        demand = {}

        # Convert list to dict if necessary
        requirements_dict = {}
        if subject_requirements:
            if isinstance(subject_requirements, list):
                # Convert list of requirements to dict
                for req in subject_requirements:
                    if isinstance(req, dict):
                        grade = req.get('grade')
                        subject_id = req.get('subject_id')
                        # Fix: Check both 'periods_per_week' (from main_v25.py) and 'periods' (legacy)
                        periods = req.get('periods_per_week') or req.get('periods')
                        if grade and subject_id and periods:
                            req_key = f"{grade}_{subject_id}"
                            requirements_dict[req_key] = periods
            elif isinstance(subject_requirements, dict):
                requirements_dict = subject_requirements

        for class_obj in classes:
            for subject in subjects:
                key = (class_obj.id, subject.id)

                # Use subject requirements if provided
                if requirements_dict:
                    req_key = f"{class_obj.grade}_{subject.id}"
                    periods = requirements_dict.get(req_key, subject.periods_per_week)
                else:
                    periods = subject.periods_per_week

                demand[key] = periods

        return demand
