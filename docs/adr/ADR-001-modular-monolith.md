# ADR-001: Modular monolith

- Status: Accepted for initial product
- Context: Product domains are tightly coupled and team size/traffic are unknown.
- Decision: One Python codebase with explicit domain modules; API and Celery worker are separate processes built from it.
- Alternatives: Microservices, serverless functions, one synchronous API process.
- Rationale: Simple local operations, shared transactions and fewer deployment boundaries while preserving module ownership.
- Trade-offs/consequences: Must enforce module boundaries and avoid shared-table coupling; scale processes independently. Extract only after measured scaling/ownership needs.
