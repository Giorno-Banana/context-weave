# Context Weave / SourceTrail 0.31.0

Raw-source Add and deterministic Search. Generative LLM calls occur only in Answer, owned by the external AML evaluator. Add/Search contain no chat-completions client, generative planner, judge, or query rewrite.

Add preserves every original role and embeds exact spans with text-embedding-v4, 1024 dimensions and batches of 10. Search keeps one existing query/option embedding call and a 24,000-character budget with top_k <= 100. Returned bodies are contiguous original text with role/date metadata.

The default query_document_adaptive mode uses the existing dense scores to detect a query whose top 12 chunks contain at least three passages from the same original user document of at least 2,000 characters. For this document case, direct questions use dense/raw-BM25 plus original-user Porter fusion. Generic references to previous answers use the ordinary dense/raw-BM25 view. Both restore bounded same-source context and literal section references. Other conversations retain 0.29 ranking and relevance-first packing. No extra embedding or generative request is made. Old assistant messages remain stored and retrievable. The experimental assistant-filter mode is not selected.

## Reproduce

Install requirements.txt, copy env.example to a private file, set embedding credentials, MEMORY_API_KEY, and a separate AE_DATABASE:

```powershell
.\start_local.ps1 -Port 18097 -PythonPath C:\service-venv\Scripts\python.exe -EnvFile @('.env')
python preflight.py --env-file .env --live --output synthetic-probe.json
python -m unittest discover -s tests
```

Authentication, atomic Add, request_id idempotency, user isolation, immediate retrieval, and persistent retries remain. Preserve existing evaluation databases. Historical LLM flags cannot enable generation because no generation implementation exists here. /health exposes aggregate document/direct/reference/conversation counters.

## Evidence and limits

62 tests passed, covering source fidelity, budgets, routing, unchanged embedding calls, authentication, idempotency, and isolation. Live synthetic preflight uses seven embedding requests and zero generation. Sixteen concurrent synthetic Adds and Searches passed. Real-embedding document probes verified both direct lookup and prior-answer references.

All 40 reused public BEAM contexts match 0.29 exactly. Public LoCoMo evidence hits remain 137/152 development and 137/153 confirmation. These are previously inspected regression panels, not unseen validation.

Public CL-Bench diagnostics used original public rubrics and the same local Qwen3.5-4B final Answer. Development confirmed complete answers changed from 0/8 to 1/8; another presentation-rubric gain has a factuality caveat and is not counted as confirmed complete. Confirmation has five paired valid answers, with 0/5 complete in both arms and three baseline timeouts. Codex reviewed semantics without a judge API or independent human review. The declared two-answer improvement gate was not met; official Smoke is exploratory. No official gain is claimed before completion. The local Answer model differs from the official evaluator.

This archive is the authoritative 0.31.0 implementation. No credentials, databases, benchmark payloads, datasets/answers, or model weights are included. Original author: 王子铭 (Giorno-Banana), MIT. SourceTrail is a submission alias; official account display is Adaptive Evidence. Method sources and excluded generative approaches are in PROVENANCE.md.
