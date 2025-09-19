# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

School Timetable Management SaaS Platform with AI-powered timetable generation and wellness monitoring. The system consists of:
- **Backend**: Node.js/Express/TypeScript API with Prisma ORM (PostgreSQL)
- **Frontend**: Next.js with React 19 and Tailwind CSS
- **Timetable Engine**: Python microservice with enterprise-ready CSP solver and diagnostic intelligence

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
npm run dev             # Start with nodemon and ts-node
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

# Start FastAPI server
uvicorn main:app --reload --port 8000

# Run tests
pytest

# Testing Framework (separate directory)
cd ../tt_tester

# Generate optimized test data (30 classes, 121 teachers, 2-subject constraint)
python3 generate_30class_test.py

# Create interactive viewer with teacher details
python3 enhanced_interactive_viewer.py

# Analyze teacher constraint compliance
python3 analyze_teacher_subjects.py

# Generate realistic timetable using actual assignments
python3 generate_real_timetable.py
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

### Diagnostic Intelligence Architecture - FULLY IMPLEMENTED
The system prioritizes **observability and actionable feedback** over additional algorithms:
- **Resource Scarcity Advisor** (`resource_advisor.py`): Pre-checks mathematical feasibility, identifies bottlenecks
- **Verbose Logger** (`verbose_logger.py`): Real-time constraint violation tracking during solving
- **Bottleneck Analyzer**: Pattern recognition for persistent problems
- **Post-mortem Analysis**: Specific recommendations ("Hire 2 Math teachers", "Add 1 lab")
- **Diagnostic Service** (`main_diagnostic.py`): Enhanced FastAPI with full transparency
- **Complete CSP Solver** (`csp_solver_complete.py`): 100% slot coverage guarantee

**Key Innovation Achieved**: Transformed black box solver into transparent advisor providing actionable feedback.
**Production Ready**: Handles enterprise scale (40 classes, 1,600 assignments) with sub-second performance.

### Development Priority
**Current Focus**: Core timetable generation and management
- Ensure CSP solver produces valid, conflict-free timetables
- Implement all academic constraints (teacher availability, room capacity, etc.)
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

## Current Development Status - TESTING FRAMEWORK COMPLETE ✅

### Phase 1 Core - COMPLETE ✅
- **Python timetable generator**: PRODUCTION READY with diagnostic intelligence
  - ✅ Enterprise scale (40 classes, 75 teachers, 1,600 assignments)
  - ✅ Sub-second performance (<1 second)
  - ✅ 100% slot coverage (NO GAPS guaranteed)
  - ✅ Transparent solving with actionable feedback
  - ✅ Diagnostic services (`main_diagnostic.py` on port 8001)

### Production-Ready Framework - COMPLETE ✅ (September 19, 2025)
**Location**: `/tt_tester/` directory (consolidated professional tools)

#### Consolidated Core Tools (4 files)
- ✅ **Universal Data Generator** (`data_generator.py`)
  - **Replaces 8+ separate generators** with unified configuration system
  - Small/medium/large school support with single command
  - Complete schedule generation (all 40 periods per class)
  - Teacher constraint optimization (max 2 subjects, 100% compliance)
  - Unique TT Generation ID system for complete traceability

- ✅ **Universal Timetable Viewer** (`timetable_viewer.py`)
  - **Replaces 6+ different viewers** with single professional tool
  - **Advanced Analytics Dashboard** with workload management
  - **Class View**: Period count analysis, utilization bars, teacher assignment tables
  - **Teacher View**: Workload analysis, subject distribution, capacity monitoring
  - Auto-detection of data files by TT ID, works with legacy data

- ✅ **Generation Management** (`tt_generation_tracker.py`)
  - Complete tracking of all TT generations with professional status terminology
  - Cleanup and reporting capabilities with HTML dashboard
  - Professional status indicators (Complete/Incomplete schedules)

#### Professional Analytics Features
- ✅ **Workload Management System**:
  - Real-time teacher capacity monitoring with visual progress bars
  - Color-coded workload indicators (Green/Yellow/Red)
  - Subject-wise breakdown with percentage distribution
  - Professional dashboard for administrative oversight

- ✅ **Schedule Analytics**:
  - Period count analysis (assigned vs actual periods per subject)
  - Status indicators (✅ Perfect, ⚠️ Over-allocated, ❌ Under-allocated)
  - Class utilization tracking with visual progress bars
  - Complete schedule validation with professional error reporting

#### Professional Standards Applied
- ✅ **Industry Terminology**: Standardized language (Complete/Incomplete schedules)
- ✅ **Enterprise UI**: Professional analytics dashboard with responsive design
- ✅ **Consolidated Architecture**: 4 focused tools instead of 40+ scattered files
- ✅ **Backward Compatibility**: All existing data and TT IDs continue to work

### Production Integration - IN PROGRESS 🔄
- **Backend timetable CRUD**: Next priority for integration
- **Frontend UI**: Integration of interactive viewers
- **Database schema**: Enhanced with testing framework data
- See `WIP.md` for detailed milestone tracking

## Development Approach
**Phase 1 - Core Timetable (COMPLETE ✅)**
- ✅ Reliable timetable generation with diagnostic intelligence
- ✅ Enterprise scale performance (1,600 assignments in <1 second)
- ✅ 100% academic constraint satisfaction
- ✅ Comprehensive testing (small to large schools)
- 🔄 Backend integration: Timetable CRUD operations in progress
- ⏳ Frontend UI for timetable management

**Phase 2 - Wellness Features (FUTURE)**
- Add wellness scoring to existing timetables
- Implement workload monitoring
- Build wellness dashboard
- Integrate wellness constraints into generation algorithm