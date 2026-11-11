# Project status

**Status:** Phase 1 architecture delivered. Phase 2 audit complete. M1 platform foundation is implemented and verified. M2 learning content engine is active but not complete or runtime-verified. This is not the product MVP: AI tutoring, assessments, learning intelligence, 3D library, billing, and production deployment are not implemented.

## Repository and audit
- The requested `D:\Projects\Studying Assistant` is not mounted. Work is in `C:\Users\mjbee\Desktop\programing\Tools\API\studying agent`; this workspace has no Git repository. The files have not been committed or transferred to D:.
- Phase 1 was architecture plus a skeleton. The Phase 2 audit confirmed there had been no application models, migrations, auth, tenant APIs, or functional auth UI.
- Documentation and implementation agree on a modular monolith, personal-organization tenant boundary, PostgreSQL/pgvector, Redis/Celery, and opaque server-managed sessions. Production email, identity vendor, cloud/object storage, embedding model/dimension, OCR provider, residency, retention/age policy, pricing, and RPO/RTO remain undecided.
- Host tools verified: Python 3.14.3, Node 24, npm 11, Docker Compose 5.3. Production images target Python 3.12 and Node 22.

## Milestone status

| Milestone | Status | Exit evidence |
|---|---|---|
| M1 Platform foundation | Complete | PostgreSQL Alembic migration applied; 11 API tests pass; live Compose stack healthy; browser signup, email verification, login, course creation, profile update and sign-out verified. |
| M2 Learning content engine | Active; blocked on dependency permissions | Upload/storage/processing source changes are in progress. No M2 migration, Docker image build, worker integration test, or frontend material UI has been verified. |
| M3 AI tutoring engine | Pending | Not implemented; provider/model/region remains a launch decision. |
| M4 Assessment engine | Pending | Not implemented. |
| M5 Learning intelligence | Pending | Not implemented. |
| M6 Immersive frontend | Pending | Not implemented; no 3D scene is shipped. |
| M7 Integration and reliability | Pending | M1 runtime was smoke-tested; full learning journey, production operations and recovery remain outstanding. |

## M1 implementation delivered
- SQLAlchemy 2 models and initial Alembic revision for users, profiles, personal organizations, memberships, courses, hashed auth sessions, email tokens, audit events, and transactional outbox.
- Email/password registration, email verification/resend, login/logout, password reset, profile read/update, opaque server-managed sessions, CSRF/origin checks, Redis rate limiting, structured request/error logging, and membership-scoped course operations.
- Celery outbox delivery to SMTP; local Compose uses Mailpit. The Celery Beat schedule is written under `/tmp` to remain writable by the non-root worker.
- Next.js auth routes, typed API helper, accessible forms, authenticated app shell, course library/create flow, course detail, and profile settings. Unimplemented future workflows are explicitly labeled.
- Backend tests cover health, registration/verification/login, CSRF, password reset/session revocation, expired tokens, unavailable email configuration, cross-tenant access, and course archive behavior.

## Validation
- `python -m ruff check apps`: passed.
- `python -m pytest apps/api/tests`: 11 passed. Existing pytest-asyncio and Starlette/httpx deprecation warnings remain.
- Web `npm run lint`, `npm run typecheck`, `npm run build`: passed.
- `docker compose config --quiet`: passed.
- Full Compose services started; API/PostgreSQL/Redis/Mailpit/worker/Nginx/web health and HTTP probes passed.
- Live integration passed: browser registration -> worker-delivered Mailpit email -> verification -> browser login -> tenant-scoped course creation -> profile update -> sign-out.

## Security and known limitations
- Rate limiting currently keys on the direct peer address. Production Nginx/proxy-aware client IP handling must use a trusted-proxy configuration before relying on IP quotas.
- Local development requires a stable `OUTBOX_ENCRYPTION_KEY` in `.env`; do not recreate services with a different key while encrypted outbox events remain pending.
- Email delivery is local SMTP only. No production SMTP, identity provider, MFA, account deletion/export, or production secrets management is configured.
- Authorization is enforced by membership-scoped queries and tested across users. PostgreSQL row-level security is not enabled.
- Frontend automated browser coverage is not yet committed; the M1 browser workflow was exercised against the live stack.
- M2 is not complete: required Python packages could not be installed after two attempts (`WinError 5`, access denied to the Python user site-packages). Per environment policy, no alternate installation location or container-based dependency-install workaround was attempted. The pre-M2 running Compose stack remains on the verified M1 image.
- No production readiness, compliance certification, or complete MVP is claimed.

## Blockers and decisions
The requested D: repository remains inaccessible. Before production, decide cloud/region, private object storage, production email/identity, embedding provider and dimension, OCR, data retention and age policy, launch audience, pricing/billing, and RPO/RTO. Existing npm audit findings should be reassessed against a compatible upstream fix; do not apply the available major-version downgrade.

## M2 decisions and next action
Selected defaults: MinIO in local development, Tesseract English OCR, and OpenAI embeddings (`text-embedding-3-small`, 1536 dimensions). Production storage/region remains undecided. Current M2 source also pins these provider choices, but until dependency access is restored, the Alembic migration is generated and reviewed, and the live Compose upload-to-processing workflow passes, M2 remains blocked and unverified.

**Next action:** restore normal project dependency-install permission, then complete M2 tests, migration generation, MinIO/API/worker integration, and the material-management UI before moving to M3.
