# Node.js Backend Integration with Python Timetable Generator Microservice

## Overview
The Python Timetable Generator is a microservice that handles the computational-intensive timetable generation and optimization, as per the PRD architecture (section 4.3: Timetable Engine Python microservice). The Node.js backend (Express) calls this service via HTTP/REST for operations like timetable generation. This keeps the backend lightweight, delegating heavy lifting to Python for CSP and GA algorithms.

**Communication Protocol:**
- **Endpoint:** `http://timetable-engine:8000` (Docker/K8s service name) or `http://localhost:8000` for local.
- **Auth:** API key in header (`X-API-Key`) or JWT from gateway (implement in FastAPI dependency).
- **Async Support:** Use Node.js promises/async-await for non-blocking calls.
- **Error Handling:** Parse JSON errors with conflicts/suggestions from Python exceptions.
- **Timeout:** Set 60s for generation; use /validate first for quick checks.

**Dependencies in Node.js:**
- `axios` for HTTP client: `npm install axios`.
- Optional: `prom-client` for metrics, `winston` for logging calls.

## Key Endpoints and Usage

### 1. Generate Timetable (`POST /generate`)
- **Purpose:** Generate 3-5 optimized timetables with wellness analysis.
- **Request Body:** GenerateRequest (JSON, matching Pydantic models).
  Example (fetch from Prisma DB first):
  ```javascript
  const requestData = {
    school_id: "school-uuid",
    academic_year_id: "ay-uuid",
    classes: [ /* array of class objects from DB */ ],
    subjects: [ /* subjects */ ],
    teachers: [ /* teachers with configs */ ],
    time_slots: [ /* time slots */ ],
    rooms: [ /* rooms */ ],
    constraints: [ /* constraints */ ],
    options: 3,
    timeout: 60,
    weights: { academic: 0.35, wellness: 0.30, efficiency: 0.20, preference: 0.15 }
  };
  ```
- **Response:** GenerateResponse (array of TimetableSolution with analysis).
- **Node.js Example (Express route):**
  ```javascript
  const axios = require('axios');

  app.post('/timetables/:id/generate', async (req, res) => {
    try {
      // Fetch data from Prisma
      const schoolId = req.params.id;
      const classes = await prisma.class.findMany({ where: { schoolId } });
      const subjects = await prisma.subject.findMany({ where: { schoolId } });
      const teachers = await prisma.teacher.findMany({ where: { user: { schoolId } } });
      const teacherConfigs = await prisma.teacherWorkloadConfig.findMany({ where: { teacherId: { in: teachers.map(t => t.id) } } });
      const timeSlots = await prisma.timeSlot.findMany({ where: { schoolId } });
      const rooms = await prisma.room.findMany({ where: { schoolId } });
      const constraints = await prisma.constraint.findMany({ where: { schoolId } });

      const payload = {
        school_id: schoolId,
        academic_year_id: req.body.academicYearId,  // From request
        classes, subjects, teachers, teacher_configs: teacherConfigs,
        time_slots: timeSlots, rooms, constraints,
        options: req.body.options || 3,
        timeout: 60,
        weights: req.body.weights || { academic: 0.35, wellness: 0.30, efficiency: 0.20, preference: 0.15 }
      };

      const response = await axios.post('http://timetable-engine:8000/generate', payload, {
        timeout: 60000,
        headers: { 'X-API-Key': process.env.TT_API_KEY, 'Content-Type': 'application/json' }
      });

      // Save results to DB (timetables, entries)
      const solutions = response.data.solutions;
      for (let i = 0; i < solutions.length; i++) {
        const sol = solutions[i];
        const newTt = await prisma.timetable.create({
          data: {
            schoolId: schoolId,
            academicYearId: payload.academic_year_id,
            version: i + 1,
            status: 'DRAFT',
            wellnessScore: sol.wellness_analysis.overall_score,
            workloadBalanceScore: sol.total_score,  // Adjust
            wellnessAnalysis: sol.wellness_analysis,
            entries: { create: sol.timetable.entries.map(e => ({ ...e, timetableId: undefined })) }
          }
        });
        // Notify users, etc.
      }

      res.json(response.data);
    } catch (error) {
      if (error.response && error.response.status === 400) {
        // Infeasible
        const { message, conflicts, suggestions } = error.response.data;
        // Log conflicts, return to user with suggestions
        res.status(400).json({ message, conflicts, suggestions });
      } else if (error.code === 'ECONNABORTED') {
        res.status(408).json({ message: 'Generation timed out' });
      } else {
        res.status(500).json({ message: 'Internal error in timetable generation' });
      }
    }
  });
  ```

### 2. Validate Constraints (`POST /validate`)
- **Purpose:** Quick feasibility check before full generation.
- **Request Body:** ValidateRequest (entities dict, constraints).
- **Response:** ValidationResult (feasible bool, conflicts, suggestions).
- **Node.js Example:**
  ```javascript
  const validatePayload = {
    constraints: constraints,  // From DB
    entities: { classes, teachers, time_slots }  // Subset
  };

  const valResponse = await axios.post('http://timetable-engine:8000/validate', validatePayload);
  if (!valResponse.data.feasible) {
    // Return suggestions to admin UI
    return res.status(400).json(valResponse.data);
  }
  // Proceed to generate
  ```

### 3. Health Check (`GET /health`)
- **Purpose:** K8s liveness/readiness probe.
- **Node.js:** Optional ping before calls.

## Deployment and Running
- **Python Service:** 
  - Install deps: `pip install -r requirements.txt`
  - Run: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` (dev) or Gunicorn for prod.
  - Docker: Dockerfile with FROM python:3.11, COPY ., pip install, CMD uvicorn.
- **Node.js Calls:** Use service discovery in K8s; env var for URL in dev.
- **Monitoring:** Python exposes /metrics for Prometheus; log calls in Node.js.
- **Error Propagation:** Catch 4xx/5xx, map to PRD responses (e.g., 400 for conflicts with suggestions in body).

## Best Practices
- **Data Fetch:** Use Prisma to query entities in Node.js before calling Python (efficient, no DB in Python).
- **Caching:** Cache frequent validations (Redis in Node.js).
- **Scalability:** Python scales horizontally; Node.js queues requests if busy.
- **Security:** Validate payloads in both; use HTTPS in prod.
- **Testing:** Mock Python service in Node.js tests with nock or msnock.

This integration enables seamless workflow: Admin requests generation -> Node.js fetches DB -> Python computes -> Node.js saves results -> UI updates.