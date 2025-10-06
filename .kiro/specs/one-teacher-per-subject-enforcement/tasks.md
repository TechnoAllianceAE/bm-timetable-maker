# Implementation Plan

- [x] 1. Implement teacher pre-assignment logic in CSP solver
  - Create `_pre_assign_teachers()` method that assigns one teacher to each (class, subject) pair
  - Implement load balancing to distribute assignments evenly across qualified teachers
  - Add validation to ensure all (class, subject) pairs have qualified teachers available
  - Return dictionary mapping (class_id, subject_id) → teacher_id
  - _Requirements: 1.1, 1.2, 3.1, 3.2_
  - _Status: COMPLETE - Method exists in csp_solver_complete_v25.py lines 195-289_

- [x] 2. Add constraint flag handling in solve() method
  - Add `enforce_teacher_consistency` parameter to `solve()` method signature
  - Call `_pre_assign_teachers()` when constraint is enabled
  - Pass `class_subject_teacher_map` to `_generate_complete_solution()`
  - Skip pre-assignment when constraint is disabled (backward compatibility)
  - _Requirements: 2.1, 2.2, 2.3_
  - _Status: COMPLETE - Parameter exists in solve() method, pre-assignment is called_

- [x] 3. Frontend and backend constraint passing
  - Frontend checkbox exists and is checked by default
  - Backend extracts `oneTeacherPerSubject` from hardRules
  - Backend creates constraint with type 'ONE_TEACHER_PER_SUBJECT'
  - Backend passes constraints array to Python service
  - _Requirements: 2.1, 2.3_
  - _Status: COMPLETE - Verified in frontend/app/admin/timetables/generate/page.tsx and backend/src/modules/timetables/timetables.service.ts_

- [x] 4. Post-validation for teacher consistency
  - Post-validator checks for teacher consistency violations
  - Reports class-subject pairs with multiple teachers
  - Provides metrics on consistent vs inconsistent pairs
  - _Requirements: 1.4, 4.4_
  - _Status: COMPLETE - validate_teacher_consistency() exists in post_validator.py_

- [x] 5. Connect main API to extract constraint flag from request
  - Extract `one_teacher_per_subject` constraint from request.constraints list
  - Pass `enforce_teacher_consistency=True` to CSP solver when constraint is enabled
  - Pass `enforce_teacher_consistency=False` when constraint is disabled or not present
  - _Requirements: 2.3, 4.1_
  - _Current Issue: main_v25.py does not extract this constraint from the request_

- [x] 6. Modify schedule generation to use pre-assigned teachers
  - Update `_generate_complete_solution()` method signature to accept `class_subject_teacher_map` parameter
  - Replace random teacher selection logic with lookup from pre-assignment map
  - For each (class, subject) period, use the pre-assigned teacher from the map
  - Check if pre-assigned teacher is available at the time slot
  - Collect conflicts when pre-assigned teacher is unavailable
  - _Requirements: 1.1, 1.2, 3.3, 3.4_
  - _Current Issue: Method is called with class_subject_teacher_map but doesn't accept it as parameter (line 169 vs line 416)_

- [x] 7. Add helper method for teacher capacity checking
  - Create `_check_teacher_limits()` method to verify daily and weekly period limits
  - Check if teacher has exceeded max_periods_per_day for the given day
  - Check if teacher has exceeded max_periods_per_week overall
  - Return boolean indicating if teacher can accept more assignments
  - Use this method in `_generate_complete_solution()` when checking pre-assigned teacher availability
  - _Requirements: 3.3, 4.1_

- [ ] 8. Enhance error handling and diagnostics
  - Improve error messages in `_pre_assign_teachers()` for "no qualified teacher" scenario
  - Improve error messages for "teacher over-allocated" scenario
  - Add error messages for "teacher unavailable at slot" scenario in generation
  - Include actionable suggestions in diagnostic output
  - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - _Note: Basic error handling exists but needs enhancement_

- [ ] 9. Create unit tests for teacher pre-assignment
  - Write test for successful teacher pre-assignment with sufficient teachers
  - Write test for error when no qualified teacher available
  - Write test for error when teacher capacity exceeded
  - Write test for load balancing across multiple qualified teachers
  - _Requirements: 1.1, 1.2, 3.1, 3.2_

- [ ] 10. Create unit tests for constraint enforcement
  - Write test verifying same teacher used for all periods of a subject
  - Write test verifying constraint can be disabled
  - Write test for handling teacher unavailability during generation
  - Write test for post-validation detecting violations
  - _Requirements: 1.1, 1.4, 2.2, 4.4_

- [ ] 11. Create integration test for end-to-end flow
  - Test complete flow from frontend checkbox to generated timetable
  - Verify teacher consistency in generated timetable entries
  - Test with real school dataset (30 classes, 100 teachers, 10 subjects)
  - Verify performance remains under 1 second
  - _Requirements: 1.1, 1.2, 1.3, 1.4_
