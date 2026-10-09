# Context Weave 0.7.0 — bounded GPT-4o-mini comparison

Use `context-weave-0.7.0-source.zip` for the complete frozen source; older loose files and archives are historical. This candidate has no official result yet. The observed best is **61.77** from the local 0.6.1 Smoke (46/46 completed, task `teval_4bfee59d2dfd1d6a`). The target, strictly above 70, remains unmet. This experiment authorizes one Textual Smoke; no Full.

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

The original evidence-search implementation is informed by ReFind (`https://github.com/imlrz/ReFind`, inspected revision `a80175ca0eeb52a938d7cab7a602bc780de8a577`, `app/retriever.py`) and prior public select6 experiments. No upstream source or prompt was copied into these modules. See PROVENANCE.md and LICENSE (MIT). No score increase is guaranteed. The cloud configuration's official result, actual charge and all fallback events will be reported after completion.
