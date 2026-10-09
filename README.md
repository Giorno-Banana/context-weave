# Context Weave

Version **0.4.1** is published as the complete [source bundle](context-weave-0.4.1-source.zip). Extract the versioned bundle into a new directory to run it. The loose Python files at the repository root are historical; use this bundle for 0.4.1. Model weights, credentials and private memories are excluded.

Bundle SHA-256: `f146ef9466e570fa5563874e58fd23506976c5ec48e3ed7bd929cd4974d2815e`. Its `SHA256SUMS.json` covers 62 files. Pin the commit containing this archive and verify both the archive digest and per-file checksums. The older [0.4.0 bundle](context-weave-0.4.0-source.zip) remains unchanged.

## Current local-model profile

- Add: local **Qwen3.5-4B**, BF16, thinking disabled, greedy decoding, two source chunks per call, LLM concurrency 1, no cloud fallback.
- Runtime revision: `sha256-82566a6da25518d98b91c78ce9a7c5a3d09aee59dd25db5b123f65811ed8acfe`. Exact runtime source, model file hashes and generation configuration are included in `local_runtime/`.
- Single and batch generation release temporary GPU allocations after each request. A separate model process is supervised, with a bounded queue, queue-inclusive deadlines, disconnect cancellation and automatic recovery after a worker failure.
- Original source spans remain the evidence. Embedding uses Bailian `text-embedding-v4`, 1024 dimensions. Search uses dense + BM25 RRF and adjacent source windows without an LLM planner.
- Official bound endpoints remain `https://wzm.tail36b9f2.ts.net/add` and `https://wzm.tail36b9f2.ts.net/search`. The new evaluation uses its own database. Service authentication is provided privately.
- Official Smoke uses Add/Search concurrency 16/16 and top_k 100; local model concurrency remains 1 with persistent Add batch checkpoints.

## 0.4.1 validation and evaluation status

[Local validation report](context-weave-0.4.1-validation.md): 71 regression tests passed. A continuous four-hour synthetic test completed **5123 requests with zero failures and zero worker restarts** on 2026-10-09. Post-request allocated GPU memory stayed at 8029.99 MiB; reserved memory stayed at 8052 MiB. Identical-input latency medians were 2.617 seconds initially and 2.512 seconds at the end, with identical outputs.

Separate real-model fault tests verified disconnect recovery and recovery after deliberately terminating the model worker. A local end-to-end Add/Search check with embeddings passed. These are local validation results, not retrieval-quality scores or a guarantee of multi-day Full capacity. An earlier long-test attempt was interrupted externally after approximately 90 minutes and is not counted as the completed four-hour test.

Official 0.4.1 Smoke is being prepared; no 0.4.1 official score or Full result is claimed. The historical score below belongs only to 0.4.0. The 0.4.1 runtime is frozen for the new evaluation.

## Official Smoke result (2026-10-08)

Version 0.4.0 completed official textual Smoke job `teval_cb6f667914fdc768`: **Succeeded, 59.47, 46/46 items, 1/1 task**. It ran from 18:30:36 to 21:17:44 (UTC+08:00), taking 2 hours 47 minutes 8 seconds. The frozen source bundle is pinned by commit `de31aa98831e440c4a0d985df64c48906f320724` and the digest above. The bundled preparation notes describe the pre-run snapshot; this section records the completed run.

During sustained operation, local inference slowed with near-full VRAM and shared GPU memory use. One restart of the unchanged model service restored roughly 3-second batches. The original platform job recovered through retries and persistent Add checkpoints. The service recorded two HTTP 503 responses during the timeout/restart episode; this was a successful recovered run, not an uninterrupted error-free run. All 134 Add requests were committed, with no pending Adds or batch checkpoints left at completion. No code, model or configuration was changed during the job.

The precise cause of the slowdown has not been isolated. Sustained inference performance and automatic recovery need improvement before Full. **No Full run has been started for version 0.4.0.**

The frozen 0.3.1 official Smoke using GPT-4o-mini scored 53.64 on 46 items in 13 minutes. The 0.4.0 score is 5.83 points higher in these two Smoke runs. This is not a Full leaderboard comparison or proof that one model is generally better.

The [published competition FAQ](https://agentmemories.ai/competition/) requires GPT-4o-mini for academic LLM components. Academic use of a local model is subject to applicable organizer permission; this release discloses the actual Qwen configuration and does not certify an exception. No account creation or official job submission is automated by the source bundle.

## Attribution and license

Submission contact: 秦天朗. Team: recursive roll. Code copyright: 王子铭. The original MIT license and full provenance are retained in the source bundle. Qwen model weights remain subject to their own model license and are not redistributed.
