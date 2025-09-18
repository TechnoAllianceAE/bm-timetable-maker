"""
Fixed CSP Solver for Timetable Generation - Phase 1
Focuses on core constraint satisfaction without wellness features

## Overview:
This solver uses Google OR-Tools CP-SAT solver to model timetabling as a constraint satisfaction problem.
The problem involves assigning subjects, teachers, and rooms to time slots for each class,
while satisfying various hard constraints (must be satisfied) and soft constraints (preferred).

## Key Concepts:
1. Variables: Boolean variables represent whether a particular assignment happens
2. Constraints: Rules that limit valid combinations of variable values
3. Solution: A complete assignment of all variables that satisfies all constraints

## Variable Structure:
- assignments[(class, subject, period_instance, slot)] = Boolean
  Indicates if a specific period instance of a subject is scheduled in a slot
- teacher_assignments[(class, slot, teacher)] = Boolean
  Indicates if a teacher is assigned to teach a class in a slot
- room_assignments[(class, slot, room)] = Boolean
  Indicates if a room is assigned to a class in a slot
"""
from typing import List, Dict, Tuple, Optional
import time
from ortools.sat.python import cp_model
from .models_phase1 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry,
    Timetable, TimetableStatus, ConstraintType, ConstraintPriority, RoomType
)

class CSPSolverFixed:
    """
    Simplified and fixed CSP Solver for Timetable Generation using OR-Tools.
    """

    def __init__(self):
        self.debug = True

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
        Solve for feasible timetables.
        Returns: (solutions, generation_time, conflicts, suggestions)
        """
        start_time = time.time()

        # Filter out break slots
        # Break slots (lunch, recess) are marked with is_break=True
        # We only schedule classes during active teaching periods
        active_slots = [ts for ts in time_slots if not ts.is_break]

        if self.debug:
            print(f"Solving for: {len(classes)} classes, {len(subjects)} subjects, "
                  f"{len(teachers)} teachers, {len(active_slots)} active slots, {len(rooms)} rooms")

        # Build teacher subject mapping for efficiency
        # This creates a lookup table: subject_id -> [qualified_teacher_ids]
        # Used later to quickly check teacher qualifications
        teacher_subjects = self._build_teacher_subject_map(teachers, subjects)

        # Build subject requirements per class
        # Determines how many periods per week each subject needs for each class
        # Uses subject defaults (periods_per_week) and constraint overrides
        periods_required = self._compute_periods_required(classes, subjects, constraints)

        # Create CSP model
        model = cp_model.CpModel()

        # === VARIABLE CREATION ===
        # The core of CSP: defining decision variables that the solver will assign values to

        # Main assignment variables: For each (class, subject, period_instance, slot)
        # Example: If Math needs 5 periods/week for Class 10A, we create 5 period instances
        # Each instance can be assigned to any valid time slot
        # This prevents the same period from being scheduled multiple times
        assignments = {}

        # Create assignment variables
        for class_obj in classes:
            for subject in subjects:
                num_periods = periods_required.get((class_obj.id, subject.id), 0)
                if num_periods == 0:
                    continue

                # Create variables for each required period
                # IMPORTANT: period_num distinguishes between different instances of the same subject
                # Example: Math period 0, Math period 1, etc. are different class sessions
                for period_num in range(num_periods):
                    for slot in active_slots:
                        # Create a Boolean variable: True if this period instance is scheduled in this slot
                        var_name = f"c{class_obj.id}_s{subject.id}_p{period_num}_t{slot.id}"
                        var = model.NewBoolVar(var_name)
                        assignments[(class_obj.id, subject.id, period_num, slot.id)] = var

        # Teacher assignment variables
        teacher_assignments = {}
        for class_obj in classes:
            for slot in active_slots:
                for teacher in teachers:
                    var_name = f"teacher_c{class_obj.id}_t{slot.id}_teach{teacher.id}"
                    var = model.NewBoolVar(var_name)
                    teacher_assignments[(class_obj.id, slot.id, teacher.id)] = var

        # Room assignment variables
        room_assignments = {}
        for class_obj in classes:
            for slot in active_slots:
                for room in rooms:
                    var_name = f"room_c{class_obj.id}_t{slot.id}_r{room.id}"
                    var = model.NewBoolVar(var_name)
                    room_assignments[(class_obj.id, slot.id, room.id)] = var

        # === CONSTRAINTS ===
        # Constraints define the rules that valid timetables must follow
        # Hard constraints MUST be satisfied (e.g., teacher can't be in two places at once)
        # Soft constraints are preferences (handled through optimization objective)

        # CONSTRAINT 1: Each period instance must be scheduled exactly once
        # This ensures every required period happens, and no period is duplicated
        # Example: If Math has 5 periods, each of the 5 instances must be assigned to exactly one slot
        for class_obj in classes:
            for subject in subjects:
                num_periods = periods_required.get((class_obj.id, subject.id), 0)
                for period_num in range(num_periods):
                    slot_vars = []
                    for slot in active_slots:
                        key = (class_obj.id, subject.id, period_num, slot.id)
                        if key in assignments:
                            slot_vars.append(assignments[key])
                    if slot_vars:
                        # Exactly one slot for this period instance
                        model.Add(sum(slot_vars) == 1)

        # CONSTRAINT 2: No class double-booking
        # A class cannot have multiple subjects scheduled at the same time
        # This prevents conflicts like Math and Science both scheduled for Class 10A at Monday 9am
        for class_obj in classes:
            for slot in active_slots:
                subject_vars = []
                for subject in subjects:
                    num_periods = periods_required.get((class_obj.id, subject.id), 0)
                    for period_num in range(num_periods):
                        key = (class_obj.id, subject.id, period_num, slot.id)
                        if key in assignments:
                            subject_vars.append(assignments[key])
                if subject_vars:
                    model.Add(sum(subject_vars) <= 1)

        # CONSTRAINT 3: Teacher assignment consistency
        # If a class has a subject scheduled in a slot, exactly one teacher must be assigned
        # If no subject is scheduled, no teacher should be assigned
        for class_obj in classes:
            for slot in active_slots:
                teacher_vars = []
                for teacher in teachers:
                    key = (class_obj.id, slot.id, teacher.id)
                    if key in teacher_assignments:
                        teacher_vars.append(teacher_assignments[key])
                if teacher_vars:
                    # Check if class has any subject in this slot
                    has_class = []
                    for subject in subjects:
                        num_periods = periods_required.get((class_obj.id, subject.id), 0)
                        for period_num in range(num_periods):
                            assign_key = (class_obj.id, subject.id, period_num, slot.id)
                            if assign_key in assignments:
                                has_class.append(assignments[assign_key])

                    if has_class:
                        # If class has a subject, needs exactly one teacher
                        model.Add(sum(teacher_vars) == sum(has_class))

        # CONSTRAINT 4: No teacher double-booking
        # A teacher cannot be assigned to multiple classes at the same time
        # This is a hard physical constraint - teacher can't be in two places at once
        for teacher in teachers:
            for slot in active_slots:
                class_vars = []
                for class_obj in classes:
                    key = (class_obj.id, slot.id, teacher.id)
                    if key in teacher_assignments:
                        class_vars.append(teacher_assignments[key])
                if class_vars:
                    model.Add(sum(class_vars) <= 1)

        # CONSTRAINT 5: Teacher qualification requirement
        # A teacher can only be assigned to teach subjects they are qualified for
        # Uses the teacher.subjects list to check qualifications
        # This is implemented as an implication: If subject X is scheduled, only qualified teachers can be assigned
        for class_obj in classes:
            for slot in active_slots:
                for subject in subjects:
                    # Get all period instances for this subject in this slot
                    subject_instances = []
                    num_periods = periods_required.get((class_obj.id, subject.id), 0)
                    for period_num in range(num_periods):
                        key = (class_obj.id, subject.id, period_num, slot.id)
                        if key in assignments:
                            subject_instances.append(assignments[key])

                    if subject_instances:
                        # If this subject is taught in this slot, teacher must be qualified
                        for teacher in teachers:
                            teacher_key = (class_obj.id, slot.id, teacher.id)
                            if teacher_key in teacher_assignments:
                                # Check if teacher is qualified
                                if subject.name not in teacher.subjects:
                                    # Teacher not qualified, cannot teach when subject is scheduled
                                    for subject_var in subject_instances:
                                        model.AddImplication(subject_var, teacher_assignments[teacher_key].Not())

        # CONSTRAINT 6: Room assignment consistency
        # Similar to teacher assignment - if a class has a subject, it needs exactly one room
        # No room should be assigned if no class is scheduled
        for class_obj in classes:
            for slot in active_slots:
                room_vars = []
                for room in rooms:
                    key = (class_obj.id, slot.id, room.id)
                    if key in room_assignments:
                        room_vars.append(room_assignments[key])
                if room_vars:
                    # Check if class has any subject in this slot
                    has_class = []
                    for subject in subjects:
                        num_periods = periods_required.get((class_obj.id, subject.id), 0)
                        for period_num in range(num_periods):
                            assign_key = (class_obj.id, subject.id, period_num, slot.id)
                            if assign_key in assignments:
                                has_class.append(assignments[assign_key])

                    if has_class:
                        # If class has a subject, needs exactly one room
                        model.Add(sum(room_vars) == sum(has_class))

        # CONSTRAINT 7: No room double-booking
        # A room cannot be used by multiple classes at the same time
        # Prevents physical conflicts of space usage
        for room in rooms:
            for slot in active_slots:
                class_vars = []
                for class_obj in classes:
                    key = (class_obj.id, slot.id, room.id)
                    if key in room_assignments:
                        class_vars.append(room_assignments[key])
                if class_vars:
                    model.Add(sum(class_vars) <= 1)

        # CONSTRAINT 8: Room capacity must be sufficient
        # A class can only be assigned to rooms that can accommodate all students
        # Example: A class of 35 students cannot use a room with capacity 30
        for class_obj in classes:
            for slot in active_slots:
                for room in rooms:
                    key = (class_obj.id, slot.id, room.id)
                    if key in room_assignments and class_obj.student_count:
                        if class_obj.student_count > room.capacity:
                            # This room cannot be used for this class
                            model.Add(room_assignments[key] == 0)

        # CONSTRAINT 9: Special room requirements (Lab/Workshop)
        # Some subjects require specific room types (e.g., Science needs a lab)
        # This constraint ensures lab subjects are only scheduled in lab rooms
        lab_rooms = [r for r in rooms if r.type == RoomType.LAB]
        lab_room_ids = set(r.id for r in lab_rooms)

        for class_obj in classes:
            for slot in active_slots:
                for subject in subjects:
                    if subject.requires_lab:
                        # If subject requires lab, must use lab room
                        subject_instances = []
                        num_periods = periods_required.get((class_obj.id, subject.id), 0)
                        for period_num in range(num_periods):
                            key = (class_obj.id, subject.id, period_num, slot.id)
                            if key in assignments:
                                subject_instances.append(assignments[key])

                        if subject_instances:
                            # If subject is scheduled, must use lab room
                            non_lab_vars = []
                            for room in rooms:
                                if room.id not in lab_room_ids:
                                    room_key = (class_obj.id, slot.id, room.id)
                                    if room_key in room_assignments:
                                        non_lab_vars.append(room_assignments[room_key])

                            if non_lab_vars:
                                for subject_var in subject_instances:
                                    # If subject scheduled, no non-lab room can be used
                                    for non_lab_var in non_lab_vars:
                                        model.AddImplication(subject_var, non_lab_var.Not())

        # CONSTRAINT 10: Teacher workload limits
        # Protects teacher wellbeing by limiting their teaching load
        # - Max periods per day: Prevents exhaustion from too many consecutive classes
        # - Max periods per week: Ensures reasonable total workload
        for teacher in teachers:
            # Max periods per day
            days = {}
            for slot in active_slots:
                day = slot.day_of_week
                if day not in days:
                    days[day] = []
                days[day].append(slot)

            for day, day_slots in days.items():
                day_vars = []
                for slot in day_slots:
                    for class_obj in classes:
                        key = (class_obj.id, slot.id, teacher.id)
                        if key in teacher_assignments:
                            day_vars.append(teacher_assignments[key])
                if day_vars:
                    model.Add(sum(day_vars) <= teacher.max_periods_per_day)

            # Max periods per week
            week_vars = []
            for slot in active_slots:
                for class_obj in classes:
                    key = (class_obj.id, slot.id, teacher.id)
                    if key in teacher_assignments:
                        week_vars.append(teacher_assignments[key])
            if week_vars:
                model.Add(sum(week_vars) <= teacher.max_periods_per_week)

        # === SOLVING PHASE ===
        # Configure the CP-SAT solver with parameters
        # max_time_in_seconds: Prevents infinite solving for complex problems
        # num_search_workers: Parallel search threads for faster solving
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        solver.parameters.num_search_workers = 4

        solutions = []

        # Solution callback to collect multiple solutions
        # OR-Tools can find multiple valid solutions to the same problem
        # We collect several to give users options with different trade-offs
        class SolutionCollector(cp_model.CpSolverSolutionCallback):
            def __init__(self, assignments, teacher_assignments, room_assignments,
                        classes, subjects, teachers, rooms, active_slots, periods_required,
                        limit):
                cp_model.CpSolverSolutionCallback.__init__(self)
                self.assignments = assignments
                self.teacher_assignments = teacher_assignments
                self.room_assignments = room_assignments
                self.classes = classes
                self.subjects = subjects
                self.teachers = teachers
                self.rooms = rooms
                self.active_slots = active_slots
                self.periods_required = periods_required
                self.solutions = []
                self.limit = limit

            def on_solution_callback(self):
                """Called each time the solver finds a valid solution"""
                if len(self.solutions) >= self.limit:
                    self.StopSearch()  # Stop after finding enough solutions
                    return

                # Extract solution from solver's current state
                # We iterate through all variables and check their assigned values
                entries = []
                entry_id = 1

                for class_obj in self.classes:
                    for slot in self.active_slots:
                        # For each class-slot combination, determine:
                        # 1. What subject (if any) is scheduled
                        # 2. Which teacher is assigned
                        # 3. Which room is assigned
                        scheduled_subject = None
                        for subject in self.subjects:
                            num_periods = self.periods_required.get((class_obj.id, subject.id), 0)
                            for period_num in range(num_periods):
                                key = (class_obj.id, subject.id, period_num, slot.id)
                                if key in self.assignments and self.Value(self.assignments[key]):
                                    scheduled_subject = subject
                                    break
                            if scheduled_subject:
                                break

                        if scheduled_subject:
                            # Find assigned teacher
                            assigned_teacher = None
                            for teacher in self.teachers:
                                key = (class_obj.id, slot.id, teacher.id)
                                if key in self.teacher_assignments and self.Value(self.teacher_assignments[key]):
                                    assigned_teacher = teacher
                                    break

                            # Find assigned room
                            assigned_room = None
                            for room in self.rooms:
                                key = (class_obj.id, slot.id, room.id)
                                if key in self.room_assignments and self.Value(self.room_assignments[key]):
                                    assigned_room = room
                                    break

                            if assigned_teacher and assigned_room:
                                entry = TimetableEntry(
                                    id=f"entry_{entry_id}",
                                    timetable_id=f"solution_{len(self.solutions)}",
                                    class_id=class_obj.id,
                                    subject_id=scheduled_subject.id,
                                    teacher_id=assigned_teacher.id,
                                    room_id=assigned_room.id,
                                    time_slot_id=slot.id,
                                    day_of_week=slot.day_of_week,
                                    period_number=slot.period_number,
                                    is_fixed=False
                                )
                                entries.append(entry)
                                entry_id += 1

                timetable = Timetable(
                    id=f"solution_{len(self.solutions)}",
                    school_id=self.classes[0].school_id if self.classes else "school-001",
                    academic_year_id="2024",
                    name=f"Timetable Solution {len(self.solutions) + 1}",
                    status=TimetableStatus.DRAFT,
                    entries=entries
                )

                self.solutions.append(timetable)
                print(f"Found solution {len(self.solutions)} with {len(entries)} entries")

        # Create and run solver with callback
        collector = SolutionCollector(
            assignments, teacher_assignments, room_assignments,
            classes, subjects, teachers, rooms, active_slots, periods_required,
            num_solutions
        )

        status = solver.Solve(model, collector)

        generation_time = time.time() - start_time

        # === RESULT PROCESSING ===
        if collector.solutions:
            # Success! Return the found solutions
            return collector.solutions, generation_time, None, None
        else:
            # No solution found - determine why and provide helpful feedback
            if status == cp_model.INFEASIBLE:
                conflicts = ["Problem is infeasible - constraints cannot be satisfied"]
                suggestions = [
                    "Reduce the number of required periods for some subjects",
                    "Add more teachers or rooms",
                    "Increase teacher availability",
                    "Check if there are enough time slots for all classes"
                ]
            else:
                conflicts = ["No solution found within time limit"]
                suggestions = ["Increase timeout", "Relax some constraints"]

            return [], generation_time, conflicts, suggestions

    def _build_teacher_subject_map(self, teachers: List[Teacher], subjects: List[Subject]) -> Dict[str, List[str]]:
        """
        Build mapping of subject IDs to qualified teacher IDs.

        This preprocessing step creates a quick lookup table to find
        which teachers can teach each subject. This avoids repeated
        iterations during constraint creation.

        Returns:
            Dict mapping subject_id -> [list of qualified teacher_ids]
        """
        subject_teachers = {}
        for subject in subjects:
            qualified = []
            for teacher in teachers:
                if subject.name in teacher.subjects:
                    qualified.append(teacher.id)
            subject_teachers[subject.id] = qualified
        return subject_teachers

    def _compute_periods_required(
        self,
        classes: List[Class],
        subjects: List[Subject],
        constraints: List[Constraint]
    ) -> Dict[Tuple[str, str], int]:
        """
        Compute required periods per class-subject combination.

        This determines how many periods per week each subject needs for each class.
        The logic follows this priority:
        1. Start with subject's default periods_per_week
        2. Override with MIN_PERIODS_PER_WEEK constraints if specified
        3. Cap with MAX_PERIODS_PER_WEEK constraints if specified

        Returns:
            Dict mapping (class_id, subject_id) -> number of required periods
        """
        periods = {}

        # Default: use subject's periods_per_week for all classes
        for class_obj in classes:
            for subject in subjects:
                periods[(class_obj.id, subject.id)] = subject.periods_per_week

        # Override with constraints if specified
        for constraint in constraints:
            if constraint.type == ConstraintType.MIN_PERIODS_PER_WEEK:
                if constraint.entity_type == "SUBJECT" and constraint.entity_id:
                    min_periods = constraint.parameters.get("min", 0)
                    for class_obj in classes:
                        periods[(class_obj.id, constraint.entity_id)] = max(
                            periods.get((class_obj.id, constraint.entity_id), 0),
                            min_periods
                        )
            elif constraint.type == ConstraintType.MAX_PERIODS_PER_WEEK:
                if constraint.entity_type == "SUBJECT" and constraint.entity_id:
                    max_periods = constraint.parameters.get("max", 10)
                    for class_obj in classes:
                        current = periods.get((class_obj.id, constraint.entity_id), 0)
                        periods[(class_obj.id, constraint.entity_id)] = min(current, max_periods)

        return periods