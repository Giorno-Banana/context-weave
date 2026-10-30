# SourceTrail 0.32.0 submission materials

System: SourceTrail; team: Qhc‘s team; category: Open-source Methods (academic); evaluation type: Textual Memory. Original author: 王子铭 / Giorno-Banana, MIT. Contact details are maintained privately with the organizer; keys are supplied only through its controlled credential workflow.

## Identity and evidence

Full task: `teval_6c99618ea0916224`, run label `sourcetrail-v320-full-20261014`, succeeded, 9,602/9,602, score52.79. Start 2026-10-14 17:26:13, completion 2026-10-16 03:02:32 (UTC+8). [Sanitized aggregate record](sourcetrail-0.32.0-official-full.json). Matching SourceTrail Smoke: `teval_a35e6262923680e0`, succeeded,63.68. This Full is not the historical best Smoke68.67.

The original fixed source commit is `e84af580a3a9a21f1eab6328d41e8b93bb52552e`. The exact terminal Full source is `releases/sourcetrail-0.32.0-full/` and `sourcetrail-0.32.0-full-recovery-source.zip`, SHA256 `4cded88da43103edf9b656c22ca6ecc4e0a024e696eb74e65347af06c1e7a6f6`. Use the immutable Git commit containing this disclosure (not a moving branch) when providing the updated material reference. [File hashes](sourcetrail-0.32.0-full-source.manifest.json) prove the restored tree matches the frozen terminal source. No claim is made that the recovery archive was publicly available before the Full.

## Registered service

Verified with the SourceTrail account's `/access/version-endpoints` on 2026-10-31:

* Add: `https://wzm.tail36b9f2.ts.net/add`
* Search: `https://wzm.tail36b9f2.ts.net/search`
* Authentication: `X-Api-Key` with the separately supplied Memory System Key. Never put either key in the URL, repository, email or screenshots.
* Proposed/evaluated concurrency: Add16 and Search16; top_k100; context budget24,000 characters. This is a configured concurrency declaration, not a throughput/SLA guarantee.
* Single Uvicorn worker, FastAPI, SQLite WAL, publicly reachable HTTPS through the participant's existing reverse proxy. See [runtime limits](OPERATIONS.md).

Add is synchronous: success is returned only after atomic persistence and immediate searchability; successful retries with the same request_id/payload are idempotent, and conflicting payloads are rejected. Search scopes only to the supplied user_id; session IDs organize source records. Returned bodies are original-source evidence, not generated answers. Source fidelity, timestamp/role retention, authentication and isolation are tested in the frozen suite.

## Method, recovery and integrity

The [provenance document](releases/sourcetrail-0.32.0-full/PROVENANCE.md) records references, original authors, independent implementation and changes through0.32; [FULL_RECOVERY.md](docs/FULL_RECOVERY.md) records the three changed/added files during Full recovery. No GPT component or local generative model is enabled in this memory service. The configured embedding is text-embedding-v4,1,024dimensions,batch10; no model swap is claimed or performed.

The participant-facing API confirms successful Full execution but does not expose sufficient evidence to certify organizer approval, absence of platform-side duplicate results, or conformity of its pipeline/dataset hashes to the current publication baseline. Those are organizer review items. Full recovery changes previously rejected long-input behavior and must be disclosed for that review.

Evaluation data and derived copies are private and used only to perform the authorized task. Do not train on, analyze beyond operational needs, reconstruct or redistribute them. The Full completion-based 30-day deletion deadline is **2026-11-15 03:02:32 UTC+8**; earlier tasks in a shared database can have earlier deadlines. Backups, caches and WAL/SHM copies count. This is a retention requirement, not a claim that a deletion job has already run or that an extension has been approved.
