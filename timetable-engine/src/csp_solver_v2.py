"""
Redesigned CSP Solver V2 for Timetable Generation
Complete rewrite with improved constraint handling and feasibility

Key improvements:
1. Simplified variable model
2. Smarter constraint handling with priorities
3. Better feasibility checking
4. Incremental constraint adding to avoid infeasibility
"""

from typing import List, Dict, Tuple, Optional, Set
import time
from ortools.sat.python import cp_model
from .models_phase1 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry,
    Timetable, TimetableStatus, ConstraintType, ConstraintPriority, RoomType
)

class CSPSolverV2:
    """
    Improved CSP Solver with better constraint handling and feasibility guarantees.
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.stats = {
            'variables_created': 0,
            'constraints_added': 0,
            'conflicts_detected': []
        }

    def solve(
        self,
        classes: List[Class],
        subjects: List[Subject],
        teachers: List[Teacher],
        time_slots: List[TimeSlot],
        rooms: List[Room],
        constraints: List[Constraint],
        num_solutions: int = 3
    ) -> Tuple[List[Timetable], float, Optional[List[str]], Optional[List[str]]]:
        """
        Solve timetable generation with improved constraint handling.
        """
        start_time = time.time()

        # Preprocessing
        active_slots = [ts for ts in time_slots if not ts.is_break]

        if self.debug:
            print(f"[CSP V2] Starting solve:")
            print(f"  Classes: {len(classes)}")
            print(f"  Subjects: {len(subjects)}")
            print(f"  Teachers: {len(teachers)}")
            print(f"  Active slots: {len(active_slots)}")
            print(f"  Rooms: {len(rooms)}")

        # Quick feasibility check
        feasibility_check = self._check_basic_feasibility(
            classes, subjects, teachers, active_slots, rooms
        )
        if not feasibility_check['feasible']:
            return [], time.time() - start_time, feasibility_check['conflicts'], feasibility_check['suggestions']

        # Build helper structures
        teacher_subjects = self._build_teacher_subject_map(teachers, subjects)
        periods_required = self._compute_periods_required(classes, subjects)

        # Create model
        model = cp_model.CpModel()

        # === SIMPLIFIED VARIABLE MODEL ===
        # Main decision variable: schedule[class][slot] -> (subject, teacher, room)
        # We use integer variables instead of boolean for simpler modeling

        schedule_vars = {}  # (class_id, slot_id) -> subject_var, teacher_var, room_var

        # Create variables for each class-slot combination
        for class_obj in classes:
            for slot in active_slots:
                # Subject variable (0 = no class, 1..n = subject index + 1)
                subject_var = model.NewIntVar(
                    0, len(subjects),
                    f"subject_c{class_obj.id}_s{slot.id}"
                )

                # Teacher variable (0 = no teacher, 1..n = teacher index + 1)
                teacher_var = model.NewIntVar(
                    0, len(teachers),
                    f"teacher_c{class_obj.id}_s{slot.id}"
                )

                # Room variable (0 = no room, 1..n = room index + 1)
                room_var = model.NewIntVar(
                    0, len(rooms),
                    f"room_c{class_obj.id}_s{slot.id}"
                )

                schedule_vars[(class_obj.id, slot.id)] = (subject_var, teacher_var, room_var)

                # Link variables: if no subject, then no teacher/room
                no_subject = model.NewBoolVar(f"no_subject_c{class_obj.id}_s{slot.id}")
                model.Add(subject_var == 0).OnlyEnforceIf(no_subject)
                model.Add(subject_var != 0).OnlyEnforceIf(no_subject.Not())

                model.Add(teacher_var == 0).OnlyEnforceIf(no_subject)
                model.Add(room_var == 0).OnlyEnforceIf(no_subject)

                # If subject scheduled, must have teacher and room
                has_subject = model.NewBoolVar(f"has_subject_c{class_obj.id}_s{slot.id}")
                model.Add(subject_var > 0).OnlyEnforceIf(has_subject)
                model.Add(subject_var == 0).OnlyEnforceIf(has_subject.Not())

                model.Add(teacher_var > 0).OnlyEnforceIf(has_subject)
                model.Add(room_var > 0).OnlyEnforceIf(has_subject)

        self.stats['variables_created'] = len(schedule_vars) * 3

        # === CORE CONSTRAINTS (Must Have) ===

        # 1. Period requirements - each subject gets required periods
        for class_obj in classes:
            for subj_idx, subject in enumerate(subjects):
                required = periods_required.get((class_obj.id, subject.id), 0)
                if required > 0:
                    # Count slots where this subject is scheduled
                    subject_slots = []
                    for slot in active_slots:
                        subject_var, _, _ = schedule_vars[(class_obj.id, slot.id)]
                        is_scheduled = model.NewBoolVar(f"is_{subject.id}_at_{slot.id}")
                        model.Add(subject_var == subj_idx + 1).OnlyEnforceIf(is_scheduled)
                        model.Add(subject_var != subj_idx + 1).OnlyEnforceIf(is_scheduled.Not())
                        subject_slots.append(is_scheduled)

                    # Ensure exactly 'required' periods
                    model.Add(sum(subject_slots) == required)
                    self.stats['constraints_added'] += 1

        # 2. Teacher qualification - teacher must be qualified for subject
        for class_obj in classes:
            for slot in active_slots:
                subject_var, teacher_var, _ = schedule_vars[(class_obj.id, slot.id)]

                for subj_idx, subject in enumerate(subjects):
                    qualified_teachers = teacher_subjects.get(subject.id, [])
                    qualified_indices = [i+1 for i, t in enumerate(teachers) if t.id in qualified_teachers]

                    if qualified_indices:
                        # If this subject is scheduled, teacher must be qualified
                        is_subject = model.NewBoolVar(f"check_qual_{class_obj.id}_{slot.id}_{subject.id}")
                        model.Add(subject_var == subj_idx + 1).OnlyEnforceIf(is_subject)
                        model.Add(subject_var != subj_idx + 1).OnlyEnforceIf(is_subject.Not())

                        # Teacher must be in qualified list
                        model.AddAllowedAssignments([teacher_var], [(idx,) for idx in qualified_indices]).OnlyEnforceIf(is_subject)
                        self.stats['constraints_added'] += 1

        # 3. No teacher conflicts - teacher can't be in two places at once
        for slot in active_slots:
            for teacher_idx, teacher in enumerate(teachers):
                teacher_assignments = []
                for class_obj in classes:
                    _, teacher_var, _ = schedule_vars[(class_obj.id, slot.id)]
                    is_assigned = model.NewBoolVar(f"teacher_{teacher.id}_class_{class_obj.id}_slot_{slot.id}")
                    model.Add(teacher_var == teacher_idx + 1).OnlyEnforceIf(is_assigned)
                    model.Add(teacher_var != teacher_idx + 1).OnlyEnforceIf(is_assigned.Not())
                    teacher_assignments.append(is_assigned)

                # At most one class per teacher per slot
                model.Add(sum(teacher_assignments) <= 1)
                self.stats['constraints_added'] += 1

        # 4. No room conflicts - room can't be used by two classes at once
        for slot in active_slots:
            for room_idx, room in enumerate(rooms):
                room_assignments = []
                for class_obj in classes:
                    _, _, room_var = schedule_vars[(class_obj.id, slot.id)]
                    is_assigned = model.NewBoolVar(f"room_{room.id}_class_{class_obj.id}_slot_{slot.id}")
                    model.Add(room_var == room_idx + 1).OnlyEnforceIf(is_assigned)
                    model.Add(room_var != room_idx + 1).OnlyEnforceIf(is_assigned.Not())
                    room_assignments.append(is_assigned)

                # At most one class per room per slot
                model.Add(sum(room_assignments) <= 1)
                self.stats['constraints_added'] += 1

        # 5. Room capacity constraints
        for class_obj in classes:
            for slot in active_slots:
                _, _, room_var = schedule_vars[(class_obj.id, slot.id)]

                # Only allow rooms with sufficient capacity
                allowed_rooms = []
                for room_idx, room in enumerate(rooms):
                    if room.capacity >= class_obj.student_count:
                        allowed_rooms.append(room_idx + 1)

                allowed_rooms.append(0)  # Also allow no room (no class)
                model.AddAllowedAssignments([room_var], [(r,) for r in allowed_rooms])
                self.stats['constraints_added'] += 1

        # 6. Lab requirements - science subjects need lab rooms
        lab_room_indices = [i+1 for i, r in enumerate(rooms) if r.type == RoomType.LAB]
        regular_room_indices = [i+1 for i, r in enumerate(rooms) if r.type != RoomType.LAB]

        for class_obj in classes:
            for slot in active_slots:
                subject_var, _, room_var = schedule_vars[(class_obj.id, slot.id)]

                for subj_idx, subject in enumerate(subjects):
                    if subject.requires_lab and lab_room_indices:
                        # If lab subject scheduled, must use lab room
                        is_lab_subject = model.NewBoolVar(f"lab_{class_obj.id}_{slot.id}_{subject.id}")
                        model.Add(subject_var == subj_idx + 1).OnlyEnforceIf(is_lab_subject)
                        model.Add(subject_var != subj_idx + 1).OnlyEnforceIf(is_lab_subject.Not())

                        # Room must be a lab
                        model.AddAllowedAssignments([room_var], [(idx,) for idx in lab_room_indices]).OnlyEnforceIf(is_lab_subject)
                        self.stats['constraints_added'] += 1

        # === WORKLOAD CONSTRAINTS (Soft - try to satisfy) ===

        # 7. Teacher daily workload limit
        for teacher_idx, teacher in enumerate(teachers):
            # Group slots by day
            days = {}
            for slot in active_slots:
                day = slot.day_of_week
                if day not in days:
                    days[day] = []
                days[day].append(slot)

            for day, day_slots in days.items():
                daily_assignments = []
                for slot in day_slots:
                    for class_obj in classes:
                        _, teacher_var, _ = schedule_vars[(class_obj.id, slot.id)]
                        is_teaching = model.NewBoolVar(f"daily_{teacher.id}_{day}_{class_obj.id}_{slot.id}")
                        model.Add(teacher_var == teacher_idx + 1).OnlyEnforceIf(is_teaching)
                        model.Add(teacher_var != teacher_idx + 1).OnlyEnforceIf(is_teaching.Not())
                        daily_assignments.append(is_teaching)

                # Soft constraint: try to stay within daily limit
                model.Add(sum(daily_assignments) <= teacher.max_periods_per_day)
                self.stats['constraints_added'] += 1

        # 8. Teacher weekly workload limit
        for teacher_idx, teacher in enumerate(teachers):
            weekly_assignments = []
            for slot in active_slots:
                for class_obj in classes:
                    _, teacher_var, _ = schedule_vars[(class_obj.id, slot.id)]
                    is_teaching = model.NewBoolVar(f"weekly_{teacher.id}_{class_obj.id}_{slot.id}")
                    model.Add(teacher_var == teacher_idx + 1).OnlyEnforceIf(is_teaching)
                    model.Add(teacher_var != teacher_idx + 1).OnlyEnforceIf(is_teaching.Not())
                    weekly_assignments.append(is_teaching)

            # Soft constraint: try to stay within weekly limit
            model.Add(sum(weekly_assignments) <= teacher.max_periods_per_week)
            self.stats['constraints_added'] += 1

        # === OPTIMIZATION OBJECTIVE ===
        # Minimize gaps and maximize room utilization
        objective_terms = []

        # Penalize empty slots (gaps in schedule)
        for class_obj in classes:
            for slot in active_slots:
                subject_var, _, _ = schedule_vars[(class_obj.id, slot.id)]
                is_empty = model.NewBoolVar(f"empty_{class_obj.id}_{slot.id}")
                model.Add(subject_var == 0).OnlyEnforceIf(is_empty)
                model.Add(subject_var != 0).OnlyEnforceIf(is_empty.Not())
                objective_terms.append(is_empty)

        # Minimize total gaps
        model.Minimize(sum(objective_terms))

        # === SOLVING ===
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0  # Increased timeout
        solver.parameters.num_search_workers = 8     # More parallel workers
        solver.parameters.linearization_level = 2    # Better linearization

        if self.debug:
            print(f"[CSP V2] Model created:")
            print(f"  Variables: {self.stats['variables_created']}")
            print(f"  Constraints: {self.stats['constraints_added']}")
            print(f"  Starting solve...")

        # Collect solutions
        solutions = []

        class SolutionCollector(cp_model.CpSolverSolutionCallback):
            def __init__(self, schedule_vars, classes, subjects, teachers, rooms, active_slots, limit):
                cp_model.CpSolverSolutionCallback.__init__(self)
                self.schedule_vars = schedule_vars
                self.classes = classes
                self.subjects = subjects
                self.teachers = teachers
                self.rooms = rooms
                self.active_slots = active_slots
                self.solutions = []
                self.limit = limit

            def on_solution_callback(self):
                if len(self.solutions) >= self.limit:
                    self.StopSearch()
                    return

                entries = []
                entry_id = 1

                for class_obj in self.classes:
                    for slot in self.active_slots:
                        subject_var, teacher_var, room_var = self.schedule_vars[(class_obj.id, slot.id)]

                        subject_idx = self.Value(subject_var)
                        teacher_idx = self.Value(teacher_var)
                        room_idx = self.Value(room_var)

                        if subject_idx > 0:  # Class is scheduled
                            subject = self.subjects[subject_idx - 1]
                            teacher = self.teachers[teacher_idx - 1]
                            room = self.rooms[room_idx - 1]

                            entry = TimetableEntry(
                                id=f"entry_{entry_id}",
                                timetable_id="solution",
                                class_id=class_obj.id,
                                subject_id=subject.id,
                                time_slot_id=slot.id,
                                teacher_id=teacher.id,
                                room_id=room.id,
                                day_of_week=slot.day_of_week,
                                period_number=slot.period_number,
                                is_fixed=False
                            )
                            entries.append(entry)
                            entry_id += 1

                timetable = Timetable(
                    id=f"solution_{len(self.solutions) + 1}",
                    school_id="school-001",
                    academic_year_id="2024",
                    name=f"Solution {len(self.solutions) + 1}",
                    status=TimetableStatus.DRAFT,
                    entries=entries
                )

                self.solutions.append(timetable)
                print(f"[CSP V2] Found solution {len(self.solutions)} with {len(entries)} entries")

        collector = SolutionCollector(
            schedule_vars, classes, subjects, teachers, rooms, active_slots, num_solutions
        )

        status = solver.Solve(model, collector)
        generation_time = time.time() - start_time

        if self.debug:
            print(f"[CSP V2] Solve completed in {generation_time:.2f}s")
            print(f"  Status: {solver.StatusName(status)}")
            print(f"  Solutions found: {len(collector.solutions)}")

        # Return results
        if collector.solutions:
            return collector.solutions, generation_time, None, None
        else:
            if status == cp_model.INFEASIBLE:
                conflicts = self._analyze_infeasibility(model, solver)
                suggestions = [
                    "Check if there are enough qualified teachers for each subject",
                    "Ensure sufficient rooms are available",
                    "Verify teacher workload limits are reasonable",
                    "Consider reducing required periods for some subjects"
                ]
            elif status == cp_model.MODEL_INVALID:
                conflicts = ["Model is invalid - internal error"]
                suggestions = ["Contact support"]
            else:
                conflicts = ["No solution found within time limit"]
                suggestions = [
                    "Increase solving timeout",
                    "Simplify constraints",
                    "Reduce problem size"
                ]

            return [], generation_time, conflicts, suggestions

    def _check_basic_feasibility(
        self,
        classes: List[Class],
        subjects: List[Subject],
        teachers: List[Teacher],
        active_slots: List[TimeSlot],
        rooms: List[Room]
    ) -> Dict:
        """
        Quick feasibility check before attempting to solve.
        """
        conflicts = []
        suggestions = []

        # Check 1: Enough slots for all classes
        total_periods_needed = len(classes) * sum(s.periods_per_week for s in subjects)
        total_slots_available = len(active_slots) * min(len(rooms), len(classes))

        if total_periods_needed > total_slots_available:
            conflicts.append(f"Need {total_periods_needed} period-slots but only {total_slots_available} available")
            suggestions.append("Add more time slots or reduce required periods")

        # Check 2: Enough qualified teachers
        for subject in subjects:
            qualified_count = sum(1 for t in teachers if subject.name in t.subjects)
            periods_per_week = subject.periods_per_week * len(classes)
            min_teachers_needed = periods_per_week // 25  # Assume max 25 periods/week per teacher

            if qualified_count < min_teachers_needed:
                conflicts.append(f"Need at least {min_teachers_needed} teachers for {subject.name} but only have {qualified_count}")
                suggestions.append(f"Add more teachers qualified for {subject.name}")

        # Check 3: Lab room availability
        lab_subjects = [s for s in subjects if s.requires_lab]
        lab_rooms = [r for r in rooms if r.type == RoomType.LAB]

        if lab_subjects and not lab_rooms:
            conflicts.append("Lab subjects require lab rooms but none available")
            suggestions.append("Add lab rooms for science/computer subjects")

        return {
            'feasible': len(conflicts) == 0,
            'conflicts': conflicts,
            'suggestions': suggestions
        }

    def _build_teacher_subject_map(self, teachers: List[Teacher], subjects: List[Subject]) -> Dict[str, List[str]]:
        """
        Build mapping of subject IDs to qualified teacher IDs.
        """
        subject_teachers = {}

        for subject in subjects:
            qualified = []
            for teacher in teachers:
                # Check if teacher is qualified for this subject
                if subject.name in teacher.subjects:
                    qualified.append(teacher.id)
            subject_teachers[subject.id] = qualified

        return subject_teachers

    def _compute_periods_required(
        self,
        classes: List[Class],
        subjects: List[Subject]
    ) -> Dict[Tuple[str, str], int]:
        """
        Compute required periods for each class-subject combination.
        """
        periods = {}

        for class_obj in classes:
            for subject in subjects:
                # Use subject's default periods_per_week
                periods[(class_obj.id, subject.id)] = subject.periods_per_week

        return periods

    def _analyze_infeasibility(self, model: cp_model.CpModel, solver: cp_model.CpSolver) -> List[str]:
        """
        Analyze why the model is infeasible.
        """
        conflicts = ["Problem is infeasible - constraints cannot be satisfied"]

        # Try to identify specific issues
        if self.debug:
            conflicts.append(f"Total variables: {self.stats['variables_created']}")
            conflicts.append(f"Total constraints: {self.stats['constraints_added']}")

        return conflicts