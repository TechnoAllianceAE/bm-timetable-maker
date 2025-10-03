"""
Verbose Logger and Bottleneck Analyzer
Provides detailed logging and analysis of constraint violations during solving
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import time


@dataclass
class ConstraintViolation:
    """Represents a single constraint violation"""
    constraint_type: str
    severity: str  # 'hard' or 'soft'
    penalty: int
    details: str
    resources_involved: List[str] = field(default_factory=list)


@dataclass
class GenerationSnapshot:
    """Snapshot of a GA generation or CSP iteration"""
    iteration: int
    timestamp: float
    fitness_score: float
    hard_violations: int
    soft_violations: int
    violations_by_type: Dict[str, int]
    worst_violations: List[ConstraintViolation]


class VerboseLogger:
    """
    Provides detailed logging of the solving process.
    Tracks constraint violations and identifies bottlenecks.
    """

    def __init__(self, verbose_level: int = 1):
        """
        Initialize logger with verbosity level.
        0 = Silent, 1 = Summary, 2 = Detailed, 3 = Debug
        """
        self.verbose_level = verbose_level
        self.history: List[GenerationSnapshot] = []
        self.violation_frequency: Dict[str, int] = defaultdict(int)
        self.resource_conflicts: Dict[str, int] = defaultdict(int)
        self.start_time = None
        self.current_best_fitness = float('inf')

    def start_logging(self):
        """Start logging session"""
        self.start_time = time.time()
        self.history = []
        self.violation_frequency.clear()
        self.resource_conflicts.clear()
        if self.verbose_level >= 1:
            print("\n" + "="*60)
            print("TIMETABLE GENERATION STARTED")
            print("="*60)

    def log_ga_generation(
        self,
        generation: int,
        best_fitness: float,
        violations: List[ConstraintViolation]
    ):
        """Log a GA generation's progress"""

        # Calculate violation counts
        hard_count = sum(1 for v in violations if v.severity == 'hard')
        soft_count = sum(1 for v in violations if v.severity == 'soft')

        # Group violations by type
        violations_by_type = defaultdict(int)
        for v in violations:
            violations_by_type[v.constraint_type] += 1
            self.violation_frequency[v.constraint_type] += 1

            # Track resource conflicts
            for resource in v.resources_involved:
                self.resource_conflicts[resource] += 1

        # Create snapshot
        snapshot = GenerationSnapshot(
            iteration=generation,
            timestamp=time.time() - self.start_time,
            fitness_score=best_fitness,
            hard_violations=hard_count,
            soft_violations=soft_count,
            violations_by_type=dict(violations_by_type),
            worst_violations=sorted(violations, key=lambda x: x.penalty, reverse=True)[:5]
        )

        self.history.append(snapshot)

        # Print progress based on verbosity
        if self.verbose_level >= 1:
            # Check if this is an improvement
            is_improvement = best_fitness < self.current_best_fitness
            self.current_best_fitness = min(self.current_best_fitness, best_fitness)

            if is_improvement or generation % 10 == 0:
                self._print_generation_summary(snapshot, is_improvement)

    def log_csp_step(
        self,
        step_type: str,  # 'assignment', 'backtrack', 'conflict'
        class_id: str,
        slot_id: str,
        details: Dict[str, Any]
    ):
        """Log a CSP solver step"""

        if self.verbose_level >= 2:
            timestamp = time.time() - self.start_time if self.start_time else 0

            if step_type == 'assignment':
                print(f"[{timestamp:.2f}s] ✓ ASSIGN: {class_id} @ {slot_id}")
                if self.verbose_level >= 3:
                    print(f"         Teacher: {details.get('teacher', 'N/A')}")
                    print(f"         Room: {details.get('room', 'N/A')}")

            elif step_type == 'conflict':
                print(f"[{timestamp:.2f}s] ✗ CONFLICT: {class_id} @ {slot_id}")
                print(f"         Reason: {details.get('reason', 'Unknown')}")
                if 'alternatives_tried' in details:
                    print(f"         Alternatives tried: {details['alternatives_tried']}")

            elif step_type == 'backtrack':
                print(f"[{timestamp:.2f}s] ↺ BACKTRACK: Undoing {class_id} @ {slot_id}")
                print(f"         Depth: {details.get('depth', 0)}")

    def analyze_bottlenecks(self) -> Dict[str, Any]:
        """
        Analyze the solving history to identify bottlenecks.
        Returns analysis with actionable insights.
        """

        if not self.history:
            return {"status": "No data to analyze"}

        analysis = {
            "total_time": time.time() - self.start_time,
            "iterations": len(self.history),
            "improvement_rate": self._calculate_improvement_rate(),
            "persistent_violations": self._identify_persistent_violations(),
            "resource_bottlenecks": self._identify_resource_bottlenecks(),
            "convergence_analysis": self._analyze_convergence()
        }

        return analysis

    def _print_generation_summary(self, snapshot: GenerationSnapshot, is_improvement: bool):
        """Print a summary of the generation"""

        improvement_marker = " ⬆️ IMPROVEMENT!" if is_improvement else ""

        print(f"\nGeneration {snapshot.iteration}: "
              f"Fitness = {snapshot.fitness_score:.0f} "
              f"(Hard: {snapshot.hard_violations}, Soft: {snapshot.soft_violations})"
              f"{improvement_marker}")

        if self.verbose_level >= 2:
            print("  Violations:")
            for vtype, count in sorted(snapshot.violations_by_type.items(),
                                      key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {vtype}: {count}")

        if self.verbose_level >= 3 and snapshot.worst_violations:
            print("  Worst violations:")
            for v in snapshot.worst_violations[:3]:
                print(f"    - {v.constraint_type}: {v.details[:50]}...")

    def _calculate_improvement_rate(self) -> float:
        """Calculate the rate of fitness improvement"""

        if len(self.history) < 2:
            return 0.0

        initial_fitness = self.history[0].fitness_score
        final_fitness = self.history[-1].fitness_score

        if initial_fitness == 0:
            return 0.0

        return (initial_fitness - final_fitness) / initial_fitness * 100

    def _identify_persistent_violations(self) -> List[Tuple[str, int]]:
        """Identify violations that persist throughout solving"""

        persistent = []

        # Look at last 20% of history
        recent_start = int(len(self.history) * 0.8)
        recent_violations = defaultdict(int)

        for snapshot in self.history[recent_start:]:
            for vtype, count in snapshot.violations_by_type.items():
                recent_violations[vtype] += count

        # Sort by frequency
        for vtype, count in sorted(recent_violations.items(),
                                  key=lambda x: x[1], reverse=True):
            persistent.append((vtype, count))

        return persistent[:5]  # Top 5 persistent violations

    def _identify_resource_bottlenecks(self) -> List[Tuple[str, int]]:
        """Identify resources that are most often involved in conflicts"""

        return sorted(self.resource_conflicts.items(),
                     key=lambda x: x[1], reverse=True)[:10]

    def _analyze_convergence(self) -> str:
        """Analyze if the algorithm is converging or stuck"""

        if len(self.history) < 10:
            return "Too early to determine"

        # Check last 10 iterations
        recent_fitness = [s.fitness_score for s in self.history[-10:]]

        # Calculate variance
        avg = sum(recent_fitness) / len(recent_fitness)
        variance = sum((f - avg) ** 2 for f in recent_fitness) / len(recent_fitness)

        if variance < 0.01:
            return "STAGNATED - Algorithm is stuck"
        elif recent_fitness[-1] < recent_fitness[0] * 0.5:
            return "CONVERGING WELL - Good progress"
        elif recent_fitness[-1] < recent_fitness[0] * 0.8:
            return "SLOW CONVERGENCE - Making progress but slowly"
        else:
            return "NOT CONVERGING - Consider different parameters"

    def generate_report(self) -> str:
        """Generate a comprehensive report of the solving process"""

        analysis = self.analyze_bottlenecks()

        report = []
        report.append("\n" + "="*60)
        report.append("TIMETABLE GENERATION REPORT")
        report.append("="*60)

        # Summary
        report.append(f"\n📊 SUMMARY")
        report.append(f"  Total Time: {analysis.get('total_time', 0):.2f} seconds")
        report.append(f"  Iterations: {analysis.get('iterations', 0)}")
        report.append(f"  Improvement Rate: {analysis.get('improvement_rate', 0):.1f}%")
        report.append(f"  Status: {analysis.get('convergence_analysis', 'N/A')}")

        # Bottlenecks
        report.append(f"\n🔍 BOTTLENECK ANALYSIS")

        if analysis.get('persistent_violations'):
            report.append("  Persistent Constraint Violations:")
            for vtype, count in analysis['persistent_violations']:
                report.append(f"    • {vtype}: {count} occurrences")

        if analysis.get('resource_bottlenecks'):
            report.append("\n  Resource Bottlenecks:")
            for resource, conflicts in analysis['resource_bottlenecks'][:5]:
                report.append(f"    • {resource}: involved in {conflicts} conflicts")

        # Recommendations
        report.append(f"\n💡 RECOMMENDATIONS")
        recommendations = self._generate_recommendations(analysis)
        for rec in recommendations:
            report.append(f"  • {rec}")

        return "\n".join(report)

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""

        recommendations = []

        # Check convergence
        convergence = analysis.get('convergence_analysis', '')
        if "STAGNATED" in convergence:
            recommendations.append("Algorithm is stuck - try increasing mutation rate or population diversity")
        elif "NOT CONVERGING" in convergence:
            recommendations.append("Algorithm not converging - verify constraints are satisfiable")

        # Check persistent violations
        persistent_violations = analysis.get('persistent_violations', [])
        if persistent_violations:
            top_violation = persistent_violations[0][0]

            if 'teacher_conflict' in top_violation.lower():
                recommendations.append(f"Teacher conflicts are the main bottleneck - consider hiring more teachers or adjusting workload limits")
            elif 'room' in top_violation.lower():
                recommendations.append(f"Room conflicts are persistent - check if you have enough specialized rooms (labs, etc.)")
            elif 'consecutive' in top_violation.lower():
                recommendations.append(f"Consecutive period constraints are too restrictive - consider relaxing them")

        # Check resource bottlenecks
        resource_bottlenecks = analysis.get('resource_bottlenecks', [])
        if resource_bottlenecks:
            top_resources = [r[0] for r in resource_bottlenecks[:3]]
            recommendations.append(f"Resources causing most conflicts: {', '.join(top_resources)} - review their availability")

        if not recommendations:
            recommendations.append("No specific bottlenecks identified - solution may be feasible with more iterations")

        return recommendations