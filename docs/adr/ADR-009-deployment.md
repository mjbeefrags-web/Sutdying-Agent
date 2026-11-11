# ADR-009: Containerized API and worker deployment

- Status: Accepted direction
- Context: Need reproducible development and independently scaled request/background processes.
- Decision: Docker images; Compose for local dependencies; production on managed container runtime with managed Postgres/Redis/object storage; Nginx as example edge proxy.
- Alternatives: VM-only install, Kubernetes from day one, production Compose.
- Consequences: No production Compose deployment; cloud/runtime vendor, region, TLS and secret manager remain open. Pin image digests and maintain backward-compatible migrations during rolling releases.
