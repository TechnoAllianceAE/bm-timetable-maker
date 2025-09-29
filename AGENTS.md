# Repository Guidelines

## Project Structure & Module Organization
- `frontend/` houses the Next.js 15 interface under `app/`; consolidate route groups here and keep shared UI in `app/(components)`.
- `backend/` contains the Express API (`src/` services, `prisma/` schema + seed) and exposes auth, timetable, and user endpoints.
- `timetable-engine/` delivers the Python solver (`src/` algorithms, `main.py` CLI entry); keep contract changes aligned with backend DTOs.

## Build, Test, and Development Commands
- Frontend: `cd frontend && npm install && npm run dev` for local dev, `npm run build` for production bundles, `npm run lint` to enforce ESLint/Tailwind rules.
- Backend: `cd backend && npm install && npm run dev` launches Nodemon; `npm run build` transpiles TypeScript; `npm run test` runs Jest + Supertest; Prisma workflows live under `npm run prisma:*`.
- Engine: `cd timetable-engine && pip install -r requirements.txt` then `python main.py`; switch to `main_diagnostic.py` when inspecting failing constraints.

## Coding Style & Naming Conventions
- TypeScript and Python files use 2-space indentation with trailing commas; group imports by origin (node, external, local).
- Use `camelCase` for functions/variables, `PascalCase` for React components and service classes, and kebab-case for Next.js route folders.
- Run `npm run lint` (frontend) and `npm run test` (backend) before opening a PR; format Prisma schema with `npx prisma format` when editing models.

## Testing Guidelines
- Backend tests belong beside code in `src/**/__tests__` or `*.spec.ts`; cover auth guards, timetable CRUD, and Prisma mappers with Jest.
- Frontend interactions should be verified with component tests (set up Testing Library + Jest) and smoke-checked via `npm run lint` until the harness lands.
- For the solver, stage fixtures in `timetable-engine/src/tests/` and add a `pytest` script to CI once the suite stabilizes.

## Commit & Pull Request Guidelines
- Follow Conventional Commit prefixes (`feat:`, `fix:`, `chore:`) as seen in recent history; avoid single-word or all-caps summaries.
- PRs must link issues, summarise behaviour changes, list schema/contract updates, and attach UI captures or sample solver output when relevant.
- Confirm successful `lint`, `test`, and engine runs in the PR body so reviewers can trust the verification trail.

## Security & Configuration Tips
- Store secrets in `.env.local` (frontend) and `.env` (backend); document required keys such as `DATABASE_URL`, `JWT_SECRET`, `FRONTEND_URL` instead of committing them.
- Run `prisma migrate dev` only against disposable databases; coordinate schema updates with engine payload expectations to avoid runtime drift.
