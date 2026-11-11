# MVP scope and release gates

## Phase 1 foundation (this repository)
Architecture, threat/privacy model, local Docker services, typed API/web/worker skeletons, health checks, documentation, and CI validation. No production-grade auth, ingestion, LLM workflow, billing, or 3D learning product is complete yet.

## MVP delivery (next implementation phases)
1. Identity, tenant-scoped courses and private document metadata/storage.
2. PDF/TXT ingestion pipeline and source-preserving retrieval.
3. Cited tutor with abstention and evaluation set.
4. Flashcard authoring/review, practice attempts, basic mastery.
5. Accessible 2D study flows; 3D library as progressive enhancement.
6. Privacy controls, operational dashboards, beta onboarding.

## Include in MVP
Single-user courses; PDF and UTF-8 text with explicit limits; asynchronous processing; course-scoped tutoring; editable flashcards; low-stakes practice; basic review scheduling; weekly study suggestions; responsive desktop-first web UI.

## Exclude
Audio/video, collaboration, institutional administration, external web retrieval, high-stakes grading, native mobile, payment processing, and gamified social ranking.

## Release gate
All P0 security/privacy findings resolved; deletion/export verified end-to-end; supported-device accessibility checks pass; ingestion and AI eval gates meet thresholds in PRD; restore drill succeeds; support/runbook and provider fallback are ready. Phase 1 does not meet the product MVP gate.
