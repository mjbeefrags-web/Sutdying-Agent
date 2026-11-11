# Production deployment

Deploy immutable versioned containers to a managed container platform. Minimum topology: TLS edge/load balancer or Nginx ingress, stateless API replicas, independently scaled worker pool, managed PostgreSQL with pgvector and backups, managed Redis, private object storage, secret manager, metrics/logging and alerting. Avoid running stateful database/cache on the app host for production.

Use separate least-privilege service identities, private network paths, encrypted storage, network egress allowlist for providers, and workload identity instead of static credentials. Nginx is a reverse-proxy example in this repository; TLS certificates and production hostnames are platform-managed. Do not deploy the Compose file as-is.

Rollout: build/test/scan → publish image by digest → migration compatibility check → deploy API/worker → smoke/readiness → observe canary → promote/rollback. Migrations use expand/contract; worker and API versions remain compatible during rolling deploy. Protect destructive migration and deletion jobs. Define region/data residency, retention, RPO/RTO and restore before launch.

Capacity and costs require measured beta load. Provider contracts, legal/data processing agreement, incident contact, and pager coverage are pre-launch decisions.
