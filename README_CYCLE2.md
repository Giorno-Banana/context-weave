# Context Weave

Text memory service for the Agent Memory Challenge, Open-source Methods / textual track. Version `0.2.0`.

Submission contact: 秦天朗. Team: recursive roll. Repository: [Giorno-Banana/context-weave](https://github.com/Giorno-Banana/context-weave).

The service persists source text through Add and returns evidence passages through Search. Retrieval combines `text-embedding-v4`, BM25, reciprocal rank fusion, and adjacent source windows. Answer generation and evaluation are handled by the competition platform.

## Configuration

- Embedding: Bailian DashScope native HTTP API, `text-embedding-v4`, 1024 dimensions, document/query input types, L2 normalization.
- Chunks: 1,000 characters with 120-character overlap.
- Search: `hybrid_window`, at most the requested `top_k` (up to 100), with a local 24,000-character context budget.
- Optional planner: `gpt-4o-mini`, disabled in the candidate configuration. Embedding calls are still required.
- Storage: single-process FastAPI and SQLite WAL, with per-user isolation and a four-user cache. Embedding requests are serialized inside the store.

## Run

Install `requirements.txt`, copy `env.example` to a private `.env`, and configure the service key and embedding credentials. Then run:

```bash
python preflight.py --env-file .env
python -m unittest discover -s tests -v
```

Follow [OPERATIONS.md](OPERATIONS.md) for deployment. The Python package and command names remain as supplied in the code; follow the documented `adaptive_evidence` entry points.

`preflight.py --env-file .env --live` performs a small synthetic test using real embedding calls. It does not start an official evaluation. Public-data retrieval diagnostics are documented in [PILOT_RESULTS.md](PILOT_RESULTS.md); they are not official answer scores. Full-scale runtime and capacity still require validation.

## License and method references

Code copyright: 王子铭. The original [MIT license](LICENSE) is retained. Submission contact and code copyright identify different roles. Method references and third-party licensing boundaries are documented in [PROVENANCE.md](PROVENANCE.md).

This repository includes service code, tests, configuration examples, and public-data sample identifiers. It excludes credentials, memory databases, model weights, private evaluation data, and answer datasets. Submission details are in [SUBMISSION.md](SUBMISSION.md).
