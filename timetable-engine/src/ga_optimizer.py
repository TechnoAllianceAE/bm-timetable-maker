from typing import List, Tuple, Dict, Any
from deap import base, creator, tools, algorithms
import random
import numpy as np
from .models_phase1 import Timetable, TimetableEntry, OptimizationWeights, TimetableStatus

class GAOptimizer:
    """
    Genetic Algorithm Optimizer for Timetable using DEAP NSGA-II.
    Optimizes feasible CSP solutions for multi-objective fitness.
    """

    def __init__(self, weights: OptimizationWeights = None):
        self.weights = weights or OptimizationWeights()
        random.seed(42)  # Reproducible

        # DEAP setup for multi-objective (maximize all 4 objectives)
        # Check if already created to avoid re-registration errors
        if not hasattr(creator, "FitnessMulti"):
            creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0, 1.0, 1.0))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMulti)

        self.toolbox = base.Toolbox()

        # Individual: List of entry indices or encoded timetable (simplified: list of (class_id, subject_id, slot_id, teacher_id, room_id) tuples
        # For evolution, represent as permutation or fixed-length list

    def optimize(self, base_solutions: List[Timetable], population_size: int = 50, generations: int = 50) -> List[Timetable]:
        """
        Optimize base CSP solutions using GA.
        Returns top ranked timetables.
        """
        if not base_solutions:
            return []

        # Initialize population from base solutions + random perturbations
        pop = self._initialize_population(base_solutions, population_size)

        # Register genetic operators
        self.toolbox.register("individual", self._create_individual, creator.Individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self._evaluate_fitness)
        self.toolbox.register("mate", self._crossover)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("select", tools.selNSGA2)

        # Run GA
        pop = algorithms.eaMuPlusLambda(pop, self.toolbox, mu=population_size, lambda_=population_size,
                                        cxpb=0.7, mutpb=0.3, ngen=generations, verbose=False)

        # Extract top individuals
        fits = [ind.fitness.values for ind in pop]
        top_indices = np.argsort([sum(w * f for w, f in zip(self.weights.__dict__.values(), fit)) for fit in fits])[-3:]  # Weighted sum for ranking

        top_solutions = [self._decode_individual(pop[i]) for i in top_indices]

        return top_solutions

    def _initialize_population(self, base_solutions: List[Timetable], size: int) -> List:
        """Initialize population from base solutions and random variations."""
        pop = []
        # Add base solutions
        for sol in base_solutions[:min(10, len(base_solutions))]:  # Up to 10 bases
            ind = self._encode_timetable(sol)
            ind.fitness.values = self._evaluate_fitness(ind)
            pop.append(ind)

        # Fill with random individuals (perturbations or random valid)
        while len(pop) < size:
            # Simple random: Shuffle entries from bases or generate random assignments (validate later)
            base = random.choice(base_solutions)
            ind = self._encode_timetable(base)
            # Mutate slightly to diversify
            self._mutate(ind, 0.1)  # Low mutation for initial
            ind.fitness.values = self._evaluate_fitness(ind)
            pop.append(ind)

        return pop

    def _encode_timetable(self, timetable: Timetable):
        """Encode Timetable to individual (list of entry tuples)."""
        ind = creator.Individual([(e.class_id, e.subject_id, e.time_slot_id, e.teacher_id, e.room_id) for e in timetable.entries])
        return ind

    def _decode_individual(self, individual) -> Timetable:
        """Decode individual to Timetable."""
        entries = [
            TimetableEntry(
                id=f"ga_entry_{i}",
                timetable_id="ga_opt",
                class_id=c,
                subject_id=s,
                time_slot_id=ts,
                teacher_id=t,
                room_id=r,
                day_of_week="MONDAY",  # TODO: Extract from time slot
                period_number=1,  # TODO: Extract from time slot
                is_fixed=False
            )
            for i, (c, s, ts, t, r) in enumerate(individual)
        ]
        return Timetable(
            id="ga_opt",
            school_id="school-001",
            academic_year_id="2024",
            entries=entries,
            status="DRAFT"
        )

    def _evaluate_fitness(self, individual) -> Tuple[float, float, float, float]:
        """Multi-objective fitness: (academic, wellness, efficiency, preference) - higher better."""
        timetable = self._decode_individual(individual)

        # Academic: % constraint satisfaction (stub: 1.0 if valid)
        academic = self._compute_academic_score(timetable)

        # Wellness: Balance (low std dev loads), low stress (few negatives)
        wellness = self._compute_wellness_score(timetable)

        # Efficiency: Minimize gaps/idle (total assigned / total possible)
        efficiency = self._compute_efficiency_score(timetable)

        # Preference: Match teacher prefs (stub: 0.8)
        preference = self._compute_preference_score(timetable)

        return academic, wellness, efficiency, preference

    def _compute_academic_score(self, timetable: Timetable) -> float:
        """Academic fitness: Period counts, no conflicts."""
        # Stub: Count entries / expected
        expected = len(timetable.entries)  # Assume all good
        return min(1.0, len(timetable.entries) / expected) if expected > 0 else 0.0

    def _compute_wellness_score(self, timetable: Timetable) -> float:
        """
        Wellness scoring - Phase 1 placeholder.
        In Phase 2, this will evaluate teacher workload balance.
        For now, return a neutral score.
        """
        # TODO: In Phase 2, implement actual wellness scoring:
        # - Check teacher workload distribution
        # - Evaluate consecutive teaching periods
        # - Measure schedule gaps
        return 0.7  # Neutral wellness score

    def _compute_efficiency_score(self, timetable: Timetable) -> float:
        """Efficiency: No gaps, full utilization."""
        # Stub: Assume high
        return 0.8  # Placeholder; compute actual gaps

    def _compute_preference_score(self, timetable: Timetable) -> float:
        """Preferences: Match teacher availability/prefs."""
        # Stub
        return 0.7

    def _crossover(self, ind1, ind2):
        """Wellness-preserving crossover: Swap subsets of entries."""
        # Simple two-point crossover on list
        size = min(len(ind1), len(ind2))
        cxpoint1 = random.randint(1, int(size * 0.3)) if size > 3 else 1
        cxpoint2 = random.randint(cxpoint1, int(size * 0.7)) if size > 3 else min(2, size - 1)

        ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] = ind2[cxpoint1:cxpoint2], ind1[cxpoint1:cxpoint2]

        # Validate feasibility (optional, penalize in fitness)
        return ind1, ind2

    def _mutate(self, individual, indpb: float) -> None:
        """Mutation: Random swap or change in entries (e.g., swap teacher/room)."""
        for i in range(len(individual)):
            if random.random() < indpb:
                # Swap two entries or change teacher
                if len(individual) > 1 and random.random() < 0.5:
                    j = random.randint(0, len(individual) - 1)
                    individual[i], individual[j] = individual[j], individual[i]
                else:
                    # Change teacher_id in tuple (random from possible)
                    current = list(individual[i])
                    current[3] = 'random_teacher_id'  # Stub; in full, sample qualified
                    individual[i] = tuple(current)

        # Re-eval fitness after mutation
        del individual.fitness.values
        individual.fitness.values = self._evaluate_fitness(individual)

# Example usage
if __name__ == "__main__":
    # Mock base solutions
    mock_timetables = []  # From CSP
    optimizer = GAOptimizer()
    optimized = optimizer.optimize(mock_timetables)
    print(f"Optimized {len(optimized)} solutions")