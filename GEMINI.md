# Project Overview

This is a full-stack application for generating and managing school timetables. The project is divided into three main parts: a Next.js frontend, a Node.js backend, and a Python timetable engine.

## Key Technologies

*   **Frontend:** Next.js, React, TypeScript, Tailwind CSS
*   **Backend:** Node.js, Express, TypeScript, Prisma
*   **Timetable Engine:** Python, FastAPI, Google OR-Tools
*   **Database:** PostgreSQL, Redis

## Architecture

The frontend is a Next.js application that communicates with the backend via a REST API. The backend, in turn, communicates with the Python timetable engine to generate the timetables. The database is used to store all the application data.

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
npm run dev
```

The backend will be available at `http://localhost:3001`.

## Timetable Engine

To run the timetable engine, use the following commands:

```bash
cd timetable-engine
pip install -r requirements.txt
python main.py
```

The timetable engine will be available at `http://localhost:8000`.

# Development Conventions

## Testing

To run the tests for each part of the application, use the following commands:

*   **Frontend:** `npm test` in the `frontend` directory.
*   **Backend:** `npm test` in the `backend` directory.
*   **Timetable Engine:** `python -m pytest` in the `timetable-engine` directory.

## Linting

To lint the code, use the `npm run lint` command in the `frontend` directory.
