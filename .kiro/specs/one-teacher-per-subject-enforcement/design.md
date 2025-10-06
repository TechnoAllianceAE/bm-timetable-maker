# Design Document

## Overview

This design implements the "one teacher per subject per class" constraint enforcement in the timetable generation system. The core approach is to pre-assign teachers to (class, subject) pairs before generating the detailed schedule, then consistently use these assignments throughout the generation process.

The implementation spans three layers:
1. **Frontend**: UI already has the checkbox (enabled by default)
2. **Backend**: Passes the constraint flag to Python service
3. **Python CSP Solver**: Enforces the constraint during generation

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Already Complete)                                │
│  - Checkbox: "One teacher per subject per class" ✓ checked │
│  - Sends hardRules.oneTeacherPerSubject = true              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend (Already Passes Flag)                              │
│  - Receives hardRules.oneTeacherPerSubject                  │
│  - Transforms to Python payload                             │
│  - Sends to Python service                                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Python CSP Solver (NEEDS IMPLEMENTATION)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Phase 1: Pre-assign Teachers                          │  │
│  │ - Create class_subject_teacher_map                    │  │
│  │ - For each (class, subject): assign one teacher       │  │
│  │ - Validate teacher availability and qualifications    │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Phase 2: Generate Schedule                            │  │
│  │ - For each period assignment:                         │  │
│  │   * Look up pre-assigned teacher from map             │  │
│  │   * Check teacher availability for this slot          │  │
│  │   * Assign if available, fail if not                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Phase 3: Validation                                   │  │
│  │ - Post-validator already checks teacher consistency   │  │
│  │ - Reports violations if any found                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. CSP Solver Enhancement

**File**: `timetable-engine/src/csp_solver_complete_v25.py`

#### New Data Structure

```python
class_subject_teacher_map: Dict[Tuple[str, str], str]
# Key: (class_id, subject_id)
# Value: teacher_id
```

#### New Method: `_pre_assign_teachers()`

```python
def _pre_assign_teachers(
    self,
    classes: List[Class],
    subjects: List[Subject],
    teachers: List[Teacher],
    teacher_subjects: Dict[str, List[Teacher]],
    enforce_consistency: bool
) -> Dict[Tuple[str, str], str]:
    """
    Pre-assign one teacher to each (class, subject) pair.
    
    Args:
        classes: List of classes
        subjects: List of subjects
        teachers: List of teachers
        teacher_subjects: Mapping of subject_id -> qualified teachers
        enforce_consistency: Whether to enforce one teacher per subject
        
    Returns:
        Dictionary mapping (class_id, subject_id) -> teacher_id
        
    Raises:
        ValueError: If no qualified teacher available for a (class, subject) pair
    """
```

**Algorithm**:
1. For each class:
   - For each subject that class needs:
     - Get list of qualified teachers for that subject
     - Select a teacher who:
       * Is qualified for the subject
       * Has capacity (not over weekly limit)
       * Preferably has fewer assignments (load balancing)
     - Record assignment in map
     - Update teacher's assignment count
2. If no qualified teacher available, raise error with diagnostic info

#### Modified Method: `_generate_complete_solution()`

**Changes**:
1. Accept `class_subject_teacher_map` parameter
2. When assigning a period for (class, subject):
   - Look up pre-assigned teacher from map
   - Check if that specific teacher is available for the time slot
   - If available: assign
   - If not available: try to find alternative slot or report conflict
3. Remove random teacher selection logic

**Before** (current code):
```python
# Find available teacher
available_teacher = None
qualified_teachers = teacher_subjects.get(subject.id, [])
random.shuffle(qualified_teachers)  # Random selection

for teacher in qualified_teachers:
    if (teacher.id, slot.id) not in teacher_busy:
        available_teacher = teacher
        break
```

**After** (new code):
```python
# Get pre-assigned teacher for this (class, subject) pair
assigned_teacher_id = class_subject_teacher_map.get((class_obj.id, subject.id))

if assigned_teacher_id:
    # Use the pre-assigned teacher
    assigned_teacher = teacher_lookup.get(assigned_teacher_id)
    
    # Check if teacher is available at this slot
    if (assigned_teacher.id, slot.id) not in teacher_busy:
        # Check daily and weekly limits
        if self._check_teacher_limits(assigned_teacher, slot, teacher_busy, active_slots):
            available_teacher = assigned_teacher
        else:
            # Teacher over limit - this is a constraint violation
            conflicts.append(f"Teacher {assigned_teacher.name} over limit for {class_obj.name} - {subject.name}")
    else:
        # Teacher busy at this slot - need to reschedule or report conflict
        conflicts.append(f"Teacher {assigned_teacher.name} not available for {class_obj.name} - {subject.name} at {slot.day_of_week} P{slot.period_number}")
else:
    # No pre-assignment (shouldn't happen if pre-assign phase worked)
    # Fall back to any qualified teacher
    qualified_teachers = teacher_subjects.get(subject.id, [])
    for teacher in qualified_teachers:
        if (teacher.id, slot.id) not in teacher_busy:
            available_teacher = teacher
            break
```

### 2. Constraint Handling

**File**: `timetable-engine/src/models_phase1_v25.py`

Check if `GenerateRequest` model already has `one_teacher_per_subject` field in constraints. If not, add it:

```python
class GenerateRequest(BaseModel):
    # ... existing fields ...
    constraints: Optional[List[Dict]] = None
    
    # Check for one_teacher_per_subject in constraints list
```

### 3. Main API Handler

**File**: `timetable-engine/main_v25.py`

Modify the `/generate` endpoint to:
1. Extract `one_teacher_per_subject` flag from request
2. Pass it to CSP solver
3. Handle errors related to teacher assignment failures

```python
# Extract constraint flag
enforce_teacher_consistency = False
if request.constraints:
    for constraint in request.constraints:
        if constraint.get('id') == 'one_teacher_per_subject' and constraint.get('enabled'):
            enforce_teacher_consistency = True
            break

# Pass to solver
timetables, gen_time, conflicts, suggestions = csp_solver.solve(
    # ... existing params ...
    enforce_teacher_consistency=enforce_teacher_consistency
)
```

## Data Models

### Class-Subject-Teacher Assignment

```python
@dataclass
class ClassSubjectAssignment:
    """Represents a pre-assigned teacher for a class-subject pair"""
    class_id: str
    class_name: str
    subject_id: str
    subject_name: str
    teacher_id: str
    teacher_name: str
    periods_required: int  # How many periods this subject needs for this class
```

## Error Handling

### Scenario 1: No Qualified Teacher Available

**Error**: Cannot find a qualified teacher for (Class 6A, Mathematics)

**Response**:
```json
{
  "status": "failed",
  "message": "Cannot satisfy teacher consistency constraint",
  "diagnostics": {
    "phase_failed": "teacher_pre_assignment",
    "violations": [
      "No qualified teacher available for Class 6A - Mathematics"
    ],
    "suggestions": [
      "Add more teachers qualified to teach Mathematics",
      "Reduce Mathematics periods for Class 6A",
      "Check teacher availability settings"
    ]
  }
}
```

### Scenario 2: Teacher Over-Allocated

**Error**: Teacher John Smith assigned to too many (class, subject) pairs

**Response**:
```json
{
  "status": "failed",
  "message": "Teacher workload exceeds limits",
  "diagnostics": {
    "phase_failed": "teacher_pre_assignment",
    "violations": [
      "Teacher John Smith: Assigned 45 periods/week (limit: 40)"
    ],
    "suggestions": [
      "Hire additional teachers",
      "Increase max_periods_per_week for John Smith",
      "Reduce subject period requirements"
    ]
  }
}
```

### Scenario 3: Teacher Unavailable at Required Slot

**Error**: Pre-assigned teacher not available when needed

**Response**:
```json
{
  "status": "failed",
  "message": "Cannot schedule all periods with assigned teachers",
  "diagnostics": {
    "phase_failed": "schedule_generation",
    "violations": [
      "Teacher Mary Johnson (Class 7B - English) not available Monday P3"
    ],
    "suggestions": [
      "Adjust teacher availability",
      "Allow flexible teacher assignments (disable one-teacher-per-subject)",
      "Reduce periods per day"
    ]
  }
}
```

## Testing Strategy

### Unit Tests

**File**: `timetable-engine/test_teacher_consistency.py`

```python
def test_teacher_pre_assignment():
    """Test that teachers are correctly pre-assigned to class-subject pairs"""
    # Setup: 2 classes, 3 subjects, 5 teachers
    # Assert: Each (class, subject) has exactly one teacher assigned
    
def test_teacher_consistency_enforcement():
    """Test that same teacher is used for all periods of a subject"""
    # Generate timetable with constraint enabled
    # Assert: For each (class, subject), all entries have same teacher_id
    
def test_no_qualified_teacher_error():
    """Test error handling when no qualified teacher available"""
    # Setup: Class needs Math, but no Math teachers available
    # Assert: Raises ValueError with diagnostic message
    
def test_teacher_overload_error():
    """Test error handling when teacher capacity exceeded"""
    # Setup: 10 classes need Math, only 1 Math teacher with 40 period limit
    # Assert: Raises ValueError with workload diagnostic
    
def test_constraint_disabled():
    """Test that constraint can be disabled"""
    # Generate with enforce_consistency=False
    # Assert: Different teachers may teach same subject to same class
```

### Integration Tests

1. **Frontend to Backend**: Verify checkbox state is passed correctly
2. **Backend to Python**: Verify constraint flag is transformed correctly
3. **End-to-End**: Generate timetable and verify teacher consistency in result

## Performance Considerations

### Time Complexity

- **Pre-assignment Phase**: O(C × S × T) where C=classes, S=subjects, T=teachers
  - For typical school: 30 classes × 10 subjects × 100 teachers = 30,000 operations
  - Expected time: <10ms

- **Generation Phase**: No significant change from current implementation
  - Teacher lookup is O(1) instead of O(T) per assignment
  - Actually faster than current random selection

### Memory Usage

- **Additional Memory**: O(C × S) for class_subject_teacher_map
  - For typical school: 30 classes × 10 subjects = 300 entries
  - Each entry: ~50 bytes (3 UUIDs)
  - Total: ~15KB additional memory
  - Negligible impact

## Backward Compatibility

- **Default Behavior**: Constraint is enabled by default (checkbox checked)
- **Opt-Out**: Users can uncheck the box to allow multiple teachers per subject
- **Existing Timetables**: No impact on already generated timetables
- **API Compatibility**: New constraint is optional, defaults to enabled

## Rollout Plan

### Phase 1: Implementation
1. Implement `_pre_assign_teachers()` method
2. Modify `_generate_complete_solution()` to use pre-assignments
3. Add constraint flag handling in main API

### Phase 2: Testing
1. Run unit tests
2. Test with real school data
3. Verify diagnostics are helpful

### Phase 3: Deployment
1. Deploy to development environment
2. User acceptance testing
3. Deploy to production

## Success Criteria

1. ✅ All periods of a subject in a class are taught by the same teacher
2. ✅ Constraint is enabled by default in UI
3. ✅ Clear error messages when constraint cannot be satisfied
4. ✅ No performance degradation (<1 second generation time maintained)
5. ✅ Post-validator confirms zero teacher consistency violations
