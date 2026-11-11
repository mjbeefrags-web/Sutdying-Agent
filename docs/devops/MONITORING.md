# Monitoring and operations

## Signals
Metrics: request count/latency/error by route class, DB pool saturation, readiness, queue depth/age, task retries/failures, ingestion stage latency, provider latency/error/token/cost, citation/abstention evaluation and 3D client performance. Avoid labels with user, course, file, prompt or raw IDs.

Logs are structured JSON with request/job ID, outcome and code; redact credentials, signed URLs, document content, prompts, answer text and personal data. Traces propagate request/job correlation; AI spans contain model/version, token counts and duration only.

## Alerts and response
Alert on sustained 5xx, readiness loss, queue oldest age, repeated terminal ingestion failures, provider spend budget, DB storage/connection exhaustion, and backup failure. Each alert has owner, severity, runbook, and actionable threshold. Keep liveness cheap; readiness uses dependency timeouts. Provide a kill switch for AI generation and ingestion.

Define SLOs before launch; initial proposals: API availability 99.5%, p95 non-AI latency <500ms, queue wait p95 <2m at beta load. No user-content observability by default.
