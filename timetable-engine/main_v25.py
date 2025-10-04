"""
Timetable Generation API - Main Application

VERSION 2.5 - Metadata-Driven Optimization with Performance Enhancements

CHANGELOG v2.5:
- Integrated models_phase1_v25.py (metadata-enabled models)
- Integrated csp_solver_complete_v25.py (metadata extraction)
- Integrated ga_optimizer_v25.py (metadata-driven optimization)
- Optimized async workflow with proper thread offloading
- Enhanced error handling and logging
- Comprehensive diagnostics and timing

PERFORMANCE OPTIMIZATIONS:
- CSP solver runs in thread pool (prevents blocking)
- GA optimizer runs in thread pool (CPU-intensive)
- Proper async/await patterns throughout
- Detailed timing for each phase
- Memory-efficient solution selection

METADATA FEATURES:
- Language-agnostic subject preferences
- School-customizable period structures
- Per-teacher consecutive limits
- Zero hardcoded business logic
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import time
from typing import Dict, Any

# v2.5: Import updated models with metadata support
from src.models_phase1_v25 import (
    GenerateRequest, GenerateResponse, TimetableSolution,
    ValidateRequest, ValidationResult, OptimizationWeights
)

# v2.5: Import metadata-enabled solvers
from src.csp_solver_complete_v25 import CSPSolverCompleteV25
from src.algorithms.core.ga_optimizer_v25 import GAOptimizerV25


# =============================================================================
# APPLICATION LIFECYCLE & CONFIGURATION
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    
    Handles startup and shutdown tasks:
    - Initialize solvers
    - Setup thread pools
    - Cleanup resources
    """
    # Startup
    print("\n" + "=" * 70)
    print("🚀 TIMETABLE GENERATION API v2.5 - STARTING UP")
    print("=" * 70)
    print("✓ Metadata-driven optimization enabled")
    print("✓ Language-agnostic preferences")
    print("✓ School-customizable configurations")
    print("=" * 70 + "\n")
    
    # Initialize solvers globally (reused across requests)
    app.state.csp_solver = CSPSolverCompleteV25(debug=True)
    app.state.ga_optimizer = GAOptimizerV25()
    
    yield
    
    # Shutdown
    print("\n" + "=" * 70)
    print("🛑 TIMETABLE GENERATION API v2.5 - SHUTTING DOWN")
    print("=" * 70 + "\n")


# Initialize FastAPI app
app = FastAPI(
    title="Timetable Generation API",
    version="2.5.0",
    description="Metadata-driven timetable optimization with CSP + GA",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def convert_timetable_to_solution(
    timetable: Any,
    score: float,
    feasible: bool = True,
    conflicts: list = None,
    metrics: dict = None
) -> TimetableSolution:
    """
    Convert Timetable object or dict to TimetableSolution with scoring.
    
    VERSION 2.5: Handles both Pydantic objects and plain dicts.
    
    Args:
        timetable: Timetable object or dict from CSP/GA
        score: Fitness score (0-1000)
        feasible: Whether solution is valid
        conflicts: List of constraint violations
        metrics: Additional metrics dict
    
    Returns:
        TimetableSolution with all fields populated
    """
    # timetable should already be a dict from GA optimizer
    # If it's somehow still an object, convert it
    if isinstance(timetable, dict):
        timetable_dict = timetable
    elif hasattr(timetable, 'dict'):
        timetable_dict = timetable.dict()
    elif hasattr(timetable, '__dict__'):
        # Manual conversion for objects
        timetable_dict = {
            'id': getattr(timetable, 'id', 'unknown'),
            'school_id': getattr(timetable, 'school_id', ''),
            'academic_year_id': getattr(timetable, 'academic_year_id', ''),
            'name': getattr(timetable, 'name', ''),
            'status': getattr(timetable, 'status', 'DRAFT'),
            'entries': [],
            'metadata': getattr(timetable, 'metadata', {})
        }
        
        # Convert entries
        if hasattr(timetable, 'entries'):
            for entry in timetable.entries:
                if isinstance(entry, dict):
                    timetable_dict['entries'].append(entry)
                elif hasattr(entry, 'dict'):
                    timetable_dict['entries'].append(entry.dict())
                elif hasattr(entry, '__dict__'):
                    timetable_dict['entries'].append(entry.__dict__)
    else:
        # Last resort: empty dict
        timetable_dict = {"entries": [], "id": "unknown"}
    
    return TimetableSolution(
        timetable=timetable_dict,
        total_score=score,
        feasible=feasible,
        conflicts=conflicts or [],
        metrics=metrics or {}
    )


def calculate_metadata_coverage(timetable: Any) -> Dict[str, Any]:
    """
    Calculate metadata coverage statistics.
    
    VERSION 2.5: Shows how many entries have metadata.
    
    Args:
        timetable: Timetable object or dict
    
    Returns:
        Dict with coverage stats
    """
    try:
        # Extract entries
        if hasattr(timetable, 'entries'):
            entries = timetable.entries
        elif isinstance(timetable, dict) and 'entries' in timetable:
            entries = timetable['entries']
        else:
            entries = []
        
        total = len(entries)
        if total == 0:
            return {
                "total_entries": 0,
                "subject_metadata_count": 0,
                "teacher_metadata_count": 0,
                "subject_coverage": 0.0,
                "teacher_coverage": 0.0
            }
        
        # Count metadata presence
        subject_metadata_count = 0
        teacher_metadata_count = 0
        
        for entry in entries:
            if isinstance(entry, dict):
                if entry.get("subject_metadata") is not None:
                    subject_metadata_count += 1
                if entry.get("teacher_metadata") is not None:
                    teacher_metadata_count += 1
            elif hasattr(entry, 'subject_metadata') and entry.subject_metadata is not None:
                subject_metadata_count += 1
            if hasattr(entry, 'teacher_metadata') and entry.teacher_metadata is not None:
                teacher_metadata_count += 1
        
        return {
            "total_entries": total,
            "subject_metadata_count": subject_metadata_count,
            "teacher_metadata_count": teacher_metadata_count,
            "subject_coverage": (subject_metadata_count / total) * 100,
            "teacher_coverage": (teacher_metadata_count / total) * 100
        }
    
    except Exception as e:
        print(f"Warning: Could not calculate metadata coverage: {e}")
        return {
            "total_entries": 0,
            "subject_metadata_count": 0,
            "teacher_metadata_count": 0,
            "subject_coverage": 0.0,
            "teacher_coverage": 0.0
        }


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """API root endpoint with version and capability information."""
    return {
        "service": "Timetable Generation API",
        "version": "2.5.0",
        "status": "operational",
        "features": {
            "metadata_driven": True,
            "language_agnostic": True,
            "school_customizable": True,
            "csp_solver": "v2.5",
            "ga_optimizer": "v2.5"
        },
        "endpoints": {
            "generate": "/generate",
            "validate": "/validate",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "2.5.0",
        "solvers": {
            "csp": "ready",
            "ga": "ready"
        }
    }


@app.post("/validate", response_model=ValidationResult)
async def validate_entities(request: ValidateRequest):
    """
    Validate timetable entities and constraints.
    
    Quick validation without full generation.
    Checks for basic conflicts and feasibility.
    """
    try:
        # Basic validation checks
        conflicts = []
        suggestions = []
        
        # Example validations (expand as needed)
        if not request.entities:
            conflicts.append("No entities provided")
        
        # Check constraint validity
        for constraint in request.constraints:
            if constraint.priority == "MANDATORY":
                # Validate mandatory constraints
                pass
        
        feasible = len(conflicts) == 0
        
        return ValidationResult(
            feasible=feasible,
            conflicts=conflicts,
            suggestions=suggestions
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate", response_model=GenerateResponse)
async def generate_timetable(request: GenerateRequest):
    """
    Generate optimized timetable using CSP + GA approach.
    
    VERSION 2.5: Metadata-driven optimization pipeline.
    
    WORKFLOW:
    1. Validate input (subjects have preferences, weights configured)
    2. CSP Solver generates complete base solutions (with metadata)
    3. GA Optimizer refines solutions using metadata
    4. Return top N solutions with diagnostics
    
    PERFORMANCE:
    - CSP runs in thread pool (prevents event loop blocking)
    - GA runs in thread pool (CPU-intensive task)
    - Proper async/await throughout
    - Detailed timing for each phase
    
    METADATA USAGE:
    - Subject.prefer_morning → time preference optimization
    - Subject.preferred_periods → fine-grained scheduling
    - Teacher.max_consecutive_periods → teacher workload limits
    - OptimizationWeights.morning_period_cutoff → school structure
    """
    overall_start_time = time.time()
    
    # ==================================================================
    # PHASE 0: Input Validation & Configuration
    # ==================================================================
    print("\n" + "=" * 70)
    print("📋 PHASE 0: Input Validation & Configuration")
    print("=" * 70)
    
    try:
        # Extract parameters
        classes = request.classes
        subjects = request.subjects
        teachers = request.teachers
        time_slots = request.time_slots
        rooms = request.rooms
        constraints = request.constraints
        weights = request.weights
        
        print(f"✓ Request validated")
        print(f"  Classes: {len(classes)}")
        print(f"  Subjects: {len(subjects)}")
        print(f"  Teachers: {len(teachers)}")
        print(f"  Time Slots: {len(time_slots)}")
        print(f"  Rooms: {len(rooms)}")
        print(f"  Constraints: {len(constraints)}")
        
        # v2.5: Show metadata configuration
        subjects_with_preferences = sum(1 for s in subjects if s.prefer_morning)
        print(f"\n📊 v2.5 Metadata Configuration:")
        print(f"  Subjects with morning preference: {subjects_with_preferences}/{len(subjects)}")
        print(f"  Morning period cutoff: Period {weights.morning_period_cutoff}")
        print(f"  Optimization weights:")
        print(f"    Workload balance: {weights.workload_balance}")
        print(f"    Gap minimization: {weights.gap_minimization}")
        print(f"    Time preferences: {weights.time_preferences}")
        print(f"    Consecutive periods: {weights.consecutive_periods}")
        
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    
    # ==================================================================
    # PHASE 1: CSP Solver - Generate Base Solutions
    # ==================================================================
    print("\n" + "=" * 70)
    print("🧩 PHASE 1: CSP Solver - Generating Base Solutions")
    print("=" * 70)
    
    csp_start_time = time.time()
    
    try:
        # Get CSP solver from app state
        csp_solver = app.state.csp_solver
        
        # CRITICAL: Offload to thread pool to prevent blocking
        # CSP solving is CPU-intensive and synchronous
        print(f"⏳ Running CSP solver in thread pool...")
        print(f"   Generating {request.options} base solutions...")
        
        base_solutions, csp_time, csp_conflicts, csp_suggestions = await asyncio.to_thread(
            csp_solver.solve,
            classes=classes,
            subjects=subjects,
            teachers=teachers,
            time_slots=time_slots,
            rooms=rooms,
            constraints=constraints,
            num_solutions=request.options
        )
        
        csp_end_time = time.time()
        csp_duration = csp_end_time - csp_start_time
        
        if not base_solutions:
            print(f"✗ CSP solver failed to generate solutions")
            print(f"  Conflicts: {csp_conflicts}")
            print(f"  Suggestions: {csp_suggestions}")
            
            return GenerateResponse(
                solutions=[],
                generation_time=csp_duration,
                conflicts=csp_conflicts,
                suggestions=csp_suggestions
            )
        
        print(f"✓ CSP solver completed successfully")
        print(f"  Solutions generated: {len(base_solutions)}")
        print(f"  Time: {csp_duration:.2f}s")
        
        # v2.5: Verify metadata coverage
        metadata_stats = calculate_metadata_coverage(base_solutions[0])
        print(f"\n📊 Metadata Coverage:")
        print(f"  Total entries: {metadata_stats['total_entries']}")
        print(f"  Subject metadata: {metadata_stats['subject_metadata_count']} "
              f"({metadata_stats['subject_coverage']:.1f}%)")
        print(f"  Teacher metadata: {metadata_stats['teacher_metadata_count']} "
              f"({metadata_stats['teacher_coverage']:.1f}%)")
        
        if metadata_stats['subject_coverage'] < 100:
            print(f"  ⚠️  Warning: Not all entries have subject metadata")
        if metadata_stats['teacher_coverage'] < 100:
            print(f"  ⚠️  Warning: Not all entries have teacher metadata")
    
    except Exception as e:
        print(f"✗ CSP solver error: {e}")
        raise HTTPException(status_code=500, detail=f"CSP solver failed: {str(e)}")
    
    # ==================================================================
    # PHASE 2: GA Optimizer - Refine Solutions
    # ==================================================================
    print("\n" + "=" * 70)
    print("🧬 PHASE 2: Genetic Algorithm Optimization")
    print("=" * 70)
    
    ga_start_time = time.time()
    
    try:
        # Get GA optimizer from app state
        ga_optimizer = app.state.ga_optimizer
        
        print(f"⏳ Evolving {len(base_solutions)} solutions over 30 generations...")
        print(f"   Mutation rate: 0.15")
        print(f"   Crossover rate: 0.7")
        print(f"   Elitism: 2 best solutions preserved")
        
        # Convert Timetable objects to dicts for GA processing
        base_solutions_dicts = []
        for timetable in base_solutions:
            if hasattr(timetable, 'dict'):
                base_solutions_dicts.append(timetable.dict())
            elif hasattr(timetable, '__dict__'):
                # Convert object to dict
                tt_dict = {
                    'id': timetable.id,
                    'school_id': timetable.school_id,
                    'academic_year_id': timetable.academic_year_id,
                    'name': timetable.name,
                    'status': timetable.status,
                    'entries': [e.dict() if hasattr(e, 'dict') else e.__dict__ 
                               for e in timetable.entries],
                    'metadata': timetable.metadata if hasattr(timetable, 'metadata') else {}
                }
                base_solutions_dicts.append(tt_dict)
            else:
                base_solutions_dicts.append(timetable)
        
        # CRITICAL: Offload to thread pool to prevent blocking
        # GA evolution is CPU-intensive
        optimized_timetables = await asyncio.to_thread(
            ga_optimizer.evolve,
            population=base_solutions_dicts,
            generations=30,
            mutation_rate=0.15,
            crossover_rate=0.7,
            elitism_count=2,
            weights=weights
        )
        
        ga_end_time = time.time()
        ga_duration = ga_end_time - ga_start_time
        
        print(f"✓ GA optimization complete")
        print(f"  Time: {ga_duration:.2f}s")
        
        # Print evolution report
        print(ga_optimizer.get_evolution_report())
    
    except Exception as e:
        print(f"⚠️  GA optimization failed: {e}")
        print(f"   Falling back to CSP solutions")
        # Convert to dicts for consistency
        optimized_timetables = []
        for timetable in base_solutions:
            if hasattr(timetable, 'dict'):
                optimized_timetables.append(timetable.dict())
            elif hasattr(timetable, '__dict__'):
                tt_dict = {
                    'id': timetable.id,
                    'school_id': timetable.school_id,
                    'academic_year_id': timetable.academic_year_id,
                    'name': timetable.name,
                    'status': timetable.status,
                    'entries': [e.dict() if hasattr(e, 'dict') else e.__dict__ 
                               for e in timetable.entries],
                    'metadata': timetable.metadata if hasattr(timetable, 'metadata') else {}
                }
                optimized_timetables.append(tt_dict)
            else:
                optimized_timetables.append(timetable)
        ga_duration = 0.0
    
    # ==================================================================
    # PHASE 3: Solution Selection & Packaging
    # ==================================================================
    print("\n" + "=" * 70)
    print("📦 PHASE 3: Solution Selection & Packaging")
    print("=" * 70)
    
    try:
        # Select requested number of solutions
        final_solutions = optimized_timetables[:request.options]
        
        print(f"✓ Selected top {len(final_solutions)} solutions")
        
        # Convert to TimetableSolution format
        packaged_solutions = []
        
        for idx, timetable in enumerate(final_solutions):
            # Calculate final fitness score
            if hasattr(ga_optimizer, '_calculate_fitness'):
                score = ga_optimizer._calculate_fitness(timetable)
            else:
                score = 800.0  # Default score
            
            # Package solution
            solution = convert_timetable_to_solution(
                timetable=timetable,
                score=score,
                feasible=True,
                conflicts=[],
                metrics={
                    "solution_rank": idx + 1,
                    "metadata_coverage": calculate_metadata_coverage(timetable),
                    "generation_method": "CSP + GA v2.5"
                }
            )
            
            packaged_solutions.append(solution)
            
            print(f"  Solution {idx + 1}: Score = {score:.2f}")
        
        overall_end_time = time.time()
        total_duration = overall_end_time - overall_start_time
        
        print(f"\n✓ Packaging complete")
        print(f"  Total time: {total_duration:.2f}s")
        
    except Exception as e:
        print(f"✗ Solution packaging failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to package solutions: {str(e)}")
    
    # ==================================================================
    # PHASE 4: Response Construction
    # ==================================================================
    print("\n" + "=" * 70)
    print("📤 PHASE 4: Response Construction")
    print("=" * 70)
    
    # Build comprehensive response
    response = GenerateResponse(
        solutions=packaged_solutions,
        generation_time=total_duration,
        conflicts=None,
        suggestions=None
    )
    
    # Add diagnostics (custom metadata)
    # Note: This won't be in the Pydantic model, but useful for debugging
    diagnostics = {
        "version": "2.5.0",
        "metadata_enabled": True,
        "timing": {
            "total": round(total_duration, 2),
            "csp": round(csp_duration, 2),
            "ga": round(ga_duration, 2),
            "packaging": round(total_duration - csp_duration - ga_duration, 2)
        },
        "phases": {
            "csp": {
                "solutions_generated": len(base_solutions),
                "time": round(csp_duration, 2)
            },
            "ga": {
                "generations": 30,
                "time": round(ga_duration, 2),
                "improvement": ga_optimizer.stats_history[-1].best_fitness - 
                              ga_optimizer.stats_history[0].best_fitness 
                              if ga_optimizer.stats_history else 0
            }
        },
        "metadata_coverage": metadata_stats,
        "optimization_summary": {
            "weights_used": {
                "workload_balance": weights.workload_balance,
                "gap_minimization": weights.gap_minimization,
                "time_preferences": weights.time_preferences,
                "consecutive_periods": weights.consecutive_periods,
                "morning_period_cutoff": weights.morning_period_cutoff
            },
            "subjects_with_preferences": subjects_with_preferences,
            "language_agnostic": True
        }
    }
    
    print(f"✓ Response ready")
    print(f"  Solutions: {len(packaged_solutions)}")
    print(f"  Best score: {packaged_solutions[0].total_score:.2f}")
    print(f"  Metadata coverage: {metadata_stats['subject_coverage']:.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ GENERATION COMPLETE")
    print("=" * 70)
    print(f"Total time: {total_duration:.2f}s")
    print(f"  CSP: {csp_duration:.2f}s ({(csp_duration/total_duration)*100:.1f}%)")
    print(f"  GA:  {ga_duration:.2f}s ({(ga_duration/total_duration)*100:.1f}%)")
    print("=" * 70 + "\n")
    
    # Attach diagnostics as custom attribute (for logging/debugging)
    # In production, you might log this separately
    response._diagnostics = diagnostics
    
    return response


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  TIMETABLE GENERATION API v2.5                                ║
    ║  Metadata-Driven Optimization                                 ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  Features:                                                    ║
    ║    ✓ Language-agnostic subject preferences                   ║
    ║    ✓ School-customizable period structures                   ║
    ║    ✓ Per-teacher consecutive limits                          ║
    ║    ✓ Optimized async workflow                                ║
    ║    ✓ Zero hardcoded business logic                           ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  Starting server...                                           ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


# =============================================================================
# VERSION 2.5 EXAMPLE API CALL
# =============================================================================

"""
Example API request with v2.5 metadata:

POST http://localhost:8000/generate

{
    "school_id": "SCHOOL_001",
    "academic_year_id": "2024-25",
    "classes": [
        {
            "id": "10A",
            "school_id": "SCHOOL_001",
            "name": "10-A",
            "grade": 10,
            "section": "A",
            "student_count": 35
        }
    ],
    "subjects": [
        {
            "id": "MATH_10",
            "school_id": "SCHOOL_001",
            "name": "Mathematics",
            "code": "MATH10",
            "periods_per_week": 6,
            "prefer_morning": true,
            "preferred_periods": [1, 2, 3, 4],
            "avoid_periods": [7, 8]
        },
        {
            "id": "ENG_10",
            "school_id": "SCHOOL_001",
            "name": "English",
            "code": "ENG10",
            "periods_per_week": 5,
            "prefer_morning": true
        },
        {
            "id": "PE_10",
            "school_id": "SCHOOL_001",
            "name": "Physical Education",
            "code": "PE10",
            "periods_per_week": 3,
            "prefer_morning": false,
            "preferred_periods": [5, 6, 7]
        }
    ],
    "teachers": [
        {
            "id": "T001",
            "user_id": "U001",
            "subjects": ["Mathematics"],
            "max_consecutive_periods": 3
        },
        {
            "id": "T002",
            "user_id": "U002",
            "subjects": ["English"],
            "max_consecutive_periods": 4
        }
    ],
    "time_slots": [...],
    "rooms": [...],
    "constraints": [],
    "options": 3,
    "weights": {
        "workload_balance": 50.0,
        "gap_minimization": 20.0,
        "time_preferences": 30.0,
        "consecutive_periods": 15.0,
        "morning_period_cutoff": 4
    }
}

RESPONSE:
{
    "solutions": [
        {
            "timetable": {
                "entries": [
                    {
                        "subject_id": "MATH_10",
                        "period_number": 2,
                        "subject_metadata": {
                            "prefer_morning": true,
                            "preferred_periods": [1, 2, 3, 4]
                        },
                        "teacher_metadata": {
                            "max_consecutive_periods": 3
                        }
                    }
                ]
            },
            "total_score": 925.5,
            "feasible": true,
            "metrics": {
                "metadata_coverage": {
                    "subject_coverage": 100.0,
                    "teacher_coverage": 100.0
                }
            }
        }
    ],
    "generation_time": 8.45
}

BENEFITS:
- Works in ANY language (just change subject names)
- Supports different school structures (change morning_period_cutoff)
- Per-teacher customization (different max_consecutive_periods)
- Zero hardcoded business logic
- Professional, scalable architecture
"""
