# Backup and recovery

PostgreSQL: managed encrypted automated backups plus point-in-time recovery; include pgvector extension/index considerations in restore test. Object store: versioning/replication policy consistent with deletion obligations; backups must not indefinitely retain deleted user content. Redis is ephemeral; outbox/database state allows safe re-enqueue. Protect backup keys and audit restore access.

Initial launch targets to approve: RPO <=15 minutes, RTO <=4 hours. Quarterly restore drill to isolated environment; verify schema, sample authorized reads, object references, vector counts, outbox recovery, and application compatibility. Record elapsed recovery and evidence. Never use production personal data in a test restore without access controls and retention controls.

Incident procedure: declare incident → preserve minimal evidence → isolate compromised credentials → assess scope/data → restore into clean environment → validate integrity → resume traffic → notify according to counsel-approved obligations → retrospective/remediation. Deletion workflows must propagate to backup expiry or cryptographic erasure according to published retention policy.
