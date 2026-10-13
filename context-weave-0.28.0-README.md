# Context Weave / SourceTrail 0.28.0

This release serves raw-source Add and deterministic Search. Generative LLM calls occur only in Answer, which is performed by the external AML evaluator. The Add/Search service has no chat-completions client or generative planner.

Add preserves original messages and uses text-embedding-v4 (1024 dimensions, batch size 10) on exact spans up to 1000 characters with 120-character overlap. Search combines dense retrieval, BM25 and Porter-stem lexical retrieval with reciprocal-rank fusion. It reserves 25% of the 24,000-character evidence budget for neighboring original spans, merges overlapping offsets from the same source, and orders retrieved messages within each ordered Add request. It does not infer chronology across opaque session or request IDs. Identical text at different dates remains separate evidence.

## Reproduce

Install requirements.txt, copy env.example to a private environment file, set embedding credentials, MEMORY_API_KEY and an explicit separate AE_DATABASE, then run:

```powershell
.\start_local.ps1 -Port 18093 -PythonPath C:\service-venv\Scripts\python.exe -EnvFile @('.env')
python preflight.py --env-file .env --live --output synthetic-probe.json
python -m unittest discover -s tests
```

The default API/profile mode is stem_window. Earlier retrieval modes remain available for controlled comparisons. Authentication, user isolation, atomic Add, request_id idempotency and persistent retries are retained. Keep existing evaluation databases intact; use a new database for this candidate.

## Validation and limits

40 automated tests pass, including original-span fidelity, bounded evidence budgets, date preservation, neighboring evidence, isolation and no generative Add/Search calls. A paired diagnostic on 305 public LoCoMo questions reused identical text-embedding-v4 source/query vectors without any new model calls. On the first 152 questions, complete evidence coverage was 135/152 for 0.27.0 and 137/152 for the selected candidate. On the separate 153-question confirmation partition it was 136/153 and 137/153. These are retrieval-coverage counts on previously available public data, not answer accuracy, unseen benchmark generalization, or an official score. The gain is small and does not establish that official Smoke will reach 70.

Original author/copyright: 王子铭 (Giorno-Banana), MIT. SourceTrail is a submission alias. Provenance and earlier version history are in PROVENANCE.md. The archive contains only source, tests and example configuration, with no credentials, databases, evaluation payloads or model weights.
