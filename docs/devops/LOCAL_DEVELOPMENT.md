# Local development

## Prerequisites and start
Install Docker Desktop/Engine with Compose v2 and Git. Copy `.env.example` to `.env` and generate a local Fernet key with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`; save it as `OUTBOX_ENCRYPTION_KEY`. Keep the key stable for the lifetime of the local database because queued email tokens are encrypted with it. These credentials and the sample Postgres password are development-only and must never be reused in production.

Run `docker compose up --build`. API liveness is `http://localhost:8000/health/live`, readiness is `http://localhost:8000/health/ready`, web is `http://localhost:3000`, Nginx is `http://localhost:8080`, and the development email inbox is `http://localhost:8025`. Compose runs the Alembic migration before API startup. PostgreSQL and Redis are private to the Compose network; access PostgreSQL with `docker compose exec postgres psql -U study -d study`. The Celery worker runs the outbox dispatcher and stores its Beat schedule under `/tmp`. Production must use a controlled one-shot migration job, not the development startup command.

Use `docker compose down` to stop containers while retaining database state. `docker compose down -v` deletes the named local database and Redis volumes; do so only when intended. API and worker share a dependency image. Compose is an ergonomic development baseline, not a production deployment template.

## Development checks
API: `python -m pip install -r requirements-dev.txt`, then `python -m pytest apps/api/tests` and `python -m ruff check apps`. Web: `cd apps/web`, `npm ci`, `npm run lint`, `npm run typecheck`, and `npm run build`. Validate Compose with `docker compose config --quiet`; inspect the active schema with `docker compose run --rm api alembic current`. The initial M1 revision creates identity, tenant, course, audit and email-outbox tables. Do not mount Docker socket, host credentials, or personal documents into application containers.

M1's verified local account flow is registration → Mailpit verification → login → personal course creation → profile update. Document upload and study activities are not available yet.

M2 defaults are MinIO, Tesseract English OCR and OpenAI embeddings. The M2 dependency installation and runtime integration are currently blocked/unverified; do not rely on upload/processing being available until the migration, Docker build and worker tests pass.

## Troubleshooting
If readiness fails, inspect `docker compose logs api postgres redis`. If registration cannot queue email, verify that `OUTBOX_ENCRYPTION_KEY` is a valid Fernet key and is present for both API and worker. If the key changes while encrypted outbox events are pending, those events cannot be delivered; do not silently replace the key. Reset only the named local DB volume when its data is disposable. Do not suppress failed service health or mark API ready when a required dependency is unavailable.
