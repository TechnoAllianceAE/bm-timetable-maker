# WIP: Teacher Consistency Constraint Fix

## Problem Summary
The "one teacher per subject per class" constraint is NOT being enforced in generated timetables.

**Example Issue:**
- Timetable ID: `cmgf13uxy00017tghbtzstdy1`
- Grade 10A English: Taught by 2 different teachers (michael.jackson@school.edu: 4 periods, lisa.thomas@school.edu: 1 period)
- Original example: Grade 10A Social Studies taught by 3 different teachers

**Database Evidence:**
- Query confirmed 89 class-subject pairs with multiple teachers in the old timetable
- Worst case: Grade 12B Science taught by 5 different teachers

## Root Cause Discovery

### The Core Issue
The Python CSP solver's teacher pre-assignment feature is NOT working because **all teacher names are showing as "None"** in the Python service logs.

**Evidence from Python logs:**
```
[CSP v2.5] Pre-assignment complete:
  Total (class, subject) pairs: 300
  Teacher workload distribution:
    None: 12/30 periods (40.0%)
    None: 10/30 periods (33.3%)
    None: 12/30 periods (40.0%)
    ...
```

This prevents the pre-assignment logic from properly identifying and assigning unique teachers to each (class, subject) pair.

## What We've Tried

### 1. ✅ Added `name` field to Python Teacher model
**File:** `timetable-engine/src/models_phase1_v25.py`
**Line:** 79
```python
class Teacher(BaseModel):
    id: str
    user_id: str
    name: Optional[str] = None  # Teacher name for display purposes
    subjects: List[str]
    availability: Optional[Dict[str, Any]] = {}
    max_periods_per_day: int = 6
    max_periods_per_week: int = 30
    max_consecutive_periods: int = 3
```
**Status:** ✅ DONE - Python service accepts this field

### 2. ✅ Added `name` field to backend teacher transformation
**File:** `backend/src/modules/timetables/timetables.service.ts`
**Line:** 213
```typescript
teachers: mappedTeachers.map(teacher => ({
  id: teacher.id,
  user_id: teacher.id,
  name: teacher.name, // Teacher name for display and debugging
  subjects: this.transformTeacherSubjects(teacher.subjects),
  availability: typeof teacher.availability === 'string'
    ? JSON.parse(teacher.availability)
    : teacher.availability,
  max_periods_per_day: teacher.maxPeriodsPerDay,
  max_periods_per_week: teacher.maxPeriodsPerWeek,
  max_consecutive_periods: 3,
})),
```
**Status:** ✅ DONE - Backend recompiled successfully at 4:09 PM

### 3. ⚠️ Added debug logging (COMPILATION FAILED)
**File:** `backend/src/modules/timetables/timetables.service.ts`
**Lines added:**
- Line 66: Check if user relation is loaded
- Line 100: Log first 3 mapped teachers
- Line 254: Log first 3 teachers being sent to Python

**Status:** ⚠️ PENDING - TypeScript compilation failing with 55 errors due to other issues

## Current Status

### Working Backend (Started 4:09 PM)
- **Process ID:** 8004
- **Port:** 5000
- **Status:** ✅ Running successfully
- **Has Fix:** ✅ YES - includes `name: teacher.name` at line 213
- **Location:** Running from bash shell 5c63ed

### Python Service
- **Port:** 8000
- **Status:** ✅ Running
- **Location:** Running from bash shell 779a59
- **Issue:** Still showing all teachers as "None" in logs

### Key Question ❓
**Why are teachers still showing as "None" in Python logs if backend has the fix?**

Possible reasons:
1. The timetable you generated (cmgf1rb3t00xf11p4kf5xraq0) was generated BEFORE the fix
2. Teacher data in mappedTeachers doesn't have names populated
3. User relation is not being loaded from database

## Next Steps

### Step 1: Verify Teacher Data in Database
Check if teachers have user associations:
```bash
sqlite3 /Users/afzal/Projects/react_apps/TimeTableAI/bm-timetable-maker/backend/prisma/dev.db "
SELECT t.id, u.email
FROM teachers t
LEFT JOIN users u ON t.userId = u.id
LIMIT 5;
"
```

### Step 2: Fix TypeScript Compilation Errors
The backend watch mode is failing. Need to:
1. Undo recent logging changes that caused errors
2. OR fix the 55 TypeScript errors
3. Get watch mode compiling again

**Quick fix:** Remove the debug logging additions at lines 66, 100, 254 to get back to working state.

### Step 3: Test with Fresh Timetable Generation
Once backend is compiling:
1. Generate a NEW timetable via frontend
2. Check backend console logs for:
   - "Sample teacher from database" - verify user data is loaded
   - "Teachers with user data: X / 116"
   - "First 3 mapped teachers" - verify names are populated
   - "First 3 teachers being sent to Python" - verify names in payload
3. Check Python console logs for teacher names (not "None")

### Step 4: Verify Pre-Assignment Working
If teacher names are flowing correctly:
1. Check Python logs for actual teacher names in pre-assignment output
2. Generate timetable
3. Verify with database query:
```bash
sqlite3 /Users/afzal/Projects/react_apps/TimeTableAI/bm-timetable-maker/backend/prisma/dev.db "
SELECT
    c.name as class_name,
    s.name as subject_name,
    COUNT(DISTINCT te.teacherId) as teacher_count,
    GROUP_CONCAT(DISTINCT u.email) as teachers
FROM timetable_entries te
JOIN classes c ON te.classId = c.id
JOIN subjects s ON te.subjectId = s.id
JOIN teachers t ON te.teacherId = t.id
JOIN users u ON t.userId = u.id
WHERE te.timetableId = '<NEW_TIMETABLE_ID>'
GROUP BY te.classId, te.subjectId
HAVING COUNT(DISTINCT te.teacherId) > 1
ORDER BY teacher_count DESC;
"
```

## Files Modified

1. ✅ `timetable-engine/src/models_phase1_v25.py` - Added `name` field to Teacher model (line 79)
2. ✅ `backend/src/modules/timetables/timetables.service.ts` - Added `name: teacher.name` (line 213)
3. ⚠️ `backend/src/modules/timetables/timetables.service.ts` - Added debug logging (lines 66, 100, 254) - CAUSING ERRORS

## Important Notes

### Backend Teacher Data Flow
```
Database (teachers + users)
  → teachersService.generate() at line 56-59
  → mappedTeachers at line 66-97 (maps user.email to teacher.name)
  → timetableData.teachers at line 210-221 (sends to Python)
  → Python receives in /generate endpoint
```

### Python Pre-Assignment Logic
**File:** `timetable-engine/src/csp_solver_complete_v25.py`
**Method:** `_pre_assign_teachers()` at lines 222-338
**Key:** Uses `teacher.name` for logging and identification at line 252

**What it does:**
1. For each (class, subject) pair
2. Finds qualified teachers (who teach that subject)
3. Assigns ONE teacher with lowest current workload
4. Stores mapping in `class_subject_teacher_map`
5. Uses this map during schedule generation

### Constraint Extraction
**File:** `timetable-engine/main_v25.py`
**Lines:** 442-463
**Status:** ✅ Working correctly - extracts `ONE_TEACHER_PER_SUBJECT` constraint and passes to solver

## Diagnostic Queries

### Check violations in latest timetable
```bash
sqlite3 /Users/afzal/Projects/react_apps/TimeTableAI/bm-timetable-maker/backend/prisma/dev.db "
SELECT
    c.name,
    c.grade,
    s.name as subject,
    COUNT(DISTINCT te.teacherId) as teacher_count
FROM timetable_entries te
JOIN classes c ON te.classId = c.id
JOIN subjects s ON te.subjectId = s.id
WHERE te.timetableId = 'cmgf1rb3t00xf11p4kf5xraq0'
GROUP BY te.classId, te.subjectId
HAVING COUNT(DISTINCT te.teacherId) > 1
LIMIT 10;
"
```

### Check if backend is running with fix
```bash
lsof -i :5000 | grep LISTEN
# Then check the timestamp of the process
ps -p <PID> -o lstart
```

## Background Processes

All running services:
- Backend (port 5000): Bash shell 5c63ed (PID 8004) - **HAS FIX**
- Python (port 8000): Bash shell 779a59 (PID 13757)
- Frontend (port 3000): Bash shell b41cba

**Note:** Multiple duplicate backend processes exist in other shells but are NOT running successfully. The ONLY working backend is in shell 5c63ed.

## Summary

**What's Working:**
- ✅ Python model accepts name field
- ✅ Backend transformation includes name field
- ✅ Backend running with fix (since 4:09 PM)
- ✅ Constraint extraction working

**What's Broken:**
- ❌ All teachers showing as "None" in Python logs
- ❌ TypeScript compilation failing (recent debug logging changes)

**Unknown:**
- ❓ Are teacher names actually being sent from backend to Python?
- ❓ Is the user relation being loaded from database?
- ❓ Do teachers have associated users in database?

**Next Action:**
Start with Step 1 (verify database) and Step 2 (fix compilation) to determine if the fix is actually working or if there's a deeper issue.
