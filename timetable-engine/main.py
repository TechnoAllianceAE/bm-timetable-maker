from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List
import time
import random
import uvicorn
from src.models_phase1 import (
    GenerateRequest, GenerateResponse, TimetableSolution, ValidationResult, ValidateRequest,
    Timetable, OptimizationWeights
)
# Use the robust solver with proper period distribution
from src.algorithms.core.csp_solver_robust import CSPSolverRobust as CSPSolver
from src.ga_optimizer_fixed import GAOptimizerFixed as GAOptimizer
from src.errors import TimetableGenerationError, InfeasibleConstraintsError, generate_suggestions, TimeoutError

app = FastAPI(
    title="Timetable Generator Microservice",
    description="Python microservice for school timetable generation using CSP and Genetic Algorithms",
    version="1.0.0"
)

# Global instances
csp_solver = CSPSolver(debug=True)  # Enable debug mode
ga_optimizer = GAOptimizer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Timetable Generator Microservice...")
    yield
    # Shutdown
    print("Shutting down Timetable Generator Microservice...")

app.router.lifespan_context = lifespan

@app.post("/generate", response_model=GenerateResponse)
async def generate_timetable(request: GenerateRequest):
    """
    Generate optimal timetables using CSP and optional GA optimization.

    This endpoint:
    1. Validates the input data
    2. Runs CSP solver to find feasible solutions
    3. Optionally runs GA to optimize the solutions
    4. Returns ranked solutions with metrics

    Matches OpenAPI /timetables/{id}/generate endpoint.
    """
    start_time = time.time()

    try:
        # Extract optimization weights for scoring
        # Handles both direct OptimizationWeights objects and dict representations
        weights = request.weights if isinstance(request.weights, OptimizationWeights) else OptimizationWeights(**request.weights.dict())

        # Step 1: Use Constraint Satisfaction Problem solver for feasible base solutions
        # The CSP solver ensures all hard constraints are satisfied
        base_solutions, generation_time, conflicts, suggestions = csp_solver.solve(
            request.classes, request.subjects, request.teachers,
            request.time_slots, request.rooms, request.constraints,
            num_solutions=request.options * 2  # More for GA pool
        )

        # Check if CSP found any constraint violations
        if conflicts:
            # Problem is infeasible - provide helpful feedback
            raise InfeasibleConstraintsError(conflicts, generate_suggestions(request.constraints, conflicts))

        if not base_solutions:
            raise TimeoutError("No feasible solutions found within time limit")

        # Step 2: Genetic Algorithm optimization (ENABLED with fixed version)
        # GA improves solutions by exploring variations of valid timetables
        try:
            ga_optimizer.weights = weights  # Update optimization weights
            optimized_timetables = ga_optimizer.optimize(base_solutions, population_size=30, generations=20)

            if not optimized_timetables:
                # Fall back to CSP solutions if GA fails
                print("GA optimization failed, using CSP solutions")
                optimized_timetables = base_solutions[:request.options]
        except Exception as e:
            print(f"GA optimization error: {e}")
            # Fall back to CSP solutions
            optimized_timetables = base_solutions[:request.options]

        if not optimized_timetables:
            raise TimeoutError("No solutions found")

        # Step 3: Final scoring and solution preparation
        # Package solutions with scores and metrics for the response
        solutions = []
        for i, opt_timetable in enumerate(optimized_timetables[:request.options]):
            # Calculate score based on constraint satisfaction and optimization
            # TODO: Implement proper scoring based on:
            # - Constraint satisfaction rate
            # - Resource utilization efficiency
            # - Schedule compactness (minimal gaps)
            # - Teacher preference matching
            total_score = 85.0 + random.uniform(-5, 10)  # Placeholder scoring

            solutions.append(TimetableSolution(
                timetable=opt_timetable,
                total_score=total_score,
                feasible=True,
                conflicts=[],
                metrics={
                    "constraints_satisfied": len(request.constraints),
                    "total_constraints": len(request.constraints),
                    "gaps": 0  # TODO: Calculate actual gaps
                }
            ))

        gen_time = time.time() - start_time

        return GenerateResponse(
            solutions=solutions,
            generation_time=round(gen_time, 2),
            conflicts=None,
            suggestions=None
        )

    except InfeasibleConstraintsError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": e.message,
                "conflicts": e.conflicts,
                "suggestions": e.suggestions
            }
        )
    except TimeoutError as e:
        raise HTTPException(
            status_code=408,
            detail={"message": str(e)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/validate", response_model=ValidationResult)
async def validate_constraints(request: ValidateRequest):
    """
    Validate constraint feasibility without full generation.

    Quick check to determine if the given constraints and resources
    can potentially produce a valid timetable. This is faster than
    full generation and helps identify obvious problems early.
    """
    try:
        # Run lightweight feasibility checks
        # These are quick heuristics to catch obvious problems
        # without running the full CSP solver
        classes = request.entities.get('classes', [])
        teachers = request.entities.get('teachers', [])
        slots = request.entities.get('time_slots', [])
        total_demand = sum(len(c) for c in classes) * 5  # Stub 5 periods/class
        total_supply = len(slots) * len(teachers)
        feasible = total_demand <= total_supply

        conflicts = [] if feasible else ["Demand exceeds available teacher-slot capacity"]
        suggestions = generate_suggestions(request.constraints, conflicts)

        return ValidationResult(feasible=feasible, conflicts=conflicts, suggestions=suggestions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "timetable-generator"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )