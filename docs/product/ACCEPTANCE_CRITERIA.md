# Acceptance criteria

| Area | Acceptance test | Target |
|---|---|---|
| Upload | Valid supported file is accepted only within configured limits and status is visible | 95% successful test uploads |
| Processing | Invalid, encrypted, empty, or oversized input produces a specific actionable error | 100% of fixture cases classified |
| Grounding | Each factual answer claim is linked to an authorized source passage or marked uncertain | >=90% citation precision on frozen evaluation set |
| Abstention | No relevant evidence results in no fabricated course-specific answer | >=95% correct abstention |
| Privacy | A user cannot read another user's course, file, chunk, or job by changing identifiers | 100% negative authorization tests |
| Delete | Deleted source content becomes inaccessible immediately and physical purge completes within documented retention window | verified with integration test and audit event |
| Learning | Review scheduler handles new, correct, incorrect, and overdue cards deterministically | property/unit tests and delayed-recall pilot |
| Accessibility | Core workflows work by keyboard; focus is visible; 3D has a 2D equivalent | WCAG 2.2 AA audit before beta |
| Performance | Non-AI API p95 at beta load | <500ms; measured, not inferred |
| Operations | DB, Redis, API and worker health/readiness observable; failed job can be retried safely | recovery drill passes |

Phase 1 testable baseline is configuration parsing, API liveness/readiness, and CI lint/type/test execution. Product targets remain future gates until implementation and measurement exist.
