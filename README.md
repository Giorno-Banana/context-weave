# Context Weave — completed 0.25.1 Smoke

Official Textual Smoke **53.51**, **46/46** completed in **58m 36s**, task `teval_2a68c3514e9a587d`. Completed `2026-10-10T20:30:56+08:00`. The previous best was **61.77** (0.6.1); change **-8.26**. The target of at least 70 is not met.

This run used local Qwen3.5-4B runtime042, text-embedding-v4, Add16/Search16. No Full or new OpenRouter calls occurred. Frozen source, active runtime, external model files and deployment profile were rechecked after evaluation. [Aggregate result](context-weave-0.25.1-official-smoke.json).

The source archive remains unchanged at commit `cd634672069d274b460886c9dda8534c0d1b5452`, SHA256 `a091770517ada6c2684d11e8fdcbb01ad49034ac3b83d6774486a0abae71f4f6`. The pre-run documentation below is historical; this dated result supersedes its pending-score status.

## Historical pre-run documentation

# Context Weave 0.25.1

Search uses scoped hybrid retrieval and local source selection. The primary selector recovers only a missing final object brace after a completed JSON array, validates every returned identifier before bounding the retained list, and uses validated batch-local identifiers. A bounded original-user statement reserve preserves relevant constraints, changes and standing instructions with conservative transcript speaker attribution. Only original source text is returned, with selected overlapping spans merged. No generated answer text or benchmark-specific rules are inserted into memory.

Actual models are Bailian text-embedding-v4 (1024 dimensions) and local Qwen3.5-4B supervised runtime0.4.2 for Add/Search. Runtime/model hashes are in local_runtime/MODEL_MANIFEST.json. No OpenRouter calls are enabled. The participant reports organizer permission for a local-model exception; this package discloses actual models without independently certifying eligibility.

Local public validation uses reused development data and a 4B reader/judge, not the official reader. Raw automatic accuracy on 50 questions was 38 to 39, including a date-judgment disagreement and a dataset regression. A Codex review of all 100 answers under the unchanged published contract was 33 to 36, with 3 wins and 0 losses; the original automatic results remain preserved. This is model adjudication, not human review. The same full-panel review was declared before running the disjoint fixed 24-question confirmation: the raw result was 14 to 14 with incomplete judgments; completing only the three unique truncated judge responses gave 14 to 15, while the separate full-panel Codex review gave 13 to 14. Public BEAM semantic rubric coverage improved from 0.46 to 0.5716667. These are local diagnostics, not an official score or an untouched test set. Best prior completed official Smoke remains 61.77; the latest prior release, 0.17.1, scored 59.99. Official 0.25.1 is pending. Detailed evidence and limitations are in EXPERIMENT.json.

Use Python3.10 and requirements.txt. Configure credentials privately using env.local.example, start the pinned local runtime on loopback18095, then API18099 with a fresh database. Add/Search require the configured token. Run `python -m unittest discover -s tests -v`. API wiring uses the same retrieval implementation evaluated in0.25.0. Source, model, runtime and configuration must remain frozen during evaluation.

The versioned archive is authoritative. It excludes credentials, model weights, stored memories and benchmark answers. Source is MIT licensed; dependencies/models retain their licenses. Original retrieval changes and attribution are documented in PROVENANCE.md. OnlySmoke is in scope; Full is not authorized.
