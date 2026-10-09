# Context Weave 0.5.0

Source-preserving memory retrieval for the Agent Memory Leaderboard Add/Search protocol.
Use the complete `context-weave-0.5.0-source.zip` bundle for this version. Older loose files and bundles remain historical versions.

## Deployment profile

- Add: local Qwen3.5-4B, BF16, thinking disabled, greedy decoding, two chunks per request. The supervised 0.4.1 model runtime is unchanged; its weights and runtime hashes are in `local_runtime/MODEL_MANIFEST.json`.
- Embeddings: Bailian text-embedding-v4, 1024 dimensions.
- Search: bounded dense, BM25, Porter and neighboring-context rank fusion; mild diversity; local CPU cross-encoder reranking; reserved character/slot budgets for source neighbors.
- Reranker: cross-encoder/ms-marco-MiniLM-L6-v2, CPU, 384-token input, 96 candidates. It scores passages and generates no text. The manifest identifies the exact downloaded model files.
- Original source text is retained. Calendar annotations are separately marked metadata anchored only to source timestamps or explicit source date prefixes. Calendar months/years retain their granularity. Overview queries include representatives from different sessions.
- Evidence is scoped to the supplied user. Search does not generate a final answer, use test labels, or reuse evidence across users.
- Candidate endpoints: `https://wzm.tail36b9f2.ts.net/v050/add` and `/v050/search`; credentials are supplied privately. Add/Search concurrency 16/16, top_k 100, returned text budget 24,000 characters including metadata.

## Run

Install `requirements.txt` for the API and the documented model-runtime requirements for local models. Download the reranker from [its publisher](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) and verify `local_runtime/RERANKER_MANIFEST.json`. Start `local_runtime/rerank_server.py --model <local-weights-directory>` with the model Python environment; it binds only to 127.0.0.1:18092. Start the unchanged Qwen supervisor using `local_runtime/start_supervised.ps1`. Overlay `local_runtime/profile.txt` on a private credential file, then run `start_local.ps1` on an available port. No cloud LLM fallback is enabled.

## Evidence and status

83 regression tests passed on 2026-10-09. The initial public LoCoMo-Refined diagnostic used 306 questions from two previously examined conversations, 305 with evidence annotations, with raw text-embedding-v4 indices and no Add LLM enrichment. This is retrospective retrieval validation, not a blind holdout or an official answer score.

At a 24,000-character budget, complete evidence coverage was 88.85% for the deployed 0.4.1 retrieval policy and 91.48% for the new evidence policy with reranking. In the first 6,000 returned characters, exact complete-source coverage rose from 74.75% to 81.64%. The reranked searches had approximately 0.69-second median latency in that diagnostic. These figures precede the separately tested calendar/overview additions; the final frozen diagnostic report is included with this release when complete.

Official 0.4.1 Smoke: 58.82, 46/46 items, 38m10s, task `teval_aa63aa25ac0b8d97`. Its runtime completed without model restarts or HTTP 503 errors. No official 0.5.0 score is claimed until the platform finishes the new Smoke. The requested 90+ score is a target, not a validated result. No Full has been started.

The actual Add model is disclosed as local Qwen. The participant reports organizer permission for this configuration; this repository does not independently certify an exception to the published academic-model rule.

See `PROVENANCE.md` for method references and limitations. MIT license; original copyright notices are retained.

Final frozen public diagnostic (same 306 questions, 305 annotated): complete-evidence coverage 91.15%, macro recall 95.52%, median search 0.75 seconds. Runtime source hashes remained unchanged throughout the test. Calendar/overview metadata is enabled in this final configuration. See `local_runtime/RETRIEVAL_VALIDATION.json`.
