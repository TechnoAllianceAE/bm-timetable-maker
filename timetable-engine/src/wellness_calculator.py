from typing import Dict, List, Any
import numpy as np
from .models import Timetable, Teacher, TeacherWorkloadConfig, WellnessAnalysis, BurnoutRiskLevel, WellnessImpact

class WellnessCalculator:
    """
    Real-time wellness calculations for timetables.
    Computes scores, risks, and recommendations based on PRD wellness constraints.
    """

    def __init__(self):
        self.wellness_weights = {
            'balance': 0.30,      # Workload distribution
            'stress': 0.30,       # Consecutive periods, gaps
            'preferences': 0.20,  # Match prefs
            'burnout_proxy': 0.20 # Overload threshold
        }

    def calculate(self, timetable: Timetable, teachers: List[Teacher], configs: List[TeacherWorkloadConfig]) -> WellnessAnalysis:
        """
        Compute wellness analysis for a timetable.
        """
        # Map configs by teacher_id
        config_map = {cfg.teacher_id: cfg for cfg in configs}

        teacher_scores = {}
        department_scores = {}
        issues = []
        recommendations = []
        burnout_risks = {}
        total_entries = len(timetable.entries)

        if total_entries == 0:
            return WellnessAnalysis(
                overall_score=0.0,
                teacher_scores={},
                department_scores={},
                issues=[],
                improvements=[],
                burnout_risks={}
            )

        # Group entries by teacher and day/slot for metrics
        teacher_loads = {t.id: {'daily': {}, 'weekly': 0, 'consecutive': {}, 'gaps': 0, 'dept': t.subjects[0] if t.subjects else 'General'} for t in teachers}  # Assume first subject as dept

        for entry in timetable.entries:
            t_id = entry.teacher_id
            if t_id not in teacher_loads:
                continue

            load = teacher_loads[t_id]
            # Assume slot has day (from time_slot_id; stub here, need to join)
            day = 'Monday'  # Stub; in full, fetch from TimeSlot
            slot_num = 1  # Stub

            if day not in load['daily']:
                load['daily'][day] = 0
                load['consecutive'][day] = 0

            load['daily'][day] += 1
            load['weekly'] += 1

            # Consecutive stub: Increment if sequential
            load['consecutive'][day] += 1

            # Prep/correction: Add based on subject
            prep = 1.0  # Stub per period
            correction = 0.5 * 40  # Stub student count
            load['prep'] = load.get('prep', 0) + prep
            load['correction'] = load.get('correction', 0) + correction

            # Gaps stub
            load['gaps'] += 5  # Min 5 min gap

        # Compute per teacher
        for t_id, load in teacher_loads.items():
            t = next((te for te in teachers if te.id == t_id), None)
            if not t:
                continue

            cfg = config_map.get(t_id, TeacherWorkloadConfig(teacher_id=t_id))

            # Daily max violation
            max_daily = max(load['daily'].values() or [0])
            daily_viol = max(0, max_daily - cfg.max_periods_per_day) / cfg.max_periods_per_day

            # Weekly
            weekly_viol = max(0, load['weekly'] - cfg.max_periods_per_week) / cfg.max_periods_per_week

            # Consecutive max
            max_consec = max(load['consecutive'].values() or [0])
            consec_viol = max(0, max_consec - cfg.max_consecutive_periods) / cfg.max_consecutive_periods

            # Stress score: High if violations or low gaps
            stress_score = 100 - (daily_viol + weekly_viol + consec_viol + (load['gaps'] / total_entries if total_entries else 0)) * 50  # 0-100, lower better? Invert for wellness
            stress_score = max(0, min(100, stress_score))

            # Burnout risk: Rule-based
            overload = (daily_viol + weekly_viol) > 0.2
            high_consec = max_consec > cfg.max_consecutive_periods
            risk = BurnoutRiskLevel.LOW
            if overload or high_consec:
                risk = BurnoutRiskLevel.MEDIUM if (daily_viol + weekly_viol) < 0.5 else BurnoutRiskLevel.HIGH
            if consec_viol > 0.5:
                risk = BurnoutRiskLevel.CRITICAL
            burnout_risks[t_id] = risk

            # Preferences match stub (assume 80%)
            pref_match = 0.8

            # Wellness score for teacher
            total_work = load['weekly'] + load.get('prep', 0) + load.get('correction', 0)
            capacity = cfg.max_periods_per_week + cfg.prep_time_required * len(t.subjects) / 60 + cfg.correction_time_per_student * 40 * len(t.subjects)  # Stub students
            utilization = min(1.0, total_work / capacity)

            # Weighted score
            balance_contrib = 1.0 - utilization  # Lower utilization better balance?
            stress_contrib = stress_score / 100
            pref_contrib = pref_match
            burnout_contrib = 1.0 if risk == BurnoutRiskLevel.LOW else 0.5 if risk == BurnoutRiskLevel.MEDIUM else 0.0

            score = (self.wellness_weights['balance'] * balance_contrib +
                     self.wellness_weights['stress'] * stress_contrib +
                     self.wellness_weights['preferences'] * pref_contrib +
                     self.wellness_weights['burnout_proxy'] * burnout_contrib) * 100

            teacher_scores[t_id] = score

            # Dept score
            dept = load['dept']
            if dept not in department_scores:
                department_scores[dept] = []
            department_scores[dept].append(score)

            # Issues and recs
            if daily_viol > 0:
                issues.append(f"Teacher {t_id} daily overload: {max_daily} > {cfg.max_periods_per_day}")
                recommendations.append(f"Reduce daily periods for {t_id} by swapping with another teacher")

            if high_consec:
                issues.append(f"Teacher {t_id} consecutive periods: {max_consec} > {cfg.max_consecutive_periods}")
                recommendations.append(f"Insert breaks for {t_id} after {cfg.max_consecutive_periods} periods")

        # Overall scores
        if teacher_scores:
            overall_teacher_avg = np.mean(list(teacher_scores.values()))
            balance_std = np.std(list(teacher_scores.values())) / overall_teacher_avg if overall_teacher_avg > 0 else 0
            overall_score = overall_teacher_avg * (1 - balance_std)  # Penalize imbalance
        else:
            overall_score = 0.0

        # Dept scores avg
        for dept, scores in department_scores.items():
            department_scores[dept] = np.mean(scores)

        # Final analysis
        return WellnessAnalysis(
            overall_score=overall_score,
            teacher_scores=teacher_scores,
            department_scores=department_scores,
            issues=issues,
            improvements=recommendations,  # Rename to improvements
            burnout_risks=burnout_risks
        )

    def compute_fitness_component(self, timetable: Timetable, teachers: List[Teacher], configs: List[TeacherWorkloadConfig]) -> float:
        """Compute wellness fitness for GA (0-1)."""
        analysis = self.calculate(timetable, teachers, configs)
        return analysis.overall_score / 100  # Normalize

# Example usage
if __name__ == "__main__":
    # Mock data
    mock_timetable = Timetable(id="test", entries=[])  # Add mocks
    mock_teachers = []  # Add mocks
    mock_configs = []
    calc = WellnessCalculator()
    analysis = calc.calculate(mock_timetable, mock_teachers, mock_configs)
    print(f"Overall wellness score: {analysis.overall_score}")