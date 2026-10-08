# Cycle 2 submission: Context Weave 0.3.1

Release preparation record dated 2026-10-08. Official Smoke pending; no Full started.

| Field | Value |
|---|---|
| Track / division | Textual / Open-source Methods |
| Version | 0.3.1 |
| Contact / team | 秦天朗 / recursive roll; contact email supplied privately |
| Repository | https://github.com/Giorno-Banana/context-weave |
| Fixed commit | Register the full SHA of this release in the controlled version form |
| License / copyright | MIT / 王子铭 (Giorno-Banana) |
| Add | https://wzm.tail36b9f2.ts.net/add |
| Search | https://wzm.tail36b9f2.ts.net/search |
| Health | https://wzm.tail36b9f2.ts.net/health |
| Authentication | X-Api-Key; Bearer and Token also accepted. Keys provided privately only |
| Hosting | Windows personal computer, approximately 31.4 GiB RAM; HTTPS via Tailscale Funnel |
| Planned Smoke concurrency | Add 16 / Search 16, subject to observed service capacity |

## Fixed method

See README for complete semantics. Add calls OpenRouter openai/gpt-4o-mini, only the OpenAI provider, no fallback, temperature 0, strict JSON schema. It selects up to three IDs of original spans (<=96 characters) per 1000-character source chunk, in batches of at most eight chunks. Integer IDs resolve to original text; original source text is retained unchanged. Selected spans reinforce embedding and BM25 inputs. Model calls have a 60-second timeout, up to three attempts and concurrency four. Successful batch work is persisted privately; completed Adds become searchable atomically. No partial output or alternative-model fallback is used after an upstream failure.

Embedding: text-embedding-v4, 1024 dimensions, document/query modes, no truncation or custom instruction. Search: dense plus BM25 RRF and adjacent windows, top_k at most 100, local context budget 24000 characters. Single-process deployment; embedding calls are serialized per batch. Four-user retrieval cache. Model/index profile changes require a new version and fresh database.

## Validation and limits

50 regression tests and a real synthetic preflight passed on 2026-10-08. The previous 0.3.0 Smoke failed with Add HTTP 503 and has no score. This version fixes diagnosed source-copy fragility, missing intermediate checkpoints and insufficient failure diagnostics. Publication, deployment verification, binding and official Smoke are tracked after release preparation. Small synthetic tests do not demonstrate Full capacity or improved quality. Full remains conditional on a successful Smoke, capacity validation and a separately agreed budget.

See PROVENANCE.md for authorship and references. No credentials, private evaluation memories or answers belong in this repository.
