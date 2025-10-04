# v2.5 Integration & Testing Guide

## Issues Fixed

### 1. ✅ GA Optimizer Return Format
**Problem**: GA was returning objects when main.py expected dicts
**Fix**: GA now always returns dicts (same format as input)

### 2. ✅ Object <-> Dict Conversions
**Problem**: Inconsistent conversions between CSP and GA
**Fix**: Explicit conversion in main.py before passing to GA

### 3. ✅ Response Construction
**Problem**: convert_timetable_to_solution didn't handle all cases
**Fix**: Enhanced to handle objects, dicts, and edge cases

---

## Quick Start

### Step 1: Copy Files
```bash
# Create src directory if it doesn't exist
mkdir -p src

# Copy v2.5 files
cp models_phase1_v25.py src/models_phase1_v25.py
cp csp_solver_complete_v25.py src/csp_solver_complete_v25.py
cp ga_optimizer_v25.py src/ga_optimizer_v25.py
cp main_v25.py main_v25.py
```

### Step 2: Run Test Suite
```bash
python test_v25_metadata_flow.py
```

**Expected output:**
```
======================================================================
v2.5 METADATA FLOW TEST SUITE
======================================================================
✓ All v2.5 modules imported successfully

TEST 1: Subject Metadata
✓ Subject.dict() works
✓ Metadata fields present in dict

TEST 2: Teacher Metadata
✓ Teacher metadata field present in dict

TEST 3: TimetableEntry Metadata
✓ Entry metadata preserved in dict conversion

TEST 4: CSP Metadata Extraction
✓ CSP solver completed in 0.45s
✓ Subject metadata extracted
✓ Teacher metadata extracted

TEST 5: GA Optimizer Processing
✓ GA completed
✓ Subject metadata preserved through GA
✓ Teacher metadata preserved through GA

TEST 6: Response Construction
✓ TimetableSolution created
✓ Solution is JSON serializable

======================================================================
✅ ALL TESTS PASSED
======================================================================
```

### Step 3: Run API Server
```bash
python main_v25.py
```

**Expected startup:**
```
======================================================================
🚀 TIMETABLE GENERATION API v2.5 - STARTING UP
======================================================================
✓ Metadata-driven optimization enabled
✓ Language-agnostic preferences
✓ School-customizable configurations
======================================================================

INFO: Started server process [12345]
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test API Endpoint
```bash
curl http://localhost:8000/

# Expected response:
{
    "service": "Timetable Generation API",
    "version": "2.5.0",
    "status": "operational",
    "features": {
        "metadata_driven": true,
        "language_agnostic": true,
        "school_customizable": true
    }
}
```

---

## Troubleshooting

### Issue: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'src.models_phase1_v25'
```

**Fix:**
1. Ensure files are in `src/` directory
2. Check Python path includes current directory
3. Verify file names match exactly (case-sensitive)

```bash
# Verify files exist
ls -la src/
# Should show:
# models_phase1_v25.py
# csp_solver_complete_v25.py
# ga_optimizer_v25.py
```

---

### Issue: Metadata Not Present

**Symptom:**
```
✗ Subject metadata MISSING
✗ Teacher metadata MISSING
```

**Debug:**
```python
# In CSP solver, add debug print
print(f"Subject metadata: {subject_metadata}")
print(f"Teacher metadata: {teacher_metadata}")

# Verify extraction methods are called
```

**Common causes:**
1. Using old models without metadata fields
2. Extraction method not called
3. Metadata lost in conversion

---

### Issue: GA Returns Wrong Format

**Symptom:**
```
TypeError: 'Timetable' object is not subscriptable
```

**Fix:**
GA now always returns dicts. If you see this error:
1. Check GA version (should be v2.5)
2. Verify main.py converts to dicts before GA
3. Check the conversion code in Phase 2

---

### Issue: JSON Serialization Error

**Symptom:**
```
TypeError: Object of type Timetable is not JSON serializable
```

**Fix:**
Ensure convert_timetable_to_solution properly converts:
```python
# Should handle all these cases:
- Pydantic objects with .dict()
- Python objects with __dict__
- Plain dicts
```

---

## Verification Checklist

Before going live, verify:

### ✅ Metadata Flow
- [ ] Subject.prefer_morning field exists
- [ ] Teacher.max_consecutive_periods field exists
- [ ] TimetableEntry.subject_metadata is populated
- [ ] TimetableEntry.teacher_metadata is populated
- [ ] CSP solver extracts metadata
- [ ] GA optimizer reads metadata
- [ ] Metadata preserved through entire pipeline

### ✅ Conversions
- [ ] CSP returns Timetable objects
- [ ] main.py converts to dicts for GA
- [ ] GA processes dicts
- [ ] GA returns dicts
- [ ] convert_timetable_to_solution handles dicts
- [ ] Final response is JSON serializable

### ✅ Performance
- [ ] CSP runs in thread pool (asyncio.to_thread)
- [ ] GA runs in thread pool
- [ ] No blocking operations in async handlers
- [ ] Response time < 10s for typical request

### ✅ Error Handling
- [ ] CSP failure falls back gracefully
- [ ] GA failure falls back to CSP solutions
- [ ] Missing metadata uses defaults
- [ ] Invalid input returns 400 error
- [ ] Server errors return 500 error

---

## A/B Testing Setup

### Run Both Versions Simultaneously

**Terminal 1: Original v1.0**
```bash
# Edit main.py to use port 8000
python main.py
```

**Terminal 2: New v2.5**
```bash
# Edit main_v25.py to use port 8001
# Change: uvicorn.run(app, port=8001)
python main_v25.py
```

### Test Script
```python
import requests
import json
import time

# Test data
test_request = {
    "school_id": "SCH_001",
    "academic_year_id": "2024-25",
    "classes": [...],
    "subjects": [...],
    "teachers": [...],
    "time_slots": [...],
    "rooms": [...],
    "constraints": [],
    "options": 3,
    "weights": {
        "workload_balance": 50.0,
        "gap_minimization": 15.0,
        "time_preferences": 25.0,
        "consecutive_periods": 10.0,
        "morning_period_cutoff": 4
    }
}

# Test v1.0
print("Testing v1.0...")
start = time.time()
response_v1 = requests.post("http://localhost:8000/generate", json=test_request)
time_v1 = time.time() - start
print(f"v1.0: {response_v1.status_code} in {time_v1:.2f}s")

# Test v2.5
print("\nTesting v2.5...")
start = time.time()
response_v2 = requests.post("http://localhost:8001/generate", json=test_request)
time_v2 = time.time() - start
print(f"v2.5: {response_v2.status_code} in {time_v2:.2f}s")

# Compare
print("\n" + "="*50)
print("COMPARISON")
print("="*50)
print(f"Response time: v1.0={time_v1:.2f}s, v2.5={time_v2:.2f}s")
print(f"Speedup: {(time_v1/time_v2):.2f}x")

if response_v2.status_code == 200:
    data_v2 = response_v2.json()
    if 'solutions' in data_v2 and len(data_v2['solutions']) > 0:
        score_v2 = data_v2['solutions'][0]['total_score']
        print(f"v2.5 best score: {score_v2:.2f}")
        
        # Check metadata
        first_entry = data_v2['solutions'][0]['timetable']['entries'][0]
        has_metadata = 'subject_metadata' in first_entry
        print(f"Metadata present: {has_metadata}")
```

---

## Metrics to Track

### Performance Metrics
- **Total generation time** (target: < 10s)
- **CSP time** (typically 40-50% of total)
- **GA time** (typically 50-60% of total)
- **Memory usage** (should be stable)

### Quality Metrics
- **Fitness scores** (higher = better, typical: 800-950)
- **Metadata coverage** (target: 100%)
- **Constraint violations** (target: 0)
- **Gap count** (lower = better)

### Reliability Metrics
- **Success rate** (target: > 95%)
- **Error rate** (target: < 5%)
- **Fallback usage** (when GA fails, falls back to CSP)

---

## Database Migration (When Ready)

### Migration SQL
```sql
-- Add new columns to subjects table
ALTER TABLE subjects 
ADD COLUMN prefer_morning BOOLEAN DEFAULT FALSE,
ADD COLUMN preferred_periods JSONB DEFAULT NULL,
ADD COLUMN avoid_periods JSONB DEFAULT NULL;

-- Add new columns to optimization_weights
ALTER TABLE optimization_weights
ADD COLUMN morning_period_cutoff INTEGER DEFAULT 4,
ADD COLUMN consecutive_periods FLOAT DEFAULT 10.0;

-- Add metadata columns to timetable_entries (if not using JSONB already)
ALTER TABLE timetable_entries
ADD COLUMN subject_metadata JSONB DEFAULT NULL,
ADD COLUMN teacher_metadata JSONB DEFAULT NULL;
```

### Data Migration Script
```python
# Auto-populate prefer_morning for existing subjects
heavy_subjects = ['math', 'physics', 'chemistry', 'science', 'calculus']

for subject in db.query(Subject).all():
    name_lower = subject.name.lower()
    if any(keyword in name_lower for keyword in heavy_subjects):
        subject.prefer_morning = True
        subject.preferred_periods = [1, 2, 3, 4]
        db.commit()
        print(f"✓ Updated {subject.name}")
```

---

## Production Deployment

### Pre-deployment Checklist
- [ ] All tests pass (test_v25_metadata_flow.py)
- [ ] A/B testing shows improvements
- [ ] Database migration tested on staging
- [ ] Performance benchmarks acceptable
- [ ] Error handling verified
- [ ] Logging configured
- [ ] Monitoring setup

### Deployment Steps
1. **Backup database**
2. **Run migrations** (add new columns)
3. **Deploy code** (main_v25.py)
4. **Verify health endpoint** (GET /health)
5. **Run smoke test** (POST /generate with sample data)
6. **Monitor logs** for errors
7. **Check metrics** (response times, success rate)
8. **Gradual rollout** (route 10% traffic, then 50%, then 100%)

### Rollback Plan
If issues occur:
1. Route traffic back to v1.0
2. Investigate errors
3. Fix and redeploy
4. Database columns are backward compatible (defaults set)

---

## Summary

### What's Fixed in This Update
1. ✅ GA optimizer returns consistent dict format
2. ✅ Main.py properly converts CSP objects to dicts
3. ✅ Response construction handles all cases
4. ✅ Test suite verifies entire pipeline

### Files Updated
- `ga_optimizer_v25.py` - Fixed evolve() return format
- `main_v25.py` - Added explicit conversions
- `test_v25_metadata_flow.py` - NEW test suite

### Next Steps
1. Run `python test_v25_metadata_flow.py`
2. If all tests pass → run `python main_v25.py`
3. Test with sample API request
4. If working → proceed with A/B testing
5. If issues → check troubleshooting section

---

## Support

If you encounter issues:

1. **Run test suite first**
   ```bash
   python test_v25_metadata_flow.py
   ```
   This will identify which component is failing

2. **Check logs**
   Look for error messages in console output

3. **Verify file structure**
   ```bash
   tree src/
   # Should show:
   # src/
   # ├── models_phase1_v25.py
   # ├── csp_solver_complete_v25.py
   # └── ga_optimizer_v25.py
   ```

4. **Test components individually**
   - CSP: Run test_csp_metadata_extraction()
   - GA: Run test_ga_processing()
   - Response: Run test_response_construction()

The v2.5 system is now ready for integration and testing!
