# WARP.md

This file provides guidance to Warp AI when working with code in this repository through the terminal interface.

## Warp AI Terminal Guidance

### Quick Start Commands
When working in Warp terminal, these are the most commonly used commands:

```bash
# Quick service startup (all services)
./START_ALL_SERVICES.sh        # macOS/Linux
START_ALL_SERVICES.bat         # Windows

# Individual service startup
cd backend && npm run start:dev                    # Backend (port 5000)
cd frontend && npm run dev                         # Frontend (port 3000) 
cd timetable-engine && python main_v301.py        # Python Engine (port 8000)

# Database operations
npm run prisma:generate && npm run prisma:push   # Quick DB setup
npm run prisma:seed                              # Add test data

# Testing and validation
cd tt_tester && python timetable_viewer.py       # View generated timetables
pytest timetable-engine/                         # Run Python tests
cd backend && npm run test                       # Run backend tests
```

### Current Version Status (for Warp AI)
- **Python Engine**: Use v3.0.1 (`main_v301.py`) - Latest and recommended
- **Backend**: NestJS on port 5000 - Fully operational
- **Frontend**: Next.js 15 on port 3000 - Core features complete
- **Database**: SQLite (dev.db) for development, PostgreSQL for production

### Development Workflow in Terminal
1. **Start services**: `./START_ALL_SERVICES.sh`
2. **Check status**: `./STATUS_ALL_SERVICES.sh` 
3. **Generate timetable**: Use frontend UI at http://localhost:3000
4. **View results**: `cd tt_tester && python timetable_viewer.py`
5. **Stop services**: `./STOP_ALL_SERVICES.sh`

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

# Service Management (macOS/Linux)
./START_ALL_SERVICES.sh  # Start all services (Backend, Frontend, Python)
./STOP_ALL_SERVICES.sh   # Stop all services
./STATUS_ALL_SERVICES.sh # Check service status

# Service Management (Windows)
START_ALL_SERVICES.bat   # Start all services
STOP_ALL_SERVICES.bat    # Stop all services
STATUS_ALL_SERVICES.bat  # Check service status
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

# Start services (v3.0.1 is latest and recommended)
python main_v301.py                                   # Latest v3.0.1 service on port 8000 (RECOMMENDED)
uvicorn main_v301:app --reload --port 8000            # Alternative start method for v3.0.1
python main_v25.py                                    # v2.5 service (fastest but complex)
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
- PostgreSQL database for all entities (SQLite for development)
- Core entities: School, User, Teacher, Class, Subject, TimeSlot, Room, Timetable
- Wellness entities defined but not yet implemented: WellnessMetrics, WorkloadAlert, TeacherWellnessProfile
- All models defined in `prisma/schema.prisma`

**Room Model Fields (Updated Oct 9, 2025):**
- `id`: String (cuid)
- `schoolId`: String
- `name`: String (required) - Room name
- `code`: String (optional) - Room code/number (e.g., "R101", "LAB-01")
- `capacity`: Int (optional) - Room capacity
- `type`: String (optional) - Room type (CLASSROOM, LAB, AUDITORIUM, etc.)

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
- **v3.0.1 Service** (`main_v301.py`): Latest with simplified room allocation and performance optimizations (RECOMMENDED)
- **v3.0 Service** (`main_v30.py`): Stable with simplified room allocation
- **v2.5 Service** (`main_v25.py`): Fastest generation but complex code (LEGACY)
- **v2.0 Service** (`main_v20.py`): Stable legacy version

#### Key Features (v3.0.1 - Current)
- **Simplified Room Allocation**: 85% fewer conflict checks, pre-assigned home classrooms
- **Performance Optimizations**: Cached lookups, pre-computed metadata, 1.5-3.6% faster than v3.0
- **Metadata-driven optimization**: Subject preferences (prefer_morning), teacher constraints (max_consecutive_periods)
- **Language-agnostic**: Customizable preference configurations per school
- **Grade-specific subject requirements**: Define custom period allocations per subject per grade level
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
- **Recent Updates** (October 9, 2025):
  - Room model now includes optional `code` field for room identification (e.g., "R101", "LAB-01")
  - Room management simplified - removed unnecessary fields (isLab, hasProjector, hasAC, floor)
  - Core room fields: name, code, capacity, type
- **Previous Fixes**:
  - User profile data now stored in JSON profile field (not separate name field)
  - Timetable deletion with cascading entry removal
  - Timetable name persistence in database

### Frontend - CORE FEATURES COMPLETE ✅
- Next.js 15 with App Router
- Authentication pages (login/register)
- Admin dashboard with timetable generation
- Constraint configuration UI (hard/soft constraints)
- Subject hour requirements with grade-specific allocations
- CSV data import interface
- Teacher and student portals
- Real-world data integration (116 teachers, 30 classes, 35 rooms, 10 subjects)
- **Recent Fixes**:
  - User edit/update now correctly handles profile JSON data
  - Timetable list displays creation timestamp (date + time)
  - Timetable names properly displayed instead of "Untitled"

## Important Implementation Details

### Python Engine Version Strategy
The timetable engine has multiple versions for iterative development:
- **Use v3.0.1** (`main_v301.py`, `csp_solver_complete_v301.py`, etc.) for new development (LATEST)
- v3.0.1 includes simplified room allocation and performance optimizations (85% conflict reduction, 1.5-3.6% faster)
- v3.0 includes simplified room allocation (85% performance improvement) 
- v2.5 includes metadata-driven optimization and language-agnostic preferences (FASTEST)
- Test metadata flow with `test_v25_metadata_flow.py` before making changes
- Legacy versions (v2.0, etc.) are kept for reference and A/B testing

### Data Flow: Backend → Python Service
1. Backend transforms Prisma entities to Python service format
2. Python service expects specific structure (see `models_phase1_v25.py`)
3. Metadata fields (prefer_morning, max_consecutive_periods) must be preserved
4. Response includes timetable entries with subject_metadata and teacher_metadata

### Subject Hour Requirements (Grade-Specific Allocations)
This feature allows schools to specify different period allocations for subjects based on grade level.

**Implementation:**
- **Frontend** (`frontend/app/admin/timetables/generate/page.tsx`): Dynamic table with grade/subject/periods inputs and real-time validation
- **Backend** (`backend/src/modules/timetables/timetables.service.ts:215-219`): Transforms camelCase to snake_case for Python service
- **CSP Solver** (`timetable-engine/src/csp_solver_complete_v25.py`): Enforces exact period counts per grade-subject combination

**Key Points:**
- Requirements are optional - if not specified, default subject values are used
- Validation prevents exceeding available time slots (periods/day × days/week)
- CSP solver creates per-class distributions based on each class's grade
- Stored in database via `SubjectRequirement` table with upsert pattern

**Testing:**
- Unit tests: `timetable-engine/test_subject_requirements.py` and `test_subject_requirements_simple.py`
- All tests pass with grade-specific allocations (e.g., Grade 6: Math=6, Grade 7: Math=8)

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

## 🎯 **CURRENT VERSION STATUS**

### Version 3.0.1 (LATEST - RECOMMENDED) ✅
```
Status: ✅ READY FOR USE
Release Date: October 8, 2025

Features:
- SIMPLIFIED ROOM ALLOCATION (85% conflict reduction)
- PERFORMANCE OPTIMIZATIONS (1.5-3.6% faster than v3.0)
- Pre-assigned home classrooms (from database)
- Only schedules shared amenities (labs, sports, library, art)
- 2-level allocation logic (vs 5-level in v2.5)
- Cached lookups and pre-computed metadata
- Maintains all v2.5/v3.0 features:
  * Metadata-driven optimization
  * Teacher consistency enforcement
  * Grade-specific subject requirements
  * 100% slot coverage guarantee

Performance:
- 85% reduction in room conflict checks vs v2.5
- 1.5-3.6% faster than v3.0 at scale
- Before (v2.5): 1,400 checks (40 rooms × 35 slots)
- After (v3.0.1): 210 checks (6 shared rooms × 35 slots)

Optimizations (new in v3.0.1):
- Pre-computed subject metadata
- Cached frequently accessed values
- Pre-shuffled subject assignments
- Reduced redundant dictionary lookups

File: timetable-engine/main_v301.py
Models: timetable-engine/src/models_phase1_v30.py (shared with v3.0)
Solver: timetable-engine/src/csp_solver_complete_v301.py

Requirements:
- All classes MUST have homeRoomId assigned in database
- Use utopia_school_generator.py for v3.0-compatible data
```

### Version 3.0 (STABLE) ✅
```
Status: ✅ STABLE
Release Date: October 8, 2025

Features:
- Simplified room allocation (85% conflict reduction)
- Pre-assigned home classrooms
- 2-level allocation logic

Performance: Good, but 3-4% slower than v3.0.1
File: timetable-engine/main_v30.py
Note: Use v3.0.1 instead for better performance
```

### Version 2.5 (FASTEST - LEGACY) ✅
```
Status: ✅ FASTEST (2-4x faster than v3.x)
Features:
- Metadata-driven optimization
- Language-agnostic subject preferences
- Teacher consecutive period limits
- CSP + GA pipeline
- Dynamic room allocation (all rooms)

Performance: Fastest generation, but complex code
File: timetable-engine/main_v25.py
Note: Use v3.0.1 for better maintainability unless speed is critical
```

## 📋 **QUICK REFERENCE**

**Default Python Service:** v3.0.1 on port 8000
**Startup Command:** `python timetable-engine/main_v301.py`
**Auto-start Script:** `START_ALL_SERVICES.bat` or `START_ALL_SERVICES.sh`
**Communication Guide:** See `COMMUNICATION_SETUP.md` for troubleshooting

**Performance Benchmarks:** See `tt_tester/ab_test_3way_output.log` for detailed comparison

## 💡 **VERSION SELECTION GUIDE**

Use **v3.0.1** if (RECOMMENDED):
- You want simplified room allocation (85% fewer conflict checks)
- You have or can assign home classrooms to all classes
- You want clearer error messages for room conflicts
- You prefer simpler, more maintainable code
- You want the best balance of performance and simplicity

Use **v2.5** if:
- You need the absolute fastest generation speed (2-4x faster than v3.x)
- You're willing to accept more complex code for speed
- You don't mind tracking all rooms for conflicts
- You want teacher consecutive period limits
- You need language-agnostic configurations

Use **v2.0** if:
- You prefer the proven legacy system
- You don't need advanced metadata features
- You want maximum simplicity

## 🔧 **WARP AI TROUBLESHOOTING**

### Common Terminal Operations

#### Service Management Issues
```bash
# Check if services are running
lsof -i :3000  # Frontend
lsof -i :5000  # Backend  
lsof -i :8000  # Python Engine

# Kill stuck services
pkill -f "npm run start:dev"    # Backend
pkill -f "npm run dev"          # Frontend
pkill -f "main_v301.py"         # Python Engine

# Clean restart all services
./STOP_ALL_SERVICES.sh && ./START_ALL_SERVICES.sh
```

#### Database Issues
```bash
# Reset database completely
rm -f prisma/dev.db*           # Remove SQLite files
npm run prisma:push            # Recreate schema
npm run prisma:seed            # Add test data

# Check database connections
npm run prisma:studio          # Open database GUI
```

#### Python Environment Issues
```bash
# Check Python dependencies
cd timetable-engine
pip list | grep -E "fastapi|uvicorn|pydantic"

# Reinstall if needed
pip install -r requirements.txt

# Test Python service manually
curl -X GET http://localhost:8000/health
```

#### File Permission Issues (macOS/Linux)
```bash
# Make scripts executable
chmod +x *.sh

# Fix common permission issues
sudo chown -R $USER:$USER node_modules/
```

### Performance Optimization Tips
- Use v3.0.1 for best performance (1.5-3.6% faster than v3.0)
- Assign home classrooms to all classes for 85% fewer room conflict checks
- Use `utopia_school_generator.py` to create v3.0-compatible test data
- Monitor generation logs in `tt_tester/` directory for bottlenecks

### Quick Health Checks
```bash
# Verify all services respond
curl -s http://localhost:3000 | grep -q "School Timetable" && echo "Frontend OK" || echo "Frontend FAIL"
curl -s http://localhost:5000/api/health | grep -q "OK" && echo "Backend OK" || echo "Backend FAIL"  
curl -s http://localhost:8000/health | grep -q "OK" && echo "Python OK" || echo "Python FAIL"
```

### Log Locations
- **Backend logs**: Check terminal running `npm run start:dev`
- **Frontend logs**: Check terminal running `npm run dev`
- **Python logs**: Check terminal running `main_v301.py`
- **Timetable generation logs**: `tt_tester/` directory
- **Database logs**: Enable via Prisma debug environment variables
