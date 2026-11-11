# ADR-002: PostgreSQL and pgvector

- Status: Accepted provisionally
- Context: Need relational transactions, tenant filters and semantic retrieval without operating a separate vector database at MVP scale.
- Decision: PostgreSQL is system of record; pgvector stores embeddings, with lexical and vector retrieval.
- Alternatives: Managed external vector DB; separate search engine; PostgreSQL only.
- Consequences: Confirm extension/version and embedding dimensions before migrations; benchmark index recall/latency and tenant filter behavior. Vector similarity is never authorization.
