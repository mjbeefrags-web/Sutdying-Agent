# Milestones and dependencies

| ID | Milestone | Exit criteria | Depends on |
|---|---|---|---|
| M0 | Phase 1 foundation | docs/config/tests validated | none |
| M1 | Identity and tenant-safe core | auth/session/courses; IDOR suite green | M0 |
| M2 | Document lifecycle | private upload, safe parser, retry/delete | M1 |
| M3 | Retrieval and grounded tutor | citations, abstention, eval gates | M2 |
| M4 | Practice and learning loop | cards, exams, review schedule, progress | M1; M2 for source-grounded generation |
| M5 | Study product UI | accessible 2D route flows and optional 3D | M1; M2-M4 incrementally |
| M6 | Private beta readiness | reliability, restore, policy, usability and cost gates | M3-M5 |
| M7 | Commercial launch | validated pricing/billing, support and legal sign-off | M6 |

Dates and staffing are intentionally unset until owners/capacity and provider/legal decisions are approved.
