"""
Resource Scarcity Advisor
Pre-computation sanity checks and post-mortem analysis for timetable generation
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import math


@dataclass
class ResourceCheck:
    """Result of a resource check"""
    check_type: str
    passed: bool
    message: str
    severity: str  # 'critical', 'warning', 'info'
    suggestions: List[str]


@dataclass
class ResourceAnalysis:
    """Complete resource analysis"""
    is_feasible: bool
    critical_issues: List[ResourceCheck]
    warnings: List[ResourceCheck]
    recommendations: List[str]
    bottleneck_resources: Dict[str, float]  # Resource -> scarcity score


class ResourceScarcityAdvisor:
    """
    Performs pre-computation sanity checks and post-mortem analysis
    to identify resource bottlenecks and provide actionable recommendations.
    """

    def __init__(self):
        self.last_analysis: Optional[ResourceAnalysis] = None

    def pre_computation_check(
        self,
        classes: List,
        subjects: List,
        teachers: List,
        time_slots: List,
        rooms: List
    ) -> ResourceAnalysis:
        """
        Perform sanity checks before attempting to generate timetable.
        Returns analysis with feasibility assessment and recommendations.
        """

        checks = []
        critical_issues = []
        warnings = []
        recommendations = []
        bottleneck_scores = {}

        # Filter active slots
        active_slots = [ts for ts in time_slots if not ts.is_break]
        total_slots_per_week = len(active_slots)

        # Check 1: Overall Teacher Load
        check = self._check_teacher_load(classes, subjects, teachers, total_slots_per_week)
        checks.append(check)
        if not check.passed:
            if check.severity == 'critical':
                critical_issues.append(check)
            else:
                warnings.append(check)

        # Check 2: Subject-Specific Teacher Availability
        subject_checks = self._check_subject_teacher_availability(
            classes, subjects, teachers
        )
        for check in subject_checks:
            checks.append(check)
            if not check.passed:
                if check.severity == 'critical':
                    critical_issues.append(check)
                else:
                    warnings.append(check)

        # Check 3: Room Capacity and Availability
        room_checks = self._check_room_availability(
            classes, subjects, rooms, total_slots_per_week
        )
        for check in room_checks:
            checks.append(check)
            if not check.passed:
                if check.severity == 'critical':
                    critical_issues.append(check)
                else:
                    warnings.append(check)

        # Check 4: Peak Usage Analysis
        peak_check = self._check_peak_usage(
            classes, subjects, rooms, active_slots
        )
        checks.append(peak_check)
        if not peak_check.passed:
            if peak_check.severity == 'critical':
                critical_issues.append(peak_check)
            else:
                warnings.append(peak_check)

        # Check 5: Specialized Room Requirements
        lab_check = self._check_specialized_rooms(
            classes, subjects, rooms, total_slots_per_week
        )
        checks.append(lab_check)
        if not lab_check.passed:
            if lab_check.severity == 'critical':
                critical_issues.append(lab_check)
            else:
                warnings.append(lab_check)

        # Calculate bottleneck scores
        bottleneck_scores = self._calculate_bottleneck_scores(
            classes, subjects, teachers, rooms, active_slots
        )

        # Generate recommendations
        recommendations = self._generate_pre_check_recommendations(
            critical_issues, warnings, bottleneck_scores
        )

        # Determine overall feasibility
        is_feasible = len(critical_issues) == 0

        analysis = ResourceAnalysis(
            is_feasible=is_feasible,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
            bottleneck_resources=bottleneck_scores
        )

        self.last_analysis = analysis
        return analysis

    def post_mortem_analysis(
        self,
        failed_solution: Any,  # The best-but-still-invalid solution
        violation_log: Dict[str, List]  # Violation history from VerboseLogger
    ) -> ResourceAnalysis:
        """
        Analyze a failed solution to identify why it couldn't be solved.
        Provides specific, actionable recommendations.
        """

        critical_issues = []
        warnings = []
        recommendations = []
        bottleneck_resources = {}

        # Analyze violation patterns
        violation_analysis = self._analyze_violation_patterns(violation_log)

        # Identify most problematic resources
        problem_resources = self._identify_problem_resources(
            failed_solution, violation_log
        )

        # Generate specific recommendations based on failure patterns
        for resource_type, issues in problem_resources.items():
            if resource_type == 'teachers':
                for teacher_id, conflict_count in issues[:3]:  # Top 3 problematic teachers
                    critical_issues.append(ResourceCheck(
                        check_type='teacher_overload',
                        passed=False,
                        message=f"Teacher {teacher_id} involved in {conflict_count} unresolvable conflicts",
                        severity='critical',
                        suggestions=[
                            f"Reduce teaching load for {teacher_id}",
                            f"Hire additional teacher with similar qualifications as {teacher_id}",
                            f"Redistribute classes from {teacher_id} to other teachers"
                        ]
                    ))
                    bottleneck_resources[f"teacher_{teacher_id}"] = conflict_count

            elif resource_type == 'rooms':
                for room_id, conflict_count in issues[:3]:
                    warnings.append(ResourceCheck(
                        check_type='room_shortage',
                        passed=False,
                        message=f"Room {room_id} oversubscribed with {conflict_count} conflicts",
                        severity='warning',
                        suggestions=[
                            f"Consider using alternative rooms for classes assigned to {room_id}",
                            f"Review if all classes really need room {room_id}",
                            f"Stagger class timings to reduce peak demand for {room_id}"
                        ]
                    ))
                    bottleneck_resources[f"room_{room_id}"] = conflict_count

        # Generate final recommendations
        recommendations = self._generate_post_mortem_recommendations(
            violation_analysis, problem_resources
        )

        return ResourceAnalysis(
            is_feasible=False,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
            bottleneck_resources=bottleneck_resources
        )

    def _check_teacher_load(
        self, classes, subjects, teachers, total_slots
    ) -> ResourceCheck:
        """Check if total teaching demand exceeds supply"""

        # Calculate total demand
        total_demand = 0
        for class_obj in classes:
            for subject in subjects:
                total_demand += subject.periods_per_week

        # Calculate total supply
        total_supply = sum(
            min(t.max_periods_per_week, total_slots)
            for t in teachers
        )

        if total_demand > total_supply:
            deficit = total_demand - total_supply
            additional_teachers = math.ceil(deficit / 20)  # Assume 20 periods per teacher

            return ResourceCheck(
                check_type='teacher_load',
                passed=False,
                message=f"Total teaching demand ({total_demand} periods) exceeds supply ({total_supply} periods)",
                severity='critical',
                suggestions=[
                    f"Hire at least {additional_teachers} additional teachers",
                    f"Reduce total periods by {deficit} across all subjects",
                    "Increase maximum teaching hours for existing teachers"
                ]
            )

        utilization = (total_demand / total_supply) * 100
        if utilization > 85:
            return ResourceCheck(
                check_type='teacher_load',
                passed=True,
                message=f"Teacher utilization at {utilization:.1f}% - system is tight",
                severity='warning',
                suggestions=["Consider hiring 1-2 additional teachers for flexibility"]
            )

        return ResourceCheck(
            check_type='teacher_load',
            passed=True,
            message=f"Teacher capacity sufficient ({utilization:.1f}% utilization)",
            severity='info',
            suggestions=[]
        )

    def _check_subject_teacher_availability(
        self, classes, subjects, teachers
    ) -> List[ResourceCheck]:
        """Check if each subject has enough qualified teachers"""

        checks = []

        for subject in subjects:
            # Calculate demand for this subject
            demand = len(classes) * subject.periods_per_week

            # Find qualified teachers
            qualified_teachers = [
                t for t in teachers
                if subject.name in t.subjects
            ]

            if not qualified_teachers:
                checks.append(ResourceCheck(
                    check_type='subject_teacher',
                    passed=False,
                    message=f"No teachers qualified to teach '{subject.name}'",
                    severity='critical',
                    suggestions=[
                        f"Hire a teacher qualified in {subject.name}",
                        f"Train existing teachers in {subject.name}",
                        f"Remove {subject.name} from curriculum"
                    ]
                ))
                continue

            # Calculate supply for this subject
            supply = sum(
                min(t.max_periods_per_week, 30)  # Cap at reasonable max
                for t in qualified_teachers
            )

            if demand > supply:
                deficit = demand - supply
                checks.append(ResourceCheck(
                    check_type='subject_teacher',
                    passed=False,
                    message=f"'{subject.name}' needs {demand} periods but only {supply} available",
                    severity='critical',
                    suggestions=[
                        f"Hire another {subject.name} teacher",
                        f"Reduce {subject.name} periods from {subject.periods_per_week} to {subject.periods_per_week - 1}",
                        f"Cross-train teachers in {subject.name}"
                    ]
                ))
            elif demand > supply * 0.9:
                checks.append(ResourceCheck(
                    check_type='subject_teacher',
                    passed=True,
                    message=f"'{subject.name}' teachers at >90% capacity",
                    severity='warning',
                    suggestions=[f"Consider additional {subject.name} teacher for flexibility"]
                ))

        return checks

    def _check_room_availability(
        self, classes, subjects, rooms, total_slots
    ) -> List[ResourceCheck]:
        """Check if there are enough rooms for all classes"""

        checks = []

        # Basic room count check
        max_concurrent_classes = len(classes)  # Worst case: all classes at same time

        if len(rooms) < max_concurrent_classes:
            deficit = max_concurrent_classes - len(rooms)
            checks.append(ResourceCheck(
                check_type='room_count',
                passed=False,
                message=f"Only {len(rooms)} rooms for {max_concurrent_classes} classes",
                severity='critical',
                suggestions=[
                    f"Add at least {deficit} more rooms",
                    "Implement shift system to reduce concurrent classes",
                    "Use multi-purpose spaces as classrooms"
                ]
            ))

        # Check room capacity
        for class_obj in classes:
            suitable_rooms = [
                r for r in rooms
                if r.capacity >= class_obj.student_count
            ]

            if not suitable_rooms:
                checks.append(ResourceCheck(
                    check_type='room_capacity',
                    passed=False,
                    message=f"No room large enough for {class_obj.name} ({class_obj.student_count} students)",
                    severity='critical',
                    suggestions=[
                        f"Find room with capacity ≥ {class_obj.student_count}",
                        f"Split {class_obj.name} into smaller sections",
                        "Upgrade existing room capacity"
                    ]
                ))
            elif len(suitable_rooms) < 2:
                checks.append(ResourceCheck(
                    check_type='room_capacity',
                    passed=True,
                    message=f"Only {len(suitable_rooms)} room(s) suitable for {class_obj.name}",
                    severity='warning',
                    suggestions=["Limited room options may cause scheduling conflicts"]
                ))

        return checks

    def _check_peak_usage(
        self, classes, subjects, rooms, active_slots
    ) -> ResourceCheck:
        """Analyze peak usage patterns"""

        # Find the busiest time slots (typically mid-morning)
        morning_slots = [
            s for s in active_slots
            if s.period_number in [2, 3, 4]  # Peak hours
        ]

        if not morning_slots:
            return ResourceCheck(
                check_type='peak_usage',
                passed=True,
                message="Peak usage analysis not applicable",
                severity='info',
                suggestions=[]
            )

        # In peak hours, all classes might need rooms
        peak_demand = len(classes)
        available_rooms = len(rooms)

        if peak_demand > available_rooms:
            return ResourceCheck(
                check_type='peak_usage',
                passed=False,
                message=f"Peak demand ({peak_demand} classes) exceeds rooms ({available_rooms})",
                severity='critical',
                suggestions=[
                    "Stagger class start times",
                    "Implement rotating schedules",
                    f"Add {peak_demand - available_rooms} temporary classrooms"
                ]
            )

        utilization = (peak_demand / available_rooms) * 100
        if utilization > 90:
            return ResourceCheck(
                check_type='peak_usage',
                passed=True,
                message=f"Peak room utilization at {utilization:.0f}%",
                severity='warning',
                suggestions=["Very tight room scheduling - consider adding buffer capacity"]
            )

        return ResourceCheck(
            check_type='peak_usage',
            passed=True,
            message=f"Peak usage manageable ({utilization:.0f}% room utilization)",
            severity='info',
            suggestions=[]
        )

    def _check_specialized_rooms(
        self, classes, subjects, rooms, total_slots
    ) -> ResourceCheck:
        """Check availability of specialized rooms (labs, etc.)"""

        # Find subjects requiring special rooms
        lab_subjects = [s for s in subjects if s.requires_lab]

        if not lab_subjects:
            return ResourceCheck(
                check_type='specialized_rooms',
                passed=True,
                message="No specialized room requirements",
                severity='info',
                suggestions=[]
            )

        # Calculate lab demand
        lab_demand = sum(
            len(classes) * subject.periods_per_week
            for subject in lab_subjects
        )

        # Count lab rooms
        lab_rooms = [r for r in rooms if r.type == 'LAB']

        if not lab_rooms:
            return ResourceCheck(
                check_type='specialized_rooms',
                passed=False,
                message=f"No lab rooms available but {lab_demand} lab periods needed",
                severity='critical',
                suggestions=[
                    "Add at least 1 laboratory room",
                    "Convert existing room to lab",
                    "Partner with nearby school for lab access"
                ]
            )

        # Calculate lab supply
        lab_supply = len(lab_rooms) * total_slots

        if lab_demand > lab_supply:
            deficit = lab_demand - lab_supply
            additional_labs = math.ceil(deficit / total_slots)

            return ResourceCheck(
                check_type='specialized_rooms',
                passed=False,
                message=f"Lab demand ({lab_demand} periods) exceeds supply ({lab_supply} periods)",
                severity='critical',
                suggestions=[
                    f"Add {additional_labs} more lab rooms",
                    "Reduce lab periods per subject",
                    "Use regular classrooms for theory portions of lab subjects"
                ]
            )

        utilization = (lab_demand / lab_supply) * 100
        if utilization > 80:
            return ResourceCheck(
                check_type='specialized_rooms',
                passed=True,
                message=f"Lab utilization at {utilization:.1f}% - tight scheduling",
                severity='warning',
                suggestions=["Consider adding another lab for flexibility"]
            )

        return ResourceCheck(
            check_type='specialized_rooms',
            passed=True,
            message=f"Lab capacity sufficient ({utilization:.1f}% utilization)",
            severity='info',
            suggestions=[]
        )

    def _calculate_bottleneck_scores(
        self, classes, subjects, teachers, rooms, active_slots
    ) -> Dict[str, float]:
        """Calculate scarcity scores for different resources"""

        scores = {}

        # Teacher scarcity by subject
        for subject in subjects:
            demand = len(classes) * subject.periods_per_week
            qualified = len([t for t in teachers if subject.name in t.subjects])
            if qualified > 0:
                supply = qualified * 20  # Assume 20 periods per teacher
                scarcity = demand / supply if supply > 0 else float('inf')
                scores[f"teachers_{subject.name}"] = min(scarcity * 100, 100)

        # Room scarcity
        total_periods_needed = sum(
            len(classes) * s.periods_per_week for s in subjects
        )
        total_room_slots = len(rooms) * len(active_slots)
        if total_room_slots > 0:
            scores["rooms_general"] = (total_periods_needed / total_room_slots) * 100

        # Lab scarcity
        lab_subjects = [s for s in subjects if s.requires_lab]
        if lab_subjects:
            lab_demand = sum(len(classes) * s.periods_per_week for s in lab_subjects)
            lab_rooms = len([r for r in rooms if r.type == 'LAB'])
            if lab_rooms > 0:
                lab_supply = lab_rooms * len(active_slots)
                scores["rooms_lab"] = (lab_demand / lab_supply) * 100

        return scores

    def _generate_pre_check_recommendations(
        self, critical_issues, warnings, bottleneck_scores
    ) -> List[str]:
        """Generate recommendations from pre-check analysis"""

        recommendations = []

        # Priority 1: Address critical issues
        if critical_issues:
            recommendations.append("⚠️  CRITICAL ISSUES MUST BE RESOLVED:")
            for issue in critical_issues[:3]:  # Top 3 critical
                if issue.suggestions:
                    recommendations.append(f"  • {issue.suggestions[0]}")

        # Priority 2: Address high bottleneck scores
        high_bottlenecks = [
            (k, v) for k, v in bottleneck_scores.items()
            if v > 85
        ]
        if high_bottlenecks:
            recommendations.append("\n📊 HIGH-RISK BOTTLENECKS:")
            for resource, score in sorted(high_bottlenecks, key=lambda x: x[1], reverse=True)[:3]:
                if 'teacher' in resource:
                    subject = resource.replace('teachers_', '')
                    recommendations.append(f"  • {subject} teachers at {score:.0f}% capacity - hire more or reduce load")
                elif 'lab' in resource:
                    recommendations.append(f"  • Lab rooms at {score:.0f}% capacity - add more labs or stagger lab sessions")
                else:
                    recommendations.append(f"  • {resource} at {score:.0f}% capacity - review resource allocation")

        # Priority 3: Warnings
        if warnings and len(recommendations) < 5:
            recommendations.append("\n⚡ WARNINGS TO CONSIDER:")
            for warning in warnings[:2]:
                if warning.suggestions:
                    recommendations.append(f"  • {warning.suggestions[0]}")

        if not recommendations:
            recommendations.append("✅ Resources appear adequate - generation should be feasible")

        return recommendations

    def _analyze_violation_patterns(self, violation_log: Dict) -> Dict:
        """Analyze patterns in constraint violations"""

        patterns = {
            'most_frequent': [],
            'trending_worse': [],
            'stuck_violations': []
        }

        # Find most frequent violations
        violation_counts = defaultdict(int)
        for violations in violation_log.values():
            for v in violations:
                violation_counts[v.get('type', 'unknown')] += 1

        patterns['most_frequent'] = sorted(
            violation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return patterns

    def _identify_problem_resources(
        self, failed_solution, violation_log
    ) -> Dict[str, List]:
        """Identify specific resources causing problems"""

        problems = {
            'teachers': [],
            'rooms': [],
            'time_slots': []
        }

        # Count resource involvement in violations
        teacher_conflicts = defaultdict(int)
        room_conflicts = defaultdict(int)

        for violations in violation_log.values():
            for v in violations:
                if 'teacher' in v.get('resources', []):
                    for resource in v['resources']:
                        if 'teacher' in resource.lower():
                            teacher_conflicts[resource] += 1
                if 'room' in v.get('resources', []):
                    for resource in v['resources']:
                        if 'room' in resource.lower():
                            room_conflicts[resource] += 1

        problems['teachers'] = sorted(
            teacher_conflicts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        problems['rooms'] = sorted(
            room_conflicts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return problems

    def _generate_post_mortem_recommendations(
        self, violation_analysis, problem_resources
    ) -> List[str]:
        """Generate specific recommendations from post-mortem analysis"""

        recommendations = []

        recommendations.append("🔴 GENERATION FAILED - ROOT CAUSE ANALYSIS:")

        # Most problematic constraint type
        if violation_analysis['most_frequent']:
            top_violation = violation_analysis['most_frequent'][0][0]
            count = violation_analysis['most_frequent'][0][1]

            recommendations.append(f"\n Primary bottleneck: '{top_violation}' ({count} violations)")

            if 'teacher' in top_violation.lower():
                recommendations.append("  → Solution: Hire additional teachers or adjust workload limits")
            elif 'room' in top_violation.lower():
                recommendations.append("  → Solution: Add more rooms or optimize room allocation")
            elif 'consecutive' in top_violation.lower():
                recommendations.append("  → Solution: Relax consecutive period constraints")

        # Specific resource problems
        if problem_resources['teachers']:
            recommendations.append("\n📍 PROBLEMATIC TEACHERS:")
            for teacher, conflicts in problem_resources['teachers'][:3]:
                recommendations.append(f"  • {teacher}: {conflicts} conflicts")
            recommendations.append("  → Action: Review these teachers' schedules and availability")

        if problem_resources['rooms']:
            recommendations.append("\n📍 PROBLEMATIC ROOMS:")
            for room, conflicts in problem_resources['rooms'][:3]:
                recommendations.append(f"  • {room}: {conflicts} conflicts")
            recommendations.append("  → Action: Check if these rooms have special constraints")

        # General advice
        recommendations.append("\n💡 GENERAL RECOMMENDATIONS:")
        recommendations.append("  1. Verify all constraints are necessary (remove nice-to-haves)")
        recommendations.append("  2. Check if the problem is over-constrained")
        recommendations.append("  3. Consider a phased approach (solve core subjects first)")
        recommendations.append("  4. Review resource allocation and availability")

        return recommendations

    def generate_report(self, analysis: ResourceAnalysis) -> str:
        """Generate a human-readable report from the analysis"""

        report = []
        report.append("\n" + "="*60)
        report.append("RESOURCE SCARCITY ANALYSIS REPORT")
        report.append("="*60)

        # Feasibility
        status = "✅ FEASIBLE" if analysis.is_feasible else "❌ INFEASIBLE"
        report.append(f"\nStatus: {status}")

        # Critical Issues
        if analysis.critical_issues:
            report.append("\n🔴 CRITICAL ISSUES:")
            for issue in analysis.critical_issues:
                report.append(f"  • {issue.message}")
                for suggestion in issue.suggestions[:2]:
                    report.append(f"    → {suggestion}")

        # Warnings
        if analysis.warnings:
            report.append("\n⚠️  WARNINGS:")
            for warning in analysis.warnings[:3]:
                report.append(f"  • {warning.message}")

        # Bottlenecks
        if analysis.bottleneck_resources:
            report.append("\n📊 RESOURCE BOTTLENECKS (Scarcity Score):")
            for resource, score in sorted(
                analysis.bottleneck_resources.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]:
                bar = "█" * int(score / 10)
                report.append(f"  {resource:20} {bar} {score:.0f}%")

        # Recommendations
        if analysis.recommendations:
            report.append("\n💡 RECOMMENDATIONS:")
            for rec in analysis.recommendations:
                report.append(f"{rec}")

        return "\n".join(report)