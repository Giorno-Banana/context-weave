# SourceTrail 0.32.0 submission materials

System: SourceTrail; team: Qhc‘s team; category: Open-source Methods (academic); evaluation type: Textual Memory. License: MIT; copyright notices are retained in LICENSE. Contact details are maintained privately with the organizer; keys are supplied only through its controlled credential workflow.

## Identity and evidence

Full task: `teval_6c99618ea0916224`, run label `sourcetrail-v320-full-20261014`, succeeded, 9,602/9,602, score52.79. Start 2026-10-14 17:26:13, completion 2026-10-16 03:02:32 (UTC+8). [Sanitized aggregate record](sourcetrail-0.32.0-official-full.json). Matching SourceTrail Smoke: `teval_a35e6262923680e0`, succeeded,63.68. This Full is not the historical best Smoke68.67.

The original fixed source commit is `e84af580a3a9a21f1eab6328d41e8b93bb52552e`. The exact terminal Full source is `releases/sourcetrail-0.32.0-full/` and `sourcetrail-0.32.0-full-recovery-source.zip`, SHA256 `4cded88da43103edf9b656c22ca6ecc4e0a024e696eb74e65347af06c1e7a6f6`. Use the immutable Git commit containing this disclosure (not a moving branch) when providing the updated material reference. [File hashes](sourcetrail-0.32.0-full-source.manifest.json) prove the restored tree matches the frozen terminal source. The current public frozen tree and archive include the long-input compatibility repair used at Full completion.

## Interface contract

Authentication uses `X-Api-Key` with a separately configured Memory System Key. Keep credentials outside source control. The application provides relative routes `/add`, `/search` and `/health`; the independent runtime supplies its own base URL.

The recorded evaluation configuration is Add16 and Search16, top_k100 and a 24,000-character evidence budget. This describes configured concurrency, not a throughput guarantee. The implementation uses one Uvicorn worker, FastAPI and SQLite WAL; see [runtime limits](OPERATIONS.md).

Add returns success only after atomic persistence and immediate searchability. Retries with the same request_id and payload are idempotent; conflicting payloads are rejected. Search scopes results to the supplied user_id. Returned bodies are original-source evidence. Source fidelity, timestamp and role retention, authentication and isolation are covered by the frozen tests.

## Method, recovery and integrity

The [provenance document](releases/sourcetrail-0.32.0-full/PROVENANCE.md) records technical changes through0.32; [FULL_RECOVERY.md](docs/FULL_RECOVERY.md) records the three changed/added files during Full recovery. No GPT component or local generative model is enabled in this memory service. The configured embedding is text-embedding-v4,1,024dimensions,batch10; no model swap is claimed or performed.

The participant-facing API confirms successful Full execution but does not expose sufficient evidence to certify organizer approval, absence of platform-side duplicate results, or conformity of its pipeline/dataset hashes to the current publication baseline. Those are organizer review items. Full recovery changes previously rejected long-input behavior and must be disclosed for that review.

Evaluation data and derived copies are private and used only to perform the authorized task. Do not train on, analyze beyond operational needs, reconstruct or redistribute them. The Full completion-based 30-day deletion deadline is **2026-11-15 03:02:32 UTC+8**; earlier tasks in a shared database can have earlier deadlines. Backups, caches and WAL/SHM copies count. This is a retention requirement, not a claim that a deletion job has already run or that an extension has been approved.
