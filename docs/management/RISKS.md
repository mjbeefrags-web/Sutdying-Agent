# Risks

| Risk | Likelihood / impact | Mitigation / trigger |
|---|---|---|
| Confident hallucinations harm learning | M / High | Evidence citation/abstention gates; expert sampling; kill switch |
| Cross-tenant document leakage | Low / Critical | Tenant-scoped repositories, negative IDOR tests, optional DB RLS |
| Prompt injection in uploads | High / High | Treat source as hostile data; no model-authorized tools; adversarial eval |
| OCR/parser resource exhaustion | M / High | Isolated bounded worker, page/size limits, malware review |
| Provider outage or price change | M / High | Provider abstraction, budgets, graceful unavailable state, rate-card updates |
| Student over-reliance or poor study advice | M / High | Explainability, low-stakes framing, uncertainty and student control |
| 3D performance/accessibility excludes users | M / Medium | 2D parity, lazy load, reduced motion and hardware testing |
| Privacy/education-law mismatch | M / Critical | Counsel review, age/region/retention decisions before beta |
| Storage deletion conflicts with backups | M / High | Explicit retention/purge design; restore tests; user-facing policy |
| Scope and staffing uncertainty | High / High | Milestones with owners/capacity before dates; hold commercial claims |

Risk owners and dates are not assigned; establish before M1 delivery planning.
