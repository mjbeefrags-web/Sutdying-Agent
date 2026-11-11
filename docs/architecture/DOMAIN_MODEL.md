# Domain model

## Aggregate roots
- Organization: membership, ownership, subscription boundary. A personal organization is provisioned for every individual.
- Course: owns source documents, study artifacts, and analytics; all are isolated by organization membership.
- SourceDocument: user-visible file identity and lifecycle; DocumentVersion captures immutable parser/index snapshots.
- StudySession: groups a learning activity and immutable attempt/review events.
- Flashcard: editable learning prompt; ReviewEvent is append-only evidence of recall.
- Exam: selected content scope and generated question set; attempt answers are private until submission.

## Lifecycle and invariants
Document states: `pending_upload → uploaded → queued → processing → ready`; failures are `failed_retryable` or `failed_terminal`; deletion moves to `deleting → deleted`. Only verified object bytes can enter processing. Every transition records timestamp and actor/system reason. Reprocessing creates a new version; never overwrite chunks in-place while active references exist.

Generated artifacts preserve provenance (source/version/chunk IDs, model/prompt/evaluation version). Student edits are first-class and do not overwrite source evidence. Review scheduling is deterministic for a fixed scheduler version, previous state, and rating. Mastery is an estimate, not a diagnosis; report data coverage and uncertainty.

## Cross-domain coordination
Application services coordinate transactions and emit versioned outbox events; no direct domain-to-domain table writes from workers. Domain events include `document.uploaded`, `document.indexed`, `practice.completed`, and `review.recorded`. Consumers are idempotent. Policies (membership, course access, lifecycle) are checked before querying or returning content.
