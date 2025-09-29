# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

School Timetable Management SaaS Platform with AI-powered timetable generation and wellness monitoring. The system consists of:
- **Backend**: Node.js/Express/TypeScript API with Prisma ORM (PostgreSQL)
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

### Backend (Node.js API)
```bash
cd backend

# Development
npm run dev             # Start with nodemon and ts-node (port 5000)
npm run build          # Compile TypeScript
npm start              # Run compiled JavaScript

# Database
npm run prisma:generate
npm run prisma:migrate
npm run prisma:seed

# Testing
npm test               # Run Jest tests
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

# Start services
uvicorn main:app --reload --port 8000           # Main service
uvicorn main_diagnostic:app --reload --port 8001 # Diagnostic service with enhanced feedback

# Run tests
pytest

# Testing Framework
cd ../tt_tester

# Generate test data using unified generator
python3 data_generator.py --size small   # 10 classes, 30 teachers
python3 data_generator.py --size medium  # 20 classes, 60 teachers
python3 data_generator.py --size large   # 40 classes, 121 teachers

# View timetables with universal viewer
python3 timetable_viewer.py --tt-id <TT_ID>  # View specific generation
python3 timetable_viewer.py                   # Auto-detect latest

# Track generation history
python3 tt_generation_tracker.py --list       # List all generations
python3 tt_generation_tracker.py --cleanup    # Remove old files
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

### Key Backend Modules
- **auth/**: JWT-based authentication with bcrypt password hashing
- **users/**: User CRUD with RBAC (admin/principal access control)
- **wellness/**: Stub for future wellness features (not priority)
- **shared/**: Common utilities and middleware

### Frontend Structure (Next.js 15 App Router)
- **app/**: Main application routes using App Router
  - **auth/**: Authentication pages (login/register)
  - **admin/**: Admin dashboard and management
  - **layout.tsx**: Root layout with providers
  - **page.tsx**: Landing page
- **components/**: Reusable React components
- **lib/**: Utility functions and API clients
- Uses Tailwind CSS for styling

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

### Diagnostic Intelligence Architecture
The system prioritizes **observability and actionable feedback**:

#### Core Components (timetable-engine/src/)
- **CSP Complete Solver** (`csp_solver_complete.py`): 100% slot coverage guarantee
- **Resource Advisor** (`resource_advisor.py`): Pre-checks mathematical feasibility
- **Verbose Logger** (`verbose_logger.py`): Real-time constraint violation tracking
- **Bottleneck Analyzer**: Pattern recognition for persistent problems
- **Post-mortem Analysis**: Actionable recommendations ("Hire 2 Math teachers", "Add 1 lab")

#### Services
- **Main Service** (`main.py`): Standard FastAPI on port 8000
- **Diagnostic Service** (`main_diagnostic.py`): Enhanced transparency on port 8001

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

### Backend Integration - IN PROGRESS 🔄
- Auth service implemented with JWT
- User management with RBAC
- Timetable CRUD operations needed
- Python service integration pending

### Frontend - BASIC STRUCTURE ⏳
- Next.js 15 with App Router setup
- Authentication pages created
- Timetable UI components needed
- Dashboard implementation pending

## Development Phases
**Phase 1 - Core Timetable (Current)**
- Focus on reliable timetable generation
- Complete CRUD operations
- Basic UI for viewing/management

**Phase 2 - Wellness (Future)**
- Workload analysis
- Burnout detection
- Wellness dashboard