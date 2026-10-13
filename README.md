# Context Weave / SourceTrail

Original author: 王子铭 (Giorno-Banana), MIT. SourceTrail is a submission alias; official display is Adaptive Evidence.

Current candidate **0.31.0**: [authoritative source archive](context-weave-0.31.0-source.zip), [release documentation](README_SOURCE_0.31.0.md), and [checksum manifest](context-weave-0.31.0-source.manifest.json). Historical root code and older archives remain for provenance; use the versioned archive to reproduce this release.

Add/Search use original-source storage, embeddings and deterministic retrieval with **zero generative LLM calls**. Embeddings remain text-embedding-v4, 1024 dimensions, batch 10. Search retains one query/option embedding call. The external evaluator owns Answer. 0.31 changes query-local long-document ranking and bounded original context, while preserving 0.29 ordinary-conversation ranking and every stored role. No benchmark data, answers, credentials, databases, or model weights are packaged.

## Official Textual Smoke history

| Version | Score | Completion | Duration |
|---|---:|---:|---:|
| 0.27.0 | 60.31 | 46/46 | 5m16s |
| 0.28.0 | 60.96 | 46/46 | 12m22s |
| 0.29.0 | **63.94** | 46/46 | 14m49s |
| 0.30.0 | 63.29 | 46/46 | 5m13s |
| 0.31.0 | Pending exploratory Smoke | — | — |

These are Smoke results, not Full. 0.30's document prior did not activate in its official run; its changed sub-scores do not prove an algorithmic gain. 0.31 public CL development has one confirmed complete-answer gain and a second rubric-only gain with a factuality caveat. Confirmation is incomplete due to local Answer timeouts and has no paired complete-answer gain. The public improvement gate failed; Smoke is exploratory. Public BEAM contexts and LoCoMo evidence hits are unchanged. See versioned documentation for reproducibility, method sources, checks and limits.
