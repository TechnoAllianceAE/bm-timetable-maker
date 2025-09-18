"""
CSP Solver V3 - Complete rewrite with proper constraint handling
This version properly distributes classes across time slots
"""

from typing import List, Dict, Tuple, Optional
import time
from ortools.sat.python import cp_model
from .models_phase1 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry,
    Timetable, TimetableStatus, ConstraintType, RoomType
)

class CSPSolverV3:
    """
    Fixed CSP Solver that properly generates timetables.
    """

    def __init__(self, debug: bool = True):
        self.debug = debug

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
        Solve timetable generation properly.
        """
        start_time = time.time()

        # Filter active slots
        active_slots = [ts for ts in time_slots if not ts.is_break]

        if self.debug:
            print(f"[CSP V3] Solving for:")
            print(f"  {len(classes)} classes")
            print(f"  {len(subjects)} subjects")
            print(f"  {len(teachers)} teachers")
            print(f"  {len(active_slots)} time slots")
            print(f"  {len(rooms)} rooms")

        # Build mappings
        teacher_subjects = self._build_teacher_subject_map(teachers, subjects)

        # Create the CP model
        model = cp_model.CpModel()

        # === DECISION VARIABLES ===
        # For each class, subject, and time slot: is this combination scheduled?
        # assignments[(class_id, subject_id, slot_id)] = BoolVar
        assignments = {}

        # Which teacher teaches each assignment
        # teacher_vars[(class_id, subject_id, slot_id)] = IntVar (teacher index)
        teacher_vars = {}

        # Which room is used for each assignment
        # room_vars[(class_id, subject_id, slot_id)] = IntVar (room index)
        room_vars = {}

        # Create variables for all possible assignments
        for class_obj in classes:
            for subject in subjects:
                for slot in active_slots:
                    # Boolean: is this class-subject scheduled at this slot?
                    var_name = f"assign_{class_obj.id}_{subject.id}_{slot.id}"
                    assignments[(class_obj.id, subject.id, slot.id)] = model.NewBoolVar(var_name)

                    # Integer: which teacher (0 = none, 1..n = teacher index)
                    teacher_var_name = f"teacher_{class_obj.id}_{subject.id}_{slot.id}"
                    teacher_vars[(class_obj.id, subject.id, slot.id)] = model.NewIntVar(
                        0, len(teachers), teacher_var_name
                    )

                    # Integer: which room (0 = none, 1..n = room index)
                    room_var_name = f"room_{class_obj.id}_{subject.id}_{slot.id}"
                    room_vars[(class_obj.id, subject.id, slot.id)] = model.NewIntVar(
                        0, len(rooms), room_var_name
                    )

        if self.debug:
            print(f"[CSP V3] Created {len(assignments)} assignment variables")

        # === CONSTRAINT 1: Each subject gets exactly the required periods per week ===
        for class_obj in classes:
            for subject in subjects:
                # Collect all slots for this class-subject
                period_vars = []
                for slot in active_slots:
                    period_vars.append(assignments[(class_obj.id, subject.id, slot.id)])

                # Sum must equal required periods
                required_periods = subject.periods_per_week
                model.Add(sum(period_vars) == required_periods)

        # === CONSTRAINT 2: At most one subject per class per slot ===
        for class_obj in classes:
            for slot in active_slots:
                # Collect all subjects that could be scheduled at this slot
                slot_vars = []
                for subject in subjects:
                    slot_vars.append(assignments[(class_obj.id, subject.id, slot.id)])

                # At most one subject can be scheduled
                model.Add(sum(slot_vars) <= 1)

        # === CONSTRAINT 3: Link assignment to teacher/room ===
        # If assigned, must have teacher and room; if not assigned, no teacher/room
        for class_obj in classes:
            for subject in subjects:
                for slot in active_slots:
                    key = (class_obj.id, subject.id, slot.id)
                    is_assigned = assignments[key]
                    teacher_var = teacher_vars[key]
                    room_var = room_vars[key]

                    # If assigned, teacher and room must be > 0
                    model.Add(teacher_var > 0).OnlyEnforceIf(is_assigned)
                    model.Add(room_var > 0).OnlyEnforceIf(is_assigned)

                    # If not assigned, teacher and room must be 0
                    model.Add(teacher_var == 0).OnlyEnforceIf(is_assigned.Not())
                    model.Add(room_var == 0).OnlyEnforceIf(is_assigned.Not())

        # === CONSTRAINT 4: Teacher must be qualified for subject ===
        for class_obj in classes:
            for subject in subjects:
                qualified_teachers = teacher_subjects.get(subject.id, [])
                qualified_indices = [i+1 for i, t in enumerate(teachers) if t.id in qualified_teachers]

                if not qualified_indices:
                    # No qualified teachers - can't schedule this subject
                    for slot in active_slots:
                        model.Add(assignments[(class_obj.id, subject.id, slot.id)] == 0)
                else:
                    # Teacher must be from qualified list
                    for slot in active_slots:
                        key = (class_obj.id, subject.id, slot.id)
                        is_assigned = assignments[key]
                        teacher_var = teacher_vars[key]

                        # Create allowed tuples: (0) for not assigned, or (qualified_index) for assigned
                        allowed = [(0,)]  # Not assigned
                        allowed.extend([(idx,) for idx in qualified_indices])

                        # Apply constraint
                        model.AddAllowedAssignments([teacher_var], allowed)

        # === CONSTRAINT 5: Teacher can't teach multiple classes at same time ===
        for teacher_idx, teacher in enumerate(teachers):
            for slot in active_slots:
                # Collect all assignments this teacher might have at this slot
                teacher_at_slot = []
                for class_obj in classes:
                    for subject in subjects:
                        key = (class_obj.id, subject.id, slot.id)
                        teacher_var = teacher_vars[key]

                        # Is this teacher teaching this class-subject at this slot?
                        is_teaching = model.NewBoolVar(f"teach_{teacher.id}_{class_obj.id}_{subject.id}_{slot.id}")
                        model.Add(teacher_var == teacher_idx + 1).OnlyEnforceIf(is_teaching)
                        model.Add(teacher_var != teacher_idx + 1).OnlyEnforceIf(is_teaching.Not())
                        teacher_at_slot.append(is_teaching)

                # At most one class per teacher per slot
                model.Add(sum(teacher_at_slot) <= 1)

        # === CONSTRAINT 6: Room can't be used by multiple classes at same time ===
        for room_idx, room in enumerate(rooms):
            for slot in active_slots:
                # Collect all assignments that might use this room at this slot
                room_at_slot = []
                for class_obj in classes:
                    for subject in subjects:
                        key = (class_obj.id, subject.id, slot.id)
                        room_var = room_vars[key]

                        # Is this room being used for this class-subject at this slot?
                        is_using = model.NewBoolVar(f"room_{room.id}_{class_obj.id}_{subject.id}_{slot.id}")
                        model.Add(room_var == room_idx + 1).OnlyEnforceIf(is_using)
                        model.Add(room_var != room_idx + 1).OnlyEnforceIf(is_using.Not())
                        room_at_slot.append(is_using)

                # At most one class per room per slot
                model.Add(sum(room_at_slot) <= 1)

        # === CONSTRAINT 7: Room capacity ===
        for class_obj in classes:
            for subject in subjects:
                for slot in active_slots:
                    key = (class_obj.id, subject.id, slot.id)
                    room_var = room_vars[key]

                    # Only allow rooms with sufficient capacity
                    allowed_rooms = [0]  # 0 = not assigned
                    for room_idx, room in enumerate(rooms):
                        if room.capacity >= class_obj.student_count:
                            # Also check if lab requirement is met
                            if subject.requires_lab:
                                if room.type == RoomType.LAB:
                                    allowed_rooms.append(room_idx + 1)
                            else:
                                allowed_rooms.append(room_idx + 1)

                    model.AddAllowedAssignments([room_var], [(r,) for r in allowed_rooms])

        # === CONSTRAINT 8: Teacher workload limits ===
        for teacher_idx, teacher in enumerate(teachers):
            # Weekly limit
            weekly_load = []
            for slot in active_slots:
                for class_obj in classes:
                    for subject in subjects:
                        key = (class_obj.id, subject.id, slot.id)
                        teacher_var = teacher_vars[key]

                        is_teaching = model.NewBoolVar(f"weekly_{teacher.id}_{class_obj.id}_{subject.id}_{slot.id}")
                        model.Add(teacher_var == teacher_idx + 1).OnlyEnforceIf(is_teaching)
                        model.Add(teacher_var != teacher_idx + 1).OnlyEnforceIf(is_teaching.Not())
                        weekly_load.append(is_teaching)

            model.Add(sum(weekly_load) <= teacher.max_periods_per_week)

            # Daily limit
            days = {}
            for slot in active_slots:
                day = slot.day_of_week
                if day not in days:
                    days[day] = []
                days[day].append(slot)

            for day, day_slots in days.items():
                daily_load = []
                for slot in day_slots:
                    for class_obj in classes:
                        for subject in subjects:
                            key = (class_obj.id, subject.id, slot.id)
                            teacher_var = teacher_vars[key]

                            is_teaching = model.NewBoolVar(f"daily_{teacher.id}_{day}_{class_obj.id}_{subject.id}_{slot.id}")
                            model.Add(teacher_var == teacher_idx + 1).OnlyEnforceIf(is_teaching)
                            model.Add(teacher_var != teacher_idx + 1).OnlyEnforceIf(is_teaching.Not())
                            daily_load.append(is_teaching)

                model.Add(sum(daily_load) <= teacher.max_periods_per_day)

        # === OBJECTIVE: Minimize gaps and distribute evenly ===
        # We want to spread classes throughout the week, not cluster them
        objective_terms = []

        # Penalize empty class-slot combinations (gaps in schedule)
        for class_obj in classes:
            for slot in active_slots:
                slot_empty = model.NewBoolVar(f"empty_{class_obj.id}_{slot.id}")

                # Slot is empty if no subject is scheduled
                subject_vars = []
                for subject in subjects:
                    subject_vars.append(assignments[(class_obj.id, subject.id, slot.id)])

                # If sum is 0, slot is empty
                model.Add(sum(subject_vars) == 0).OnlyEnforceIf(slot_empty)
                model.Add(sum(subject_vars) > 0).OnlyEnforceIf(slot_empty.Not())

                objective_terms.append(slot_empty)

        # Minimize total empty slots
        model.Minimize(sum(objective_terms))

        # === SOLVING ===
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        solver.parameters.num_search_workers = 4

        if self.debug:
            print("[CSP V3] Starting solve...")

        # Solution collector
        class SolutionCollector(cp_model.CpSolverSolutionCallback):
            def __init__(self, assignments, teacher_vars, room_vars,
                        classes, subjects, teachers, rooms, active_slots, limit):
                cp_model.CpSolverSolutionCallback.__init__(self)
                self.assignments = assignments
                self.teacher_vars = teacher_vars
                self.room_vars = room_vars
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

                # Extract assignments that are actually scheduled
                for class_obj in self.classes:
                    for subject in self.subjects:
                        for slot in self.active_slots:
                            key = (class_obj.id, subject.id, slot.id)

                            # Check if this assignment is active
                            if self.Value(self.assignments[key]):
                                teacher_idx = self.Value(self.teacher_vars[key])
                                room_idx = self.Value(self.room_vars[key])

                                if teacher_idx > 0 and room_idx > 0:
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
                print(f"[CSP V3] Found solution {len(self.solutions)} with {len(entries)} entries")

        collector = SolutionCollector(
            assignments, teacher_vars, room_vars,
            classes, subjects, teachers, rooms, active_slots, num_solutions
        )

        status = solver.Solve(model, collector)
        generation_time = time.time() - start_time

        if self.debug:
            print(f"[CSP V3] Solve completed in {generation_time:.2f}s")
            print(f"  Status: {solver.StatusName(status)}")
            print(f"  Solutions found: {len(collector.solutions)}")

        if collector.solutions:
            return collector.solutions, generation_time, None, None
        else:
            if status == cp_model.INFEASIBLE:
                return [], generation_time, ["Problem is infeasible"], ["Check constraints"]
            else:
                return [], generation_time, ["No solution found"], ["Increase timeout"]

    def _build_teacher_subject_map(self, teachers: List[Teacher], subjects: List[Subject]) -> Dict[str, List[str]]:
        """Build mapping of subject IDs to qualified teacher IDs."""
        subject_teachers = {}

        for subject in subjects:
            qualified = []
            for teacher in teachers:
                if subject.name in teacher.subjects:
                    qualified.append(teacher.id)
            subject_teachers[subject.id] = qualified

        return subject_teachers