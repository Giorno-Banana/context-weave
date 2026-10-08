# Context Weave 0.3.1 status

Updated: 2026-10-08. Open-source Methods / textual memory.

This release replaces free-form quoted cues with GPT-4o-mini selection of deterministic original-span IDs, adds persistent batch checkpoints, and records sanitized failure/timing diagnostics. Original sources and Search evidence remain unchanged. Embeddings use text-embedding-v4, 1024 dimensions; Search uses hybrid_window and no planner. A fresh database is required.

50 mocked regression tests and the live synthetic preflight passed. Official binding and Smoke are pending at release preparation. No score, quality gain, Full capacity or Full result is claimed. The 0.3.0 Smoke failed with Add HTTP 503; diagnostics reproduced validation fragility and repeated prefix work, but did not recover the exact historical trigger.

Contact: 秦天朗. Team: recursive roll. Repository: https://github.com/Giorno-Banana/context-weave. Copyright and provenance are documented in LICENSE and PROVENANCE.md.
