# Context Weave 0.9.0 — local 9B evidence planner

This candidate retains the retrieval algorithm and prompts of 0.6.1 and changes the local model and serving runtime. Add and Search use **Qwen3.5-9B-Q5_K_M**, served by pinned **llama.cpp b11429, CUDA**. Source text is retained; Search returns original evidence rather than generated answers.

- Add selects identifiers of exact source spans and repeats those spans only for indexing. Batch size 2; model concurrency 1; timeout 180 seconds.
- Embedding: Bailian text-embedding-v4, 1024 dimensions. No OpenRouter calls or cloud LLM fallback.
- Search: dense/BM25 hybrid retrieval, up to 3 expansion queries and 128 candidates; up to 16 selected source IDs per batch. Final packing remains selected evidence, four baseline hits, and adjacent messages from the same ordered Add request. Selected budget 12,000 characters; fallback 24,000; top_k at most 100.
- Local inference: temperature 0, seed 42, thinking disabled, context 8192, one slot, all model layers on GPU, prompt caching and context shifting disabled. No question or source state is shared between requests. Model output is validated against the current source-ID allowlist.
- Weight and active binary/launcher hashes: `local_runtime/LLAMACPP_MANIFEST.json`. GGUF source: unsloth/Qwen3.5-9B-GGUF, revision 3885219b6810b007914f3a7950a8d1b469d598a5. Model and binary assets are downloaded separately, not redistributed here.
- Historical 4B Torch runtime files remain for provenance and regression tests. `MODEL_MANIFEST.json` and `start_supervised.ps1` describe that older runtime; they are **not the active 0.9.0 serving configuration**.

No official score exists for 0.9.0 yet. Best prior complete Smoke: **61.77 (0.6.1)**; the 0.7.0 cloud comparison scored 59.28. The target remains a complete official Smoke above 70; public development results do not establish an official score. See `EXPERIMENT.json` for the preregistered engineering and separate exploratory criteria, results, review, and limitations. Full is not authorized.

## Reproduce

Use Python 3.10 with `requirements.txt`. Obtain the exact GGUF and llama.cpp assets identified by the runtime manifest. Launch `local_runtime/start_llamacpp.ps1 -Backend cuda -AssetDirectory PATH -LogDirectory PRIVATE_PATH`, then start the API with `start_local.ps1` and private credentials plus the `env.local.example` profile. Set absolute deployment paths explicitly. The Qwen tokenizer JSON SHA256 is 5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42; the 4B and 9B tokenizer files are identical.

Run `python -m unittest discover -s tests -v`. The source archive for each version is authoritative; older loose repository files are historical. Archives omit credentials, model weights, stored memories, and benchmark answers. Add/Search require the configured service token. Source, profile and runtime are frozen before official evaluation.

## Attribution and eligibility

Original project implementation informed by ReFind's bounded original-evidence search and earlier public experiments. No upstream source or prompt was copied for this model change. See `PROVENANCE.md` and `LICENSE`; third-party models and dependencies retain their licenses. The participant reports organizer permission for local-model use in the academic track. This repository does not independently certify that exception.
