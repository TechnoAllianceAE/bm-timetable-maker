import pytest
from unittest.mock import MagicMock
from ..src.models import Class, Subject, Teacher, TimeSlot, Room, Constraint, GenerateRequest
from ..src.csp_solver import CSPSolver
from ..src.ga_optimizer import GAOptimizer
from ..src.wellness_calculator import WellnessCalculator