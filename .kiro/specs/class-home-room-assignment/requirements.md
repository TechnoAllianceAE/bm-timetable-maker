# Requirements Document

## Introduction

This feature ensures that each class is assigned a dedicated home room for the entire academic year. The home room serves as the default location for all regular lessons, while special rooms (labs, music rooms, etc.) are used only when specifically required by the subject. This reflects real-world school operations where students have a primary classroom and only move to specialized facilities when needed.

## Requirements

### Requirement 1: Home Room Assignment

**User Story:** As a school administrator, I want each class to have a dedicated home room for the academic year, so that students have a consistent primary location and room allocation is simplified.

#### Acceptance Criteria

1. WHEN a timetable is generated THEN the system SHALL assign each class a unique home room for the entire academic year
2. WHEN a class is assigned a home room THEN that room SHALL NOT be assigned as a home room to any other class
3. IF a class has a home room assigned THEN the system SHALL use that home room for all lessons by default
4. WHEN multiple classes exist THEN the system SHALL ensure no home room conflicts occur (one home room per class)

### Requirement 2: Special Room Handling

**User Story:** As a school administrator, I want certain rooms designated as special-purpose rooms (labs, music rooms, etc.), so that they are only used when required by specific subjects and not assigned as home rooms.

#### Acceptance Criteria

1. WHEN a room is marked as a special room (lab, music room, etc.) THEN the system SHALL NOT assign it as a home room to any class
2. IF a subject requires a special room THEN the system SHALL allocate that special room for those specific lessons only
3. WHEN a lesson does not require a special room THEN the system SHALL use the class's home room
4. WHEN special rooms are defined THEN they SHALL remain available for use by any class when needed

### Requirement 3: Hard Constraint Enforcement

**User Story:** As a timetable generator, I want home room assignments to be enforced as a hard constraint, so that the rule is never violated in any generated timetable.

#### Acceptance Criteria

1. WHEN the timetable generation algorithm runs THEN home room assignment SHALL be enforced as a hard constraint
2. IF a timetable violates home room assignment rules THEN the system SHALL reject that timetable as invalid
3. WHEN a lesson is scheduled THEN the system SHALL automatically assign the class's home room unless the subject requires a special room
4. WHEN validating a timetable THEN the system SHALL verify that all non-special-room lessons use the class's home room

### Requirement 4: Room Type Configuration

**User Story:** As a school administrator, I want to configure which rooms are special-purpose rooms, so that the system knows which rooms should not be used as home rooms.

#### Acceptance Criteria

1. WHEN defining a room THEN the system SHALL allow marking it as a special room with a room type (lab, music room, art room, etc.)
2. IF a room is not marked as special THEN the system SHALL consider it available for home room assignment
3. WHEN a subject is defined THEN the system SHALL allow specifying if it requires a special room type
4. WHEN matching subjects to rooms THEN the system SHALL only use special rooms for subjects that require them

### Requirement 5: Home Room Persistence

**User Story:** As a school administrator, I want home room assignments to persist throughout the academic year, so that classes maintain consistency and students know their primary location.

#### Acceptance Criteria

1. WHEN a home room is assigned to a class THEN that assignment SHALL remain constant for the entire academic year
2. IF a timetable is regenerated THEN the system SHALL maintain existing home room assignments unless explicitly changed
3. WHEN viewing a class's schedule THEN the system SHALL clearly indicate which room is the home room
4. WHEN a class's home room needs to change THEN the system SHALL require explicit administrator action
