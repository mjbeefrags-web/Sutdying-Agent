# ADR-010: Bounded asynchronous document processing

- Status: Accepted for M2; runtime verification pending
- Context: Course PDFs may be scanned or malformed, and parsing/OCR/embedding must not block API requests or bypass tenant authorization.
- Decision: Accept PDF only for the first upload path; store source bytes in private MinIO in local development. Use a transactional outbox to enqueue Celery processing. Extract page text with pypdf; render only low-text pages with pypdfium2 and run local Tesseract English OCR. Enforce upload/page/chunk/image bounds and expose processing state and stable error codes. Keep text chunks and embeddings linked to immutable document versions.
- Alternatives: Synchronous API parsing, cloud OCR first, unbounded parser workers, public/presigned storage objects.
- Consequences: OCR is English-only until language support is validated; scanned PDFs require Tesseract in the worker image. Parser limits reduce but do not eliminate hostile-file risk; production requires stronger worker isolation and malware scanning. The code and migration must pass dependency, database and live-worker tests before this ADR's implementation is considered verified.
