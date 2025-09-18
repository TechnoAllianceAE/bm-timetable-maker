"""
Robust CSP Solver using OR-Tools CP-SAT
This implementation correctly distributes periods across the week
"""

from typing import List, Dict, Tuple, Optional, Set
import time
from ortools.sat.python import cp_model
from ...models_phase1 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry,
    Timetable, TimetableStatus, RoomType, ConstraintType
)


class CSPSolverRobust:
    """
    Robust CSP Solver that correctly handles timetable generation.
    Key improvements:
    - Proper variable indexing to prevent Monday P1 bug
    - Explicit period distribution across days
    - Better constraint propagation
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.model = None
        self.solver = None
        self.assignments = {}
        self.teacher_assignments = {}
        self.room_assignments = {}

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
        Generate timetables using CSP approach with proper period distribution.
        """
        start_time = time.time()

        # Filter active time slots (exclude breaks)
        active_slots = [ts for ts in time_slots if not ts.is_break]

        if not active_slots:
            return [], 0, ["No active time slots available"], None

        if self.debug:
            print(f"[CSP] Starting with {len(classes)} classes, {len(subjects)} subjects, {len(active_slots)} slots")

        # Build teacher-subject mapping
        teacher_subjects = self._build_teacher_subject_map(teachers, subjects)

        # Calculate periods required
        periods_required = self._calculate_periods_required(classes, subjects)

        # Create and solve model
        solutions = []
        for attempt in range(num_solutions * 2):  # Try more times to get enough solutions
            if self.debug:
                print(f"\n[CSP] Attempt {attempt + 1}")

            # Create fresh model for each attempt
            self.model = cp_model.CpModel()
            self.assignments = {}
            self.teacher_assignments = {}
            self.room_assignments = {}

            # Create variables
            self._create_variables(
                classes, subjects, teachers, active_slots, rooms,
                periods_required, teacher_subjects
            )

            # Add constraints
            self._add_constraints(
                classes, subjects, teachers, active_slots, rooms,
                periods_required, teacher_subjects, constraints
            )

            # Add objectives for better distribution
            self._add_objectives(classes, subjects, active_slots)

            # Solve
            self.solver = cp_model.CpSolver()
            self.solver.parameters.max_time_in_seconds = 5.0

            # Add randomization for different solutions
            self.solver.parameters.random_seed = attempt * 42

            status = self.solver.Solve(self.model)

            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                solution = self._extract_solution(
                    classes, subjects, teachers, active_slots, rooms,
                    periods_required
                )

                # Verify the solution is different from previous ones
                if solution and self._is_unique_solution(solution, solutions):
                    solutions.append(solution)
                    if self.debug:
                        print(f"[CSP] Found solution {len(solutions)} with {len(solution.entries)} entries")

                    if len(solutions) >= num_solutions:
                        break

        generation_time = time.time() - start_time

        if solutions:
            return solutions, generation_time, None, None
        else:
            return [], generation_time, ["Could not find feasible solution"], ["Try relaxing constraints"]

    def _build_teacher_subject_map(self, teachers: List[Teacher], subjects: List[Subject]) -> Dict:
        """Build mapping of subject to qualified teachers."""
        teacher_subjects = {}
        for subject in subjects:
            teacher_subjects[subject.id] = []
            for teacher in teachers:
                if subject.name in teacher.subjects:
                    teacher_subjects[subject.id].append(teacher)
        return teacher_subjects

    def _calculate_periods_required(self, classes: List[Class], subjects: List[Subject]) -> Dict:
        """Calculate periods required for each class-subject combination."""
        periods_required = {}
        for class_obj in classes:
            for subject in subjects:
                # For now, all subjects get same periods per week
                periods_required[(class_obj.id, subject.id)] = subject.periods_per_week
        return periods_required

    def _create_variables(
        self, classes, subjects, teachers, active_slots, rooms,
        periods_required, teacher_subjects
    ):
        """Create decision variables for the CSP model."""

        # Main assignment variables: for each class-subject-period_instance-slot combination
        for class_obj in classes:
            for subject in subjects:
                num_periods = periods_required.get((class_obj.id, subject.id), 0)
                if num_periods == 0:
                    continue

                for period_num in range(num_periods):
                    for slot in active_slots:
                        # Create a boolean variable for this assignment
                        var_name = f"c{class_obj.id}_s{subject.id}_p{period_num}_t{slot.id}"
                        self.assignments[(class_obj.id, subject.id, period_num, slot.id)] = \
                            self.model.NewBoolVar(var_name)

        # Teacher assignment variables
        for teacher in teachers:
            for slot in active_slots:
                for class_obj in classes:
                    for subject in subjects:
                        if teacher in teacher_subjects.get(subject.id, []):
                            var_name = f"teach_{teacher.id}_c{class_obj.id}_s{subject.id}_t{slot.id}"
                            key = (teacher.id, class_obj.id, subject.id, slot.id)
                            self.teacher_assignments[key] = self.model.NewBoolVar(var_name)

        # Room assignment variables
        for room in rooms:
            for slot in active_slots:
                for class_obj in classes:
                    var_name = f"room_{room.id}_c{class_obj.id}_t{slot.id}"
                    key = (room.id, class_obj.id, slot.id)
                    self.room_assignments[key] = self.model.NewBoolVar(var_name)

    def _add_constraints(
        self, classes, subjects, teachers, active_slots, rooms,
        periods_required, teacher_subjects, constraints
    ):
        """Add all constraints to the model."""

        # CONSTRAINT 1: Each period instance must be scheduled exactly once
        for class_obj in classes:
            for subject in subjects:
                num_periods = periods_required.get((class_obj.id, subject.id), 0)
                for period_num in range(num_periods):
                    slot_vars = []
                    for slot in active_slots:
                        key = (class_obj.id, subject.id, period_num, slot.id)
                        if key in self.assignments:
                            slot_vars.append(self.assignments[key])

                    if slot_vars:
                        # Exactly one slot must be chosen for this period
                        self.model.Add(sum(slot_vars) == 1)

        # CONSTRAINT 2: No class can have multiple subjects at the same time
        for class_obj in classes:
            for slot in active_slots:
                class_at_slot = []
                for subject in subjects:
                    num_periods = periods_required.get((class_obj.id, subject.id), 0)
                    for period_num in range(num_periods):
                        key = (class_obj.id, subject.id, period_num, slot.id)
                        if key in self.assignments:
                            class_at_slot.append(self.assignments[key])

                # At most one subject can be scheduled for this class at this time
                if class_at_slot:
                    self.model.Add(sum(class_at_slot) <= 1)

        # CONSTRAINT 3: Teacher can teach only one class at a time
        for teacher in teachers:
            for slot in active_slots:
                teacher_at_slot = []
                for class_obj in classes:
                    for subject in subjects:
                        if teacher not in teacher_subjects.get(subject.id, []):
                            continue

                        # Check all period instances of this subject
                        num_periods = periods_required.get((class_obj.id, subject.id), 0)
                        for period_num in range(num_periods):
                            assignment_key = (class_obj.id, subject.id, period_num, slot.id)
                            teacher_key = (teacher.id, class_obj.id, subject.id, slot.id)

                            if assignment_key in self.assignments and teacher_key in self.teacher_assignments:
                                # Link assignment to teacher
                                self.model.Add(
                                    self.teacher_assignments[teacher_key] <=
                                    sum(self.assignments[(class_obj.id, subject.id, p, slot.id)]
                                        for p in range(num_periods)
                                        if (class_obj.id, subject.id, p, slot.id) in self.assignments)
                                )
                                teacher_at_slot.append(self.teacher_assignments[teacher_key])

                # Teacher can teach at most one class at this time
                if teacher_at_slot:
                    self.model.Add(sum(teacher_at_slot) <= 1)

        # CONSTRAINT 4: Room can host only one class at a time
        for room in rooms:
            for slot in active_slots:
                room_at_slot = []
                for class_obj in classes:
                    key = (room.id, class_obj.id, slot.id)
                    if key in self.room_assignments:
                        room_at_slot.append(self.room_assignments[key])

                # At most one class in this room at this time
                if room_at_slot:
                    self.model.Add(sum(room_at_slot) <= 1)

        # CONSTRAINT 5: Link assignments to room usage
        for class_obj in classes:
            for slot in active_slots:
                # If any subject is assigned to this class at this slot, a room must be assigned
                subjects_at_slot = []
                for subject in subjects:
                    num_periods = periods_required.get((class_obj.id, subject.id), 0)
                    for period_num in range(num_periods):
                        key = (class_obj.id, subject.id, period_num, slot.id)
                        if key in self.assignments:
                            subjects_at_slot.append(self.assignments[key])

                if subjects_at_slot:
                    # Need exactly one room if any subject is scheduled
                    room_vars = []
                    for room in rooms:
                        key = (room.id, class_obj.id, slot.id)
                        if key in self.room_assignments:
                            room_vars.append(self.room_assignments[key])

                    if room_vars:
                        # If any subject scheduled, exactly one room needed
                        is_scheduled = self.model.NewBoolVar(f"scheduled_{class_obj.id}_{slot.id}")
                        self.model.Add(sum(subjects_at_slot) <= 1)  # At most one subject
                        self.model.Add(is_scheduled == sum(subjects_at_slot))
                        self.model.Add(sum(room_vars) == is_scheduled)

        # CONSTRAINT 6: Room capacity must be respected
        for class_obj in classes:
            for room in rooms:
                if room.capacity < class_obj.student_count:
                    # This room cannot host this class
                    for slot in active_slots:
                        key = (room.id, class_obj.id, slot.id)
                        if key in self.room_assignments:
                            self.model.Add(self.room_assignments[key] == 0)

        # CONSTRAINT 7: Lab requirements
        for class_obj in classes:
            for subject in subjects:
                if subject.requires_lab:
                    # Must use lab rooms
                    for slot in active_slots:
                        num_periods = periods_required.get((class_obj.id, subject.id), 0)
                        for period_num in range(num_periods):
                            assignment_key = (class_obj.id, subject.id, period_num, slot.id)
                            if assignment_key in self.assignments:
                                # If this subject is scheduled, must use a lab room
                                lab_room_vars = []
                                for room in rooms:
                                    if room.type == RoomType.LAB:
                                        room_key = (room.id, class_obj.id, slot.id)
                                        if room_key in self.room_assignments:
                                            lab_room_vars.append(self.room_assignments[room_key])

                                if lab_room_vars:
                                    # If subject scheduled at this slot, must have lab room
                                    self.model.Add(
                                        self.assignments[assignment_key] <= sum(lab_room_vars)
                                    )

        # CONSTRAINT 8: Teacher workload limits
        for teacher in teachers:
            # Daily limit
            days = set(slot.day_of_week for slot in active_slots)
            for day in days:
                day_slots = [s for s in active_slots if s.day_of_week == day]
                daily_periods = []
                for slot in day_slots:
                    for class_obj in classes:
                        for subject in subjects:
                            key = (teacher.id, class_obj.id, subject.id, slot.id)
                            if key in self.teacher_assignments:
                                daily_periods.append(self.teacher_assignments[key])

                if daily_periods:
                    self.model.Add(sum(daily_periods) <= teacher.max_periods_per_day)

            # Weekly limit
            weekly_periods = []
            for slot in active_slots:
                for class_obj in classes:
                    for subject in subjects:
                        key = (teacher.id, class_obj.id, subject.id, slot.id)
                        if key in self.teacher_assignments:
                            weekly_periods.append(self.teacher_assignments[key])

            if weekly_periods:
                self.model.Add(sum(weekly_periods) <= teacher.max_periods_per_week)

    def _add_objectives(self, classes, subjects, active_slots):
        """Add objectives to improve solution quality."""

        # Objective: Spread periods across different days
        day_distribution_penalty = []

        days = sorted(set(slot.day_of_week for slot in active_slots))

        for class_obj in classes:
            for subject in subjects:
                # Count how many periods of this subject are on each day
                for day in days:
                    day_slots = [s for s in active_slots if s.day_of_week == day]
                    periods_on_day = []

                    for slot in day_slots:
                        for period_num in range(subject.periods_per_week):
                            key = (class_obj.id, subject.id, period_num, slot.id)
                            if key in self.assignments:
                                periods_on_day.append(self.assignments[key])

                    if len(periods_on_day) > 1:
                        # Penalize having multiple periods of same subject on same day
                        # Create auxiliary variable for "more than 1 period on this day"
                        excess = self.model.NewIntVar(0, len(periods_on_day),
                                                      f"excess_{class_obj.id}_{subject.id}_{day}")
                        self.model.Add(excess == sum(periods_on_day))

                        # Add quadratic penalty for concentration
                        penalty = self.model.NewIntVar(0, len(periods_on_day) * len(periods_on_day),
                                                       f"penalty_{class_obj.id}_{subject.id}_{day}")
                        self.model.AddMultiplicationEquality(penalty, excess, excess)
                        day_distribution_penalty.append(penalty)

        # Minimize the total penalty
        if day_distribution_penalty:
            self.model.Minimize(sum(day_distribution_penalty))

    def _extract_solution(
        self, classes, subjects, teachers, active_slots, rooms, periods_required
    ) -> Optional[Timetable]:
        """Extract timetable from solved model."""

        if self.solver.StatusName() not in ['OPTIMAL', 'FEASIBLE']:
            return None

        entries = []
        entry_id = 1

        # Extract assignments
        for class_obj in classes:
            for subject in subjects:
                num_periods = periods_required.get((class_obj.id, subject.id), 0)

                for period_num in range(num_periods):
                    for slot in active_slots:
                        key = (class_obj.id, subject.id, period_num, slot.id)
                        if key in self.assignments and self.solver.Value(self.assignments[key]):
                            # This period is scheduled at this slot

                            # Find assigned teacher
                            assigned_teacher = None
                            for teacher in teachers:
                                teacher_key = (teacher.id, class_obj.id, subject.id, slot.id)
                                if teacher_key in self.teacher_assignments:
                                    if self.solver.Value(self.teacher_assignments[teacher_key]):
                                        assigned_teacher = teacher
                                        break

                            # Find assigned room
                            assigned_room = None
                            for room in rooms:
                                room_key = (room.id, class_obj.id, slot.id)
                                if room_key in self.room_assignments:
                                    if self.solver.Value(self.room_assignments[room_key]):
                                        assigned_room = room
                                        break

                            # Create entry if we have all components
                            if assigned_teacher and assigned_room:
                                entry = TimetableEntry(
                                    id=f"entry_{entry_id}",
                                    timetable_id="solution",
                                    class_id=class_obj.id,
                                    subject_id=subject.id,
                                    time_slot_id=slot.id,
                                    teacher_id=assigned_teacher.id,
                                    room_id=assigned_room.id,
                                    day_of_week=slot.day_of_week,
                                    period_number=slot.period_number,
                                    is_fixed=False
                                )
                                entries.append(entry)
                                entry_id += 1

        if self.debug:
            print(f"[CSP] Extracted {len(entries)} entries from solution")
            # Debug: Show distribution across days
            day_counts = {}
            for entry in entries:
                day_counts[entry.day_of_week] = day_counts.get(entry.day_of_week, 0) + 1
            print(f"[CSP] Day distribution: {day_counts}")

        # Create timetable
        timetable = Timetable(
            id="solution",
            school_id="school-001",
            academic_year_id="2024",
            name="Generated Timetable",
            status=TimetableStatus.DRAFT,
            entries=entries
        )

        return timetable

    def _is_unique_solution(self, solution: Timetable, existing_solutions: List[Timetable]) -> bool:
        """Check if solution is sufficiently different from existing ones."""

        if not existing_solutions:
            return True

        # Create a signature for the solution
        new_sig = set()
        for entry in solution.entries:
            new_sig.add((entry.class_id, entry.subject_id, entry.time_slot_id))

        # Check against existing solutions
        for existing in existing_solutions:
            existing_sig = set()
            for entry in existing.entries:
                existing_sig.add((entry.class_id, entry.subject_id, entry.time_slot_id))

            # If more than 80% overlap, consider it too similar
            overlap = len(new_sig & existing_sig)
            if overlap > 0.8 * len(new_sig):
                return False

        return True