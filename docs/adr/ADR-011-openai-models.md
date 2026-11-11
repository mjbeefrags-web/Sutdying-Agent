# ADR-011: OpenAI embedding provider default

- Status: Accepted for MVP implementation; production data-processing review pending
- Context: Semantic retrieval needs a concrete embedding model and dimension for the initial pgvector schema while preserving a provider boundary.
- Decision: Use the OpenAI API behind an application-facing embedding adapter. Default to `text-embedding-3-small` with 1536 dimensions. Store model name per document version and reject vectors with a wrong dimension or non-finite values. Keep API credentials in local environment/deployment secret storage; never log document text or credentials.
- Alternatives: Google embedding API, a self-hosted model, or postponing semantic indexing.
- Consequences: The initial vector schema is fixed at 1536 dimensions and requires a migration to change. Missing/invalid credentials must produce an explicit processing failure, never a fake vector or ready state. Before production, approve region, retention, privacy terms, cost budget, and user disclosure. A matching chat model remains a separate M3 decision.
