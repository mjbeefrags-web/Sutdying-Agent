# API specification (v1)

Base `/api/v1`; JSON; UUID path IDs; timestamps RFC 3339 UTC. FastAPI exposes OpenAPI; review compatibility before publishing an external client. Authentication uses an opaque server-managed cookie; CSRF and same-origin checks protect browser mutations. Resource routes require membership in the owning organization.

## Implemented M1 routes

| Method | Route | Purpose |
|---|---|---|
| POST | `/auth/register` | Create account, profile, personal organization and verification email outbox item (`202`) |
| POST | `/auth/email/verify` | Consume a one-time email verification token |
| POST | `/auth/email/resend` | Resend verification link with generic response |
| POST | `/auth/login` | Verify credentials and set opaque session plus CSRF cookies |
| GET | `/auth/session` | Return the authenticated user/profile |
| POST | `/auth/logout` | CSRF-protected session revocation and cookie deletion (`204`) |
| POST | `/auth/password-reset/request` | Queue a reset link with a generic response (`202`) |
| POST | `/auth/password-reset/confirm` | Consume reset token, update password and revoke sessions |
| GET/PATCH | `/account/profile` | Read or update the authenticated profile |
| GET | `/organizations` | List organizations reachable through the current user's memberships |
| GET/POST | `/organizations/{organization_id}/courses` | List or create courses after membership check |
| GET/PATCH/DELETE | `/courses/{course_id}` | Read, update or archive an accessible course |
| GET | `/courses` | List accessible, non-archived courses |
| GET | `/health/live`, `/health/ready` | Process liveness and PostgreSQL/Redis dependency readiness |

All mutation requests from the browser require the configured `Origin`; authenticated mutations additionally require the CSRF cookie value in `X-CSRF-Token`. Registration and reset responses do not disclose whether an email address exists. Email is delivered through the transactional outbox and worker.

## Planned routes (not implemented)

| Method | Route | Purpose |
|---|---|---|
| POST | `/courses/{course_id}/documents` | Request upload URL / create upload |
| POST | `/documents/{id}/complete` | Verify upload and enqueue ingestion |
| GET/DELETE | `/documents/{id}` | Processing state / request deletion |
| GET | `/jobs/{job_id}` | Authorized processing status |
| POST | `/courses/{course_id}/tutor/messages` | Ask a grounded question; return answer/citations or job/stream |
| POST/GET | `/courses/{course_id}/flashcards` | Create/list cards |
| POST | `/flashcards/{id}/reviews` | Record recall result, return next due |
| POST/GET | `/courses/{course_id}/exams` | Generate/list practice exam |
| POST | `/exams/{id}/attempts` | Begin or submit attempt |
| GET | `/courses/{course_id}/analytics` | Authorized aggregate progress |
| POST/GET | `/account/exports`, `/account/deletion` | Request and track privacy operations |
| GET | `/health/live`, `/health/ready` | Process liveness and dependency readiness |

Use cursor pagination and bounded page size. Upload completion, generation and deletion accept `Idempotency-Key`. AI generation returns `202` with job ID when asynchronous, otherwise bounded streaming response with explicit completion/error event. Citation schema: document/version ID, page/section, chunk reference, quote excerpt, confidence/retrieval metadata hidden or exposed only when useful. Never accept client-provided chunk text as evidence.

## Errors
`{"error":{"code":"document_not_ready","message":"The document is still processing.","request_id":"...","details":{}}}`. Return generic 404 for unauthorized resource IDs when existence disclosure is unnecessary. Rate limits are per user/tenant and provider-cost class. API schema changes use additive evolution; breaking changes require a new version.

## Contract omissions
Planned routes above are design-only, not an OpenAPI implementation. Billing, OAuth/provider callbacks, session rotation policy, upload presigning, streaming protocol and per-feature quotas remain undecided or unimplemented. Current M1 rate limits are configured per auth operation and course creation; production proxy-aware IP identity must be configured before relying on IP-based limits.
