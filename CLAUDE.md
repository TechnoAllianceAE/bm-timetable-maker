# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

School Timetable Management SaaS Platform with AI-powered timetable generation and wellness monitoring. The system consists of:
- **Backend**: NestJS/TypeScript API with Prisma ORM (PostgreSQL)
- **Frontend**: Next.js 15 with React 19 and Tailwind CSS
- **Timetable Engine**: Python FastAPI microservice with enterprise-ready CSP solver and diagnostic intelligence

## Common Development Commands

### Root Project
```bash
# Install dependencies
npm install

# Database operations
npm run prisma:generate  # Generate Prisma client
npm run prisma:migrate  # Run database migrations
npm run prisma:push     # Push schema changes to database
npm run prisma:seed     # Seed database with test data

# Development
npm run dev              # Start TypeScript development server
npm run build           # Build TypeScript code
npm start               # Start production server
```

### Backend (NestJS API)
```bash
cd backend

# Development
npm run start:dev       # Start NestJS with watch mode (port 5000)
npm run build          # Build NestJS application
npm run start:prod     # Run production build

# Database
npm run prisma:generate
npm run prisma:migrate
npm run prisma:seed

# Testing
npm run test           # Run Jest tests
npm run test:watch     # Run tests in watch mode
npm run test:e2e       # Run end-to-end tests
npm run test:cov       # Run tests with coverage

# Code Quality
npm run lint           # Lint TypeScript files
npm run format         # Format code with Prettier
```

### Frontend (Next.js)
```bash
cd frontend

# Development
npm run dev            # Start Next.js development server (port 3000)
npm run build         # Build production bundle
npm start             # Start production server
npm run lint          # Run ESLint
```

### Timetable Engine (Python)
```bash
cd timetable-engine

# Install dependencies
pip install -r requirements.txt

# Start services (v2.5 is latest with metadata-driven optimization)
python main_v25.py                                    # Latest v2.5 service on port 8000
uvicorn main_v25:app --reload --port 8000             # Alternative start method
python test_v25_metadata_flow.py                      # Test v2.5 metadata flow

# Legacy services (if needed)
python main_v20.py                                    # v2.0 service

# Run tests
pytest

# Testing Framework
cd ../tt_tester

# Generate test data using unified generator
python data_generator.py --size small   # 10 classes, 30 teachers
python data_generator.py --size medium  # 20 classes, 60 teachers
python data_generator.py --size large   # 40 classes, 121 teachers

# View timetables with universal viewer
python timetable_viewer.py --tt-id <TT_ID>  # View specific generation
python timetable_viewer.py                   # Auto-detect latest

# Track generation history
python tt_generation_tracker.py --list       # List all generations
python tt_generation_tracker.py --cleanup    # Remove old files

# A/B Testing
python ab_test_runner.py                     # Run A/B tests between versions
```

## Architecture Overview

### Service Communication Flow
1. Frontend (Next.js) → Backend API (Node.js) for all core operations
2. Backend → Timetable Engine (Python) for timetable generation via HTTP
3. Backend handles all authentication, data persistence, and business logic
4. Python service handles complex algorithmic timetable generation

### Database Schema
- PostgreSQL database for all entities
- Core entities: School, User, Teacher, Class, Subject, TimeSlot, Room, Timetable
- Wellness entities defined but not yet implemented: WellnessMetrics, WorkloadAlert, TeacherWellnessProfile
- All models defined in `prisma/schema.prisma`

### Key Backend Modules (NestJS)
Located in `backend/src/modules/`:
- **auth/**: JWT-based authentication with Passport.js and bcrypt
- **users/**: User CRUD with RBAC (admin/principal access control)
- **schools/**: School management
- **teachers/**: Teacher management and metadata
- **classes/**: Class/section management
- **subjects/**: Subject definitions with metadata (prefer_morning, etc.)
- **rooms/**: Room and facility management
- **timetables/**: Timetable generation, CRUD, and validation
- **prisma/**: Prisma module for database access

Backend uses NestJS modular architecture with dependency injection.

### Frontend Structure (Next.js 15 App Router)
Located in `frontend/app/`:
- **auth/**: Authentication pages (login/register)
- **admin/**: Admin dashboard and timetable management
  - Includes timetable generation form with constraint configuration
  - CSV data import functionality
- **teacher/**: Teacher portal and views
- **student/**: Student portal and schedule views
- **layout.tsx**: Root layout with providers
- **page.tsx**: Landing page
- Uses Tailwind CSS for styling
- API integration via axios to backend on port 5000

### Timetable Generation Process (PRODUCTION READY)
1. Backend receives generation request with constraints
2. Backend calls Python service `/generate` endpoint with school data
3. **Pre-computation Sanity Check**: Resource Advisor validates mathematical feasibility
4. **CSP Complete Solver**: Guarantees 100% slot coverage with smart resource allocation
5. **Diagnostic Intelligence**: Real-time constraint tracking and bottleneck analysis
6. **Fallback Mechanisms**: Self-study periods ensure no gaps in timetable
7. Returns complete solutions with actionable diagnostics (success/failure)
8. Backend persists selected timetable to database

**Enterprise Scale Achieved**: 40 classes, 75 teachers, 1,600 assignments in <1 second

### Timetable Engine Architecture
The system uses **metadata-driven optimization** with multiple solver versions:

#### Core Components (timetable-engine/src/)
- **Models** (`models_phase1_v25.py`): Latest Pydantic models with metadata support
- **CSP Solver** (`csp_solver_complete_v25.py`): 100% slot coverage guarantee with metadata extraction
- **GA Optimizer** (`ga_optimizer_v25.py`): Genetic algorithm with metadata-driven preferences
- **Algorithms** (`src/algorithms/`): Supporting algorithms and utilities

#### Available Services
- **v2.5 Service** (`main_v25.py`): Latest with metadata-driven optimization (RECOMMENDED)
- **v2.0 Service** (`main_v20.py`): Stable legacy version

#### Key Features (v2.5)
- **Metadata-driven optimization**: Subject preferences (prefer_morning), teacher constraints (max_consecutive_periods)
- **Language-agnostic**: Customizable preference configurations per school
- **CSP + GA Pipeline**: Complete solver followed by genetic algorithm refinement
- **100% Slot Coverage**: No gaps in timetables, self-study periods as fallback

**Production Ready**: Handles enterprise scale (40 classes, 1,600 assignments) in <1 second

### Development Priority
**Current Focus**: Core timetable generation and management
- CSP solver produces valid, conflict-free timetables
- All academic constraints (teacher availability, room capacity, etc.)
- CRUD operations for timetables
- Basic UI for timetable viewing and management

**Future Enhancement**: Wellness monitoring (after timetable works correctly)
- Workload analysis and burnout detection
- Real-time wellness metrics
- Alert system for wellness issues

## Environment Variables Required
```
DATABASE_URL=postgresql://user:password@localhost:5432/school_timetable
JWT_SECRET=your-secret-key
PYTHON_TIMETABLE_URL=http://localhost:8000
```

## Current Development Status

### Timetable Engine - PRODUCTION READY ✅
- Enterprise scale: 40 classes, 75 teachers, 1,600 assignments
- Performance: <1 second generation time
- 100% slot coverage guaranteed (no gaps)
- Transparent solving with actionable feedback
- Diagnostic services on port 8001

### Testing Framework (`tt_tester/`)
**Core Tools:**
- **Data Generator** (`data_generator.py`): Unified test data generation for small/medium/large schools
- **Timetable Viewer** (`timetable_viewer.py`): Interactive analytics dashboard with workload management
- **Generation Tracker** (`tt_generation_tracker.py`): Track and manage all timetable generations

**Features:**
- Teacher workload monitoring with visual indicators
- Schedule analytics and validation
- Professional terminology and reporting
- Complete traceability with unique TT IDs

### Backend - FULLY OPERATIONAL ✅
- NestJS modular architecture with dependency injection
- JWT authentication with Passport.js
- User management with RBAC
- Complete CRUD for all entities (schools, teachers, classes, subjects, rooms)
- Timetable generation integration with Python service
- CSV data import for bulk operations
- Swagger API documentation available

### Frontend - CORE FEATURES COMPLETE ✅
- Next.js 15 with App Router
- Authentication pages (login/register)
- Admin dashboard with timetable generation
- Constraint configuration UI (hard/soft constraints)
- CSV data import interface
- Teacher and student portals
- Real-world data integration (116 teachers, 30 classes, 35 rooms, 10 subjects)

## Important Implementation Details

### Python Engine Version Strategy
The timetable engine has multiple versions for iterative development:
- **Use v2.5** (`main_v25.py`, `models_phase1_v25.py`, etc.) for new development
- v2.5 includes metadata-driven optimization and language-agnostic preferences
- Test metadata flow with `test_v25_metadata_flow.py` before making changes
- Legacy versions (v2.0, v3, etc.) are kept for reference and A/B testing

### Data Flow: Backend → Python Service
1. Backend transforms Prisma entities to Python service format
2. Python service expects specific structure (see `models_phase1_v25.py`)
3. Metadata fields (prefer_morning, max_consecutive_periods) must be preserved
4. Response includes timetable entries with subject_metadata and teacher_metadata

### Testing Strategy
- **Unit tests**: pytest in `timetable-engine/`
- **Integration tests**: Jest in `backend/`
- **E2E tests**: Available via `npm run test:e2e` in backend
- **Visual testing**: Use `tt_tester/timetable_viewer.py` to inspect generated timetables
- **A/B testing**: Use `tt_tester/ab_test_runner.py` to compare solver versions

### Database Management
- Schema defined in `prisma/schema.prisma`
- Use `npm run prisma:migrate` for schema changes (creates migration files)
- Use `npm run prisma:push` for quick dev iterations (no migration files)
- CSV import scripts available for bulk data loading
- SQLite dev.db used for development (PostgreSQL recommended for production)

## Development Phases
**Phase 1 - Core Timetable (Current)**
- Focus on reliable timetable generation
- Complete CRUD operations
- Basic UI for viewing/management

**Phase 2 - Wellness (Future)**
- Workload analysis
- Burnout detection
- Wellness dashboard
- V2.5 Testing & Status Report

## 🔍 Analysis Complete

I've thoroughly reviewed the v2.5 implementation and existing test results. Here's what I found:

## ⚠️ **CRITICAL ISSUES IDENTIFIED**

### 1. **File Structure Problem**
- `src/models_phase1_v25.py` contains **GA optimizer code** instead of Pydantic models
- This is a **file naming/organization error** - the models and optimizer code are mixed up
- The correct GA optimizer is in `src/algorithms/core/ga_optimizer_v25.py`

### 2. **Missing Pydantic Models**
- The test file `test_v25_metadata_flow.py` expects to import models (Subject, Teacher, Class, etc.) from `src.models_phase1_v25`
- These models don't exist in that location, causing import failures
- Need to locate or create proper `models_phase1_v25.py` with Pydantic model definitions

### 3. **Validation Errors in v2.5**
From the existing A/B test results (`ab_test_results_TT_20251004_102303_1163e6f3.html`):
- ✅ **v2.0 works perfectly** - 2.59s for 30 classes, 1200 assignments, 100% coverage
- ❌ **v2.5 fails** - Response construction validation errors
- GA optimizer returns wrong object types (Timetable instead of TimetableSolution)

## 📊 **CURRENT TEST RESULTS SUMMARY**

### Version 2.0 Performance (PRODUCTION READY ✅)
```
Status: ✅ SUCCESS
Total Time: 2.59s
├─ CSP: 0.71s (27%)
└─ GA: 1.88s (73%)

Solutions: 3 generated
Coverage: 100% (1200/1200 entries)
Scale: 30 classes, 120 teachers, 35 rooms
Quality: No gaps, all constraints satisfied
```

### Version 2.5 Status (NOT WORKING ❌)
```
Status: ❌ FAILED
Failure Point: Response construction
Error: Pydantic validation errors
Cause: GA returning wrong object types

Issues:
- 9 validation errors for GenerateResponse
- Missing fields: timetable, total_score, feasible
- Object conversion broken
```

## 🎯 **RECOMMENDATIONS**

### Immediate Actions:
1. **Use v2.0 for production** - It's stable, fast, and reliable
2. **Fix v2.5 file structure** - Organize models separately from GA optimizer
3. **Create proper models_phase1_v25.py** with Pydantic definitions
4. **Fix response construction** in main_v25.py to handle object conversions

### Before v2.5 Can Work:
- [ ] Separate models from GA optimizer code
- [ ] Create/locate proper Pydantic models with metadata fields
- [ ] Fix convert_timetable_to_solution() function
- [ ] Run test_v25_metadata_flow.py to verify pipeline
- [ ] Re-run A/B test after fixes

## 📄 **AVAILABLE REPORTS**

I found an existing HTML report from today's testing:
- **File**: `tt_tester/ab_test_results_TT_20251004_102303_1163e6f3.html`
- **Contains**: Detailed comparison of v2.0 vs v2.5
- **Verdict**: v2.0 works, v2.5 has implementation issues

## 💡 **CONCLUSION**

**v2.5 is not ready for testing** due to file structure and import issues. The metadata-driven approach is sound in theory, but the implementation has organizational problems that prevent the test suite from even running.

**v2.0 is production-ready** and performs excellently for enterprise-scale problems (2.59s for 1200 assignments).

**Next Steps**: Fix the file structure issues before attempting to run v2.5 tests.