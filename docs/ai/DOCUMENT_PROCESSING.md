# Document processing

## Ingestion stages
1. Issue short-lived, scoped upload URL for private object prefix; enforce declared and actual size.
2. Verify checksum, file signature, MIME, page count and encryption state; quarantine until checks pass.
3. Extract PDF text per page; parse TXT as UTF-8. OCR fallback only for image-only/low-text pages, with language and confidence metadata.
4. Normalize whitespace while retaining page/offset mapping; never execute macros/scripts or fetch remote links.
5. Detect empty/unsupported/corrupt content; emit explicit terminal or retryable status.
6. Chunk by headings/pages and token budget; persist version and chunks transactionally; generate embeddings in bounded batches.
7. Mark version ready only after all chunks/embeddings succeed; emit outbox event.

## M2 implementation choices
The selected local baseline is private MinIO storage, pypdf text extraction, pypdfium2 rendering, and Tesseract English OCR for low-text pages. The chosen embedding default is OpenAI `text-embedding-3-small` (1536 dimensions). The upload path and worker code are in progress and remain unverified until the declared dependencies install, the follow-on Alembic revision is generated/applied, and the MinIO-to-worker flow passes integration tests. No OpenAI key is included; without a locally configured key, processing must end in an explicit failure, not `ready`.

## Safety and operations
Parser runs with CPU, memory, wall-time, file-size and decompression limits, no network, non-root container, read-only filesystem where feasible. OCR runs only on pages that need it; resource-intensive work is queued and quota-limited. Store source object encrypted/private; signed URLs expire quickly. Deletion invalidates jobs, caches and vectors and schedules object purge.

Track parser/OCR/embedding versions, page count, confidence, elapsed time and error code. Reprocessing creates a new immutable version. Keep fixtures for scanned, rotated, encrypted, malformed, multilingual and adversarial PDFs. No OCR/parser pipeline is implemented in Phase 1.
