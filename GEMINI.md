# Project Overview

This is a full-stack application for generating and managing school timetables. The project is divided into three main parts: a Next.js frontend, a NestJS backend, and a Python timetable engine.

## Key Technologies

*   **Frontend:** Next.js, React, TypeScript, Tailwind CSS
*   **Backend:** NestJS, TypeScript, Prisma
*   **Timetable Engine:** Python, FastAPI, Google OR-Tools
*   **Database:** PostgreSQL, Redis

## Architecture

The frontend is a Next.js application that communicates with the backend via a REST API. The backend, in turn, communicates with the Python timetable engine to generate the timetables. The database is used to store all the application data.

# Current Status

**Phase 1 Complete - Python Engine v2.5 Production Ready**

*   **End-to-End Integration:** All components (frontend, backend, timetable engine) are fully integrated.
*   **Enterprise-Scale Performance:** The system can generate timetables for 1,600 assignments in under one second.
*   **Production-Ready Backend:** The NestJS backend includes a comprehensive API for all operations.
*   **Complete Frontend:** The Next.js frontend provides UI for rule configuration, diagnostics, and data management.
*   **Grade-Specific Subject Requirements:** The latest feature allows for defining different period allocations for each subject based on grade level.
*   **Known Limitation:** The Genetic Algorithm (GA) Optimizer is currently a placeholder and does not perform actual optimization.

# Development Phases

*   **Phase 1 (Complete):** Core timetable generation and management.
*   **Phase 2 (Planned):** Advanced optimization (implementing the GA Optimizer) and wellness features (workload analysis, burnout detection).

# Python Engine Versions

*   **v2.5 (Recommended):** Latest version with metadata-driven optimization, including subject/teacher preferences and grade-specific requirements.
*   **v2.0 (Legacy):** Stable legacy version without the latest features.

# Building and Running

## Frontend

To build and run the frontend, use the following commands:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Backend

To build and run the backend, use the following commands:

```bash
cd backend
npm install
npm run start:dev
```

The backend will be available at `http://localhost:5000`.

## Timetable Engine

To run the timetable engine, use the following commands:

```bash
cd timetable-engine
pip install -r requirements.txt
python main_v25.py
```

The timetable engine will be available at `http://localhost:8000`.

# Service Management

Convenience scripts are available to start and stop all services at once.

*   **Start all services:** `START_ALL_SERVICES.bat`
*   **Stop all services:** `STOP_ALL_SERVICES.bat`

# Development Conventions

## Testing

To run the tests for each part of the application, use the following commands:

*   **Frontend:** `npm test` in the `frontend` directory.
*   **Backend:** `npm test` in the `backend` directory.
*   **Timetable Engine:** `pytest` in the `timetable-engine` directory.

## Linting

*   **Backend:** `npm run lint` in the `backend` directory.
*   **Frontend:** `npm run lint` in the `frontend` directory.
