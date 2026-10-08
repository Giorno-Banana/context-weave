# Context Weave

Version **0.4.0** is published as the complete [reproducible source bundle](context-weave-0.4.0-source.zip) committed in this repository. Extract that bundle into a new directory to run this version. It includes all memory-service code, 58 regression tests, configuration examples, documentation and the exact local model-server source snapshot. Model weights, private memories and credentials are excluded.

Bundle SHA-256: `e620cf902a72bc4b56fe9fd90bd62e7299594e7d162f7c093b3ca84efeb01cc6`.

The bundle contains its own `SHA256SUMS.json` covering 51 source files. Pin the Git commit containing this bundle and verify both the bundle digest and its per-file manifest. The loose Python files at the repository root retain the historical 0.3.1 release; use the versioned bundle for 0.4.0.

## Current local-model profile

- Add: local **Qwen3.5-4B**, BF16, thinking disabled, temperature 0, two source chunks per call, LLM concurrency 1, no cloud fallback.
- Model/runtime revision: `sha256-8267024d0feba058a3f26e5602a829432fe3d1da84bad553f98985b004f047d8`. The full fingerprint and runtime source are inside `local_runtime/` in the bundle.
- Add selects IDs of original source spans. Generated text never becomes evidence.
- Embedding: Bailian `text-embedding-v4`, 1024 dimensions.
- Search: dense + BM25 RRF with adjacent original-source windows; no LLM planner.
- Alternate configuration: OpenRouter `openai/gpt-4o-mini`, OpenAI provider only. It uses a separate database and never silently replaces the local model.
- Official bound Add/Search URLs: `https://wzm.tail36b9f2.ts.net/add` and `https://wzm.tail36b9f2.ts.net/search`. The platform keeps these endpoints immutable for an existing key. The `/v040/add` and `/v040/search` aliases reach the same frozen deployment. Service authentication is supplied privately.
- Official Smoke concurrency: Add 16 / Search 16, the platform minimum. Local LLM concurrency remains 1; incoming Add requests queue and use persistent batch checkpoints.

58 regression tests, a real Qwen plus embedding preflight and a 32-chunk synthetic HTTP check passed on 2026-10-08. The latter completed in 43.531 seconds. These short checks do not establish Full capacity.

## Official Smoke result (2026-10-08)

Version 0.4.0 completed official textual Smoke job `teval_cb6f667914fdc768`: **Succeeded, 59.47, 46/46 items, 1/1 task**. It ran from 18:30:36 to 21:17:44 (UTC+08:00), taking 2 hours 47 minutes 8 seconds. The frozen source bundle is pinned by commit `de31aa98831e440c4a0d985df64c48906f320724` and the digest above. The bundled preparation notes describe the pre-run snapshot; this section records the completed run.

During sustained operation, local inference slowed with near-full VRAM and shared GPU memory use. One restart of the unchanged model service restored roughly 3-second batches. The original platform job recovered through retries and persistent Add checkpoints. The service recorded two HTTP 503 responses during the timeout/restart episode; this was a successful recovered run, not an uninterrupted error-free run. All 134 Add requests were committed, with no pending Adds or batch checkpoints left at completion. No code, model or configuration was changed during the job.

The precise cause of the slowdown has not been isolated. Sustained inference performance and automatic recovery need improvement before Full. **No Full run has been started for version 0.4.0.**

The frozen 0.3.1 official Smoke using GPT-4o-mini scored 53.64 on 46 items in 13 minutes. The 0.4.0 score is 5.83 points higher in these two Smoke runs. This is not a Full leaderboard comparison or proof that one model is generally better.

The [published competition FAQ](https://agentmemories.ai/competition/) requires GPT-4o-mini for academic LLM components. Academic use of a local model is subject to applicable organizer permission; this release discloses the actual Qwen configuration and does not certify an exception. No account creation or official job submission is automated by the source bundle.

## Attribution and license

Submission contact: 秦天朗. Team: recursive roll. Code copyright: 王子铭. The original MIT license and full provenance are retained in the source bundle. Qwen model weights remain subject to their own model license and are not redistributed.
