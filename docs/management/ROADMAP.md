# Roadmap

## Phase 1 — Architecture and foundation (complete)
Product/technical design, ADRs, local Compose baseline, API/worker skeleton and documented exit gates.

## Phase 2 — Secure platform foundation (M1 complete)
Identity/session, personal tenant bootstrap, courses, audit events, migrations and auth/tenant tests. M1 exit verified against PostgreSQL, Redis, SMTP/Mailpit, Celery, browser auth and course workflows.

## Phase 3 — Learning content engine (M2 active, blocked)
Private document upload lifecycle, scoped MinIO development storage, safe extraction, Tesseract fallback, source versioning, pgvector embeddings and visible status. Selected local defaults are MinIO, Tesseract and OpenAI `text-embedding-3-small` (1536 dimensions). Complete migration, runtime, security and UI verification before exit. Development dependency installation is currently denied by Windows access policy; no alternate install path has been used.

## Phase 4 — AI intelligence (M3 pending)
Provider adapters, embeddings, retrieval/reranking, grounded tutor and generation, evaluation harness, quotas/telemetry. Exit only after authorization, citation, quality, security and cost gates pass.

## Phase 5 — Assessment and learning intelligence (M4/M5 pending)
Source-backed cards and exams, deterministic grading, immutable review evidence, explainable mastery and study recommendations.

## Phase 6 — Frontend experience (M6 pending)
Accessible 2D study flows first, then progressive 3D library, responsive design, user testing and performance budget. Keep 2D as a complete fallback.

## Phase 7 — Integration, commercial readiness and launch (M7 pending)
End-to-end student workflow, observability, backup/restore drills, pricing/legal/privacy/support decisions, closed beta and measured launch gate.

Order may overlap only where contracts are stable; security and deletion remain cross-cutting P0 requirements. No future milestone is considered complete based on a UI placeholder or mocked response.
