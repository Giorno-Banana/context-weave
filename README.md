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
- Planned version-specific Add/Search URLs: `https://wzm.tail36b9f2.ts.net/v040/add` and `https://wzm.tail36b9f2.ts.net/v040/search`. Service authentication is supplied privately.
- Initial Smoke limits: Add concurrency 1 / Search concurrency 4.

58 regression tests, a real Qwen plus embedding preflight and a 32-chunk synthetic HTTP check passed on 2026-10-08. The latter completed in 43.531 seconds. These tests do not establish Full capacity or a quality score. Official 0.4.0 Smoke and Full are pending at this release preparation snapshot.

The frozen 0.3.1 official Smoke scored 53.64 on 46 items in 13 minutes. That is a historical result for GPT-4o-mini and does not certify the local-model version.

The [published competition FAQ](https://agentmemories.ai/competition/) requires GPT-4o-mini for academic LLM components. Academic use of a local model is subject to applicable organizer permission; this release discloses the actual Qwen configuration and does not certify an exception. No account creation or official job submission is automated by the source bundle.

## Attribution and license

Submission contact: 秦天朗. Team: recursive roll. Code copyright: 王子铭. The original MIT license and full provenance are retained in the source bundle. Qwen model weights remain subject to their own model license and are not redistributed.