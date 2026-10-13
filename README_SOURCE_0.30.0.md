# Context Weave / SourceTrail 0.30.0

Raw-source Add and deterministic Search. Generative LLM calls occur only in Answer, owned by the external AML evaluator. Add/Search contain no chat-completions client, generative planner, judge, or query rewrite.

Add preserves original messages and embeds exact source spans using text-embedding-v4, 1024 dimensions and batches of 10. Search retains one existing query/option embedding call, dense/BM25/Porter reciprocal-rank fusion, relevance-first source admission, bounded standing-instruction reservation, and neighboring original spans. Returned bodies remain contiguous original text with role/date metadata; the budget remains 24,000 characters, top_k <= 100.

The default document_focus mode adds an original-user lexical ranking stream only when the longest original user source is at least 12,000 characters and occupies at least half of all original source characters in that user's memory scope. Other scopes use the 0.29.0 ranking. Assistant messages remain stored and searchable. The prior adds no embedding or generative request. /health exposes aggregate counts of prior-enabled and ordinary-conversation rankings. Experimental whole-source, linked-section, and global-user-priority modes are not the released API default.

## Reproduce

Install requirements.txt, copy env.example to a private environment file, set embedding credentials, MEMORY_API_KEY, and a separate AE_DATABASE, then run:

```powershell
.\start_local.ps1 -Port 18096 -PythonPath C:\service-venv\Scripts\python.exe -EnvFile @('.env')
python preflight.py --env-file .env --live --output synthetic-probe.json
python -m unittest discover -s tests
```

Authentication, atomic Add, request_id idempotency, user isolation, immediate retrieval, and persistent retry state remain. Preserve existing evaluation databases; use a separate candidate database. Historical LLM flags cannot enable generation because no such implementation is present.

## Evidence and limits

56 automated tests passed, including source fidelity, budgets, conditional prior activation, unchanged query embedding counts, authentication, idempotency, and isolation. Live synthetic preflight passed with seven embedding requests and no Add/Search generation.

On reused public BEAM panels, all 40 retrieved contexts are identical to 0.29.0. Public LoCoMo complete evidence hits are unchanged: 137/152 development and 137/153 confirmation. These previously inspected panels are regression checks, not unseen validation.

Eight distinct public CL-Bench development contexts were selected by a declared length filter and SHA-256 order before their rubrics were inspected. With the same local Qwen3.5-4B final Answer and public rubrics, strict complete answers changed from 0/8 to 1/8. Codex performed semantic review, not an independent human or judge API. This did not meet the declared two-answer improvement gate. The remaining format/citation failures and the local Answer timeout are retained in private research records. This candidate's official Smoke is an exploratory check; no official score is claimed before completion. The local Answer model differs from the official evaluator.

This versioned source archive and manifest identify the 0.30.0 implementation. No credentials, databases, evaluation payloads, public datasets/answers, or model weights are included. Original author/copyright: 王子铭 (Giorno-Banana), MIT. SourceTrail is a submission alias. See PROVENANCE.md.