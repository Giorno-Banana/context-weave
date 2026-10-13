# Context Weave / SourceTrail

Original author: 王子铭 (Giorno-Banana), MIT. SourceTrail is a submission alias.

The current candidate is **0.30.0**, an Answer-only generation memory service. The authoritative implementation is [context-weave-0.30.0-source.zip](context-weave-0.30.0-source.zip), with [release documentation](README_SOURCE_0.30.0.md) and [checksum manifest](context-weave-0.30.0-source.manifest.json). Historical root source and older archives remain for provenance; use the versioned archive to reproduce this candidate.

Add/Search use raw-source storage, embeddings, and deterministic retrieval. They make **zero generative LLM calls**. Embeddings remain text-embedding-v4, 1024 dimensions, batch 10; Search retains one query/option embedding call. The official external evaluator owns Answer. The candidate conditionally adds original-user lexical priority for a scope dominated by one long original user document, while preserving 0.29 ranking for other conversations. No benchmark data, answers, credentials, databases, or model weights are packaged.

## Official Textual Smoke history

| Version | Score | Completion | Duration |
|---|---:|---:|---:|
| 0.27.0 | 60.31 | 46/46 | 5m16s |
| 0.28.0 | 60.96 | 46/46 | 12m22s |
| 0.29.0 | **63.94** | 46/46 | 14m49s |
| 0.30.0 | Pending exploratory Smoke | — | — |

These are Smoke results, not Full scores. 0.30 public development diagnostics improved strict complete answers from 0/8 to 1/8, below the declared two-answer gate. Public BEAM contexts and LoCoMo evidence hits are unchanged. An independent public-document confirmation run was interrupted by local Answer timeout and is incomplete. Official Smoke is needed to establish any candidate gain. See the versioned documentation for reproduction, method attribution, tests, and limits.
