# ADR-003: Celery with Redis broker

- Status: Accepted for initial background jobs
- Context: Extraction, OCR, embeddings and evaluation are long-running and retryable.
- Decision: Celery worker process with Redis broker; PostgreSQL outbox records durable intent and supports redelivery.
- Alternatives: Synchronous processing, cloud task service, Kafka.
- Consequences: At-least-once delivery; every job idempotent, bounded, observable and versioned. Redis is not source of truth; evaluate managed broker if operations or delivery guarantees require it.
