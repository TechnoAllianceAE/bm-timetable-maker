# Timetable Ranking Architecture

## Current State
- GA does both generation AND ranking
- Fitness function buried inside GA class
- Inefficient for just ranking existing timetables

## Proposed Separation

### 1. Core Evaluator (For Ranking)
```python
# src/evaluation/timetable_evaluator.py
class TimetableEvaluator:
    """Pure evaluation logic - no genetic operations"""
    
    def evaluate(self, timetable: Dict) -> EvaluationResult:
        """Fast scoring for ranking purposes"""
        pass
    
    def batch_evaluate(self, timetables: List[Dict]) -> List[EvaluationResult]:
        """Efficient batch processing"""
        pass
    
    def compare(self, tt1: Dict, tt2: Dict) -> ComparisonResult:
        """Direct comparison between two timetables"""
        pass
```

### 2. Generation Algorithms (For Creating)
```python
# src/algorithms/generators/
class GAGenerator:
    """Uses TimetableEvaluator for fitness"""
    def __init__(self, evaluator: TimetableEvaluator):
        self.evaluator = evaluator
    
    def generate(self, constraints: Dict) -> List[Dict]:
        # GA logic here, uses evaluator.evaluate()
        pass

class GreedyGenerator:
    def generate(self, constraints: Dict) -> Dict:
        # Fast initial solution
        pass

class HillClimbingGenerator:
    def improve(self, initial_tt: Dict) -> Dict:
        # Local optimization
        pass
```

### 3. Ranking Service
```python
# src/services/ranking_service.py
class RankingService:
    def __init__(self, evaluator: TimetableEvaluator):
        self.evaluator = evaluator
    
    def rank_candidates(self, timetables: List[Dict]) -> List[RankedTimetable]:
        """Main ranking entry point"""
        results = self.evaluator.batch_evaluate(timetables)
        return self._sort_by_score(timetables, results)
    
    def find_best_partial(self, partials: List[Dict]) -> Dict:
        """Specifically for partial solution ranking"""
        pass
```

## Benefits

### Performance
- **Ranking**: O(n) for n timetables vs O(generations × population_size)
- **No unnecessary evolution**: Just evaluate what you have
- **Batch processing**: Vectorized operations where possible

### Maintainability
- **Single responsibility**: Each component has one job
- **Reusable evaluator**: Use same logic for GA, ranking, validation
- **Testable**: Easy to unit test evaluation logic

### Flexibility
- **Pluggable generators**: GA, simulated annealing, etc.
- **Different ranking strategies**: MCDA, ML, weighted scoring
- **Configurable weights**: Easy to adjust without touching GA

## Migration Strategy

1. **Phase 1**: Extract evaluator from GA
2. **Phase 2**: Create ranking service using evaluator
3. **Phase 3**: Refactor GA to use evaluator
4. **Phase 4**: Add alternative ranking methods (MCDA, etc.)

## Usage Examples

```python
# For ranking existing timetables
evaluator = TimetableEvaluator(weights)
ranker = RankingService(evaluator)
best_tt = ranker.rank_candidates(candidate_timetables)[0]

# For generating new timetables
generator = GAGenerator(evaluator)
new_timetables = generator.generate(constraints)

# For improving existing timetable
improver = HillClimbingGenerator(evaluator)
better_tt = improver.improve(current_timetable)
```