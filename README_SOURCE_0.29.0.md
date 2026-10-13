# Context Weave / SourceTrail 0.29.0

Raw-source Add and deterministic Search. Generative LLM calls occur only in Answer, owned by the external AML evaluator. Add/Search contain no chat-completions client, generative planner, judge or query rewrite.

Add preserves original messages and embeds exact source spans with text-embedding-v4, 1024 dimensions and batches of10, unchanged from0.28.0. Search retains the existing query embedding request and dense/BM25/Porter lexical reciprocal-rank fusion. The default mode is focus_stem_rules. It admits relevant evidence first, reserves a bounded portion for literal user standing instructions, admits distinct source messages before long-source tails, and adds bounded neighboring spans. Overlapping offsets are merged only within the same original message. Every returned body is a contiguous original span with its original role/date. No chronology is inferred from opaque IDs. The evidence budget remains24,000 characters and top_k<=100.

## Reproduce

Install requirements.txt, copy env.example to a private environment file, set embedding credentials, MEMORY_API_KEY and a separate AE_DATABASE, then run:

```powershell
.\start_local.ps1 -Port 18094 -PythonPath C:\service-venv\Scripts\python.exe -EnvFile @('.env')
python preflight.py --env-file .env --live --output synthetic-probe.json
python -m unittest discover -s tests
```

Authentication, user isolation, atomic Add, request_id idempotency, immediate retrieval and persistent retry state are retained. Use a new candidate database; preserve existing evaluation databases. Internal research modes remain for diagnostics; the released API/profile selects focus_stem_rules.

## Evidence and limits

49 automated tests cover source fidelity, budgets, dates, source diversity, cache invalidation, authentication, idempotency, and unchanged query embedding counts. On20 public BEAM development questions, a paired local Qwen3.5-4B Answer-only comparison produced7 complete baseline answers and11 candidate answers under unchanged public rubrics. Review was performed by Codex in the optimization conversation, not an independent human or judge API. No additional Add/Search generation occurred. The same152 public LoCoMo development questions retained137 complete evidence hits for both. These are public diagnostics with a different Answer model, not official scores or proof of generalization. On the separate20-question public BEAM confirmation conversation, complete answers improved from5 to7, with no complete-answer losses; the153-question LoCoMo confirmation retained137 complete evidence hits for both. Both public selection gates passed. The public temporal rubric contains one known ideal-answer inconsistency; the same unchanged rubric was used for both arms.

The main repository preserves earlier releases. This versioned source archive and its manifest identify the0.29.0 implementation. No credentials, databases, evaluation payloads or model weights are included.

Original author/copyright: 王子铭 (Giorno-Banana), MIT. SourceTrail is a submission alias. See PROVENANCE.md for original work and method references.
