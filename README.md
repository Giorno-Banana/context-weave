# Context Weave 0.5.1

Use `context-weave-0.5.1-source.zip` for the complete fixed source. Older loose files are historical.

Add runs local Qwen3.5-4B through the unchanged supervised 0.4.1 runtime. Embeddings are Bailian text-embedding-v4 (1024 dimensions). Search uses dense/BM25/Porter/context fusion, a local CPU cross-encoder, conservative source-anchored calendar metadata, and overview diversity. Adjacent original spans are now bundled within the same ordered Add request. Source text, role, and timestamps are retained; bundle IDs derive from their member source IDs. Each bundle is capped at 4,000 characters, the total at 96,000 characters, and result count at the supplied top_k (100 for AML). No final answer is generated. No cross-user memory, benchmark labels, or official evaluation payloads are used for tuning.

The reranker is `cross-encoder/ms-marco-MiniLM-L6-v2`, CPU, six threads, batches of 16, 384 model input tokens. Version 0.5.1 removes an incompatible 6,000-character query schema limit. Long questions are accepted and tokenized with the same bounded model input; the returned source text is unchanged. Failures log only an exception class and HTTP status. Exact model hashes and runtime sources are included; weights are excluded.

Install `requirements.txt` for the API and the local-model runtime dependencies. Start the Qwen supervisor as documented in `local_runtime/`. Download reranker weights from https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2 and verify the manifest, then run `local_runtime/rerank_server.py --model <weights> --port 18093` with the model environment. Overlay `local_runtime/profile.txt` on a private credentials file and start `start_local.ps1` on an available local port. No cloud LLM fallback is enabled.

The official LDBD key has immutable endpoints, so `/add` and `/search` at `https://wzm.tail36b9f2.ts.net` are switched to the selected bound version only while no job is running. The version-specific `/v051` prefix is also provided for verification. Credentials remain private. The previous 0.4.1 and 0.5.0 deployments remain available locally for comparison.

## Validation and limits

Version 0.4.1 completed official Smoke with 58.82. The 0.5.0 Smoke task `teval_8f1b30715f47d766` failed with Search HTTP 503 after 33m57s and has no score. A synthetic test reproduced HTTP 422 for queries longer than 6,000 characters in its reranker, which the API maps to 503; the exact private failing query was not inspected. No 0.5.1 official score is claimed before completion. The participant's requested 90+ score is a target, not a measured result. No Full has started.

Public retrospective retrieval diagnostics use four LoCoMo-Refined conversations (607 questions, 606 with evidence annotations), raw v4 indices without Add LLM enrichment, and no official evaluation data. The two previously examined conversations had 91.15% complete-evidence coverage with individual 24k results; bundle96k reached 98.36%. An additional pair had 91.03% versus 98.34%. The mean contexts grew to about 86k and 82k characters. These are retrieval coverage figures, not question-answer accuracy, a blind holdout, or AML scores. Wider context can add noise; official Smoke is required to measure its impact. The frozen comparison and source hashes are in `local_runtime/BUNDLE_VALIDATION.json`.

The actual Add model is disclosed as local Qwen. The participant reports organizer permission; this repository does not independently certify an exception to the published academic-model rule. See `PROVENANCE.md` for inspected repositories, exact revisions where known, and limitations. MIT; original copyright notices are retained.

86 regression tests passed on 2026-10-09. Live reranker probes with synthetic queries of 500, 6,001 and 30,000 characters returned HTTP 200 and finite scores.
