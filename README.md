# Context Weave 0.6.1 — local evidence planner candidate

Use context-weave-0.6.1-source.zip for this complete frozen candidate; older loose source files are historical. The official Textual Smoke completed on 2026-10-09 with **61.77**, all **46/46** items finished in **49m 33s**. This is 2.30 points above the previous observed best of 59.47, and 2.95 above the stable 0.4.1 result of 58.82. The requested target, strictly above 70, **has not been met**. The public API root currently runs this tested 0.6.1 candidate. No Full was started.

The evaluated source archive is unchanged from commit `70a0ca133d540d103f86a461d7214d2ab953396d`; SHA256 is `a356f32f420f48bc3fd6ab58c05f33eb5e7e754c9f744750674acb93652fa936`. Post-run checks matched all 67 source files and the 9 actual model-runtime files. See [official result](context-weave-0.6.1-official-smoke.json), task `teval_4bfee59d2dfd1d6a`.

Runtime limitations: two local model generations timed out, and the existing supervisor automatically recycled the worker twice. The API continued using original-retrieval fallback; the platform job succeeded. There were seven query-expansion fallback events and five selection fallback events (counts are events, not necessarily distinct questions). This run establishes an observed improvement, not a guarantee of future scores or fault-free operation.

## Method

Add is unchanged: local Qwen3.5-4B selects identifiers of exact source spans, which are repeated only for indexing. Source text is retained. The production embedding is Bailian text-embedding-v4, 1024 dimensions.

Search starts with the original dense/BM25 retrieval. A local Qwen call proposes up to three internal search queries, then bounded calls select integer identifiers from up to 128 candidate sources, with at most 16 selected identifiers per batch. A batch with no directly useful evidence must return an empty list. Search returns only exact original source renderings, selected neighboring messages from the same ordered Add request, and a small reserve of direct hits. The selected context budget is 12,000 characters. The planner never returns a final answer, generated fact, or its reasoning as a memory.

Planner inputs use the pinned Qwen tokenizer and are capped at 7,200 content tokens, below the 8,192-token runtime limit. Long questions retain head and tail excerpts for planning; the full original question continues to drive baseline retrieval. Model output must match the exact JSON schema and current-request identifier allowlist. Invalid or unavailable planning falls back to original retrieval, whose budget is 24,000 characters. Fall-back events are logged without payloads. No query or memory cache is shared across requests or users.

The API version is 0.6.1; the unchanged supervised Add/LLM worker runtime remains 0.4.1. These version numbers identify different components.

## Running

Install requirements.txt for the API, and the existing local-model runtime dependencies documented in local_runtime/. Provide the Qwen3.5-4B weights separately; they are not bundled. The tokenizer JSON must have SHA256 5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42.

Run the existing supervised model on loopback port 18091. In a private environment profile set AE_LOCAL_EVIDENCE_SEARCH=1, AE_LOCAL_EVIDENCE_EXPAND=1, AE_PLANNER_TOKENIZER to the absolute tokenizer.json path, AE_SELECTED_CONTEXT_CHARS=12000, AE_CONTEXT_CHARS=24000, AE_MODE=hybrid_window, and a separate AE_DATABASE. Use start_local.ps1 with the private credentials file and this profile, an available API port, and a Python environment containing the pinned tokenizers package. The local-only profile removes cloud LLM credentials; it does not enable a cloud fallback.

## Verification status

77 regression tests passed. Live synthetic HTTP checks covered authentication, immediate searchable persistence, duplicate Add, cross-user isolation, a question longer than 6,000 characters, and four concurrent Search calls. Public paired QA is complete (baseline 29/50, candidate 30/50; inconclusive); no local result is an official score. LoCoMo uses cached v4 document embeddings; the independent LongMemEval transfer diagnostic reuses verified BGE embeddings. Both answer and judge are local Qwen3.5-4B, so local judgment error and model differences remain limitations.

## Attribution

The bounded search/selection design is informed by ReFind (https://github.com/imlrz/ReFind, inspected revision a80175ca0eeb52a938d7cab7a602bc780de8a577, app/retriever.py) and this project's earlier public select6 experiments. No upstream source or prompt is copied into the new module. Earlier source attribution and licensing remain in PROVENANCE.md and LICENSE. Local Qwen use is disclosed; the participant reports organizer permission. This repository does not independently certify an exception to the published model rule.

## 0.6.1 correction

The earlier 0.6.0 public test exposed irrelevant batches being selected wholesale. Version 0.6.1 explicitly requires empty selections when no requested fact or necessary context is supported, caps each batch at 16 selected IDs, and validates this bound. BM25 query terms are accumulated in sorted order to remove process-dependent floating-point tie variation. Six additional live synthetic semantic probes passed, including irrelevant evidence, identity separation, updates, Chinese rules and quoted instruction handling. The API and model remain local; no cloud LLM is called.

## Public comparison decision

The 50-question development comparison yielded 29 baseline and 30 candidate correct answers under the automatic local judge, with 9 wins and 8 losses; the paired 95% bootstrap interval is -14 to +18 percentage points. The predeclared statistical advancement criterion was NOT met. Source identity remained unchanged. Selection validation failures were zero; four query-expansion calls fell back to baseline expansion behavior. These are development diagnostics, not official scores. A separate prospective plan, recorded before candidate answers, permits one exploratory official Smoke after mechanical validation and excludes major public regressions. It does not override or relabel the failed statistical gate. See local_runtime/SEARCH_VALIDATION.json. No Full will be started by this experiment.
