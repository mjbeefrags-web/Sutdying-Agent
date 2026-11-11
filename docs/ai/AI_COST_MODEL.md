# AI cost model

Monthly variable cost per active user is estimated as:
`questions × (input_tokens × input_price + output_tokens × output_price) / 1e6`
`+ documents × pages × extraction/OCR_cost_per_page`
`+ embedding_tokens × embedding_price / 1e6`
`+ rerank_calls × rerank_price`
Add storage, DB/vector capacity, queue, observability and taxes separately. Provider prices change; populate a dated internal rate card, not hard-coded assumptions.

## Controls
Set per-user daily/monthly budgets, max upload pages/bytes, max retrieved chunks/context, output token caps, bounded retries, concurrency limits, cache only policy-safe deterministic results, use smaller models only after quality eval. Alert at 50/80/100% budget and on unit-cost regression. Make expensive OCR/rerank opt-in/fallback by confidence. Never silently downgrade privacy region or model quality.

Track cost per successful grounded answer, indexed page, generated question and retained user. Run p50/p95 load tests and scenario forecasts before pricing decisions. Phase 1 has no provider credentials or real cost integration.
