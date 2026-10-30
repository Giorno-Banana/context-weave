# Context Weave

Text memory service for the Agent Memory Challenge, Open-source Methods / textual track. Version `0.3.1`; official version binding and Smoke are pending at release preparation.

Submission contact: 秦天朗. Team: recursive roll. Repository: [Giorno-Banana/context-weave](https://github.com/Giorno-Banana/context-weave).

## Method

Add preserves original source text, role, session and timestamp. Chunks contain at most 1,000 characters, with 120-character overlap. Each chunk is deterministically divided into original spans of at most 96 characters. OpenRouter `openai/gpt-4o-mini`, pinned to the OpenAI provider without fallback, selects up to three span IDs per chunk. Structured output uses per-chunk integer enums and three selection slots; the program resolves selected IDs back to exact source spans. Generated text never becomes evidence. Selected original spans reinforce embedding and BM25 indexing.

Bailian `text-embedding-v4` supplies 1,024-dimensional, L2-normalized document/query embeddings. Search combines dense and BM25 rankings with reciprocal rank fusion and adjacent source windows. The `hybrid_window` profile returns at most the requested top_k (maximum 100) and uses a local 24,000-character context budget. Search returns original source passages only; final answers and evaluation belong to the competition platform. The separate Search planner stays disabled.

## Reliability and storage

The service uses single-process FastAPI and SQLite WAL. Successful GPT and embedding batches are checkpointed separately from completed memories. Checkpoints are scoped to user, request, payload and database model profile; interrupted retries reuse completed work after process restart. A changed payload cannot reuse a pending request ID. No source is searchable until the whole Add commits atomically; temporary work is removed at commit or local user purge. Embedding access is serialized per small batch, releasing the lock between batches. A four-user retrieval cache is invalidated after each completed Add.

Provider HTTP status, timeout/validation category, attempts, batch offsets and timings are logged without credentials, source content or user/request identifiers. Failures return 503 with Retry-After; there is no fallback to another model or to non-LLM indexing. Version 0.3.1 requires a fresh database and rejects older profiles.

## Run and verification

Install `requirements.txt`, copy `env.example` to a private `.env`, and configure the service key, Bailian endpoint/key and `OPENROUTER_API_KEY`. Keep `AE_ADD_INDEXER=1` and `AE_PLANNER=0`. Follow [OPERATIONS.md](OPERATIONS.md); Python entry points remain under `adaptive_evidence`.

```bash
python preflight.py --env-file .env
python -m unittest discover -s tests -v
python preflight.py --env-file .env --live
```

On 2026-10-08, 50 mocked regression tests and the small live synthetic preflight passed. Tests cover exact source selection, routing, failure recovery, pending-data invisibility, restart checkpoints, payload conflicts, scope isolation, log redaction and original-source Search results. Additional load/deployment checks and the official Smoke are tracked separately. These checks do not establish Full capacity or retrieval quality. The earlier 0.3.0 Smoke ended with Add HTTP 503 without a score; its exact trigger was not recoverable from the old logs. Historical public-data diagnostics in [PILOT_RESULTS.md](PILOT_RESULTS.md) describe the 0.2.0 baseline.

## License and references

Code copyright: 王子铭. The original [MIT license](LICENSE) is retained. Submission contact and copyright identify different roles. [PROVENANCE.md](PROVENANCE.md) records method references and licensing boundaries. The repository excludes keys, memory databases, private evaluation data and model weights. See [SUBMISSION.md](SUBMISSION.md) for deployment details.

OpenRouter: [Quickstart](https://openrouter.ai/docs/quickstart), [Structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection).
