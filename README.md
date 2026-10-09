# Context Weave 0.7.0 — bounded GPT-4o-mini comparison

Use `context-weave-0.7.0-source.zip` for the complete frozen source; older loose files and archives are historical. The official Textual Smoke completed on 2026-10-09 with **59.28**, all **46/46** items finished in **14m 14s** (task `teval_1d33fe2565bafa28`). This is **2.49 points below** the best local 0.6.1 score of **61.77**. The target, strictly above 70, **has not been met**. No Full was started. The cloud candidate was not promoted: its paid API was stopped after this one authorized comparison, and the public root was restored to local 0.6.1.

Total OpenRouter charge was **USD 0.1115622**, including all preflight and official Add/Search calls, below the USD 1 authorization. All 447 calls were accounted for with no pending/unknown charges. There were four source-selection fallback events, zero expansion fallback events, and zero Add/embedding failures. Two HTTP 405 method probes were observed separately. All 71 frozen source files and the deployment profile matched after evaluation. [Full aggregate result](context-weave-0.7.0-official-smoke.json).

Timing improved from 49m 33s to 14m 14s. The largest aggregate regression was Context Learning & Execution (55 to 30); temporal reasoning rose from 40 to 50, governance from 39.44 to 42.22, safety from 58.33 to 66.67, and streaming fell from 67.71 to 64.58. Fact recall, compositional inference and personalization were unchanged. These aggregates do not establish which internal call caused the changes.

The evaluated source archive remains unchanged from commit `5e4b53878432a53ee041fa27b620f8f5805b4415`, SHA256 `92a576fe17fbda961d633955570fb4c419f5b135d2a48ec0e2fcb5b87dc6c2be`. The frozen archive retains its truthful pre-run status; this root README and the aggregate result record the completed evaluation.

## Method and controlled changes

The 0.6.1 dense/BM25 retrieval, query expansion, source-ID selection, 128-candidate pool, direct-hit reserve, neighboring messages, 12,000-character selected context and 24,000-character fallback remain unchanged. GPT-4o-mini now performs both Add cue selection and Search planning through OpenRouter, pinned to OpenAI with provider fallbacks disabled. Search returns only original source renderings. It never returns the planner's generated answer or reasoning as a memory.

Add uses the existing cloud structured-output span-ID implementation (eight chunks per call); the prior local configuration used two chunks with the JSON schema repeated in its prompt. Search retains the same prompts, bounds and Qwen tokenizer clipping used in 0.6.1, with strict response validation. This is a comparison of complete cloud and local configurations, not a perfectly isolated model-only ablation. The Qwen tokenizer is used only to preserve clipping and batching, never for cloud billing. No local model inference is used in this cloud profile. Embeddings remain Bailian text-embedding-v4, 1024 dimensions.

An explored larger evidence reserve was rejected after a public development comparison fell from 31/50 to 29/50. It is not included here. Public samples are development diagnostics, not official scores. No private official question, answer or evidence label was inspected for tuning.

## Spending policy

Add, Search, preflight and every retry share one persistent SQLite ledger with a USD 1 maximum for the entire experiment. Each attempt first reserves USD 0.03 atomically; this exceeds 128K input tokens at USD 0.15/M and at most 1024 output tokens at USD 0.60/M. Requests pin these provider price ceilings, forbid additional per-request fees, and contain text only. Successful responses settle the reported OpenRouter `usage.cost`, rounded upward. Missing charges, timeouts, connection failures and process death retain the whole reservation. Restarting does not reset the ledger or change its cap. Unexpected charges above the reservation halt further calls. No new request is sent if insufficient budget remains.

Budget exhaustion makes Add fail explicitly and makes Search retain the already-declared original-retrieval fallback. These events must be disclosed in the result. The USD 1 cap covers OpenRouter inference for this experiment; existing Bailian embedding charges are separate. A fresh memory database is required. Never delete/reset the budget ledger to resume this experiment.

## Run and reproduce

Install `requirements.txt`. Set private `OPENROUTER_API_KEY`, `DASHSCOPE_API_KEY`, `AE_EMBEDDING_URL` and `MEMORY_API_KEY`. Use `env.openrouter.example` as the non-secret profile, including absolute paths for `AE_DATABASE`, `AE_CLOUD_BUDGET_DB` and `AE_PLANNER_TOKENIZER`. The tokenizer is the public Qwen3.5-4B `tokenizer.json`, SHA256 `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`. Model weights are unnecessary for the cloud profile. Run `start_local.ps1 -PythonPath <python> -EnvFile <credentials>,<profile> -Port <port>`. Start in a separate database from any local model run.

`python -m unittest discover -s tests -v` runs offline regression checks, including concurrent spending reservations, restart persistence, unknown charges, retry accounting and rejection of generated/foreign source identifiers. Tests and real synthetic HTTP preflight must pass before official submission. Source and deployment configuration are frozen for the run. Historical local-runtime and operational documents remain bundled for provenance; this README and EXPERIMENT.json specify 0.7.0.

## Attribution and limits

The original evidence-search implementation is informed by ReFind (`https://github.com/imlrz/ReFind`, inspected revision `a80175ca0eeb52a938d7cab7a602bc780de8a577`, `app/retriever.py`) and prior public select6 experiments. No upstream source or prompt was copied into these modules. See PROVENANCE.md and LICENSE (MIT). No score increase is guaranteed. The completed result and fallback events are reported above; the score target remains unmet.
