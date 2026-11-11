# ADR-004: Source-grounded RAG

- Status: Accepted
- Context: Course answers must reference student-owned material and abstain when evidence is inadequate.
- Decision: Retrieve authorized immutable chunks, combine lexical/vector scores, optionally rerank, and validate structured citations against candidates.
- Alternatives: Fine-tuning, model-only answers, unrestricted web search.
- Consequences: Source extraction quality and retrieval eval are release gates; model output is untrusted; costs include embeddings/retrieval/rerank. No answer is labeled grounded unless citations validate.
