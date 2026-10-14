# Context Weave / SourceTrail

Original author: 王子铭 (Giorno-Banana), MIT. SourceTrail is a submission alias; official display is Adaptive Evidence.

Best measured release **0.31.0**: [authoritative source archive](context-weave-0.31.0-source.zip), [release documentation](README_SOURCE_0.31.0.md), and [checksum manifest](context-weave-0.31.0-source.manifest.json). Historical root code and older archives remain for provenance; use the versioned archive to reproduce this release.

Add/Search use original-source storage, embeddings and deterministic retrieval with **zero generative LLM calls**. Embeddings remain text-embedding-v4, 1024 dimensions, batch 10. Search retains one query/option embedding call. The external evaluator owns Answer. 0.31 changes query-local long-document ranking and bounded original context, while preserving 0.29 ordinary-conversation ranking and every stored role. No benchmark data, answers, credentials, databases, or model weights are packaged.

## Official Textual Smoke history

| Version | Score | Completion | Duration |
|---|---:|---:|---:|
| 0.27.0 | 60.31 | 46/46 | 5m16s |
| 0.28.0 | 60.96 | 46/46 | 12m22s |
| 0.29.0 | 63.94 | 46/46 | 14m49s |
| 0.30.0 | 63.29 | 46/46 | 5m13s |
| 0.31.0 | **68.54** | 46/46 | 4m29s |

These are Smoke results, not Full. 0.30's document prior did not activate in its official run; its changed sub-scores do not prove an algorithmic gain. 0.31 public CL development has one confirmed complete-answer gain and a second rubric-only gain with a factuality caveat. Confirmation is incomplete due to local Answer timeouts and has no paired complete-answer gain. The public improvement gate failed; Smoke is exploratory. Public BEAM contexts and LoCoMo evidence hits are unchanged. See versioned documentation for reproducibility, method sources, checks and limits.

0.31 official Textual Smoke completed on 2026-10-14 with **68.54**, up 4.60 points from the previous best and 7.58 from the optimization starting baseline. It completed 46/46 evaluations in 269 seconds. Aggregate source routing activated for six searches (two direct, four reference); Add/Search generative calls remained zero. This is one Smoke result, not a Full result or a repeatability guarantee. The 70-point target is not yet reached. [Official aggregate record](context-weave-0.31.0-official-smoke.json).

Candidate **0.32.0**: [source archive](context-weave-0.32.0-source.zip), [documentation](README_SOURCE_0.32.0.md), [checksum manifest](context-weave-0.32.0-source.manifest.json). It protects direct evidence before source expansion, retaining 0.31 ranking and existing call counts. Public regression panels retain BEAM contexts and LoCoMo evidence hits; CL diagnostics are incomplete and show no established complete-answer gain. The strict public improvement gate failed; the next official Smoke is exploratory, with no score claim before completion.
