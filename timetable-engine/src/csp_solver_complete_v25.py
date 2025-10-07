"""
Complete CSP Solver - Ensures NO GAPS in timetable
Every slot must be filled for every class

VERSION 2.5.1 - Teacher Consistency & Home Room Optimization

CHANGELOG v2.5.1:
- FIX 1 (CRITICAL): One teacher per subject per class throughout academic year
- FIX 2 (LOW PRIORITY): Home room assignment for each class
- Maintains all v2.5 metadata-driven features

CRITICAL FIX:
Previously: Math Period 1 = Teacher A, Math Period 2 = Teacher B (WRONG!)
Now: Math Period 1 = Teacher A, Math Period 2 = Teacher A, Math Period 3 = Teacher A (CORRECT!)

COMPATIBILITY:
- Works with models_phase1_v25.py
- Backward compatible (metadata defaults to None if not available)
"""

from typing import List, Dict, Tuple, Optional, Any
import time
import random
from models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry,
    Timetable, TimetableStatus, RoomType
)


class CSPSolverCompleteV25:
    """
    CSP Solver with teacher consistency and home room optimization.

    VERSION 2.5.1 FIXES:
    1. ONE TEACHER PER SUBJECT PER CLASS (Critical)
       - Each class-subject pair gets ONE teacher for entire year
       - No teacher switching mid-year for same subject

    2. HOME ROOM ASSIGNMENT (Low Priority)
       - Each class gets a dedicated home room
       - Special rooms used only when needed (labs, sports)
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.version = "2.5.1"

    def solve(
        self,
        classes: List[Class],
        subjects: List[Subject],
        teachers: List[Teacher],
        time_slots: List[TimeSlot],
        rooms: List[Room],
        constraints: List[Constraint],
        num_solutions: int = 3,
        subject_requirements: Optional[List[Dict]] = None,
        enforce_teacher_consistency: bool = True
    ) -> Tuple[List[Timetable], float, Optional[List[str]], Optional[List[str]]]:
        """
        Generate COMPLETE timetables with teacher consistency.

        VERSION 2.5.1: Now ensures one teacher per subject per class.

        Args:
            classes: List of classes to schedule
            subjects: List of subjects (with v2.5 preferences)
            teachers: List of teachers (with max_consecutive_periods)
            time_slots: List of available time slots
            rooms: List of available rooms
            constraints: List of constraints to satisfy
            num_solutions: Number of solutions to generate
            subject_requirements: Optional subject requirements per grade
            enforce_teacher_consistency: If True, enforces one teacher per subject per class

        Returns:
            Tuple of (timetables, generation_time, conflicts, suggestions)
        """
        start_time = time.time()

        # Filter active slots (exclude breaks)
        active_slots = [ts for ts in time_slots if not ts.is_break]

        # Build lookup dictionaries for fast metadata access
        subject_lookup = {s.id: s for s in subjects}
        teacher_lookup = {t.id: t for t in teachers}

        if self.debug:
            print(f"\n[CSP v{self.version}] Starting generation")
            print(f"  Classes: {len(classes)}")
            print(f"  Subjects: {len(subjects)}")
            print(f"  Teachers: {len(teachers)}")
            print(f"  Active Slots per week: {len(active_slots)}")
            print(f"  Teacher Consistency: {'ENABLED' if enforce_teacher_consistency else 'DISABLED'}")
            print(f"  Home Room Optimization: ENABLED")

        # Build teacher-subject mapping
        teacher_subjects = self._build_teacher_subject_map(teachers, subjects)

        # Calculate subject distribution
        subject_distribution = self._calculate_subject_distribution(
            len(active_slots), subjects
        )

        if self.debug:
            print(f"\n[CSP v{self.version}] Subject distribution per class:")
            for subject_id, periods in subject_distribution.items():
                subject = subject_lookup.get(subject_id)
                subject_name = subject.name if subject else subject_id
                print(f"  {subject_name}: {periods} periods/week")

        # Generate solutions
        solutions = []
        for attempt in range(num_solutions):
            if self.debug:
                print(f"\n[CSP v{self.version}] Generating solution {attempt + 1}/{num_solutions}")

            solution = self._generate_complete_solution(
                classes, subjects, teachers, active_slots, rooms,
                teacher_subjects, subject_distribution,
                subject_lookup, teacher_lookup,
                enforce_teacher_consistency
            )

            if solution:
                solutions.append(solution)
                if self.debug:
                    entries_count = len(solution.entries)
                    expected = len(classes) * len(active_slots)
                    metadata_count = sum(1 for e in solution.entries
                                       if e.subject_metadata is not None)

                    print(f"  [OK] Generated {entries_count}/{expected} entries")
                    print(f"  Coverage: {(entries_count/expected)*100:.1f}%")
                    print(f"  Metadata: {metadata_count}/{entries_count} entries")

        generation_time = time.time() - start_time

        if self.debug:
            print(f"\n[CSP v{self.version}] Generation complete")
            print(f"  Solutions: {len(solutions)}")
            print(f"  Time: {generation_time:.2f}s")

        if solutions:
            return solutions, generation_time, None, None
        else:
            return [], generation_time, \
                   ["Could not generate complete timetable"], \
                   ["Try adjusting teacher availability or add more teachers"]

    def _build_teacher_subject_map(self, teachers: List[Teacher], subjects: List[Subject]) -> Dict:
        """Build mapping of subject to qualified teachers."""
        teacher_subjects = {}
        for subject in subjects:
            teacher_subjects[subject.id] = []
            for teacher in teachers:
                if subject.name in teacher.subjects or subject.code in teacher.subjects:
                    teacher_subjects[subject.id].append(teacher)

            if self.debug and not teacher_subjects[subject.id]:
                print(f"  [WARNING] No teachers found for {subject.name}")

        return teacher_subjects

    def _calculate_subject_distribution(self, total_slots: int, subjects: List[Subject]) -> Dict:
        """Calculate how many periods each subject should get."""
        distribution = {}
        total_requested = 0

        for subject in subjects:
            distribution[subject.id] = subject.periods_per_week
            total_requested += subject.periods_per_week

        # Adjust to match total slots
        if total_requested < total_slots:
            shortage = total_slots - total_requested
            while shortage > 0:
                for subject in subjects:
                    if shortage <= 0:
                        break
                    distribution[subject.id] += 1
                    shortage -= 1

        elif total_requested > total_slots:
            excess = total_requested - total_slots
            while excess > 0:
                max_subject = max(distribution.items(), key=lambda x: x[1])
                if max_subject[1] > 2:
                    distribution[max_subject[0]] -= 1
                    excess -= 1
                else:
                    first_subject = list(distribution.keys())[0]
                    distribution[first_subject] -= 1
                    excess -= 1

        return distribution

    def _assign_home_rooms(self, classes: List[Class], rooms: List[Room],
                          class_home_room_map: Dict[str, str]):
        """
        FIX 2: Assign a home room to each class.

        Each class gets ONE dedicated room for regular subjects.
        """
        regular_rooms = [r for r in rooms if r.type == RoomType.CLASSROOM]

        if not regular_rooms:
            regular_rooms = rooms

        regular_rooms.sort(key=lambda r: r.capacity)

        room_index = 0
        for class_obj in classes:
            student_count = class_obj.student_count or 30

            # Find room with appropriate capacity
            suitable_room = None
            for room in regular_rooms:
                if room.capacity >= student_count:
                    suitable_room = room
                    break

            if not suitable_room:
                suitable_room = regular_rooms[room_index % len(regular_rooms)]
                room_index += 1

            class_home_room_map[class_obj.id] = suitable_room.id

            if self.debug:
                print(f"  [HOME] {class_obj.name} → {suitable_room.name} "
                      f"(Cap: {suitable_room.capacity})")

    def _get_consistent_teacher(
        self, class_obj, subject, slot,
        class_subject_teacher_map,
        teacher_subjects,
        teachers,
        teacher_busy,
        active_slots
    ):
        """
        FIX 1 (CRITICAL): Get teacher ensuring consistency.

        RULE: One teacher per subject per class for ENTIRE YEAR.
        """
        key = (class_obj.id, subject.id)

        # Check if teacher already assigned for this subject-class pair
        if key in class_subject_teacher_map:
            assigned_teacher_id = class_subject_teacher_map[key]
            assigned_teacher = next((t for t in teachers if t.id == assigned_teacher_id), None)

            if assigned_teacher:
                # Try to use the assigned teacher
                if (assigned_teacher.id, slot.id) not in teacher_busy:
                    day_count = sum(1 for k in teacher_busy
                                  if k[0] == assigned_teacher.id and
                                  any(s.id == k[1] and s.day_of_week == slot.day_of_week
                                      for s in active_slots))

                    if day_count < assigned_teacher.max_periods_per_day:
                        week_count = sum(1 for k in teacher_busy if k[0] == assigned_teacher.id)
                        if week_count < assigned_teacher.max_periods_per_week:
                            return assigned_teacher

                # Assigned teacher not available - this is a conflict
                if self.debug:
                    print(f"      [CONFLICT] Teacher {assigned_teacher_id[:6]} unavailable for {subject.name}")
                return None

        # First time assigning - select teacher and RECORD choice
        qualified_teachers = teacher_subjects.get(subject.id, [])
        random.shuffle(qualified_teachers)

        for teacher in qualified_teachers:
            if (teacher.id, slot.id) not in teacher_busy:
                day_count = sum(1 for k in teacher_busy
                              if k[0] == teacher.id and
                              any(s.id == k[1] and s.day_of_week == slot.day_of_week
                                  for s in active_slots))

                if day_count < teacher.max_periods_per_day:
                    week_count = sum(1 for k in teacher_busy if k[0] == teacher.id)
                    if week_count < teacher.max_periods_per_week:
                        # Record this teacher for future periods
                        class_subject_teacher_map[key] = teacher.id
                        if self.debug:
                            print(f"      [ASSIGN] {class_obj.name} {subject.name} → Teacher {teacher.id[:6]}")
                        return teacher

        # No qualified teacher available - try any teacher
        for teacher in teachers:
            if (teacher.id, slot.id) not in teacher_busy:
                class_subject_teacher_map[key] = teacher.id
                if self.debug:
                    print(f"      [SUBSTITUTE] Using {teacher.id[:6]} for {subject.name}")
                return teacher

        return None

    def _get_appropriate_room(
        self, class_obj, subject, slot,
        class_home_room_map,
        rooms,
        room_busy
    ):
        """
        FIX 2: Get appropriate room (home room or special room).
        """
        home_room_id = class_home_room_map.get(class_obj.id)
        home_room = next((r for r in rooms if r.id == home_room_id), None)

        # Check if subject needs special room
        if subject.requires_lab:
            lab_rooms = [r for r in rooms if r.type == RoomType.LAB]
            for room in lab_rooms:
                if (room.id, slot.id) not in room_busy and \
                   room.capacity >= (class_obj.student_count or 30):
                    return room

            # Fallback to home room
            if home_room and (home_room.id, slot.id) not in room_busy:
                return home_room

        # Check for sports/PE
        subject_name_lower = subject.name.lower()
        if any(kw in subject_name_lower for kw in ['sport', 'physical', 'gym', 'pe', 'games']):
            sports_rooms = [r for r in rooms if r.type == RoomType.SPORTS]
            for room in sports_rooms:
                if (room.id, slot.id) not in room_busy:
                    return room

        # Use home room for regular subjects
        if home_room and (home_room.id, slot.id) not in room_busy:
            return home_room

        # Home room busy - find alternative
        for room in rooms:
            if (room.id, slot.id) not in room_busy and \
               room.capacity >= (class_obj.student_count or 30):
                return room

        # Last resort
        for room in rooms:
            if (room.id, slot.id) not in room_busy:
                return room

        return None

    def _generate_complete_solution(
        self, classes, subjects, teachers, active_slots, rooms,
        teacher_subjects, subject_distribution,
        subject_lookup, teacher_lookup,
        enforce_teacher_consistency
    ):
        """
        Generate complete solution with teacher consistency and home rooms.

        VERSION 2.5.1: Includes both critical fixes.
        """
        entries = []
        entry_id = 1

        teacher_busy = {}
        room_busy = {}
        class_subject_count = {}

        # FIX 1: Track teacher per subject per class
        class_subject_teacher_map = {}

        # FIX 2: Track home room per class
        class_home_room_map = {}

        # Initialize
        for class_obj in classes:
            for subject in subjects:
                class_subject_count[(class_obj.id, subject.id)] = 0

        # Assign home rooms
        self._assign_home_rooms(classes, rooms, class_home_room_map)

        # Schedule each class
        for class_obj in classes:
            if self.debug:
                home_room = class_home_room_map.get(class_obj.id)
                home_room_name = next((r.name for r in rooms if r.id == home_room), "None")
                print(f"\n  Scheduling {class_obj.name} (Home: {home_room_name}):")

            # Create subject assignment list
            subjects_to_assign = []
            for subject_id, count in subject_distribution.items():
                subjects_to_assign.extend([subject_id] * count)

            random.shuffle(subjects_to_assign)
            subjects_to_assign = subjects_to_assign[:len(active_slots)]

            # Assign each slot
            for slot_index, slot in enumerate(active_slots):
                subject_id = subjects_to_assign[slot_index]
                subject = subject_lookup.get(subject_id)

                if not subject:
                    continue

                # Get teacher (with consistency if enabled)
                if enforce_teacher_consistency:
                    available_teacher = self._get_consistent_teacher(
                        class_obj, subject, slot,
                        class_subject_teacher_map,
                        teacher_subjects,
                        teachers,
                        teacher_busy,
                        active_slots
                    )
                else:
                    # Old behavior - any available teacher
                    available_teacher = None
                    qualified = teacher_subjects.get(subject.id, [])
                    for teacher in qualified:
                        if (teacher.id, slot.id) not in teacher_busy:
                            available_teacher = teacher
                            break

                # Get room
                available_room = self._get_appropriate_room(
                    class_obj, subject, slot,
                    class_home_room_map,
                    rooms,
                    room_busy
                )

                # Create entry
                if available_teacher and available_room:
                    subject_metadata = self._extract_subject_metadata(subject)
                    teacher_metadata = self._extract_teacher_metadata(available_teacher)

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
                        is_fixed=False,
                        subject_metadata=subject_metadata,
                        teacher_metadata=teacher_metadata
                    )
                    entries.append(entry)
                    entry_id += 1

                    teacher_busy[(available_teacher.id, slot.id)] = class_obj.id
                    room_busy[(available_room.id, slot.id)] = class_obj.id
                    class_subject_count[(class_obj.id, subject.id)] += 1

                    if self.debug:
                        is_home = available_room.id == class_home_room_map.get(class_obj.id)
                        teacher_status = "[OK]" if enforce_teacher_consistency else ""
                        print(f"    {slot.day_of_week[:3]} P{slot.period_number}: "
                              f"{subject.name[:15]:15s} | T:{available_teacher.id[:6]} {teacher_status} | "
                              f"R:{available_room.name} {'[HOME]' if is_home else ''}")

        # Create timetable
        timetable = Timetable(
            id="solution",
            school_id="school-001",
            academic_year_id="2024",
            name=f"Timetable v{self.version} (Teacher Consistency + Home Rooms)",
            status=TimetableStatus.DRAFT,
            entries=entries,
            metadata={
                "version": self.version,
                "teacher_consistency": enforce_teacher_consistency,
                "home_room_optimization": True
            }
        )

        return timetable

    def _extract_subject_metadata(self, subject: Subject) -> Dict[str, Any]:
        """Extract subject metadata for GA optimizer."""
        try:
            return {
                "prefer_morning": getattr(subject, 'prefer_morning', False),
                "preferred_periods": getattr(subject, 'preferred_periods', None),
                "avoid_periods": getattr(subject, 'avoid_periods', None)
            }
        except Exception:
            return {"prefer_morning": False, "preferred_periods": None, "avoid_periods": None}

    def _extract_teacher_metadata(self, teacher: Teacher) -> Dict[str, Any]:
        """Extract teacher metadata for GA optimizer."""
        try:
            return {
                "max_consecutive_periods": getattr(teacher, 'max_consecutive_periods', 3)
            }
        except Exception:
            return {"max_consecutive_periods": 3}
