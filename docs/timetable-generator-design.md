# Timetable Generator Design Document

## Overview
The Timetable Generator is a Python microservice responsible for the core computational logic of automated timetable creation with wellness optimization, as specified in the PRD (sections 4.3, 6.1-6.5). It operates as part of the microservices architecture, receiving requests from the Node.js backend via the API Gateway. The service uses constraint satisfaction and optimization algorithms to generate 3-5 conflict-free timetable options, ranked by a multi-objective fitness function that balances academic requirements (35%) and teacher wellness (30%).

**Key Goals:**
- Generate optimal timetables in <60 seconds for schools with up to 100 teachers and 50 classes.
- Enforce hard/soft constraints (academic: periods, labs; wellness: consecutive periods, breaks, workload limits).
- Provide wellness analysis (scores, risks, recommendations) for each option.
- Handle infeasible cases with conflict explanations and relaxation suggestions.

**Integration:**
- **Input:** JSON payload from Node.js (fetched from PostgreSQL via Prisma), including school ID, classes, subjects, teachers, constraints, time slots, rooms.
- **Output:** Array of timetable solutions (entries as class-subject-teacher-room-time assignments) with metadata (wellness scores, analysis).
- **Communication:** HTTP/REST (POST /generate), async via FastAPI. Optional: WebSockets for progress updates on long runs.
- **Deployment:** Docker container, Kubernetes orchestration (as per Appendix A). Scales horizontally for multi-school.

## Technology Stack
- **Framework:** FastAPI (async, type-safe, auto-generates OpenAPI docs; aligns with PRD's Python FastAPI microservice).
- **Algorithms:**
  - CSP Solver: OR-Tools CP-SAT (efficient for timetabling; supports custom constraints/heursitics).
  - Genetic Algorithm: DEAP (for NSGA-II multi-objective optimization).
- **Data Handling:** Pydantic (models for validation/serialization, matching Prisma schemas/OpenAPI).
- **Computations:** NumPy/SciPy (matrix ops for scoring), concurrent.futures (parallel evaluation).
- **Logging/Monitoring:** structlog, Prometheus client (for metrics like generation time).
- **Testing:** pytest (unit/integration), Hypothesis (property-based for constraints).
- **No Direct DB:** Relies on API inputs; if needed, SQLAlchemy + asyncpg for direct queries (but prefer stateless).

## API Design
Endpoints match/extend OpenAPI spec (/timetables/{id}/generate):

- **POST /generate**
  - Request Body: `GenerateRequest` (Pydantic model: school_data (dict of entities), options (int, default 3), timeout (int, default 60), weights (dict: academic=0.35, wellness=0.30, etc.)).
  - Response: `GenerateResponse` (list of `TimetableSolution`: timetable_entries (list), wellness_analysis (dict), score (float)).
  - Behavior: Validate input, run CSP for feasible solutions, GA for optimization, return ranked options.

- **POST /validate** (optional): Check constraints feasibility without full generation.
  - Request: `ValidateRequest` (constraints subset).
  - Response: `ValidationResult` (feasible: bool, conflicts: list, suggestions: list).

- **GET /health**: Liveness probe.

Security: API key or JWT from gateway; rate limiting.

## Data Models (Pydantic)
- `SchoolData`: Nested models for Class, Subject, Teacher (with wellness config), TimeSlot, Room, Constraint (type: str, value: dict).
- `TimetableEntry`: class_id, subject_id, teacher_id, time_slot_id, room_id, wellness_impact (enum).
- `WellnessAnalysis`: overall_score, teacher_scores (dict[teacher_id: score]), issues (list), recommendations (list).
- Enums: Match Prisma (e.g., WellnessImpact: POSITIVE/NEUTRAL/NEGATIVE).

## Algorithm Workflow
### 1. Pre-processing (Input Validation & Setup)
- Parse entities into variables/domains (e.g., variables: class-period tuples; domains: teacher-subject-room combos).
- Extract constraints: Hard (must satisfy), Soft (penalize violations).
- Wellness setup: Compute teacher capacities, burnout thresholds from configs.

### 2. CSP Solver (Feasible Solutions)
- Model as CP-SAT problem:
  - Variables: Assignments (class, period) → (teacher, subject, room).
  - Domains: Feasible combos (teacher qualified? room available?).
  - Constraints:
    - Academic: No overlaps, min/max periods, lab rooms for science.
    - Wellness: Max consecutive (≤3), daily hours (≤6), gaps (≥10 min), no early+late same day.
  - Heuristics: Workload-balanced MRV (minimum remaining values, prioritize low-workload teachers); forward checking with wellness propagation.
- Solve: Find 10-20 feasible base solutions (timeout: 30s); use parallel workers for branches.

Pseudocode:
```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()
# Define vars, domains, constraints...
solver = cp_model.CpSolver()
status = solver.Solve(model)
if status == cp_model.OPTIMAL:
  # Extract solution
```

### 3. Multi-Objective Optimization (GA)
- Population: Feasible CSP solutions + perturbations.
- Fitness: `f = 0.35*academic + 0.30*wellness + 0.20*efficiency + 0.15*preferences`
  - Academic: Constraint satisfaction %.
  - Wellness: Balance (std dev workloads), stress min (consecutive/gaps), burnout risk (ML proxy or rule-based).
  - Efficiency: Minimize gaps/idle time.
  - Preferences: Match teacher prefs (e.g., no early classes).
- Operations: NSGA-II selection, wellness-preserving crossover (swap periods without violating hard constraints), mutation (local swaps).
- Generations: 50-100, population 50; early stop if convergence.
- Output: Pareto front, select top 3-5.

Pseudocode:
```python
from deap import base, creator, tools
import random

creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0, 1.0, 1.0))  # Maximize all
creator.create("Individual", list, fitness=creator.FitnessMulti)

# Toolbox setup, eval function with scoring
# algorithms.eaMuPlusLambda(pop, toolbox, mu=50, lambda_=100, cxpb=0.7, mutpb=0.3, ngen=100)
```

### 4. Post-processing (Analysis & Ranking)
- For each solution: Compute wellness metrics (individual/dept scores, risks via simple rules or ML stub).
- Detect issues: Overloads, imbalances; suggest fixes (e.g., "Swap Math with History for Teacher X").
- Rank by total fitness; include trade-off explanations.

### 5. Error Handling
- Infeasible: Return conflicts (e.g., "Insufficient teachers for Science labs"), relaxation suggestions (e.g., "Reduce max consecutive to 4").
- Timeout: Return best partial solution.
- Validation: Pydantic for inputs; custom exceptions for domain errors.

## Workflow Diagram
```mermaid
graph TD
    A[Node.js Request: POST /generate] --> B[FastAPI: Validate Input Pydantic]
    B --> C[Pre-process: Parse Entities & Constraints]
    C --> D[CSP Solver: OR-Tools CP-SAT<br/>Feasible Base Solutions<br/>(Workload MRV Heuristic)]
    D --> E[If No Feasible: Detect Conflicts<br/>Suggest Relaxations]
    D --> F[Genetic Algorithm: DEAP NSGA-II<br/>Population from CSP Outputs<br/>Multi-Objective Fitness<br/>50 Gens, Wellness-Preserving Ops]
    F --> G[Post-process: Wellness Analysis<br/>Compute Scores, Risks, Recs<br/>Rank Top 3-5]
    G --> H[Response: Timetable Solutions<br/>with Analysis]
    E --> H
    style D fill:#f9f,stroke:#333
    style F fill:#bbf,stroke:#333
```

## Implementation Phases (Todo Alignment)
1. Setup FastAPI app, Pydantic models, basic /generate endpoint (stub solver).
2. Implement CSP module (ortools integration, wellness constraints).
3. Implement GA module (DEAP, fitness functions).
4. Add wellness computations (rule-based; ML stub for burnout).
5. Error handling, validation.
6. Tests: Use seeded data (20 teachers, 6 classes, 10 subjects); mock OR-Tools for unit tests.
7. Optimizations: ThreadPoolExecutor for parallel GA evals; Redis caching for repeated solves.
8. Docs: OpenAPI auto-gen; integration guide for Node.js (axios calls).

## Risks & Mitigations
- Complexity: Start with simplified CSP (no wellness), iterate.
- Performance: Benchmark with seeded data; fallback to heuristic if timeout.
- Scalability: Async FastAPI; deploy with Gunicorn/Uvicorn workers.

## Next Steps
- Switch to Code mode to implement.
- Install deps: `pip install fastapi uvicorn ortools deap pydantic numpy scipy`.
- Run: `uvicorn main:app --reload`.

This design ensures alignment with PRD while being modular and testable.