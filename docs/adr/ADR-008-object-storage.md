# ADR-008: Private object storage adapter

- Status: Accepted for local development; production vendor/region undecided
- Context: Lecture bytes are large, require lifecycle, signed upload and deletion controls.
- Decision: Store bytes in private S3-compatible object storage; persist key, checksum and lifecycle metadata in Postgres. Use a local MinIO server for development and the official MinIO Python SDK. Production storage remains a later vendor/region decision; no public test bucket is permitted.
- Alternatives: PostgreSQL blobs, public CDN bucket, local filesystem in production.
- Consequences: MinIO standalone is a local development/evaluation service only. Select the production provider/region, encryption, malware scanning, lifecycle and backup/delete policies before launch. The current MinIO container is built from the upstream pinned source release because the upstream release instructs container users to build the release image.
