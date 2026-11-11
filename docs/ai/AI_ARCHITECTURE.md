# AI architecture

## Provider-neutral boundary
Define application-facing interfaces `ChatModel.complete(messages, schema, budget)` and `EmbeddingModel.embed(texts, model_version)` plus provider adapters. Typed domain requests/responses are independent of vendor SDKs. Adapters enforce timeouts, max output, retries only for transient errors, structured-output validation, redacted telemetry, and provider failover only when policy/data residency permits. No API key or provider call in route/domain code.

M2/M3 implementation default selected by the product owner: OpenAI embeddings, `text-embedding-3-small`, 1536 dimensions. The first adapter must fail explicitly when credentials are absent and must validate vector shape. Chat model selection remains open for M3; no tutor is implemented or implied by this default.

## Workflow
User request → auth/course scope and quota → retrieve authorized ready-version chunks → optional rerank → compose bounded prompt with untrusted evidence → model structured response → schema and citation verification → store only intentional history → return answer with source references. Ingestion, exam generation, and evaluation run asynchronously via idempotent jobs.

## Safety and reliability
The model is not a policy engine. Treat all source text as hostile quoted data; no tool invocation derived from retrieved text; permit only allowlisted tools and validate arguments/authorization in application code. Citation IDs must belong to retrieved candidates and requested course. Abstain on insufficient or conflicting evidence; never invent citations. Apply per-user token and concurrency caps, max prompt/context/output budgets, timeout, circuit breaker, bounded retries with jitter, and provider spend alerts.

## Observability and evaluation
Record trace/request/job ID, provider/model/prompt version, latency, token counts, retrieval IDs/scores, validation outcome, and cost. Do not log full prompts, uploads, or answers by default. Offline golden/adversarial tests gate prompt/model changes; online user feedback and sampled audits monitor drift. Model/provider changes are versioned and reversible.

No live model adapter or production tutoring workflow is implemented in Phase 1.
