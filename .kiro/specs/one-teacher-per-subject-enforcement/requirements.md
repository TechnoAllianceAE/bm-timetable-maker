# Requirements Document

## Introduction

This feature ensures that within each classroom, each subject is taught by exactly one teacher throughout the timetable. This is a fundamental educational requirement where students should have consistency in their subject teachers. While a teacher may teach multiple subjects to the same class or teach the same subject to different classes, within a single class-subject combination, there must be only one teacher assigned.

## Requirements

### Requirement 1: Teacher-Subject Consistency per Class

**User Story:** As a school administrator, I want each subject in a class to be taught by the same teacher throughout the week, so that students have consistent instruction and teachers can build better rapport with their students.

#### Acceptance Criteria

1. WHEN generating a timetable THEN the system SHALL ensure that for each (class, subject) pair, all periods are assigned to the same teacher
2. WHEN a teacher is assigned to teach Subject X to Class A in period 1 THEN the system SHALL assign the same teacher to all other periods of Subject X for Class A
3. IF a teacher teaches Math to Class 6A THEN that teacher SHALL be the only teacher for Math in Class 6A across all periods
4. WHEN validating a timetable THEN the system SHALL report violations where a (class, subject) pair has multiple teachers assigned

### Requirement 2: Hard Constraint Enforcement

**User Story:** As a school administrator, I want the one-teacher-per-subject rule to be a hard constraint enabled by default, so that all generated timetables automatically comply with this educational requirement.

#### Acceptance Criteria

1. WHEN the timetable generation form loads THEN the "One teacher per subject per class" checkbox SHALL be checked by default
2. WHEN the hard rule is enabled THEN the CSP solver SHALL enforce teacher consistency during generation
3. WHEN the hard rule is disabled THEN the CSP solver SHALL allow multiple teachers per (class, subject) pair
4. WHEN generation fails due to teacher consistency constraints THEN the system SHALL provide diagnostic feedback about which (class, subject) pairs cannot be satisfied

### Requirement 3: Teacher Assignment Strategy

**User Story:** As a system, I need to assign teachers to (class, subject) pairs at the beginning of timetable generation, so that all subsequent period assignments use the same teacher.

#### Acceptance Criteria

1. WHEN starting timetable generation THEN the system SHALL create a mapping of (class_id, subject_id) → teacher_id
2. WHEN assigning a period for a (class, subject) pair THEN the system SHALL look up the pre-assigned teacher from the mapping
3. IF no teacher has been assigned to a (class, subject) pair THEN the system SHALL select an available qualified teacher and record it in the mapping
4. WHEN a pre-assigned teacher is not available for a specific time slot THEN the system SHALL report a constraint violation

### Requirement 4: Validation and Diagnostics

**User Story:** As a school administrator, I want clear feedback when teacher consistency violations occur, so that I can understand and resolve scheduling conflicts.

#### Acceptance Criteria

1. WHEN post-validation detects multiple teachers for a (class, subject) pair THEN the system SHALL report the class name, subject name, and list of teachers involved
2. WHEN generation fails due to teacher consistency THEN the system SHALL suggest adding more qualified teachers or adjusting teacher availability
3. WHEN viewing diagnostics THEN the system SHALL show which (class, subject) pairs have teacher consistency issues
4. WHEN a timetable is successfully generated THEN the system SHALL confirm that all (class, subject) pairs have single teacher assignments
