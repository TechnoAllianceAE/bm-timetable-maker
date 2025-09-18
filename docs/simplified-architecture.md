# Simplified Architecture Plan
## Integrating Wellness Monitor into Main Backend

### Current Issues with Separate Wellness Service
- Duplicate dependencies and infrastructure
- Unnecessary network overhead between services
- Complex deployment and monitoring
- Data consistency challenges across services
- Over-engineered for the actual complexity

### Proposed Simplified Architecture

```
┌─────────────────────────────────────────┐
│           Frontend (Next.js)            │
│     - Timetable UI                      │
│     - Wellness Dashboard                │
│     - Admin Panel                       │
└─────────────┬───────────────────────────┘
              │ HTTPS/WebSocket
              │
┌─────────────▼───────────────────────────┐
│        Main Backend (Node.js)           │
│  ┌─────────────────────────────────────┐ │
│  │         Core Services               │ │
│  │  - Authentication                   │ │
│  │  - User Management                  │ │
│  │  - Timetable CRUD                   │ │
│  │  - Data Import/Export               │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │      Wellness Module (NEW)          │ │
│  │  - Workload Monitoring              │ │
│  │  - Burnout Detection                │ │
│  │  - Alert System                     │ │
│  │  - Analytics & Reporting            │ │
│  │  - Real-time Metrics                │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │      Background Jobs                │ │
│  │  - Wellness Calculations            │ │
│  │  - Alert Processing                 │ │
│  │  - Report Generation                │ │
│  └─────────────────────────────────────┘ │
└─────────────┬───────────────────────────┘
              │ HTTP API
              │
┌─────────────▼───────────────────────────┐
│      Timetable Engine (Python)          │
│  - CSP Solver with Wellness Constraints │
│  - Genetic Algorithm Optimization       │
│  - ML Burnout Prediction               │
│  - Complex Algorithm Processing         │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│           Database Layer                │
│  - PostgreSQL (Primary Data)           │
│  - Redis (Caching & Real-time)         │
└─────────────────────────────────────────┘
```

### Benefits of Simplified Architecture

1. **Reduced Complexity**
   - Single Node.js service to deploy and monitor
   - Unified logging and error handling
   - Simpler database transactions

2. **Better Performance**
   - No network latency between wellness and core services
   - Shared database connections and caching
   - More efficient data access patterns

3. **Easier Development**
   - Single codebase for backend logic
   - Shared utilities and middleware
   - Unified testing strategy

4. **Cost Effective**
   - Fewer infrastructure resources
   - Simpler deployment pipeline
   - Reduced operational overhead

### Implementation Plan

#### Phase 1: Merge Wellness Features
1. Move wellness logic from separate service into main backend
2. Create wellness module structure within backend/src/
3. Integrate wellness routes into main Express app
4. Consolidate database schemas

#### Phase 2: Enhanced Integration
1. Add wellness middleware to existing routes
2. Implement real-time wellness monitoring
3. Create unified API documentation
4. Add comprehensive testing

#### Phase 3: Optimization
1. Implement background job processing for wellness calculations
2. Add caching strategies for wellness metrics
3. Optimize database queries for wellness data
4. Performance testing and tuning

### New Backend Structure

```
backend/
├── src/
│   ├── app.ts                 # Main Express app
│   ├── auth/                  # Authentication (existing)
│   ├── users/                 # User management (existing)
│   ├── timetable/            # Timetable management (existing)
│   ├── wellness/             # NEW: Wellness module
│   │   ├── services/
│   │   │   ├── workloadMonitor.ts
│   │   │   ├── burnoutDetector.ts
│   │   │   ├── alertManager.ts
│   │   │   └── wellnessAnalytics.ts
│   │   ├── routes/
│   │   │   ├── wellness.ts
│   │   │   ├── workload.ts
│   │   │   └── alerts.ts
│   │   ├── middleware/
│   │   │   ├── wellnessCheck.ts
│   │   │   └── workloadValidator.ts
│   │   └── models/
│   │       ├── WellnessMetrics.ts
│   │       └── WorkloadConfig.ts
│   ├── jobs/                 # Background job processors
│   │   ├── wellnessCalculator.ts
│   │   ├── alertProcessor.ts
│   │   └── reportGenerator.ts
│   ├── shared/               # Shared utilities
│   └── types/                # TypeScript definitions
├── prisma/
│   └── schema.prisma         # Unified schema with wellness tables
└── package.json              # Single dependency management
```

### Migration Strategy

1. **Keep wellness-monitor temporarily** during migration
2. **Copy wellness logic** into main backend incrementally
3. **Test integration** thoroughly before removing old service
4. **Update frontend** to use unified API endpoints
5. **Remove wellness-monitor** once migration is complete

This approach maintains all the wellness functionality while significantly simplifying the architecture and reducing operational complexity.