import pytest
from unittest.mock import patch, MagicMock
from ..src.models import (
    Class, Subject, Teacher, TimeSlot, Room, Constraint, TimetableEntry, Timetable,
    WellnessAnalysis, BurnoutRiskLevel, DayOfWeek, RoomType, ConstraintType, ConstraintPriority,
    GenerateRequest
)
from ..src.csp_solver import CSPSolver
from ..src.ga_optimizer import GAOptimizer
from ..src.wellness_calculator import WellnessCalculator
from ..src.errors import InfeasibleConstraintsError

@pytest.fixture
def mock_classes():
    return [
        Class(id="c1", school_id="s1", name="Class 9A", grade=9, section="A"),
        Class(id="c2", school_id="s1", name="Class 9B", grade=9, section="B")
    ]

@pytest.fixture
def mock_subjects():
    return [
        Subject(id="s1", school_id="s1", name="Mathematics", department="Math", credits=6, min_periods_per_week=6),
        Subject(id="s2", school_id="s1", name="English", department="Languages", credits=5, min_periods_per_week=5)
    ]

@pytest.fixture
def mock_teachers():
    return [
        Teacher(id="t1", user_id="u1", subjects=["Mathematics"], max_periods_per_day=6, max_periods_per_week=30),
        Teacher(id="t2", user_id="u2", subjects=["English"], max_periods_per_day=6, max_periods_per_week=30)
    ]

@pytest.fixture
def mock_time_slots():
    return [
        TimeSlot(id="ts1", school_id="s1", day=DayOfWeek.MONDAY, start_time="09:00", end_time="10:00"),
        TimeSlot(id="ts2", school_id="s1", day=DayOfWeek.MONDAY, start_time="10:00", end_time="11:00"),
        TimeSlot(id="ts3", school_id="s1", day=DayOfWeek.TUESDAY, start_time="09:00", end_time="10:00")
    ]

@pytest.fixture
def mock_rooms():
    return [
        Room(id="r1", school_id="s1", name="Room 101", capacity=40, type=RoomType.CLASSROOM),
        Room(id="r2", school_id="s1", name="Lab 1", capacity=30, type=RoomType.LAB)
    ]

@pytest.fixture
def mock_constraints():
    return [
        Constraint(id="const1", school_id="s1", type=ConstraintType.ACADEMIC_MIN_PERIODS, entity_id="s1", value={"min": 2}, priority=ConstraintPriority.HARD),
        Constraint(id="const2", school_id="s1", type=ConstraintType.WELLNESS_MAX_CONSECUTIVE, entity_id="general", value={"max": 2}, priority=ConstraintPriority.HARD)
    ]

@pytest.fixture
def mock_timetable():
    return Timetable(
        id="test_tt",
        school_id="s1",
        academic_year_id="ay1",
        entries=[
            TimetableEntry(class_id="c1", subject_id="s1", teacher_id="t1", time_slot_id="ts1", room_id="r1", wellness_impact=WellnessImpact.NEUTRAL),
            TimetableEntry(class_id="c1", subject_id="s2", teacher_id="t2", time_slot_id="ts2", room_id="r1", wellness_impact=WellnessImpact.POSITIVE),
            TimetableEntry(class_id="c2", subject_id="s1", teacher_id="t1", time_slot_id="ts3", room_id="r2", wellness_impact=WellnessImpact.NEUTRAL)
        ]
    )

def test_csp_solver_feasible(mock_classes, mock_subjects, mock_teachers, mock_time_slots, mock_rooms, mock_constraints):
    solver = CSPSolver()
    # Mock solver to return feasible
    with patch.object(solver.solver, 'Solve', return_value=cp_model.OPTIMAL):
        solutions, gen_time, conflicts, suggestions = solver.solve(mock_classes, mock_subjects, mock_teachers, mock_time_slots, mock_rooms, mock_constraints, num_solutions=1)
        assert len(solutions) > 0
        assert conflicts is None
        assert gen_time > 0

def test_csp_solver_infeasible(mock_classes, mock_subjects, mock_teachers, mock_time_slots, mock_rooms, mock_constraints):
    solver = CSPSolver()
    with patch.object(solver.solver, 'Solve', return_value=cp_model.INFEASIBLE):
        solutions, gen_time, conflicts, suggestions = solver.solve(mock_classes, mock_subjects, mock_teachers, mock_time_slots, mock_rooms, mock_constraints, num_solutions=1)
        assert len(solutions) == 0
        assert conflicts is not None
        assert len(conflicts) > 0

def test_ga_optimizer(mock_timetable):
    optimizer = GAOptimizer()
    base_solutions = [mock_timetable]
    optimized = optimizer.optimize(base_solutions, population_size=5, generations=2)
    assert len(optimized) > 0
    assert all(isinstance(s, Timetable) for s in optimized)

def test_wellness_calculator(mock_timetable, mock_teachers):
    configs = [TeacherWorkloadConfig(teacher_id=t.id) for t in mock_teachers]
    calc = WellnessCalculator()
    analysis = calc.calculate(mock_timetable, mock_teachers, configs)
    assert isinstance(analysis, WellnessAnalysis)
    assert analysis.overall_score >= 0 and analysis.overall_score <= 100
    assert len(analysis.teacher_scores) > 0

def test_generate_request_validation():
    request = GenerateRequest(
        school_id="s1",
        academic_year_id="ay1",
        classes=[Class(id="c1", school_id="s1", name="Test", grade=9)],
        subjects=[Subject(id="s1", school_id="s1", name="Test", credits=1)],
        teachers=[Teacher(id="t1", user_id="u1", subjects=["Test"])],
        time_slots=[TimeSlot(id="ts1", school_id="s1", day=DayOfWeek.MONDAY, start_time="09:00", end_time="10:00")],
        rooms=[Room(id="r1", school_id="s1", name="Room")],
        constraints=[],
        options=3,
        timeout=60
    )
    assert request.options == 3
    assert request.weights.academic == 0.35  # Default

def test_infeasible_error():
    conflicts = ["Teacher shortage"]
    suggestions = ["Hire more"]
    err = InfeasibleConstraintsError(conflicts, suggestions)
    assert err.conflicts == conflicts
    assert err.suggestions == suggestions