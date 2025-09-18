from typing import List, Dict, Any
from .models_phase1 import Constraint

class TimetableGenerationError(Exception):
    """Base exception for timetable generation errors."""
    def __init__(self, message: str, conflicts: List[str] = None, suggestions: List[str] = None):
        self.message = message
        self.conflicts = conflicts or []
        self.suggestions = suggestions or []
        super().__init__(self.message)

class InfeasibleConstraintsError(TimetableGenerationError):
    """Raised when constraints cannot be satisfied."""
    def __init__(self, conflicts: List[str], suggestions: List[str]):
        super().__init__("Constraints are infeasible", conflicts, suggestions)

class TimeoutError(TimetableGenerationError):
    """Raised on generation timeout."""
    def __init__(self, partial_solutions: int = 0):
        message = f"Generation timed out with {partial_solutions} partial solutions"
        super().__init__(message, [], ["Increase timeout or relax constraints"])

class WellnessViolationError(TimetableGenerationError):
    """Raised for severe wellness violations."""
    def __init__(self, violations: Dict[str, Any]):
        conflicts = [f"Teacher {k}: {v}" for k, v in violations.items()]
        suggestions = ["Redistribute workload or adjust configs"]
        super().__init__("Wellness constraints violated", conflicts, suggestions)

# Utility to generate suggestions
def generate_suggestions(constraints: List[Constraint], conflicts: List[str]) -> List[str]:
    """Generate AI-like suggestions for conflicts."""
    suggestions = []
    for conflict in conflicts:
        if "teacher shortage" in conflict.lower():
            suggestions.append("Hire additional teachers or relax subject qualifications")
        if "consecutive periods" in conflict.lower():
            suggestions.append("Increase max consecutive periods in wellness config to 4")
        if "daily hours" in conflict.lower():
            suggestions.append("Reduce daily teaching hours or add free periods")
        if "lab" in conflict.lower():
            suggestions.append("Add more lab rooms or schedule labs in off-peak times")
    if not suggestions:
        suggestions.append("Review and prioritize constraints (hard vs soft)")
    return suggestions

# Integrate with CSP (example)
# In csp_solver.py, in solve:
# if status == cp_model.INFEASIBLE:
#     conflicts = self._extract_conflicts(constraints)
#     suggestions = generate_suggestions(constraints, conflicts)
#     raise InfeasibleConstraintsError(conflicts, suggestions)