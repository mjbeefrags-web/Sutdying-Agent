# AI evaluation strategy

Maintain a versioned, permissioned corpus of representative synthetic/licensed course fixtures; avoid student content in training/evaluation without explicit informed consent and retention terms. Every item has expected evidence, answerability, citation spans and risk labels.

## Gates
- Retrieval: Recall@10 >=0.85 on answerable cases; unauthorized-chunk leakage = 0.
- Citation: precision >=0.90; every citation resolves to exact source version/page.
- Answer correctness: expert-rated grounded correctness >=0.85 on golden set; abstention >=0.95 when unanswerable.
- Injection set: document-contained instruction attempts cause no policy/tool changes or secret disclosure.
- Structured generation: schema validity >=0.99 after bounded repair; no unsupported question answer key.

These are proposed release thresholds; calibrate with subject experts before beta. Report confidence intervals, per-document-type results, and regression delta. Use deterministic retrieval tests, blinded human review, adversarial red-team prompts, latency/token/cost benchmarks, and shadow evaluation before provider/model switch. No model is deployed solely because a vendor benchmark is strong.

Collect user thumbs/flags as signals, not ground truth. Provide data deletion and consent controls. Log evaluation versions and retain only minimized, policy-approved samples.
