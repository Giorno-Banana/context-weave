# Context Weave 0.10.0 — bounded evidence candidates

This release separates the internal candidate pool from the final response character budget. Evidence at lower retrieval ranks can reach the selector before text truncation. Search returns complete original source chunks and metadata; it does not generate answers or new memory facts.

- Add and Search model: local Qwen3.5-4B, temperature0. The active supervised runtime is0.4.2 with chunked prefill above1024 tokens. Runtime code, dependencies and weight hashes are recorded in `local_runtime/MODEL_MANIFEST.json`.
- Embedding: Bailian text-embedding-v4,1024 dimensions. No OpenRouter calls in this experiment.
- Each original/expanded query exposes up to128 ranked source chunks internally. The final pool reserves60 direct hits and12 from each expansion before reciprocal-rank fusion, capped at128. Expansion remains capped at3 queries. Existing selection prompts and final packing are unchanged.
- Selected output is capped at12,000 characters; selection failure falls back to the original24,000-character retrieval. API top_k is at most100. Per-user storage isolation and exact source preservation are retained.
- Runtime042 is not bit-identical to041:7 of8 historical parity checks matched. The public study compares the combined candidate, including this runtime difference.
- No official score exists for0.10.0 yet. Best complete prior official Smoke is61.77 (0.6.1). The0.7.0 cloud comparison scored59.28 and0.9.0 local9B scored55.84. This candidate has no guaranteed score. The target remains a complete official Smoke above70.
- The prospective public screen and its limitations are in `EXPERIMENT.json`. It uses reused development questions and same-model grading, so its score is not an official score or evidence of statistical significance.
- The participant reports organizer permission for a local-model academic-track exception. This repository discloses the actual model and does not independently certify eligibility. Full is not authorized in this experiment.

## Reproduce

Use Python 3.10 and `requirements.txt`. Local model dependencies and settings are pinned in the runtime manifest. Download Qwen/Qwen3.5-4B and verify all recorded weight and tokenizer hashes. Configure credentials using `env.example` and paths and ports using `env.local.example`. Start `local_runtime/start_supervised.ps1` with port 18095, then start the API using `start_local.ps1`. A GPU with adequate memory is required for the published model configuration.

Run `python -m unittest discover -s tests -v`. The published versioned source archive is authoritative; older loose repository files are historical. The archive contains no credentials, model weights, stored memories or benchmark answers. Add/Search require the configured memory-system token. Source and deployment configuration are frozen before official evaluation.

## Method provenance

This is original project code informed by ReFind's original-evidence collection and ActiveMemoryIndex's source context preservation. The change addresses premature character truncation in this project's public development diagnosis. No upstream code, prompts or benchmark answers were copied into the service. See `PROVENANCE.md` for references. Project code is MIT licensed; models and dependencies retain their own licenses.

## Deployment validation

80 regression tests and 8 semantic checks passed. Sixteen concurrent synthetic HTTP searches completed within 52 seconds. Eight concurrent public long-memory retrievals completed within 116 seconds with no model failures or restarts. The initial plan was Add 16 and Search 8; the platform subsequently required a minimum Search concurrency of 16. The final submitted limits will be Add 16 and Search 16, as disclosed below. These checks establish operation under the tested workload, not a score guarantee or a universal latency bound.

## Concurrency amendment before Smoke

The website rejects Search concurrency below 16. A supplementary test ran 16 concurrent public long-memory queries: maximum 229.203 seconds, no model failures or restarts. Its stricter internal 180-second target was missed; the original failed status is retained. The [current official documentation](https://agentmemories.ai/zh-cn/docs) allows a request to run up to 30 minutes. This supports an exploratory Smoke at Add 16 / Search 16; it does not establish a universal latency guarantee. See `context-weave-0.10.0-concurrency-amendment.json` for the exact result and decision. The source archive, model runtime and API profile remain unchanged. The archived source documents preserve the earlier proposed setting; this dated external run configuration supersedes that proposal. No Full has been launched.
