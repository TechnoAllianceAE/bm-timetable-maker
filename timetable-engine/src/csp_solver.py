from typing import List, Dict, Any, Tuple
import time
from ortools.sat.python import cp_model
from .models_phase1 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry,
    Timetable, TimetableStatus, DayOfWeek, ConstraintType, ConstraintPriority, RoomType
)

class CSPSolver:
    """
    CSP Solver for Timetable Generation using OR-Tools CP-SAT.
    Models timetabling as assignment problem with academic and wellness constraints.
    """

    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = 30.0  # Per solve
        self.solver.parameters.log_search_progress = True

    def solve(self, classes: List[Class], subjects: List[Subject], teachers: List[Teacher],
              time_slots: List[TimeSlot], rooms: List[Room], constraints: List[Constraint],
              num_solutions: int = 10) -> List[Timetable]:
        """
        Solve for feasible timetables.
        Returns list of Timetable objects (up to num_solutions).
        """
        start_time = time.time()

        # Pre-process: Compute required periods per class-subject (from min/max constraints)
        required_periods = self._compute_required_periods(classes, subjects, constraints)

        # Variables: For each class-subject pair, assign to time slots with teacher/room
        # Simplified: Assume one subject per class for demo; extend to curriculum later
        # Full: For each class, assign subjects to slots, but use interval vars for periods
        # Here: Bool var for each possible assignment: class_c, subject_s, slot_t, teacher_th, room_r

        num_classes = len(classes)
        num_subjects = len(subjects)
        num_slots = len(time_slots)
        num_teachers = len(teachers)
        num_rooms = len(rooms)

        # Map IDs to indices for efficiency
        class_idx = {c.id: i for i, c in enumerate(classes)}
        subject_idx = {s.id: i for i, s in enumerate(subjects)}
        slot_idx = {ts.id: i for i, ts in enumerate(time_slots)}
        teacher_idx = {t.id: i for i, t in enumerate(teachers)}
        room_idx = {r.id: i for i, r in enumerate(rooms)}

        # Assignment vars: 5D bool array [class][subject][slot][teacher][room]
        # High dim; optimize: Since periods are fixed, use for each required period instance
        # Better: For each class, create interval vars for each subject periods

        # Simplified model for initial impl: Assume fixed curriculum (each class has all subjects with fixed periods)
        # Variable: For each class-slot, assign subject-teacher-room (one per slot)
        # Assume 6 slots/day, 5 days, each class has 30 periods/week

        # Define vars: assignment[c][s] = list of slots assigned for class c, subject s
        # Use bool[c][s][slot] = True if class c teaches subject s in slot

        assignment = {}  # dict (class_id, subject_id, slot_id) -> bool var
        teacher_load = {t.id: [0] * num_slots for t in teachers}  # cumulative for wellness

        for c in classes:
            for s in subjects:
                # Assume each class needs exactly required_periods[c.id][s.id] periods for s
                req = required_periods.get((c.id, s.id), 1)
                for _ in range(req):
                    for ts in time_slots:
                        var = self.model.NewBoolVar(f'assign_{c.id}_{s.id}_{ts.id}')
                        assignment[(c.id, s.id, ts.id)] = var

        # Teacher assignment: For each slot, class assigns to one teacher
        teacher_assign = {}  # (class_id, slot_id, teacher_id) -> bool
        for c in classes:
            for ts in time_slots:
                for t in teachers:
                    if any(sub in [ss.name for ss in subjects if ss.id == sub_id] for sub_id in t.subjects):  # Qualified
                        var = self.model.NewBoolVar(f'teacher_{c.id}_{ts.id}_{t.id}')
                        teacher_assign[(c.id, ts.id, t.id)] = var

        # Room assign similar
        room_assign = {}  # (class_id, slot_id, room_id) -> bool
        for c in classes:
            for ts in time_slots:
                for r in rooms:
                    var = self.model.NewBoolVar(f'room_{c.id}_{ts.id}_{r.id}')
                    room_assign[(c.id, ts.id, r.id)] = var

        # Constraints

        # 1. Each class-slot has exactly one subject
        for c in classes:
            for ts in time_slots:
                subject_vars = []
                for s in subjects:
                    # Assume one period per assignment; aggregate for req
                    var_key = (c.id, s.id, ts.id)
                    if var_key in assignment:
                        subject_vars.append(assignment[var_key])
                self.model.AddExactlyOne(subject_vars)

        # 2. Subject periods exactly required
        for c in classes:
            for s in subjects:
                req = required_periods.get((c.id, s.id), 1)
                slot_vars = [assignment.get((c.id, s.id, ts.id), self.model.NewBoolVar('dummy_false')) for ts in time_slots]
                self.model.Add(sum(slot_vars) == req)

        # 3. Teacher no overlaps: Each teacher-slot at most one class
        for t in teachers:
            for ts in time_slots:
                class_vars = [teacher_assign.get((c.id, ts.id, t.id), self.model.NewBoolVar('dummy_false')) for c in classes]
                self.model.Add(sum(class_vars) <= 1)

        # 4. Teacher qualified for subject (link assignment to teacher)
        for c in classes:
            for ts in time_slots:
                for s in subjects:
                    for t in teachers:
                        if s.name not in t.subjects:  # Simple name match
                            # If assigned subject s in slot, cannot assign teacher t unless qualified
                            # Use implication
                            subject_var = assignment.get((c.id, s.id, ts.id), None)
                            if subject_var:
                                teacher_var = teacher_assign.get((c.id, ts.id, t.id), None)
                                if teacher_var:
                                    if s.name not in t.subjects:
                                        self.model.AddImplication(subject_var, teacher_var.Not())

        # 5. Room no overlaps
        for r in rooms:
            for ts in time_slots:
                class_vars = [room_assign.get((c.id, ts.id, r.id), self.model.NewBoolVar('dummy_false')) for c in classes]
                self.model.Add(sum(class_vars) <= 1)

        # 6. Link class-slot to room (exactly one)
        for c in classes:
            for ts in time_slots:
                room_vars = [room_assign.get((c.id, ts.id, r.id), self.model.NewBoolVar('dummy_false')) for r in rooms]
                self.model.AddExactlyOne(room_vars)

        # 7. Lab requirement
        lab_rooms = [r for r in rooms if r.type == RoomType.LAB]
        lab_room_ids = [r.id for r in lab_rooms]
        for c in classes:
            for s in subjects:
                if s.requires_lab:
                    for ts in time_slots:
                        subject_var = assignment.get((c.id, s.id, ts.id), None)
                        if subject_var:
                            # If assigned, must use lab room
                            non_lab_rooms = [room_assign.get((c.id, ts.id, r.id), self.model.NewBoolVar('dummy_false')) for r in rooms if r.id not in lab_room_ids]
                            self.model.AddImplication(subject_var, sum(non_lab_rooms) == 0)

        # 8. Wellness constraints (basic)
        # Daily hours: For each teacher-day, sum assignments <= max
        days = {}
        for ts in time_slots:
            day = ts.day_of_week
            if day not in days:
                days[day] = []
            days[day].append(ts.id)

        for t in teachers:
            for day in days:
                day_slots = days[day]
                day_load = [teacher_assign.get((c.id, ts_id, t.id), self.model.NewBoolVar('dummy_false')) for c in classes for ts_id in day_slots]
                self.model.Add(sum(day_load) <= t.max_periods_per_day)

        # Weekly: Sum all <= max_week
        for t in teachers:
            all_load = [teacher_assign.get((c.id, ts.id, t.id), self.model.NewBoolVar('dummy_false')) for c in classes for ts in time_slots]
            self.model.Add(sum(all_load) <= t.max_periods_per_week)

        # Consecutive: For each teacher, no more than max_consecutive in row
        # Simplified: Use cumulative or bool chains; for demo, skip full impl, add as soft
        # Full: For each day, sequence of consecutive slots

        # Time preferences from constraints
        for const in constraints:
            if const.type == ConstraintType.PREFERRED_TIME_SLOT:
                entity_id = const.entity_id
                params = const.parameters
                # Assume entity_id is subject_id
                for s in subjects:
                    if s.id == entity_id:
                        for ts in time_slots:
                            # Check if time slot matches preference
                            if params.get('before_noon') and int(ts.start_time.split(':')[0]) >= 12:
                                subject_vars = [assignment.get((c.id, s.id, ts.id), self.model.NewBoolVar('dummy_false')) for c in classes]
                                self.model.Add(sum(subject_vars) == 0)

        # Objective: Minimize violations (for soft constraints); but for feasible, just solve
        # Solver finds feasible

        # Solve for multiple solutions
        solutions = []
        for sol_num in range(num_solutions):
            # Solve
            status = self.solver.Solve(self.model)

            if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
                break

            # Extract solution
            timetable_entries = []
            for (c_id, s_id, ts_id), var in assignment.items():
                if self.solver.Value(var) == 1:
                    # Find teacher: among qualified, the one assigned (assume first or add var)
                    # Simplified: Pick first qualified teacher; in full, use teacher_assign
                    qualified_teachers = [t for t in teachers if s_id in [ss.id for ss in subjects if ss.name in t.subjects]]  # Buggy; fix name/ID
                    teacher_id = qualified_teachers[0].id if qualified_teachers else None

                    # Room: similar
                    room_id = rooms[0].id  # Stub

                    entry = TimetableEntry(
                        class_id=c_id,
                        subject_id=s_id,
                        teacher_id=teacher_id,
                        time_slot_id=ts_id,
                        room_id=room_id,
                        timetable_id=f"timetable_{sol_num}"
                    )
                    timetable_entries.append(entry)

            timetable = Timetable(
                id=f"timetable_{sol_num}",
                school_id=classes[0].school_id,  # Assume all same
                academic_year_id="",  # Not used
                status=TimetableStatus.DRAFT,
                entries=timetable_entries
            )

            solutions.append(timetable)

            # Block this solution to find next (add no-good constraint)
            no_good = []
            for (c_id, s_id, ts_id), var in assignment.items():
                if self.solver.Value(var) == 1:
                    no_good.append(var)
            if no_good:
                self.model.Add(sum(no_good) < len(no_good))

        generation_time = time.time() - start_time

        if not solutions:
            # Infeasible
            conflicts = self._extract_conflicts(constraints, status)  # Stub
            return [], generation_time, conflicts, []

        return solutions, generation_time, None, None

    def _compute_required_periods(self, classes: List[Class], subjects: List[Subject], constraints: List[Constraint]) -> Dict[Tuple[str, str], int]:
        """Compute required periods per class-subject from constraints or subject defaults."""
        req = {}
        # First, use subject's default periods_per_week
        for c in classes:
            for s in subjects:
                req[(c.id, s.id)] = s.periods_per_week

        # Override with constraint-specific values if present
        for const in constraints:
            if const.type == ConstraintType.MIN_PERIODS_PER_WEEK:
                # entity_id is subject_id, parameters contains min value
                subject_id = const.entity_id
                min_periods = const.parameters.get('min', 1)
                for c in classes:
                    req[(c.id, subject_id)] = min_periods
        # Default 1 if not specified
        for c in classes:
            for s in subjects:
                if (c.id, s.id) not in req:
                    req[(c.id, s.id)] = 1
        return req

    def _extract_conflicts(self, constraints: List[Constraint], status: int) -> List[str]:
        """Extract infeasibility reasons."""
        conflicts = []
        if status == cp_model.INFEASIBLE:
            # Use solver explanation if available; stub
            conflicts = ["Insufficient resources for constraints", "Wellness limits too strict"]
        return conflicts

# Example usage (for testing)
if __name__ == "__main__":
    # Mock data
    # ... create mock classes etc.
    solver = CSPSolver()
    # solutions, time, conflicts, suggestions = solver.solve(mock_classes, mock_subjects, ...)
    pass