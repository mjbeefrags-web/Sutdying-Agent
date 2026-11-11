# Retrieval-augmented generation

1. Authenticate and resolve course membership; query only active document versions in that course.
2. Rewrite question only if needed without adding facts; embed query using same recorded embedding family/version.
3. Hybrid retrieval: lexical search plus pgvector cosine; apply metadata filters before ranking. Candidate initial k=30; rerank top 10 after evaluation.
4. Build context under a configurable token budget (initial ceiling 6k evidence tokens; model-specific total budget remains configurable). Include document title, page/section and stable chunk ID.
5. Instruct the model to answer solely from evidence, cite every material claim, distinguish inference, and return insufficient-evidence when unsupported.
6. Validate structured response; reject citations outside candidate set; verify excerpt/source version; abstain or regenerate once on schema failure, not indefinitely.
7. Return answer, citations, and a concise uncertainty indicator. Clicking citation opens source location.

## Chunk/retrieval policy
Initial chunk target 500-800 tokens with 80-token overlap, respecting headings/page boundaries; evaluate alternatives by course document type. Keep chunk text and offsets linked to immutable source version. Filter deleted/inaccessible content before vector search; vector index is not an authorization boundary. Cache keys include tenant, course, source version and policy; invalidate on deletion/reindex.

## Failure modes
No relevant evidence → abstain and suggest upload/search clarification. Conflicting sources → surface both with dates/labels. Retrieval/model timeout → explicit retryable failure and retain draft. Corrupt citation → fail closed, do not emit generated answer as grounded.
