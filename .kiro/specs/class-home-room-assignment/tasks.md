# Implementation Plan

- [ ] 1. Update database schema with home room fields
  - Add `isSpecialRoom` and `specialRoomType` fields to Room model
  - Add `homeRoomId` relation to Class model
  - Add `requiredRoomType` field to Subject model
  - Create and run Prisma migration
  - _Requirements: 1.1, 2.1, 4.1_

- [ ] 2. Update backend data models and DTOs
  - [ ] 2.1 Update Room DTOs to include special room fields
    - Modify `CreateRoomDto` to include `isSpecialRoom` and `specialRoomType`
    - Modify `UpdateRoomDto` to include special room fields
    - Add validation for special room type enum
    - _Requirements: 4.1, 4.2_

  - [ ] 2.2 Update Class DTOs to include home room reference
    - Create `AssignHomeRoomDto` with `homeRoomId` field
    - Update class response DTOs to include home room data
    - Add validation to ensure home room exists and is not special
    - _Requirements: 1.1, 1.2, 5.1_

  - [ ] 2.3 Update Subject DTOs to include room requirements
    - Modify `CreateSubjectDto` to include `requiredRoomType`
    - Modify `UpdateSubjectDto` to include room requirement field
    - Add validation for room type matching
    - _Requirements: 2.2, 4.3_

- [ ] 3. Implement backend room management endpoints
  - [ ] 3.1 Add endpoint to get available home rooms
    - Create GET `/api/rooms/available-home-rooms` endpoint
    - Filter out special rooms and already-assigned home rooms
    - Return list of available rooms with capacity info
    - Write unit tests for filtering logic
    - _Requirements: 1.2, 2.1, 4.2_

  - [ ] 3.2 Update room service to handle special room configuration
    - Modify `RoomsService.update()` to handle special room fields
    - Add validation to prevent special rooms from being home rooms
    - Add method to check if room is available as home room
    - Write unit tests for validation logic
    - _Requirements: 2.1, 4.1, 4.2_

- [ ] 4. Implement backend class home room assignment
  - [ ] 4.1 Add endpoint to assign home room to class
    - Create PATCH `/api/classes/:id/home-room` endpoint
    - Validate room exists, is not special, and is not already assigned
    - Update class record with home room assignment
    - Write unit tests for assignment logic
    - _Requirements: 1.1, 1.2, 1.4, 5.1, 5.4_

  - [ ] 4.2 Update class service to include home room data
    - Modify `ClassesService.findOne()` to include home room relation
    - Modify `ClassesService.findAll()` to include home room data
    - Add method to validate home room assignment
    - Write unit tests for home room retrieval
    - _Requirements: 1.1, 5.3_

  - [ ] 4.3 Add home room validation logic
    - Create validation method to check home room uniqueness
    - Create validation method to check room capacity vs class size
    - Create validation method to ensure room is not special
    - Write unit tests for all validation scenarios
    - _Requirements: 1.2, 1.4, 2.1_

- [ ] 5. Update Python timetable engine models
  - [ ] 5.1 Extend Room model with special room fields
    - Add `is_special_room: bool` field to Room model
    - Add `special_room_type: Optional[str]` field to Room model
    - Update model validation and serialization
    - Write unit tests for model validation
    - _Requirements: 2.1, 4.1_

  - [ ] 5.2 Extend Class model with home room reference
    - Add `home_room_id: Optional[str]` field to Class model
    - Update model validation
    - Write unit tests for model with home room
    - _Requirements: 1.1, 5.1_

  - [ ] 5.3 Extend Subject model with room requirements
    - Add `required_room_type: Optional[str]` field to Subject model
    - Update model validation
    - Write unit tests for subject with room requirements
    - _Requirements: 2.2, 4.3_

- [ ] 6. Implement CSP solver home room logic
  - [ ] 6.1 Add home room validation method
    - Create `_validate_home_room_assignments()` method
    - Check each class has valid home room (if assigned)
    - Check no special rooms used as home rooms
    - Check no duplicate home room assignments
    - Check home room capacity is sufficient
    - Return validation errors with clear messages
    - Write unit tests for all validation cases
    - _Requirements: 1.2, 1.4, 2.1, 3.1, 3.2_

  - [ ] 6.2 Implement room assignment logic
    - Create `_assign_room_for_entry()` method
    - Priority 1: Use special room if subject requires it
    - Priority 2: Use class home room for regular subjects
    - Priority 3: Fallback to any available room
    - Handle room busy conflicts
    - Write unit tests for assignment priority logic
    - _Requirements: 1.3, 2.2, 2.3, 2.4, 3.3_

  - [ ] 6.3 Integrate room assignment into CSP solver
    - Replace existing room assignment logic in `_generate_complete_solution()`
    - Call `_assign_room_for_entry()` for each timetable entry
    - Handle cases where no appropriate room is available
    - Update debug logging to show home room usage
    - Write integration tests for complete timetable generation
    - _Requirements: 1.3, 2.3, 3.3, 5.2_

  - [ ] 6.4 Add home room validation to solve method
    - Call `_validate_home_room_assignments()` at start of `solve()`
    - Return early with errors if validation fails
    - Provide clear error messages and suggestions
    - Write integration tests for validation failures
    - _Requirements: 3.1, 3.2, 3.4_

- [ ] 7. Update frontend room management UI
  - [ ] 7.1 Add special room configuration to room form
    - Add checkbox for "Is Special Room" in RoomForm component
    - Add dropdown for special room type (shown when checkbox is checked)
    - Add validation to prevent empty special room type when checked
    - Update form submission to include special room fields
    - Write component tests for form validation
    - _Requirements: 4.1, 4.2_

  - [ ] 7.2 Update rooms list to show special room indicator
    - Add column or badge to show if room is special
    - Display special room type when applicable
    - Add filter to show only regular rooms or only special rooms
    - Write component tests for display logic
    - _Requirements: 4.2_

- [ ] 8. Implement frontend home room assignment UI
  - [ ] 8.1 Add home room column to classes table
    - Display home room name in classes list
    - Show "Not Assigned" if no home room
    - Add visual indicator for classes without home rooms
    - Write component tests for display
    - _Requirements: 1.1, 5.3_

  - [ ] 8.2 Create home room assignment modal
    - Add "Assign Home Room" button to each class row
    - Create modal component to select home room
    - Fetch and display available home rooms (non-special, unassigned)
    - Show room capacity and current assignment status
    - Handle assignment API call and error display
    - Write component tests for modal interactions
    - _Requirements: 1.1, 1.2, 5.1, 5.4_

  - [ ] 8.3 Add home room bulk assignment feature
    - Create UI to assign home rooms to multiple classes at once
    - Show suggested assignments based on capacity matching
    - Allow manual override of suggestions
    - Validate assignments before submission
    - Write component tests for bulk assignment
    - _Requirements: 1.1, 5.1_

- [ ] 9. Update frontend timetable display
  - [ ] 9.1 Add visual indicators for home room vs special room
    - Add different background color or icon for special room lessons
    - Add tooltip showing room type on hover
    - Update timetable legend to explain indicators
    - Write component tests for visual indicators
    - _Requirements: 2.3, 5.3_

  - [ ] 9.2 Add home room summary to timetable view
    - Display class's home room at top of timetable
    - Show statistics: % of lessons in home room vs special rooms
    - Add filter to highlight special room usage
    - Write component tests for summary display
    - _Requirements: 5.3_

- [ ] 10. Create data migration script
  - [ ] 10.1 Script to identify and mark special rooms
    - Identify rooms with type LAB, SPORTS, LIBRARY, AUDITORIUM
    - Mark them as special rooms with appropriate type
    - Generate report of rooms marked as special
    - Write tests for migration logic
    - _Requirements: 2.1, 4.1_

  - [ ] 10.2 Script to assign default home rooms to existing classes
    - Match classes to available rooms based on capacity
    - Ensure one-to-one mapping (no duplicate assignments)
    - Prioritize rooms in same building/floor if data available
    - Generate report of assignments made
    - Write tests for assignment algorithm
    - _Requirements: 1.1, 5.1_

- [ ] 11. Add integration tests for complete workflow
  - Create test scenario with multiple classes and rooms
  - Configure special rooms (labs, music room)
  - Assign home rooms to classes
  - Configure subjects with room requirements
  - Generate timetable via API
  - Verify home rooms used correctly in generated timetable
  - Verify special rooms used only for required subjects
  - Test error cases (no home room, insufficient special rooms)
  - _Requirements: 1.1, 1.2, 1.3, 2.2, 2.3, 3.1, 3.3, 3.4_

- [ ] 12. Add documentation and user guide
  - Document home room assignment workflow in admin guide
  - Document special room configuration process
  - Add API documentation for new endpoints
  - Create troubleshooting guide for common issues
  - Add examples of room type configurations
  - _Requirements: 4.1, 4.2, 5.4_
