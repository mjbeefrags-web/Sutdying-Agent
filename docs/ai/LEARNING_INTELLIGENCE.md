# Learning intelligence

## Practice and grading
Generated questions are drafts until schema, source, answer-key, ambiguity, and difficulty checks pass; student may edit before use. Objective answers use deterministic grading. Free response feedback is formative, cites source/rubric, separates correctness from style, and provides an appeal/teacher-review path before any high-stakes use (high-stakes grading is out of scope).

## Spaced repetition and mastery
Record immutable review event: card, user, timestamp, rating, response latency and scheduler version. Start with a simple deterministic Leitner/interval scheduler; do not claim a validated FSRS implementation until licensed/versioned algorithm and conformance tests are selected. Due date is explainable and user-adjustable. Mastery aggregates recent independent retrieval outcomes with recency and uncertainty; expose evidence count and confidence, avoid a single opaque score.

## Adaptive plan
Inputs: exam date (optional), availability, due reviews, estimated topic mastery and user priority. Produce a bounded suggestion set with reason, estimated duration, and source/topic; user explicitly accepts/edits. Never create external calendar events or increase workload without consent. Detect sparse data and label recommendations provisional.

## Evaluation
Compare recommendations against fixed baselines; delayed retrieval after 1/7/30 days where consented. Monitor calibration and subgroup performance; no sensitive-trait inference. Users can inspect and correct topic/card associations.
