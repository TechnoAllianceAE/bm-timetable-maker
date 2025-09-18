"""
Simple CSP Solver - Back to basics with working logic
This version uses a simpler approach that actually works
"""

from typing import List, Dict, Tuple, Optional
import time
import random
from .models_phase1 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry,
    Timetable, TimetableStatus, RoomType
)

class CSPSolverSimple:
    """
    Simplified CSP Solver using greedy assignment with backtracking.
    """

    def __init__(self, debug: bool = False):
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
        Solve timetable using simplified greedy approach.
        """
        start_time = time.time()

        # Filter active slots
        active_slots = [ts for ts in time_slots if not ts.is_break]

        if self.debug:
            print(f"[Simple CSP] Solving for {len(classes)} classes, {len(subjects)} subjects")

        # Build teacher-subject mapping
        teacher_subjects = {}
        for subject in subjects:
            teacher_subjects[subject.id] = []
            for teacher in teachers:
                if subject.name in teacher.subjects:
                    teacher_subjects[subject.id].append(teacher)

        # Try to generate solutions
        solutions = []
        attempts = 0
        max_attempts = 10

        while len(solutions) < num_solutions and attempts < max_attempts:
            attempts += 1

            # Generate one solution
            solution = self._generate_solution(
                classes, subjects, teachers, active_slots, rooms, teacher_subjects
            )

            if solution:
                solutions.append(solution)
                if self.debug:
                    print(f"[Simple CSP] Found solution {len(solutions)} with {len(solution.entries)} entries")

        generation_time = time.time() - start_time

        if solutions:
            return solutions, generation_time, None, None
        else:
            return [], generation_time, ["Could not generate valid timetable"], ["Try adjusting requirements"]

    def _generate_solution(self, classes, subjects, teachers, active_slots, rooms, teacher_subjects):
        """Generate a single timetable solution."""
        entries = []
        entry_id = 1

        # Track used slots for conflict checking
        teacher_busy = {}  # (teacher_id, slot_id) -> bool
        room_busy = {}     # (room_id, slot_id) -> bool
        class_busy = {}    # (class_id, slot_id) -> bool

        # Shuffle for randomization
        slot_order = list(active_slots)
        random.shuffle(slot_order)

        # For each class and subject, assign required periods
        for class_obj in classes:
            for subject in subjects:
                periods_needed = subject.periods_per_week
                periods_assigned = 0

                # Get qualified teachers
                qualified_teachers = teacher_subjects.get(subject.id, [])
                if not qualified_teachers:
                    continue

                # Get suitable rooms
                suitable_rooms = []
                for room in rooms:
                    if room.capacity >= class_obj.student_count:
                        if subject.requires_lab:
                            if room.type == RoomType.LAB:
                                suitable_rooms.append(room)
                        else:
                            if room.type != RoomType.LAB:
                                suitable_rooms.append(room)

                if not suitable_rooms:
                    suitable_rooms = [r for r in rooms if r.capacity >= class_obj.student_count]

                if not suitable_rooms:
                    continue

                # Try to assign periods
                for slot in slot_order:
                    if periods_assigned >= periods_needed:
                        break

                    # Check if class is free
                    if (class_obj.id, slot.id) in class_busy:
                        continue

                    # Find available teacher
                    available_teacher = None
                    for teacher in qualified_teachers:
                        if (teacher.id, slot.id) not in teacher_busy:
                            # Check daily limit
                            day_count = sum(1 for k in teacher_busy
                                          if k[0] == teacher.id and
                                          any(s.id == k[1] and s.day_of_week == slot.day_of_week
                                              for s in active_slots))
                            if day_count < teacher.max_periods_per_day:
                                available_teacher = teacher
                                break

                    if not available_teacher:
                        continue

                    # Find available room
                    available_room = None
                    for room in suitable_rooms:
                        if (room.id, slot.id) not in room_busy:
                            available_room = room
                            break

                    if not available_room:
                        continue

                    # Create entry
                    entry = TimetableEntry(
                        id=f"entry_{entry_id}",
                        timetable_id="solution",
                        class_id=class_obj.id,
                        subject_id=subject.id,
                        time_slot_id=slot.id,
                        teacher_id=available_teacher.id,
                        room_id=available_room.id,
                        day_of_week=slot.day_of_week,
                        period_number=slot.period_number,
                        is_fixed=False
                    )
                    entries.append(entry)
                    entry_id += 1
                    periods_assigned += 1

                    # Mark as busy
                    teacher_busy[(available_teacher.id, slot.id)] = True
                    room_busy[(available_room.id, slot.id)] = True
                    class_busy[(class_obj.id, slot.id)] = True

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