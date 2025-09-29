# Backend Service

TypeScript Express API that powers authentication, user management, and timetable orchestration for the School Timetable Management platform.

## Requirements

- Node.js 18+
- SQLite (default) or any Prisma-supported database (configure via `DATABASE_URL`)
- Python timetable engine running locally (defaults to `http://localhost:8000`)

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `PORT` | `3000` | HTTP port for the Express server |
| `API_PREFIX` | `/api/v1` | Base path prefix for all API routes |
| `JWT_SECRET` | `your-secret-key-change-in-prod` | Secret used to sign JWTs |
| `TIMETABLE_ENGINE_URL` | `http://localhost:8000` | Base URL for the Python timetable microservice |
| `TIMETABLE_ENGINE_TIMEOUT` | `90000` | Timeout (ms) for generation requests |
| `DATABASE_URL` | `file:../prisma/dev.db` | Prisma datasource connection string |

Create a `.env` file in `backend/` if you need to override defaults.

## Installation & Local Development

```bash
cd backend
npm install
npm run dev
```

The dev server runs with `nodemon` + `ts-node` and automatically recompiles on changes.

### Compile to JavaScript

```bash
npm run build
```

## Core Routes

All routes are available under the configured `API_PREFIX` (default `/api/v1`).

### Auth

- `POST /auth/register` – create a new user and issue JWT
- `POST /auth/login` – authenticate user and issue JWT

### Users (admin/principal only unless otherwise stated)

- `GET /users?schoolId=` – list users in the current school
- `POST /users` – create user (auto-creates teacher profile when role is `TEACHER`)
- `GET /users/:id` – fetch user details; owner or privileged roles only
- `PUT /users/:id` – update email, role, profile, or preferences
- `DELETE /users/:id` – remove a user

### Timetables (admin/principal privileges required for generation)

- `GET /timetables` – list timetables for the signed-in user’s school
- `POST /timetables` – create a draft timetable for an academic year
- `GET /timetables/:id` – fetch timetable with associated entries
- `GET /timetables/:id/entries` – list entries for a timetable
- `POST /timetables/:id/generate` – call the Python engine and persist the best solution

Request bodies are validated with Joi via the shared `validateRequest` middleware. All private routes require a `Bearer` token issued by the auth endpoints.

## Timetable Generation Flow

1. Admin/principal creates a timetable draft via `POST /timetables`.
2. Generation endpoint gathers classes, subjects, teachers, rooms, time slots, and constraints for the school.
3. Service calls the Python microservice (`/generate`) and selects the highest-scoring solution.
4. Existing entries are replaced with generated ones inside a single transaction.
5. Timetable status transitions from `DRAFT → GENERATING → ACTIVE` (or `FAILED` when an exception occurs).

Ensure the Python service is running before triggering generation. You can point `TIMETABLE_ENGINE_URL` to the diagnostic FastAPI server if needed.

## Database Notes

- Prisma uses the schema in `prisma/schema.prisma`.
- Migrations have not been generated yet; run `npx prisma migrate dev --name init` when ready. Because the repo runs in a restricted environment, you may need to execute migrations locally on your machine.
- JSON-like columns are currently stored as stringified JSON for compatibility with SQLite.

## Testing

Test scaffolding (`jest` + `supertest`) is included in `package.json`. Add integration tests under `src/__tests__` and run:

```bash
npm test
```

---

For details on the overall product roadmap, refer to the root `README.md` and `WIP.md` files.
