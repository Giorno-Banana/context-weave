# Context Weave

Text memory service for the Agent Memory Challenge, Open-source Methods / textual track. Version `0.3.0` (candidate; official version binding and Smoke pending).

Submission contact: 秦天朗. Team: recursive roll. Repository: [Giorno-Banana/context-weave](https://github.com/Giorno-Banana/context-weave).

The service persists source text through Add and returns evidence passages through Search. Retrieval combines `text-embedding-v4`, BM25, reciprocal rank fusion, and adjacent source windows. Answer generation and evaluation are handled by the competition platform.

## Configuration

- Embedding: Bailian DashScope native HTTP API, `text-embedding-v4`, 1024 dimensions, document/query input types, L2 normalization.
- Chunks: 1,000 characters with 120-character overlap.
- Search: `hybrid_window`, at most the requested `top_k` (up to 100), with a local 24,000-character context budget.
- Add LLM: OpenRouter `openai/gpt-4o-mini`, pinned to the OpenAI provider with no provider or model fallback. Each batch contains at most eight chunks. The model selects up to three exact source phrases per chunk; validated phrases reinforce both embedding input and BM25 indexing.
- Search returns original source text, never generated text. The separate optional Search planner remains disabled.
- Storage: single-process FastAPI and SQLite WAL, with per-user isolation and a four-user cache. Embedding requests are serialized inside the store.

## Run

Install `requirements.txt`, copy `env.example` to a private `.env`, and configure the service key, Bailian embedding credentials, and `OPENROUTER_API_KEY`. Keep `AE_ADD_INDEXER=1` and `AE_PLANNER=0` for this candidate. Start with a fresh database: version 0.3.0 rejects older database profiles. Then run:

```bash
python preflight.py --env-file .env
python -m unittest discover -s tests -v
```

Follow [OPERATIONS.md](OPERATIONS.md) for deployment. The Python package and command names remain as supplied in the code; follow the documented `adaptive_evidence` entry points.

`preflight.py --env-file .env --live` performs a small synthetic test using real embedding and GPT-4o-mini calls. It does not start an official evaluation. Historical version 0.2.0 public-data retrieval diagnostics are documented in [PILOT_RESULTS.md](PILOT_RESULTS.md); they are not version 0.3.0 results or official answer scores. Full-scale runtime and capacity still require validation.

## License and method references

Code copyright: 王子铭. The original [MIT license](LICENSE) is retained. Submission contact and code copyright identify different roles. Method references and third-party licensing boundaries are documented in [PROVENANCE.md](PROVENANCE.md).

This repository includes service code, tests, configuration examples, and public-data sample identifiers. It excludes credentials, memory databases, model weights, private evaluation data, and answer datasets. Submission details are in [SUBMISSION.md](SUBMISSION.md).

## Version 0.3.0 validation

46 mocked regression tests pass, including Add-time routing, rejection of invented or cross-source quotes, atomic failure, user isolation, concurrent request idempotence, restart compatibility, and source-only output. On 2026-10-06, a real synthetic preflight passed with 3 GPT-4o-mini requests and 7 embedding requests. A separate HTTP probe passed, followed by 16 concurrent Add requests (128 synthetic chunks, 32.03 seconds total) and 16 concurrent Search requests (1.58 seconds total). These small probes do not establish Full-scale capacity or quality. Official version binding, Smoke, and Full remain pending at release preparation; no measured quality improvement is claimed.

OpenRouter reference: [Quickstart](https://openrouter.ai/docs/quickstart), [Structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection).
