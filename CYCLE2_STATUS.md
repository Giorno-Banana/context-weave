# Context Weave 0.3.0 status

Updated: 2026-10-06. Open-source Methods / textual memory.

The Add stage now calls OpenRouter openai/gpt-4o-mini to select exact source phrases that reinforce embedding and BM25 indexing. The model is pinned to OpenAI, structured outputs are required, and fallback routing is disabled. The source text and offsets remain unchanged. Search returns only source evidence.

text-embedding-v4 still provides 1024-dimensional embeddings. The separate Search planner remains disabled. The new index profile requires a fresh database and does not reuse version 0.2.0 evaluation memory.

46 mocked regression tests pass. Real OpenRouter access and synthetic integration tests passed on 2026-10-06: 3 GPT calls and 7 embedding calls in preflight, network API checks, then 16 concurrent Add and 16 concurrent Search requests. Add processed 128 synthetic chunks in 32.03 seconds; the Search batch took 1.58 seconds. Public deployment, publication verification, new official version binding, and Smoke remain pending at release preparation. Full capacity and sustained availability still need verification. This file does not claim any new official score or improved retrieval quality.

Submission contact: 秦天朗. Team: recursive roll. Repository: https://github.com/Giorno-Banana/context-weave. Code copyright: see LICENSE. Historical public-data diagnostics in PILOT_RESULTS.md describe the 0.2.0 baseline, not this model-assisted indexer.
