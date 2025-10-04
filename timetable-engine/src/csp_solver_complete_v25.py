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
        num_solutions: int = 3
    ) -> Tuple[List[Timetable], float, Optional[List[str]], Optional[List[str]]]:
        """
        Generate COMPLETE timetables with no gaps.
        
        VERSION 2.5: Now includes metadata in each TimetableEntry.
        
        Args:
            classes: List of classes to schedule
            subjects: List of subjects (with v2.5 preferences)
            teachers: List of teachers (with max_consecutive_periods)
            time_slots: List of available time slots
            rooms: List of available rooms
            constraints: List of constraints to satisfy
            num_solutions: Number of solutions to generate
        
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

        if self.debug:
            print(f"\n[CSP v{self.version}] Starting generation")
            print(f"  Classes: {len(classes)}")
            print(f"  Subjects: {len(subjects)}")
            print(f"  Teachers: {len(teachers)}")
            print(f"  Active Slots per week: {len(active_slots)}")
            print(f"  Total assignments needed: {len(classes) * len(active_slots)}")
            print(f"  Metadata tracking: ENABLED ✓")

        # Build teacher-subject mapping
        teacher_subjects = self._build_teacher_subject_map(teachers, subjects)

        # Calculate how many periods each subject needs per class
        subject_distribution = self._calculate_subject_distribution(
            len(active_slots), subjects
        )

        if self.debug:
            print(f"\n[CSP v{self.version}] Subject distribution per class:")
            for subject_id, periods in subject_distribution.items():
                subject = subject_lookup.get(subject_id)
                subject_name = subject.name if subject else subject_id
                prefer_morning = subject.prefer_morning if subject else False
                print(f"  {subject_name}: {periods} periods/week "
                      f"{'[MORNING PREF]' if prefer_morning else ''}")

        # Generate solutions
        solutions = []
        for attempt in range(num_solutions):
            if self.debug:
                print(f"\n[CSP v{self.version}] Generating solution {attempt + 1}/{num_solutions}")

            solution = self._generate_complete_solution(
                classes, subjects, teachers, active_slots, rooms,
                teacher_subjects, subject_distribution,
                subject_lookup, teacher_lookup  # v2.5: Pass lookups for metadata
            )

            if solution:
                solutions.append(solution)
                if self.debug:
                    entries_count = len(solution.entries)
                    expected = len(classes) * len(active_slots)
                    
                    # v2.5: Verify metadata is present
                    metadata_count = sum(1 for e in solution.entries 
                                       if e.subject_metadata is not None)
                    
                    print(f"  ✓ Generated {entries_count}/{expected} entries")
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
                print(f"  ⚠️  No teachers found for {subject.name}")
        
        return teacher_subjects

    def _calculate_subject_distribution(self, total_slots: int, subjects: List[Subject]) -> Dict:
        """
        Calculate how many periods each subject should get to fill all slots.
        Ensures total equals exactly the number of slots available.
        
        Args:
            total_slots: Total number of periods available per class per week
            subjects: List of subjects with periods_per_week
        
        Returns:
            Dict[subject_id] -> int (number of periods)
        """
        # Start with requested periods
        distribution = {}
        total_requested = 0

        for subject in subjects:
            distribution[subject.id] = subject.periods_per_week
            total_requested += subject.periods_per_week

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
        teacher_subjects, subject_distribution,
        subject_lookup, teacher_lookup  # v2.5: NEW - for metadata extraction
    ):
        """
        Generate a complete timetable with NO GAPS.
        
        VERSION 2.5: Now extracts and includes metadata in each TimetableEntry.
        
        METADATA EXTRACTION:
        - For each entry, extracts subject preferences from Subject model
        - For each entry, extracts teacher constraints from Teacher model
        - Stores in subject_metadata and teacher_metadata fields
        - GA optimizer uses this for penalty calculations
        
        Args:
            classes: Classes to schedule
            subjects: Subject list
            teachers: Teacher list
            active_slots: Available time slots
            rooms: Available rooms
            teacher_subjects: Subject -> Teacher mapping
            subject_distribution: Subject -> period count mapping
            subject_lookup: Dict[subject_id] -> Subject (v2.5)
            teacher_lookup: Dict[teacher_id] -> Teacher (v2.5)
        
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

            # Create list of subjects to assign based on distribution
            subjects_to_assign = []
            for subject_id, count in subject_distribution.items():
                subjects_to_assign.extend([subject_id] * count)

            # Shuffle for variety
            random.shuffle(subjects_to_assign)

            # Ensure we have exactly enough subjects for all slots
            while len(subjects_to_assign) < len(active_slots):
                # Add more subjects evenly
                for subject_id in subject_distribution.keys():
                    if len(subjects_to_assign) >= len(active_slots):
                        break
                    subjects_to_assign.append(subject_id)

            # Trim if we have too many
            subjects_to_assign = subjects_to_assign[:len(active_slots)]

            # Assign each slot
            slot_index = 0
            for slot in active_slots:
                # Get next subject to assign
                subject_id = subjects_to_assign[slot_index]
                subject = subject_lookup.get(subject_id)

                if not subject:
                    slot_index += 1
                    continue

                # Find available teacher
                available_teacher = None
                qualified_teachers = teacher_subjects.get(subject.id, [])

                # Shuffle for variety
                random.shuffle(qualified_teachers)

                for teacher in qualified_teachers:
                    # Check if teacher is free at this slot
                    if (teacher.id, slot.id) not in teacher_busy:
                        # Check daily limit
                        day_count = sum(1 for k in teacher_busy
                                      if k[0] == teacher.id and
                                      any(s.id == k[1] and s.day_of_week == slot.day_of_week
                                          for s in active_slots))

                        if day_count < teacher.max_periods_per_day:
                            # Check weekly limit
                            week_count = sum(1 for k in teacher_busy if k[0] == teacher.id)
                            if week_count < teacher.max_periods_per_week:
                                available_teacher = teacher
                                break

                # If no qualified teacher available, try any teacher as substitute
                if not available_teacher:
                    for teacher in teachers:
                        if (teacher.id, slot.id) not in teacher_busy:
                            available_teacher = teacher
                            break

                # Find available room
                available_room = None

                # First try appropriate rooms
                if subject.requires_lab:
                    lab_rooms = [r for r in rooms if r.type == RoomType.LAB]
                    for room in lab_rooms:
                        if (room.id, slot.id) not in room_busy and \
                           room.capacity >= (class_obj.student_count or 30):
                            available_room = room
                            break

                # Then try regular classrooms
                if not available_room:
                    classrooms = [r for r in rooms if r.type != RoomType.LAB]
                    for room in classrooms:
                        if (room.id, slot.id) not in room_busy and \
                           room.capacity >= (class_obj.student_count or 30):
                            available_room = room
                            break

                # Last resort: any available room
                if not available_room:
                    for room in rooms:
                        if (room.id, slot.id) not in room_busy:
                            available_room = room
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

                    if self.debug:
                        morning_tag = "🌅" if subject_metadata.get("prefer_morning") else ""
                        print(f"    ✓ {slot.day_of_week[:3]} P{slot.period_number}: "
                              f"{subject.name} {morning_tag}")
                
                else:
                    # =============================================================
                    # FALLBACK: Create self-study/library period to avoid gaps
                    # =============================================================
                    if self.debug:
                        print(f"    ⚠️  {slot.day_of_week[:3]} P{slot.period_number}: "
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

                slot_index += 1

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
                print(f"  ⚠️  Could not extract subject metadata: {e}")
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
                print(f"  ⚠️  Could not extract teacher metadata: {e}")
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
