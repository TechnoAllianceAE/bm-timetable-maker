"""
Fixed Genetic Algorithm Optimizer for Timetable Optimization
Uses DEAP library to improve timetable solutions found by CSP solver
Phase 1: Focus on academic quality and efficiency without wellness
"""

from typing import List, Tuple, Dict, Any
from deap import base, creator, tools, algorithms
import random
import numpy as np
from .models_phase1 import Timetable, TimetableEntry, OptimizationWeights, TimetableStatus

class GAOptimizerFixed:
    """
    Genetic Algorithm Optimizer for improving timetable solutions.

    The GA takes valid timetables from the CSP solver and attempts to
    improve them through evolutionary operations like crossover and mutation.

    Fitness objectives (Phase 1):
    1. Academic quality - constraint satisfaction
    2. Resource efficiency - room and time utilization
    3. Schedule compactness - minimize gaps
    4. Preference matching - soft constraints
    """

    def __init__(self, weights: OptimizationWeights = None):
        """
        Initialize GA optimizer with optimization weights.

        Args:
            weights: Optimization weights for different objectives
        """
        self.weights = weights or OptimizationWeights()
        random.seed(42)  # For reproducibility during testing

        # Setup DEAP for multi-objective optimization
        # We maximize all objectives (convert minimization to negative scores)
        if not hasattr(creator, "FitnessMulti"):
            # Weights: (academic, efficiency, compactness, preferences)
            creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0, 1.0, 1.0))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMulti)

        self.toolbox = base.Toolbox()
        self.setup_genetic_operators()

    def setup_genetic_operators(self):
        """
        Register genetic operators with DEAP toolbox.
        """
        # Register operators
        self.toolbox.register("evaluate", self._evaluate_fitness)
        self.toolbox.register("mate", self._crossover)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("select", tools.selNSGA2)  # Multi-objective selection

    def optimize(
        self,
        base_solutions: List[Timetable],
        population_size: int = 50,
        generations: int = 50
    ) -> List[Timetable]:
        """
        Optimize timetables using genetic algorithm.

        Args:
            base_solutions: Valid timetables from CSP solver
            population_size: Number of individuals in population
            generations: Number of generations to evolve

        Returns:
            List of optimized timetables (top 3-5 solutions)
        """
        if not base_solutions:
            return []

        print(f"GA Optimizer: Starting with {len(base_solutions)} base solutions")

        # Initialize population from base solutions
        population = self._initialize_population(base_solutions, population_size)

        if not population:
            print("GA Optimizer: Failed to initialize population")
            return base_solutions[:3]  # Return original solutions

        # Statistics tracking
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)

        # Run genetic algorithm
        try:
            # Use simple evolutionary algorithm
            for gen in range(generations):
                # Select the next generation
                offspring = self.toolbox.select(population, len(population))
                offspring = list(map(self.toolbox.clone, offspring))

                # Apply crossover
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < 0.7:  # Crossover probability
                        self.toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values

                # Apply mutation
                for mutant in offspring:
                    if random.random() < 0.3:  # Mutation probability
                        self.toolbox.mutate(mutant)
                        del mutant.fitness.values

                # Evaluate individuals with invalid fitness
                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = list(map(self.toolbox.evaluate, invalid_ind))
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit

                # Replace population
                population[:] = offspring

                # Print statistics every 10 generations
                if gen % 10 == 0:
                    record = stats.compile(population)
                    print(f"Gen {gen}: {record}")

        except Exception as e:
            print(f"GA Optimizer error during evolution: {e}")
            # Return best solutions found so far

        # Extract top solutions based on weighted fitness
        sorted_pop = sorted(population, key=lambda x: self._weighted_score(x.fitness.values), reverse=True)
        top_individuals = sorted_pop[:min(5, len(sorted_pop))]

        # Decode back to Timetable objects
        top_solutions = []
        for ind in top_individuals:
            try:
                timetable = self._decode_individual(ind)
                top_solutions.append(timetable)
            except Exception as e:
                print(f"Error decoding individual: {e}")
                continue

        print(f"GA Optimizer: Returning {len(top_solutions)} optimized solutions")
        return top_solutions if top_solutions else base_solutions[:3]

    def _initialize_population(self, base_solutions: List[Timetable], size: int) -> List:
        """
        Initialize GA population from base solutions.

        Creates initial population by:
        1. Including all base solutions
        2. Creating variations through mutation
        3. Filling remaining slots with random perturbations
        """
        population = []

        # Add all base solutions first
        for solution in base_solutions:
            try:
                individual = self._encode_timetable(solution)
                individual.fitness.values = self._evaluate_fitness(individual)
                population.append(individual)
            except Exception as e:
                print(f"Error encoding base solution: {e}")
                continue

        # Create variations to fill population
        while len(population) < size and base_solutions:
            # Pick a random base solution
            base = random.choice(base_solutions)
            try:
                individual = self._encode_timetable(base)
                # Apply light mutation for diversity
                self._mutate_light(individual)
                individual.fitness.values = self._evaluate_fitness(individual)
                population.append(individual)
            except Exception as e:
                print(f"Error creating variation: {e}")
                continue

            # Safety check to prevent infinite loop
            if len(population) == 0:
                break

        return population

    def _encode_timetable(self, timetable: Timetable):
        """
        Encode a Timetable object into GA individual representation.

        Each individual is a list of tuples representing timetable entries:
        (class_id, subject_id, time_slot_id, teacher_id, room_id)
        """
        encoded = [
            (e.class_id, e.subject_id, e.time_slot_id, e.teacher_id, e.room_id)
            for e in timetable.entries
        ]
        return creator.Individual(encoded)

    def _decode_individual(self, individual) -> Timetable:
        """
        Decode GA individual back to Timetable object.
        """
        entries = []
        for i, (class_id, subject_id, slot_id, teacher_id, room_id) in enumerate(individual):
            entry = TimetableEntry(
                id=f"ga_entry_{i}",
                timetable_id="ga_optimized",
                class_id=class_id,
                subject_id=subject_id,
                time_slot_id=slot_id,
                teacher_id=teacher_id,
                room_id=room_id,
                day_of_week="MONDAY",  # Will be extracted from actual time slot
                period_number=1,  # Will be extracted from actual time slot
                is_fixed=False
            )
            entries.append(entry)

        return Timetable(
            id="ga_optimized",
            school_id="school-001",  # Will be passed from context
            academic_year_id="2024",  # Will be passed from context
            name="GA Optimized Timetable",
            status=TimetableStatus.DRAFT,
            entries=entries
        )

    def _evaluate_fitness(self, individual) -> Tuple[float, float, float, float]:
        """
        Evaluate fitness of an individual timetable.

        Returns tuple of fitness values:
        (academic_score, efficiency_score, compactness_score, preference_score)

        All scores are in range [0, 1] where 1 is best.
        """
        try:
            timetable = self._decode_individual(individual)

            # Calculate individual fitness components
            academic = self._compute_academic_score(timetable)
            efficiency = self._compute_efficiency_score(timetable)
            compactness = self._compute_compactness_score(timetable)
            preferences = self._compute_preference_score(timetable)

            return (academic, efficiency, compactness, preferences)
        except Exception as e:
            print(f"Error evaluating fitness: {e}")
            return (0.0, 0.0, 0.0, 0.0)  # Worst fitness for invalid individuals

    def _compute_academic_score(self, timetable: Timetable) -> float:
        """
        Score based on academic constraint satisfaction.

        Measures:
        - All required periods are scheduled
        - No conflicts or overlaps
        - Subject distribution quality
        """
        # Basic scoring based on number of entries
        # A complete timetable should have sufficient entries
        num_entries = len(timetable.entries)
        expected_entries = 30  # Approximate for 2 classes, 3 subjects, 5 periods each

        # Score based on completeness
        completeness = min(num_entries / expected_entries, 1.0) if expected_entries > 0 else 0.0

        # TODO: Add more sophisticated scoring:
        # - Check for actual conflicts
        # - Verify all subjects have required periods
        # - Check teacher qualifications

        return completeness

    def _compute_efficiency_score(self, timetable: Timetable) -> float:
        """
        Score based on resource utilization efficiency.

        Measures:
        - Room utilization rate
        - Teacher utilization rate
        - Time slot usage efficiency
        """
        # Placeholder scoring
        # High efficiency means resources are well-utilized
        return 0.75  # TODO: Implement actual efficiency calculation

    def _compute_compactness_score(self, timetable: Timetable) -> float:
        """
        Score based on schedule compactness.

        Measures:
        - Minimal gaps in teacher schedules
        - Minimal gaps in class schedules
        - Clustered subject sessions
        """
        # Placeholder scoring
        # Compact schedules have fewer gaps
        return 0.70  # TODO: Implement gap calculation

    def _compute_preference_score(self, timetable: Timetable) -> float:
        """
        Score based on soft constraint satisfaction.

        Measures:
        - Teacher time preferences
        - Subject time preferences
        - Room preferences
        """
        # Placeholder scoring
        return 0.65  # TODO: Implement preference matching

    def _weighted_score(self, fitness_values: Tuple) -> float:
        """
        Calculate weighted score from multi-objective fitness values.

        Uses weights from OptimizationWeights to combine objectives.
        """
        academic, efficiency, compactness, preferences = fitness_values

        # Map to optimization weights
        weighted = (
            self.weights.academic_requirements * academic +
            self.weights.resource_utilization * efficiency +
            self.weights.gap_minimization * compactness +
            self.weights.teacher_preferences * preferences
        )

        return weighted

    def _crossover(self, ind1, ind2) -> Tuple:
        """
        Perform crossover between two individuals.

        Uses two-point crossover to exchange genetic material.
        Preserves timetable structure while exploring new combinations.
        """
        size = min(len(ind1), len(ind2))

        if size <= 2:
            return (ind1, ind2)  # Too small to crossover

        # Two-point crossover
        point1 = random.randint(1, size // 3)
        point2 = random.randint(2 * size // 3, size - 1)

        # Exchange segments
        ind1[point1:point2], ind2[point1:point2] = ind2[point1:point2], ind1[point1:point2]

        return (ind1, ind2)

    def _mutate(self, individual) -> Tuple:
        """
        Mutate an individual timetable.

        Mutation operations:
        - Swap two random entries
        - Change teacher for an entry
        - Change room for an entry
        - Swap time slots
        """
        mutation_prob = 0.1  # Probability of mutating each gene

        for i in range(len(individual)):
            if random.random() < mutation_prob:
                mutation_type = random.choice(['swap', 'teacher', 'room', 'slot'])

                if mutation_type == 'swap' and len(individual) > 1:
                    # Swap with another random entry
                    j = random.randint(0, len(individual) - 1)
                    individual[i], individual[j] = individual[j], individual[i]

                elif mutation_type in ['teacher', 'room', 'slot']:
                    # Modify specific component
                    entry = list(individual[i])

                    if mutation_type == 'teacher':
                        # TODO: Select from qualified teachers
                        pass  # Keep original for now
                    elif mutation_type == 'room':
                        # TODO: Select from available rooms
                        pass  # Keep original for now
                    elif mutation_type == 'slot':
                        # TODO: Select from available slots
                        pass  # Keep original for now

                    individual[i] = tuple(entry)

        return (individual,)

    def _mutate_light(self, individual):
        """
        Light mutation for population initialization.

        Applies smaller changes to preserve solution validity.
        """
        if len(individual) > 1 and random.random() < 0.3:
            # Just swap two entries
            i = random.randint(0, len(individual) - 1)
            j = random.randint(0, len(individual) - 1)
            individual[i], individual[j] = individual[j], individual[i]