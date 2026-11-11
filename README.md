# Study Platform

Phase 1 foundation for a private, course-grounded study workspace. The repository is a modular monorepo; the product/architecture specifications live in [`docs/`](docs/).

## Local development
1. Install Docker with Compose v2.
2. Copy `.env.example` to `.env` (its values are local placeholders only).
3. Generate an outbox encryption key with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` and set `OUTBOX_ENCRYPTION_KEY` in `.env`.
4. Run `docker compose up --build`.
5. Open `http://localhost:3000` (web), `http://localhost:8000/health/live` (API), `http://localhost:8080` (Nginx proxy), or `http://localhost:8025` (development email inbox).

Validate Compose with `docker compose config --quiet`. API checks: `python -m pip install -r requirements-dev.txt`, then `python -m pytest` and `python -m ruff check apps`. Web checks from `apps/web`: `npm ci`, `npm run lint`, `npm run typecheck`, `npm run build`.

## Repository map
- `apps/web`: Next.js/TypeScript shell (no production product flows yet).
- `apps/api`: FastAPI service, configuration, health endpoints and Alembic setup.
- `apps/worker`: Celery worker entry point and health task.
- `packages/contracts`, `packages/shared`: future generated contracts and cross-app utilities.
- `infrastructure`: Docker, Nginx and GitHub references; active workflow is in `.github/workflows`.
- `docs`: product, architecture, design, AI, DevOps, management and ADRs.

## Phase 1 status
Configuration and health skeleton only. Authentication, schema migrations, tenant CRUD, document processing, AI, learning workflows, billing and the full UI are not implemented. See [`PROJECT_STATUS.md`](docs/management/PROJECT_STATUS.md) and [`BACKLOG.md`](docs/management/BACKLOG.md).
