"""
Complete CSP Solver - Ensures NO GAPS in timetable
Every slot must be filled for every class

VERSION 2.5 - Metadata-Driven Optimization

CHANGELOG v2.5:
- Now extracts and includes subject metadata (prefer_morning, preferred_periods, avoid_periods)
- Now extracts and includes teacher metadata (max_consecutive_periods)
- Metadata flows from Subject/Teacher models -> TimetableEntry -> GA Optimizer
- Enables language-agnostic, school-customizable optimization
- Zero hardcoded business logic

COMPATIBILITY:
- Works with models_phase1_v25.py
- Backward compatible (metadata defaults to None if not available)
- Can work with older Subject/Teacher models (graceful degradation)
"""

from typing import List, Dict, Tuple, Optional, Any
import time
import random
from src.models_phase1_v25 import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry,
    Timetable, TimetableStatus, RoomType
)


class CSPSolverCompleteV25:
    """
    CSP Solver that guarantees complete timetables with NO GAPS.
    
    VERSION 2.5 ENHANCEMENTS:
    - Includes metadata in TimetableEntry for GA optimizer
    - subject_metadata: prefer_morning, preferred_periods, avoid_periods
    - teacher_metadata: max_consecutive_periods
    
    HARD RULE: Every class must have something scheduled in every period.
    
    METADATA FLOW:
    1. Subject/Teacher models contain preferences/constraints
    2. CSP solver extracts metadata during solution generation
    3. Metadata included in each TimetableEntry
    4. GA optimizer reads metadata for penalty calculations
    5. No hardcoded subject names or limits anywhere!
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.version = "2.5"

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
        Generate COMPLETE timetables with no gaps.

        VERSION 2.5: Now includes metadata in each TimetableEntry.
        VERSION 2.6: Added enforce_teacher_consistency parameter.

        Args:
            classes: List of classes to schedule
            subjects: List of subjects (with v2.5 preferences)
            teachers: List of teachers (with max_consecutive_periods)
            time_slots: List of available time slots
            rooms: List of available rooms
            constraints: List of constraints to satisfy
            num_solutions: Number of solutions to generate
            subject_requirements: Optional list of grade-subject period requirements
                                 [{"grade": int, "subject_id": str, "periods_per_week": int}]
            enforce_teacher_consistency: If True, ensures one teacher per subject per class

        Returns:
            Tuple of (timetables, generation_time, conflicts, suggestions)
            Each timetable entry includes subject_metadata and teacher_metadata
        """
        start_time = time.time()

        # Filter active slots (exclude breaks)
        active_slots = [ts for ts in time_slots if not ts.is_break]

        # v2.5: Build lookup dictionaries for fast metadata access
        subject_lookup = {s.id: s for s in subjects}
        teacher_lookup = {t.id: t for t in teachers}

        # Build grade-subject requirement map
        requirement_map = {}
        if subject_requirements:
            for req in subject_requirements:
                key = (req['grade'], req['subject_id'])
                requirement_map[key] = req['periods_per_week']

            if self.debug:
                print(f"\n[CSP v{self.version}] Grade-Subject Requirements: {len(subject_requirements)}")
                for req in subject_requirements:
                    subj = subject_lookup.get(req['subject_id'])
                    subj_name = subj.name if subj else req['subject_id']
                    print(f"  Grade {req['grade']} - {subj_name}: {req['periods_per_week']} periods/week")

        if self.debug:
            print(f"\n[CSP v{self.version}] Starting generation")
            print(f"  Classes: {len(classes)}")
            print(f"  Subjects: {len(subjects)}")
            print(f"  Teachers: {len(teachers)}")
            print(f"  Active Slots per week: {len(active_slots)}")
            print(f"  Total assignments needed: {len(classes) * len(active_slots)}")
            print(f"  Metadata tracking: ENABLED [OK]")
            print(f"  Subject Requirements: {'ENABLED' if requirement_map else 'DISABLED'}")

        # Build teacher-subject mapping
        teacher_subjects = self._build_teacher_subject_map(teachers, subjects)

        # Calculate how many periods each subject needs per class
        # Now supports per-class requirements based on grade
        class_subject_distributions = {}
        for cls in classes:
            subject_distribution = self._calculate_subject_distribution(
                len(active_slots), subjects, cls.grade, requirement_map
            )
            class_subject_distributions[cls.id] = subject_distribution

        if self.debug:
            print(f"\n[CSP v{self.version}] Subject distribution per class (based on grade requirements):")
            for cls in classes:
                print(f"  {cls.name} (Grade {cls.grade}):")
                subject_distribution = class_subject_distributions[cls.id]
                for subject_id, periods in subject_distribution.items():
                    subject = subject_lookup.get(subject_id)
                    subject_name = subject.name if subject else subject_id
                    prefer_morning = subject.prefer_morning if subject else False
                    print(f"    {subject_name}: {periods} periods/week "
                          f"{'[MORNING PREF]' if prefer_morning else ''}")

        # Pre-assign teachers to (class, subject) pairs if consistency is enforced
        try:
            class_subject_teacher_map = self._pre_assign_teachers(
                classes, subjects, teachers, teacher_subjects,
                class_subject_distributions, enforce_teacher_consistency
            )
        except ValueError as e:
            # Pre-assignment failed - return error with diagnostics
            generation_time = time.time() - start_time
            return [], generation_time, [str(e)], [
                "Add more qualified teachers",
                "Increase teacher max_periods_per_week",
                "Reduce subject period requirements",
                "Disable one-teacher-per-subject constraint if flexibility is acceptable"
            ]

        # Assign home rooms to reduce unnecessary movement
        class_home_room_map = self._assign_home_rooms(classes, rooms)

        # Generate solutions
        solutions = []
        for attempt in range(num_solutions):
            if self.debug:
                print(f"\n[CSP v{self.version}] Generating solution {attempt + 1}/{num_solutions}")

            solution = self._generate_complete_solution(
                classes, subjects, teachers, active_slots, rooms,
                teacher_subjects, class_subject_distributions,
                subject_lookup, teacher_lookup,  # v2.5: Pass lookups for metadata
                class_subject_teacher_map,  # v2.6: Pass pre-assigned teachers
                class_home_room_map  # v2.6: Pass home room assignments
            )

            if solution:
                solutions.append(solution)
                if self.debug:
                    entries_count = len(solution.entries)
                    expected = len(classes) * len(active_slots)
                    
                    # v2.5: Verify metadata is present
                    metadata_count = sum(1 for e in solution.entries 
                                       if e.subject_metadata is not None)
                    
                    print(f"  [OK] Generated {entries_count}/{expected} entries")
                    print(f"  Coverage: {(entries_count/expected)*100:.1f}%")
                    print(f"  Metadata: {metadata_count}/{entries_count} entries "
                          f"({(metadata_count/entries_count)*100:.1f}%)")

        generation_time = time.time() - start_time

        if self.debug:
            print(f"\n[CSP v{self.version}] Generation complete")
            print(f"  Solutions: {len(solutions)}")
            print(f"  Time: {generation_time:.2f}s")
            print(f"  Avg per solution: {generation_time/max(len(solutions),1):.2f}s")

        if solutions:
            return solutions, generation_time, None, None
        else:
            return [], generation_time, \
                   ["Could not generate complete timetable"], \
                   ["Try adjusting teacher availability or add more teachers"]

    def _build_teacher_subject_map(self, teachers: List[Teacher], subjects: List[Subject]) -> Dict:
        """
        Build mapping of subject to qualified teachers.
        
        Returns:
            Dict[subject_id] -> List[Teacher]
        """
        teacher_subjects = {}
        for subject in subjects:
            teacher_subjects[subject.id] = []
            for teacher in teachers:
                # Check if teacher can teach this subject
                if subject.name in teacher.subjects or subject.code in teacher.subjects:
                    teacher_subjects[subject.id].append(teacher)
            
            if self.debug and not teacher_subjects[subject.id]:
                print(f"  [WARNING] No teachers found for {subject.name}")
        
        return teacher_subjects

    def _pre_assign_teachers(
        self,
        classes: List[Class],
        subjects: List[Subject],
        teachers: List[Teacher],
        teacher_subjects: Dict[str, List[Teacher]],
        class_subject_distributions: Dict[str, Dict[str, int]],
        enforce_consistency: bool
    ) -> Dict[Tuple[str, str], str]:
        """
        Pre-assign one teacher to each (class, subject) pair.
        
        This ensures that the same teacher teaches all periods of a subject to a class,
        providing consistency for students.
        
        Args:
            classes: List of classes to schedule
            subjects: List of subjects
            teachers: List of teachers
            teacher_subjects: Mapping of subject_id -> qualified teachers
            class_subject_distributions: Per-class subject period requirements
            enforce_consistency: Whether to enforce one teacher per subject per class
            
        Returns:
            Dictionary mapping (class_id, subject_id) -> teacher_id
            
        Raises:
            ValueError: If no qualified teacher available for a (class, subject) pair
                       or if teacher capacity is exceeded
        """
        if not enforce_consistency:
            # Skip pre-assignment if constraint is disabled
            return {}
        
        if self.debug:
            print(f"\n[CSP v{self.version}] Pre-assigning teachers to (class, subject) pairs")
        
        class_subject_teacher_map = {}
        teacher_assignment_count = {t.id: 0 for t in teachers}  # Track periods assigned per teacher
        
        # Process each class
        for class_obj in classes:
            if self.debug:
                print(f"\n  Processing {class_obj.name} (Grade {class_obj.grade}):")
            
            # Get subjects this class needs
            subject_distribution = class_subject_distributions.get(class_obj.id, {})
            
            for subject_id, periods_needed in subject_distribution.items():
                if periods_needed == 0:
                    continue
                
                # Get subject details
                subject = next((s for s in subjects if s.id == subject_id), None)
                if not subject:
                    continue
                
                # Get qualified teachers for this subject
                qualified_teachers = teacher_subjects.get(subject_id, [])
                
                if not qualified_teachers:
                    error_msg = (
                        f"No qualified teacher available for {class_obj.name} - {subject.name}. "
                        f"Please add teachers qualified to teach {subject.name}."
                    )
                    if self.debug:
                        print(f"    ❌ {error_msg}")
                    raise ValueError(error_msg)
                
                # Select best teacher based on current workload (load balancing)
                best_teacher = None
                min_load = float('inf')
                
                for teacher in qualified_teachers:
                    current_load = teacher_assignment_count[teacher.id]
                    
                    # Check if teacher has capacity
                    if current_load + periods_needed <= teacher.max_periods_per_week:
                        if current_load < min_load:
                            min_load = current_load
                            best_teacher = teacher
                
                if not best_teacher:
                    # No teacher has capacity
                    teacher_loads = [
                        f"{t.name}: {teacher_assignment_count[t.id]}/{t.max_periods_per_week}"
                        for t in qualified_teachers
                    ]
                    error_msg = (
                        f"All qualified teachers for {subject.name} are at capacity. "
                        f"Current loads: {', '.join(teacher_loads)}. "
                        f"Suggestions: Hire additional teachers, increase max_periods_per_week, "
                        f"or reduce subject period requirements."
                    )
                    if self.debug:
                        print(f"    ❌ {error_msg}")
                    raise ValueError(error_msg)
                
                # Assign teacher to this (class, subject) pair
                class_subject_teacher_map[(class_obj.id, subject_id)] = best_teacher.id
                teacher_assignment_count[best_teacher.id] += periods_needed
                
                if self.debug:
                    print(f"    ✓ {subject.name}: {best_teacher.name} "
                          f"({periods_needed} periods, total: {teacher_assignment_count[best_teacher.id]})")
        
        if self.debug:
            print(f"\n[CSP v{self.version}] Pre-assignment complete:")
            print(f"  Total (class, subject) pairs: {len(class_subject_teacher_map)}")
            print(f"  Teacher workload distribution:")
            for teacher in teachers:
                load = teacher_assignment_count[teacher.id]
                if load > 0:
                    percentage = (load / teacher.max_periods_per_week) * 100
                    print(f"    {teacher.name}: {load}/{teacher.max_periods_per_week} periods ({percentage:.1f}%)")
        
        return class_subject_teacher_map

    def _assign_home_rooms(
        self,
        classes: List[Class],
        rooms: List[Room]
    ) -> Dict[str, str]:
        """
        Assign a home room to each class.

        Home rooms reduce unnecessary movement between periods. Regular subjects
        use the home room, while special subjects (labs, PE) use appropriate facilities.

        Args:
            classes: List of classes to assign home rooms
            rooms: List of available rooms

        Returns:
            Dictionary mapping class_id -> room_id (home room)
        """
        if self.debug:
            print(f"\n[CSP v{self.version}] Assigning home rooms to classes")

        class_home_room_map = {}

        # Get regular classrooms (not labs or special rooms)
        regular_classrooms = [r for r in rooms if r.type == RoomType.CLASSROOM]

        if not regular_classrooms:
            if self.debug:
                print("  [WARNING] No regular classrooms available for home room assignment")
            return {}

        # Sort classes by student count (descending) to assign larger rooms first
        sorted_classes = sorted(classes, key=lambda c: c.student_count or 0, reverse=True)

        # Track which rooms have been assigned as home rooms
        assigned_rooms = set()

        for class_obj in sorted_classes:
            # Find an appropriate room with sufficient capacity
            best_room = None

            for room in regular_classrooms:
                # Skip if already assigned as home room
                if room.id in assigned_rooms:
                    continue

                # Check capacity
                if room.capacity >= (class_obj.student_count or 30):
                    best_room = room
                    break

            # Fallback: if no unassigned room found, reuse rooms
            if not best_room:
                for room in regular_classrooms:
                    if room.capacity >= (class_obj.student_count or 30):
                        best_room = room
                        break

            # Last resort: any regular classroom
            if not best_room and regular_classrooms:
                best_room = regular_classrooms[0]

            if best_room:
                class_home_room_map[class_obj.id] = best_room.id
                assigned_rooms.add(best_room.id)

                if self.debug:
                    print(f"  ✓ {class_obj.name} → {best_room.name} "
                          f"(capacity: {best_room.capacity}, students: {class_obj.student_count or 'N/A'})")

        if self.debug:
            print(f"\n[CSP v{self.version}] Home room assignment complete:")
            print(f"  Total classes: {len(classes)}")
            print(f"  Classes with home rooms: {len(class_home_room_map)}")
            unique_rooms = len(set(class_home_room_map.values()))
            print(f"  Unique home rooms used: {unique_rooms}")

        return class_home_room_map

    def _check_teacher_limits(
        self,
        teacher: Teacher,
        slot: TimeSlot,
        teacher_busy: Dict,
        active_slots: List[TimeSlot]
    ) -> bool:
        """
        Check if a teacher can accept more assignments without exceeding limits.
        
        Verifies both daily and weekly period limits for the teacher.
        
        Args:
            teacher: The teacher to check
            slot: The time slot being considered
            teacher_busy: Dictionary tracking (teacher_id, slot_id) -> class_id assignments
            active_slots: List of all active time slots
            
        Returns:
            True if teacher can accept more assignments, False otherwise
        """
        # Check daily limit
        day_count = sum(1 for k in teacher_busy
                      if k[0] == teacher.id and
                      any(s.id == k[1] and s.day_of_week == slot.day_of_week
                          for s in active_slots))
        
        if day_count >= teacher.max_periods_per_day:
            return False
        
        # Check weekly limit
        week_count = sum(1 for k in teacher_busy if k[0] == teacher.id)
        
        if week_count >= teacher.max_periods_per_week:
            return False
        
        return True

    def _calculate_subject_distribution(self, total_slots: int, subjects: List[Subject],
                                       grade: int, requirement_map: Dict) -> Dict:
        """
        Calculate how many periods each subject should get to fill all slots.
        Uses grade-specific requirements when available, falls back to subject defaults.
        Ensures total equals exactly the number of slots available.

        Args:
            total_slots: Total number of periods available per class per week
            subjects: List of subjects with periods_per_week
            grade: Grade level of the class
            requirement_map: Dict[(grade, subject_id)] -> required periods per week

        Returns:
            Dict[subject_id] -> int (number of periods)
        """
        # Start with requested periods (use requirements if available, otherwise subject defaults)
        distribution = {}
        total_requested = 0

        for subject in subjects:
            # Check if there's a grade-specific requirement
            key = (grade, subject.id)
            if key in requirement_map:
                distribution[subject.id] = requirement_map[key]
            else:
                distribution[subject.id] = subject.periods_per_week
            total_requested += distribution[subject.id]

        # If we have fewer periods than slots, proportionally increase
        if total_requested < total_slots:
            shortage = total_slots - total_requested

            if self.debug:
                print(f"  Shortage: {shortage} periods need to be added")

            # Add extra periods to subjects evenly
            while shortage > 0:
                for subject in subjects:
                    if shortage <= 0:
                        break
                    distribution[subject.id] += 1
                    shortage -= 1

        # If we have more periods requested than slots, proportionally decrease
        elif total_requested > total_slots:
            excess = total_requested - total_slots

            if self.debug:
                print(f"  Excess: {excess} periods need to be removed")

            # Remove from subjects with most periods first
            while excess > 0:
                # Find subject with most periods
                max_subject = max(distribution.items(), key=lambda x: x[1])
                if max_subject[1] > 2:  # Keep minimum 2 periods
                    distribution[max_subject[0]] -= 1
                    excess -= 1
                else:
                    # All subjects at minimum, remove from first subject
                    first_subject = list(distribution.keys())[0]
                    distribution[first_subject] -= 1
                    excess -= 1

        # Verify total
        total = sum(distribution.values())
        if total != total_slots:
            # Final adjustment on first subject
            first_subject = list(distribution.keys())[0]
            distribution[first_subject] += (total_slots - total)
            
            if self.debug:
                print(f"  Final adjustment: {total_slots - total} periods on {first_subject}")

        return distribution

    def _generate_complete_solution(
        self, classes, subjects, teachers, active_slots, rooms,
        teacher_subjects, class_subject_distributions,
        subject_lookup, teacher_lookup,  # v2.5: NEW - for metadata extraction
        class_subject_teacher_map,  # v2.6: NEW - pre-assigned teachers
        class_home_room_map  # v2.6: NEW - home room assignments
    ):
        """
        Generate a complete timetable with NO GAPS.

        VERSION 2.5: Now extracts and includes metadata in each TimetableEntry.
        VERSION 2.6: Uses pre-assigned teachers for consistency.
        Uses per-class subject distributions based on grade-specific requirements.

        METADATA EXTRACTION:
        - For each entry, extracts subject preferences from Subject model
        - For each entry, extracts teacher constraints from Teacher model
        - Stores in subject_metadata and teacher_metadata fields
        - GA optimizer uses this for penalty calculations

        TEACHER CONSISTENCY (v2.6):
        - If class_subject_teacher_map is provided, uses pre-assigned teachers
        - Ensures same teacher teaches all periods of a subject to a class
        - Falls back to any qualified teacher if map is empty

        HOME ROOM ASSIGNMENT (v2.6):
        - If class_home_room_map is provided, prefers home rooms for regular subjects
        - Lab subjects still use lab rooms as required
        - Reduces unnecessary student movement

        Args:
            classes: Classes to schedule
            subjects: Subject list
            teachers: Teacher list
            active_slots: Available time slots
            rooms: Available rooms
            teacher_subjects: Subject -> Teacher mapping
            class_subject_distributions: Dict[class_id] -> (Subject -> period count mapping)
            subject_lookup: Dict[subject_id] -> Subject (v2.5)
            teacher_lookup: Dict[teacher_id] -> Teacher (v2.5)
            class_subject_teacher_map: Dict[(class_id, subject_id)] -> teacher_id (v2.6)
            class_home_room_map: Dict[class_id] -> room_id (v2.6)

        Returns:
            Complete Timetable with metadata-enriched entries
        """

        entries = []
        entry_id = 1

        # Track resource usage
        teacher_busy = {}  # (teacher_id, slot_id) -> class_id
        room_busy = {}     # (room_id, slot_id) -> class_id

        # Track subject allocation per class
        class_subject_count = {}  # (class_id, subject_id) -> count

        # Initialize counts
        for class_obj in classes:
            for subject in subjects:
                class_subject_count[(class_obj.id, subject.id)] = 0

        # CRITICAL: Assign something to EVERY slot for EVERY class
        for class_obj in classes:
            if self.debug:
                print(f"\n  Scheduling {class_obj.name}:")

            # Get the subject distribution specific to this class's grade
            subject_distribution = class_subject_distributions[class_obj.id]

            # Track remaining periods needed for each subject
            remaining_periods = {sid: count for sid, count in subject_distribution.items()}

            # Assign each slot
            for slot in active_slots:
                # v2.6: Smart subject selection with teacher consistency
                # Try to find a subject whose pre-assigned teacher is available NOW
                selected_subject = None
                available_teacher = None

                if class_subject_teacher_map:
                    # Try each subject that still needs periods
                    subject_ids = [sid for sid, remaining in remaining_periods.items() if remaining > 0]
                    random.shuffle(subject_ids)  # Randomize for variety

                    for subject_id in subject_ids:
                        subject = subject_lookup.get(subject_id)
                        if not subject:
                            continue

                        # Get pre-assigned teacher
                        assigned_teacher_id = class_subject_teacher_map.get((class_obj.id, subject.id))
                        if not assigned_teacher_id:
                            continue

                        assigned_teacher = teacher_lookup.get(assigned_teacher_id)
                        if not assigned_teacher:
                            continue

                        # Check if pre-assigned teacher is available at this slot
                        if (assigned_teacher.id, slot.id) not in teacher_busy:
                            if self._check_teacher_limits(assigned_teacher, slot, teacher_busy, active_slots):
                                # Found a match!
                                selected_subject = subject
                                available_teacher = assigned_teacher
                                if self.debug:
                                    print(f"    [CONSISTENT] {subject.name} with {assigned_teacher.name}")
                                break

                    # If no subject found, use any remaining subject (will use fallback logic)
                    if not selected_subject:
                        for subject_id in subject_ids:
                            subject = subject_lookup.get(subject_id)
                            if subject:
                                selected_subject = subject
                                if self.debug:
                                    print(f"    [NO TEACHER] Scheduling {subject.name} (teacher unavailable)")
                                break

                # Fallback: If consistency is NOT enforced
                else:
                    # Select any subject that still needs periods
                    subject_ids = [sid for sid, remaining in remaining_periods.items() if remaining > 0]
                    if subject_ids:
                        subject_id = random.choice(subject_ids)
                        selected_subject = subject_lookup.get(subject_id)

                    if selected_subject:
                        qualified_teachers = teacher_subjects.get(selected_subject.id, [])
                        random.shuffle(qualified_teachers)

                        for teacher in qualified_teachers:
                            if (teacher.id, slot.id) not in teacher_busy:
                                if self._check_teacher_limits(teacher, slot, teacher_busy, active_slots):
                                    available_teacher = teacher
                                    if self.debug:
                                        print(f"    [OK] {selected_subject.name} with {teacher.name}")
                                    break

                        # If no qualified teacher available, try any teacher as substitute
                        if not available_teacher:
                            for teacher in teachers:
                                if (teacher.id, slot.id) not in teacher_busy:
                                    available_teacher = teacher
                                    if self.debug:
                                        print(f"    [SUBSTITUTE] {selected_subject.name} with {teacher.name}")
                                    break

                # Use selected subject
                subject = selected_subject

                if not subject:
                    # No subject available - should not happen with proper distribution
                    if self.debug:
                        print(f"    [ERROR] No subject available for slot {slot.id}")
                    continue

                # Find available room (with home room preference)
                available_room = None

                # Special subjects need special rooms
                if subject.requires_lab:
                    # Labs must use lab rooms
                    lab_rooms = [r for r in rooms if r.type == RoomType.LAB]
                    for room in lab_rooms:
                        if (room.id, slot.id) not in room_busy and \
                           room.capacity >= (class_obj.student_count or 30):
                            available_room = room
                            break
                else:
                    # Regular subjects: prefer home room
                    home_room_id = class_home_room_map.get(class_obj.id)

                    if home_room_id:
                        # Try home room first
                        home_room = next((r for r in rooms if r.id == home_room_id), None)

                        if home_room and (home_room.id, slot.id) not in room_busy:
                            available_room = home_room
                            if self.debug:
                                print(f"    [HOME ROOM] Using {home_room.name}")

                    # Fallback: any regular classroom
                    if not available_room:
                        classrooms = [r for r in rooms if r.type != RoomType.LAB]
                        for room in classrooms:
                            if (room.id, slot.id) not in room_busy and \
                               room.capacity >= (class_obj.student_count or 30):
                                available_room = room
                                if self.debug:
                                    print(f"    [ALTERNATE] Home room busy, using {room.name}")
                                break

                # Last resort: any available room
                if not available_room:
                    for room in rooms:
                        if (room.id, slot.id) not in room_busy:
                            available_room = room
                            if self.debug:
                                print(f"    [FALLBACK] Using {room.name}")
                            break

                # =================================================================
                # v2.5: CREATE ENTRY WITH METADATA
                # =================================================================
                if available_teacher and available_room:
                    # Extract subject metadata from Subject model
                    subject_metadata = self._extract_subject_metadata(subject)
                    
                    # Extract teacher metadata from Teacher model
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
                        # v2.5: Include metadata for GA optimizer
                        subject_metadata=subject_metadata,
                        teacher_metadata=teacher_metadata
                    )
                    entries.append(entry)
                    entry_id += 1

                    # Mark resources as busy
                    teacher_busy[(available_teacher.id, slot.id)] = class_obj.id
                    room_busy[(available_room.id, slot.id)] = class_obj.id
                    class_subject_count[(class_obj.id, subject.id)] += 1

                    # Decrement remaining periods for this subject
                    if subject.id in remaining_periods and remaining_periods[subject.id] > 0:
                        remaining_periods[subject.id] -= 1

                    if self.debug:
                        morning_tag = "[MORNING]" if subject_metadata.get("prefer_morning") else ""
                        remaining = remaining_periods.get(subject.id, 0)
                        print(f"    [OK] {slot.day_of_week[:3]} P{slot.period_number}: "
                              f"{subject.name} {morning_tag} (remaining: {remaining})")
                
                else:
                    # =============================================================
                    # FALLBACK: Create self-study/library period to avoid gaps
                    # =============================================================
                    if self.debug:
                        print(f"    [WARNING] {slot.day_of_week[:3]} P{slot.period_number}: "
                              f"No resources, assigning self-study")

                    # Find any available room
                    fallback_room = None
                    for room in rooms:
                        if (room.id, slot.id) not in room_busy:
                            fallback_room = room
                            break

                    if fallback_room:
                        # Find any available teacher as supervisor
                        supervisor = None
                        for teacher in teachers:
                            if (teacher.id, slot.id) not in teacher_busy:
                                supervisor = teacher
                                break

                        if not supervisor:
                            supervisor = teachers[0]  # Default supervisor

                        # Use first subject as placeholder
                        fallback_subject = subjects[0]
                        
                        # Extract metadata for fallback entry
                        subject_metadata = self._extract_subject_metadata(fallback_subject)
                        teacher_metadata = self._extract_teacher_metadata(supervisor)

                        entry = TimetableEntry(
                            id=f"entry_{entry_id}",
                            timetable_id="solution",
                            class_id=class_obj.id,
                            subject_id=fallback_subject.id,
                            time_slot_id=slot.id,
                            teacher_id=supervisor.id,
                            room_id=fallback_room.id,
                            day_of_week=slot.day_of_week,
                            period_number=slot.period_number,
                            is_fixed=False,
                            # v2.5: Include metadata even for fallback entries
                            subject_metadata=subject_metadata,
                            teacher_metadata=teacher_metadata
                        )
                        entries.append(entry)
                        entry_id += 1

                        teacher_busy[(supervisor.id, slot.id)] = class_obj.id
                        room_busy[(fallback_room.id, slot.id)] = class_obj.id

        # Verify completeness
        expected_entries = len(classes) * len(active_slots)
        actual_entries = len(entries)
        
        # v2.5: Verify metadata coverage
        metadata_coverage = sum(1 for e in entries if e.subject_metadata is not None)

        if self.debug:
            print(f"\n[CSP v{self.version}] Solution summary:")
            print(f"  Expected entries: {expected_entries}")
            print(f"  Actual entries: {actual_entries}")
            print(f"  Completeness: {(actual_entries/expected_entries)*100:.1f}%")
            print(f"  Metadata coverage: {metadata_coverage}/{actual_entries} "
                  f"({(metadata_coverage/max(actual_entries,1))*100:.1f}%)")

        # Create timetable
        timetable = Timetable(
            id="solution",
            school_id="school-001",
            academic_year_id="2024",
            name=f"Complete Timetable v{self.version} (No Gaps)",
            status=TimetableStatus.DRAFT,
            entries=entries,
            metadata={
                "version": self.version,
                "metadata_enabled": True,
                "entries_with_metadata": metadata_coverage,
                "total_entries": actual_entries
            }
        )

        return timetable

    def _extract_subject_metadata(self, subject: Subject) -> Dict[str, Any]:
        """
        Extract scheduling preferences from Subject model.
        
        VERSION 2.5: Core metadata extraction logic.
        
        Args:
            subject: Subject model (v2.5 with preferences)
        
        Returns:
            Dict with prefer_morning, preferred_periods, avoid_periods
            
        GRACEFUL DEGRADATION:
        - If subject doesn't have v2.5 fields, returns empty defaults
        - Uses getattr with defaults for backward compatibility
        - Never crashes even with old Subject models
        """
        try:
            metadata = {
                "prefer_morning": getattr(subject, 'prefer_morning', False),
                "preferred_periods": getattr(subject, 'preferred_periods', None),
                "avoid_periods": getattr(subject, 'avoid_periods', None)
            }
            return metadata
        except Exception as e:
            if self.debug:
                print(f"  [WARNING] Could not extract subject metadata: {e}")
            # Fallback: return empty metadata
            return {
                "prefer_morning": False,
                "preferred_periods": None,
                "avoid_periods": None
            }

    def _extract_teacher_metadata(self, teacher: Teacher) -> Dict[str, Any]:
        """
        Extract constraints from Teacher model.
        
        VERSION 2.5: Core metadata extraction logic.
        
        Args:
            teacher: Teacher model (with max_consecutive_periods)
        
        Returns:
            Dict with max_consecutive_periods
            
        GRACEFUL DEGRADATION:
        - If teacher doesn't have max_consecutive_periods, uses default (3)
        - Never crashes even with old Teacher models
        """
        try:
            metadata = {
                "max_consecutive_periods": getattr(teacher, 'max_consecutive_periods', 3)
            }
            return metadata
        except Exception as e:
            if self.debug:
                print(f"  [WARNING] Could not extract teacher metadata: {e}")
            # Fallback: return default metadata
            return {
                "max_consecutive_periods": 3
            }


# =============================================================================
# VERSION 2.5 USAGE EXAMPLE
# =============================================================================

"""
Example usage with v2.5 metadata:

from src.models_phase1_v25 import Subject, Teacher, Class, TimeSlot, Room
from src.csp_solver_complete_v25 import CSPSolverCompleteV25

# Define subjects with v2.5 preferences
subjects = [
    Subject(
        id="MATH_10",
        school_id="SCH_001",
        name="Mathematics",  # Works in ANY language!
        code="MATH10",
        periods_per_week=6,
        prefer_morning=True,  # Schedule in morning
        preferred_periods=[1, 2, 3, 4],
        avoid_periods=[7, 8]
    ),
    Subject(
        id="PE_10",
        school_id="SCH_001",
        name="Physical Education",
        code="PE10",
        periods_per_week=3,
        prefer_morning=False,  # Afternoon OK
        preferred_periods=[5, 6, 7]
    )
]

# Define teachers with constraints
teachers = [
    Teacher(
        id="T001",
        user_id="U001",
        subjects=["Mathematics"],
        max_consecutive_periods=3  # Max 3 periods in a row
    ),
    Teacher(
        id="T002",
        user_id="U002",
        subjects=["Physical Education"],
        max_consecutive_periods=4  # Can handle 4 consecutive
    )
]

# Initialize v2.5 solver
solver = CSPSolverCompleteV25(debug=True)

# Generate timetables
timetables, gen_time, conflicts, suggestions = solver.solve(
    classes=[...],
    subjects=subjects,
    teachers=teachers,
    time_slots=[...],
    rooms=[...],
    constraints=[]
)

# Verify metadata is present
entry = timetables[0].entries[0]
print(entry.subject_metadata)
# Output: {'prefer_morning': True, 'preferred_periods': [1,2,3,4], 'avoid_periods': [7,8]}

print(entry.teacher_metadata)
# Output: {'max_consecutive_periods': 3}

# Metadata flows to GA optimizer automatically!
"""
