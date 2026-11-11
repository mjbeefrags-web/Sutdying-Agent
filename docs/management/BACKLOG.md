# Prioritized GitHub-ready backlog

Effort uses XS (<1d), S (1-3d), M (1-2w), L (2-4w), XL (>4w); estimates are planning ranges, not commitments. Prefix IDs are stable issue labels and can be copied into GitHub issue titles.

## Completed — M1 platform foundation

### [M] Establish API domain and migration baseline
**Status:** Complete.
**Delivered:** SQLAlchemy identity/tenant/course schema, initial reviewed PostgreSQL migration, health/readiness and structured errors/logging.
**Verification:** Migration applied to PostgreSQL in Compose; readiness fails closed on dependency errors; backend tests pass.

### [L] Implement verified identity and revocable sessions
**Status:** Complete for the M1 local email/password scope; production identity, MFA and provider decisions remain open.
**Delivered:** Registration, verification/resend, login/logout, reset, secure opaque sessions, CSRF/origin checks, rate limits and outbox email.
**Verification:** Auth lifecycle, expiry, logout/reset revocation, CSRF and live Mailpit flow.

### [L] Add personal organizations and tenant-scoped courses
**Status:** Complete for personal organizations and course CRUD/archive.
**Verification:** Cross-user course and organization access denied; browser creates and opens a course.

### [M] Deliver M1 account and course UI
**Status:** Complete for auth, library, course detail and profile settings.
**Delivered:** Accessible login/register/verify/reset routes, authenticated shell, course create/list, profile edit.
**Verification:** Lint, typecheck, production build and live browser flow pass. Document reader, tutor, assessments, analytics and 3D are not included.

## P0 — M2 learning content engine (active, not verified)

**Selected defaults:** MinIO for local object storage, Tesseract English OCR, OpenAI `text-embedding-3-small` (1536 dimensions). Production object storage/region remains open.
**Blocker:** Windows denied the normal dependency installation (`WinError 5`, Python user site-packages access denied). Do not mark any M2 item complete until dependencies, migration, worker and UI are verified.

### [L] Implement private document upload lifecycle
**Description:** Add course-scoped document metadata/state, bounded upload API, private local object-storage adapter for development, and idempotent processing jobs.
**Dependencies:** M1 identity, tenant/course model and worker/outbox baseline; production object-storage decision before deployment.
**Acceptance:** Membership is checked for every operation; extension/MIME/signature/size are validated; object access is private; status and safe deletion are visible; duplicate/retry behavior is explicit.
**Tests:** Valid/invalid/oversize/replay/concurrent uploads, authorization negatives, persistence and worker idempotency.
**Effort:** L.

### [L] Build safe PDF and text ingestion
**Description:** Extract text/page locations from supported PDFs, create immutable source versions and chunks, and surface unsupported/scanned PDFs as explicit states. Add OCR only after provider selection.
**Dependencies:** Document lifecycle; parser/OCR decision for OCR support.
**Acceptance:** Parser has resource limits and no network access; malformed/encrypted files fail safely; processing can retry idempotently; OCR is never represented as available until integrated.
**Tests:** Malformed/encrypted/scanned fixtures, page citations, memory/time bounds and retry behavior.
**Effort:** L.

## P0 — Architecture and decisions

### [M] Approve deployment, privacy, and AI provider decisions
**Description:** Resolve cloud/region, object store, identity/vendor, OCR, embedding dimensions, retention/age policy, and target launch audience; update ADRs and threat model.
**Dependencies:** M0; product/legal/security stakeholder review.
**Acceptance:** Each choice has an owner, evidence, data-flow impact, cost/exit plan, and approval; no production secrets or provider credentials in repository.
**Tests:** Architecture review, privacy threat-model review, dependency compatibility and cost assumptions checked.
**Effort:** M.

## P0 — Foundation/security

### [M] Deliver account export and deletion workflow
**Description:** Export user data and orchestrate deletion of relational, object, vector, cache and provider-retained data as policy allows.
**Dependencies:** Identity, tenant model, object store.
**Acceptance:** Explicit confirmation/status; access revoked immediately; verified purge/retention evidence; audit without content.
**Tests:** end-to-end deletion and export fixtures, retry/idempotency and backup-retention behavior.
**Effort:** M.

## P1 — Learning engine

### [L] Implement private document upload lifecycle
**Description:** Scoped upload, checksum validation, state machine, private storage adapter and idempotent jobs.
**Dependencies:** tenant model, object storage decision.
**Acceptance:** File signature/size checks; duplicate handling; visible states; safe deletion; no public object access.
**Tests:** valid/invalid/oversize/replay/concurrent upload and cross-tenant tests.
**Effort:** L.

### [L] Build safe PDF and text ingestion
**Description:** Isolated extraction, OCR fallback, immutable versions, source locations and chunk creation.
**Dependencies:** upload lifecycle, parser/OCR decision.
**Acceptance:** Explicit errors and resource limits; no network access; versioned parser metadata; idempotent retry.
**Tests:** malformed/encrypted/scanned fixtures, decompression/time/memory bounds.
**Effort:** L.

### [L] Build retrieval and grounded tutor
**Description:** Provider-neutral embedding/chat adapters, hybrid retrieval, citations, abstention and rate/cost guardrails.
**Dependencies:** ingestion, embedding/model/region decision.
**Acceptance:** citations resolve to authorized chunks; fail closed on invalid citation; per-user budgets; no sensitive prompt logs.
**Tests:** retrieval golden set, injection, leakage, provider timeout/schema/cost tests.
**Effort:** L.

### [M] Add flashcard authoring and spaced review
**Description:** Editable cards and deterministic versioned review scheduler.
**Dependencies:** tenant model; ingestion for citations.
**Acceptance:** User can edit/delete; every review is immutable; next due explainable; scheduler version stored.
**Tests:** transition table/property tests, duplicate submissions and tenant isolation.
**Effort:** M.

### [L] Add practice exams and explainable mastery
**Description:** Low-stakes exams, answer review and topic evidence summaries.
**Dependencies:** learning model; RAG for source-backed generation.
**Acceptance:** Answer key hidden until submission; generated items trace to sources; mastery shows evidence/uncertainty.
**Tests:** authorization, grading, source validation, accessibility and calibration eval.
**Effort:** L.

## P1/P2 — Product experience and operations

### [L] Deliver accessible 2D study workflows
**Description:** Library list, course workspace, reader, tutor, practice, analytics and profile routes.
**Dependencies:** API contracts; may use fixtures initially.
**Acceptance:** loading/empty/error states, keyboard completion, reduced motion, WCAG audit findings triaged.
**Tests:** component, Playwright smoke, axe, zoom and screen reader checks.
**Effort:** L.

### [M] Add progressive 3D library
**Description:** Lazy optional R3F library with semantic list fallback and performance guard.
**Dependencies:** 2D library route.
**Acceptance:** WebGL-disabled/reduced-motion/keyboard users complete same task; scene under asset/frame budgets.
**Tests:** browser context-loss, capability fallback, low-tier device and performance test.
**Effort:** M.

### [M] Production observability and recovery drills
**Description:** Metrics/logs/traces/alerts, runbooks, backup restore and incident simulation.
**Dependencies:** deployment platform and SLO decisions.
**Acceptance:** no content/secret leakage; alerts actionable; restore meets approved RPO/RTO.
**Tests:** alert simulation, restore drill, log redaction test.
**Effort:** M.

### [M] Beta validation and commercial decision
**Description:** Usability study, pricing research, legal/privacy review, support readiness.
**Dependencies:** M6 feature gates and target audience approval.
**Acceptance:** measured activation/grounding/usability results; pricing and privacy policy approved; unresolved risks have owners.
**Tests:** research protocol and release checklist review.
**Effort:** M.

### [L] Implement subscription entitlements and billing
**Description:** Add a hosted payment-provider integration only after pricing and provider/privacy review; keep subscriptions and entitlements in the modular monolith.
**Dependencies:** Beta validation, commercial/legal approval, account lifecycle.
**Acceptance:** Verified signatures and idempotent webhooks; server-side entitlement checks; cancellation/refund/failed-payment states; no card data stored by this platform; accessible account controls.
**Tests:** Provider sandbox webhooks, replay/forgery tests, entitlement authorization and cancellation lifecycle.
**Effort:** L.

### [M] Execute controlled launch readiness gate
**Description:** Prepare support, incident response, abuse handling, analytics consent, deployment runbooks, and staged beta/launch rollout.
**Dependencies:** M6, approved pricing/privacy terms, tested backup restore and SLOs.
**Acceptance:** Owners staffed; release gates signed; support/escalation path available; rollback and kill-switch rehearsals complete; no unresolved critical/high risks.
**Tests:** Launch tabletop, restore/rollback drill, monitoring alert simulation and go/no-go review.
**Effort:** M.
