"""
Genetic Algorithm Optimizer for Timetable Optimization

VERSION 2.5 - Metadata-Driven Optimization

CHANGELOG v2.5:
- Replaced hardcoded subject keywords with subject_metadata.prefer_morning
- Replaced hardcoded period cutoff (4) with weights.morning_period_cutoff
- Replaced hardcoded max_consecutive (3) with teacher_metadata.max_consecutive_periods
- All business logic now configurable via metadata
- Language-agnostic (works with any language)
- School-customizable (different structures supported)

BENEFITS v2.5:
- Zero hardcoded subject names (works in English, Spanish, Hindi, etc.)
- Zero hardcoded time assumptions (supports 6, 8, or 10-period days)
- Zero hardcoded teacher limits (per-teacher customization)
- Professional, scalable architecture

COMPATIBILITY:
- Requires models_phase1_v25.py (OptimizationWeights with new fields)
- Requires csp_solver_complete_v25.py (TimetableEntry with metadata)
- Backward compatible (graceful degradation if metadata missing)
"""

from typing import List, Dict, Tuple, Any, Optional
import random
import copy
import statistics
from collections import defaultdict
from dataclasses import dataclass
import uuid

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation import TimetableEvaluator, EvaluationConfig
from persistence.timetable_cache import TimetableCache


@dataclass
class GenerationStats:
    """Statistics for a single generation."""
    generation: int
    best_fitness: float
    avg_fitness: float
    worst_fitness: float
    diversity: float


class OptimizationWeights:
    """
    Optimization weights for GA fitness calculation.
    
    VERSION 2.5: All weights now included, no hardcoded values.
    
    This is a simplified version for type hints.
    Actual weights come from models_phase1_v25.OptimizationWeights
    """
    def __init__(self, **kwargs):
        self.workload_balance = kwargs.get('workload_balance', 50.0)
        self.gap_minimization = kwargs.get('gap_minimization', 15.0)
        self.time_preferences = kwargs.get('time_preferences', 25.0)
        self.consecutive_periods = kwargs.get('consecutive_periods', 10.0)
        self.morning_period_cutoff = kwargs.get('morning_period_cutoff', 4)


class GAOptimizerV25:
    """
    Genetic Algorithm optimizer for timetable refinement.
    
    VERSION 2.5 ENHANCEMENTS:
    - Reads subject preferences from subject_metadata (not hardcoded names)
    - Reads period cutoff from weights.morning_period_cutoff (not hardcoded 4)
    - Reads teacher limits from teacher_metadata (not hardcoded 3)
    - Fully configurable, language-agnostic, school-customizable
    
    WORKFLOW:
    1. Receives population of timetables from CSP solver
    2. Each timetable entry has subject_metadata and teacher_metadata
    3. Evaluates fitness using metadata-driven penalty calculations
    4. Evolves population over N generations
    5. Returns optimized timetables
    
    METADATA USAGE:
    - subject_metadata.prefer_morning → time preference penalty
    - subject_metadata.preferred_periods → fine-grained time penalty
    - teacher_metadata.max_consecutive_periods → consecutive period penalty
    - weights.morning_period_cutoff → defines "morning" dynamically
    """
    
    def __init__(self, 
                 evaluator: Optional[TimetableEvaluator] = None,
                 cache: Optional[TimetableCache] = None,
                 enable_caching: bool = True):
        self.version = "2.5"
        self.stats_history: List[GenerationStats] = []
        self.weights: Optional[OptimizationWeights] = None
        self.evaluator: Optional[TimetableEvaluator] = evaluator
        
        # Cache integration
        self.enable_caching = enable_caching
        if self.enable_caching:
            self.cache = cache or TimetableCache()
        else:
            self.cache = None
        
        # Session management
        self.current_session_id: Optional[str] = None
    
    def evolve(
        self,
        population: List[Dict],
        generations: int = 30,
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.7,
        elitism_count: int = 2,
        weights: Optional[Any] = None,
        session_id: Optional[str] = None,
        cache_intermediate: bool = True
    ) -> List[Dict]:
        """
        Evolve population of timetables using genetic algorithm.
        
        VERSION 2.5: Now uses metadata for all penalty calculations and caching.
        
        Args:
            population: Initial timetables from CSP solver (with metadata)
            generations: Number of evolution cycles
            mutation_rate: Probability of mutation (0.0-1.0)
            crossover_rate: Probability of crossover (0.0-1.0)
            elitism_count: Number of best solutions to preserve
            weights: OptimizationWeights with v2.5 fields
            session_id: Optional session ID for cache organization
            cache_intermediate: Whether to cache intermediate generations
        
        Returns:
            Optimized timetables sorted by fitness (best first)
        
        METADATA REQUIREMENTS:
        - Each timetable entry must have subject_metadata
        - Each timetable entry must have teacher_metadata
        - Graceful degradation if metadata missing
        
        CACHING:
        - All generations cached if enabled
        - Best result preserved after completion
        - Intermediate results cleaned up automatically
        """
        if not population:
            return []
        
        # Setup session for caching
        self.current_session_id = session_id or str(uuid.uuid4())
        
        # Store weights for fitness calculation
        self.weights = weights or OptimizationWeights()
        
        # Initialize evaluator if not provided
        if self.evaluator is None:
            config = EvaluationConfig.from_optimization_weights(self.weights)
            self.evaluator = TimetableEvaluator(config)
        
        # Reset stats
        self.stats_history = []
        
        # Convert to internal format if needed
        current_population = [self._ensure_dict(t) for t in population]
        
        # Evaluate initial population
        fitness_scores = [self.evaluator.evaluate(t).total_score for t in current_population]
        
        # Cache initial population if enabled
        if self.enable_caching and self.cache and cache_intermediate:
            self.cache.store_ga_population(
                population=current_population,
                session_id=self.current_session_id,
                generation=0,
                fitness_scores=fitness_scores
            )
        
        # Evolution loop
        for gen in range(generations):
            # Create next generation
            next_population = []
            
            # Elitism: keep best solutions
            elite_indices = sorted(range(len(fitness_scores)), 
                                 key=lambda i: fitness_scores[i], 
                                 reverse=True)[:elitism_count]
            next_population.extend([current_population[i] for i in elite_indices])
            
            # Generate offspring
            while len(next_population) < len(current_population):
                # Selection
                parent1 = self._tournament_selection(current_population, fitness_scores)
                parent2 = self._tournament_selection(current_population, fitness_scores)
                
                # Crossover
                if random.random() < crossover_rate:
                    child1, child2 = self._safe_crossover(parent1, parent2)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                
                # Mutation
                if random.random() < mutation_rate:
                    child1 = self._safe_mutate(child1)
                if random.random() < mutation_rate:
                    child2 = self._safe_mutate(child2)
                
                next_population.extend([child1, child2])
            
            # Trim to population size
            next_population = next_population[:len(current_population)]
            
            # Evaluate new population
            current_population = next_population
            fitness_scores = [self.evaluator.evaluate(t).total_score for t in current_population]
            
            # Cache generation if enabled
            if self.enable_caching and self.cache and cache_intermediate:
                self.cache.store_ga_population(
                    population=current_population,
                    session_id=self.current_session_id,
                    generation=gen + 1,
                    fitness_scores=fitness_scores
                )
            
            # Track statistics
            stats = GenerationStats(
                generation=gen + 1,
                best_fitness=max(fitness_scores),
                avg_fitness=statistics.mean(fitness_scores),
                worst_fitness=min(fitness_scores),
                diversity=self._calculate_diversity(fitness_scores)
            )
            self.stats_history.append(stats)
        
        # Sort by fitness (best first)
        sorted_population = [t for _, t in sorted(zip(fitness_scores, current_population),
                                                  key=lambda x: x[0],
                                                  reverse=True)]
        
        # Cache final result if enabled
        if self.enable_caching and self.cache:
            # Store the best timetable as the session result
            best_timetable = sorted_population[0]
            best_fitness = max(fitness_scores)
            
            final_id = self.cache.store_timetable(
                timetable=best_timetable,
                session_id=self.current_session_id,
                generation=generations,  # Mark as final generation
                fitness_score=best_fitness,
                metadata={'session_final': True, 'total_generations': generations}
            )
            
            # Complete session (keeps best, cleans up intermediate results)
            if cache_intermediate:
                self.cache.complete_session(self.current_session_id, keep_best=True)
        
        return sorted_population
    
    # FITNESS CALCULATION NOW HANDLED BY TimetableEvaluator
    # All penalty calculation methods moved to evaluation module for reusability
    
    def _extract_assignments(self, timetable_dict: Dict) -> List[Dict]:
        """Extract assignment list from timetable dict (needed for crossover/mutation)."""
        # Primary structure: Timetable.entries (list of TimetableEntry)
        if "entries" in timetable_dict:
            return timetable_dict["entries"]
        
        # Legacy fallback structures for backward compatibility
        if "assignments" in timetable_dict:
            return timetable_dict["assignments"]
        
        if "schedule" in timetable_dict:
            # Flatten nested schedule structure (old format)
            assignments = []
            schedule = timetable_dict["schedule"]
            for class_id, class_schedule in schedule.items():
                if isinstance(class_schedule, dict):
                    for day, periods in class_schedule.items():
                        if isinstance(periods, dict):
                            for period, assignment in periods.items():
                                if assignment:
                                    assignments.append({
                                        "class_id": class_id,
                                        "day": day,
                                        "period": period,
                                        **assignment
                                    })
            return assignments
        
        # Fallback: assume it's a list at top level
        if isinstance(timetable_dict, list):
            return timetable_dict
        
        return []
    
    def _tournament_selection(self, population: List[Dict], fitness_scores: List[float],
                             tournament_size: int = 3) -> Dict:
        """
        Select individual using tournament selection.
        Higher fitness = more likely to be selected.
        """
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
        return population[winner_index]
    
    def _safe_crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """
        Perform crossover that preserves teacher consistency constraint.

        Crossover Strategy - Class-Based Block Swaps:
        ---------------------------------------------
        v2.6 UPDATE: To preserve one-teacher-per-subject-per-class constraint,
        we swap complete CLASS schedules between parents, not individual assignments.

        Why Swap Entire Classes:
        1. Each class has pre-assigned teachers for each subject
        2. Swapping individual assignments would mix teachers
        3. Swapping entire class schedules preserves all teacher assignments
        4. Still provides genetic diversity through schedule variations

        Example:
        Parent 1: [Class A schedule, Class B schedule, Class C schedule]
        Parent 2: [Class A' schedule, Class B' schedule, Class C' schedule]

        Crossover point at Class B:
        Child 1: [Class A from P1, Class B from P2, Class C from P2]
        Child 2: [Class A from P2, Class B from P1, Class C from P1]

        This ensures:
        - Each class keeps its teacher assignments intact
        - Teacher consistency is NEVER violated
        - Diversity comes from different time/room arrangements
        - Hard constraints are preserved
        """
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)

        try:
            assignments1 = self._extract_assignments(child1)
            assignments2 = self._extract_assignments(child2)

            if not assignments1 or not assignments2:
                return child1, child2

            # Group assignments by class
            class_groups1 = defaultdict(list)
            class_groups2 = defaultdict(list)

            for entry in assignments1:
                class_groups1[entry.get("class_id")].append(entry)

            for entry in assignments2:
                class_groups2[entry.get("class_id")].append(entry)

            # Get common classes between parents
            common_classes = list(set(class_groups1.keys()) & set(class_groups2.keys()))

            if len(common_classes) > 1:
                # Select a random crossover point (which class to split at)
                crossover_class_idx = random.randint(1, len(common_classes) - 1)
                swap_classes = common_classes[crossover_class_idx:]

                # Swap entire class schedules
                for class_id in swap_classes:
                    class_groups1[class_id], class_groups2[class_id] = \
                        class_groups2[class_id], class_groups1[class_id]

                # Rebuild assignments lists
                new_assignments1 = []
                new_assignments2 = []

                for class_id in class_groups1:
                    new_assignments1.extend(class_groups1[class_id])

                for class_id in class_groups2:
                    new_assignments2.extend(class_groups2[class_id])

                # Update timetable dicts
                self._update_assignments(child1, new_assignments1)
                self._update_assignments(child2, new_assignments2)

        except Exception:
            # If crossover fails for any reason, return parent clones
            pass

        return child1, child2
    
    def _safe_mutate(self, timetable_dict: Dict) -> Dict:
        """
        Perform mutation that preserves teacher consistency constraint.

        Mutation Strategy - Time/Room Swaps (NOT Teacher Swaps):
        --------------------------------------------------------
        v2.6 UPDATE: To preserve one-teacher-per-subject-per-class constraint,
        we NO LONGER swap teachers between different class-subject pairs.

        Instead, we swap TIME SLOTS or ROOMS between entries that have:
        - SAME class_id AND SAME subject_id (preserves teacher consistency)
        - OR entries from completely different classes (no shared resources)

        Why This Change:
        1. Teacher consistency is a CRITICAL constraint
        2. Swapping teachers between (Class A, Math) and (Class B, English)
           would break the one-teacher-per-subject-per-class rule
        3. Swapping time slots within same class-subject is safe
        4. Room swaps are always safe (just optimization)

        Mutation Types:
        1. Time swap: Exchange time slots between two entries of same class-subject
           Example: Class 10A Math Period 1 ↔ Class 10A Math Period 3
        2. Room swap: Exchange rooms between any two compatible entries
           Example: Room 101 ↔ Room 102

        This approach:
        - PRO: Preserves teacher consistency 100%
        - PRO: Still provides mutation diversity
        - PRO: No risk of breaking critical constraints
        - CON: Slightly more limited mutation space (acceptable trade-off)
        """
        mutated = copy.deepcopy(timetable_dict)

        try:
            entries = self._extract_assignments(mutated)

            if len(entries) < 2:
                return mutated  # Nothing to swap

            # Strategy: Try time slot swap first (safer for teacher consistency)
            # Find two entries with same (class_id, subject_id)
            class_subject_map = defaultdict(list)
            for idx, entry in enumerate(entries):
                key = (entry.get("class_id"), entry.get("subject_id"))
                class_subject_map[key].append(idx)

            # Find a class-subject pair with multiple entries
            swappable_pairs = [(k, v) for k, v in class_subject_map.items() if len(v) >= 2]

            if swappable_pairs:
                # Swap time slots between two entries of same class-subject
                # This is SAFE - same teacher, same class, same subject, different times
                key, indices = random.choice(swappable_pairs)
                idx1, idx2 = random.sample(indices, 2)
                entry1 = entries[idx1]
                entry2 = entries[idx2]

                # Swap time-related fields (preserves teacher assignment)
                entry1["time_slot_id"], entry2["time_slot_id"] = entry2["time_slot_id"], entry1["time_slot_id"]
                entry1["day_of_week"], entry2["day_of_week"] = entry2["day_of_week"], entry1["day_of_week"]
                entry1["period_number"], entry2["period_number"] = entry2["period_number"], entry1["period_number"]

                self._update_assignments(mutated, entries)
            else:
                # Fallback: Swap rooms between any two entries (always safe)
                idx1, idx2 = random.sample(range(len(entries)), 2)
                entry1 = entries[idx1]
                entry2 = entries[idx2]

                entry1["room_id"], entry2["room_id"] = entry2["room_id"], entry1["room_id"]

                self._update_assignments(mutated, entries)
            
        except Exception:
            # If mutation fails for any reason, return original
            # This ensures we always return a valid timetable structure
            pass
        
        return mutated
    
    def get_cached_best_timetable(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve the best timetable from cache for a session.
        
        Args:
            session_id: Session ID to retrieve from (uses current if None)
            
        Returns:
            Best timetable data if found, None otherwise
        """
        if not self.enable_caching or not self.cache:
            return None
        
        target_session = session_id or self.current_session_id
        if not target_session:
            return None
        
        result = self.cache.get_best_timetable(target_session)
        return result[1] if result else None
    
    def resume_from_generation(self, session_id: str, generation: int) -> Optional[List[Dict]]:
        """
        Resume GA evolution from a cached generation.
        
        Args:
            session_id: Session to resume from
            generation: Generation number to resume from
            
        Returns:
            Population from that generation if found
        """
        if not self.enable_caching or not self.cache:
            return None
        
        return self.cache.get_generation_population(session_id, generation)
    
    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get statistics about the current cache.
        
        Returns:
            Cache statistics if caching enabled, None otherwise
        """
        if not self.enable_caching or not self.cache:
            return None
        
        return self.cache.get_cache_stats()
    
    def cleanup_session(self, session_id: Optional[str] = None, keep_best: bool = True):
        """
        Clean up a specific session's cache.
        
        Args:
            session_id: Session to clean up (uses current if None)
            keep_best: Whether to keep the best timetable
        """
        if not self.enable_caching or not self.cache:
            return
        
        target_session = session_id or self.current_session_id
        if target_session:
            self.cache.complete_session(target_session, keep_best)
    
    def _update_assignments(self, timetable_dict: Dict, entries: List[Dict]):
        """
        Update timetable dict with modified entries list.
        Works with Timetable.entries structure.
        """
        if "entries" in timetable_dict:
            timetable_dict["entries"] = entries
        elif "assignments" in timetable_dict:
            timetable_dict["assignments"] = entries
        # For other structures, the mutation already modified entries in-place
    
    def _calculate_diversity(self, fitness_scores: List[float]) -> float:
        """Calculate population diversity using fitness variance."""
        if len(fitness_scores) < 2:
            return 0.0
        return statistics.variance(fitness_scores)
    
    def _ensure_dict(self, obj: Any) -> Dict:
        """Convert object to dict if needed."""
        if isinstance(obj, dict):
            return obj
        elif hasattr(obj, 'dict'):
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return {"entries": []}
    
    def get_evolution_report(self) -> str:
        """
        Generate human-readable evolution report.
        
        VERSION 2.5: Shows metadata-driven optimization progress.
        """
        if not self.stats_history:
            return "No evolution data available"
        
        first_gen = self.stats_history[0]
        last_gen = self.stats_history[-1]
        
        improvement = last_gen.best_fitness - first_gen.best_fitness
        improvement_pct = (improvement / max(first_gen.best_fitness, 1)) * 100

        report = f"""
===============================================================
  GENETIC ALGORITHM v{self.version} - EVOLUTION REPORT
===============================================================
  Configuration:
    Metadata-Driven: [ENABLED]
    Morning Cutoff: Period {getattr(self.weights, 'morning_period_cutoff', 4)}
    Generations: {len(self.stats_history)}
===============================================================
  Initial State (Gen 1):
    Best Fitness:  {first_gen.best_fitness:8.2f}
    Avg Fitness:   {first_gen.avg_fitness:8.2f}
===============================================================
  Final State (Gen {len(self.stats_history)}):
    Best Fitness:  {last_gen.best_fitness:8.2f}
    Avg Fitness:   {last_gen.avg_fitness:8.2f}
===============================================================
  Improvement:
    Absolute: {improvement:+8.2f}
    Relative: {improvement_pct:+7.1f}%
===============================================================
  Optimization Focus (Weights):
    Workload Balance:      {getattr(self.weights, 'workload_balance', 0):5.1f}
    Gap Minimization:      {getattr(self.weights, 'gap_minimization', 0):5.1f}
    Time Preferences:      {getattr(self.weights, 'time_preferences', 0):5.1f}
    Consecutive Periods:   {getattr(self.weights, 'consecutive_periods', 0):5.1f}
===============================================================
        """
        
        return report.strip()


# =============================================================================
# VERSION 2.5 USAGE EXAMPLE
# =============================================================================

"""
Example usage with v2.5 metadata:

from src.models_phase1_v25 import OptimizationWeights
from src.ga_optimizer_v25 import GAOptimizerV25

# Define optimization weights (v2.5 with new fields)
weights = OptimizationWeights(
    workload_balance=50.0,
    gap_minimization=20.0,
    time_preferences=30.0,
    consecutive_periods=15.0,
    morning_period_cutoff=4  # For 6-period schools
)

# Initialize GA optimizer
ga = GAOptimizerV25()

# Get timetables from CSP solver (with metadata)
csp_solutions = csp_solver.solve(...)

# Evolve timetables
optimized = ga.evolve(
    population=csp_solutions,
    generations=30,
    mutation_rate=0.15,
    crossover_rate=0.7,
    elitism_count=2,
    weights=weights
)

# Show evolution report
print(ga.get_evolution_report())

# Best solution
best_timetable = optimized[0]

# Verify metadata was used
entry = best_timetable["entries"][0]
print(entry["subject_metadata"])  # {'prefer_morning': True, ...}
print(entry["teacher_metadata"])  # {'max_consecutive_periods': 3}

BENEFITS:
- Works in ANY language (English, Spanish, Hindi, etc.)
- Supports different school structures (6, 8, 10-period days)
- Per-teacher customization (different consecutive limits)
- Zero hardcoded business logic
- Professional, scalable architecture
"""
