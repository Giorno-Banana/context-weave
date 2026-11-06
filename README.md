# SourceTrail 0.32.0 — completed Textual Full disclosure

For release reproduction and the scope of the legacy research package, see the [source guide](catalog/REPRODUCTION.md).

SourceTrail provides a text memory Add/Search service. The current submission team is **Qhc‘s team**; [MIT license](LICENSE). Older documentation uses other submission aliases and contacts; those describe historical registrations, not this Full submission.

The official Full task `teval_6c99618ea0916224` completed **9,602/9,602** evaluations with **52.79** on 2026-10-16 (UTC+8). A fresh official GET confirmed success on 2026-10-31. Full success does not establish organizer approval or public-list eligibility. The matching SourceTrail-account prerequisite Smoke scored **63.68**; the historical **68.67** best Smoke belongs to a different account and must not be presented as this Full score.

## Fixed source and recovery disclosure

* Original 0.32 source: commit [`e84af580a3a9a21f1eab6328d41e8b93bb52552e`](https://github.com/Giorno-Banana/context-weave/tree/e84af580a3a9a21f1eab6328d41e8b93bb52552e), [original archive](context-weave-0.32.0-source.zip).
* Exact terminal Full source: [readable frozen tree](releases/sourcetrail-0.32.0-full), [unchanged recovery archive](sourcetrail-0.32.0-full-recovery-source.zip), [SHA-256 file manifest](sourcetrail-0.32.0-full-source.manifest.json).
* Recovery archive SHA-256: `4cded88da43103edf9b656c22ca6ecc4e0a024e696eb74e65347af06c1e7a6f6`.
* The current public frozen source and recovery archive already include the long-input embedding compatibility repair used at Full completion. [Recovery explanation](docs/FULL_RECOVERY.md) records the historical changes from the original 0.32 source while resuming the same Full task. Organizer acceptance of that change must be verified; this repository does not assert that a successful task waives version consistency review.

Add stores original messages, roles, source order and timestamps. Search uses text-embedding-v4 (1,024 dimensions), dense/lexical reciprocal-rank fusion and deterministic original-source packing with a 24,000-character budget and at most top_k=100 records. Add/Search make **zero generative LLM calls**. Embedding API calls remain enabled. The external AML evaluator owns final Answer and grading.

## Reproduce and review

Use [OPERATIONS.md](OPERATIONS.md) for exact-source startup and private configuration, [SUBMISSION.md](SUBMISSION.md) for interface parameters and source identity, [version change history](releases/sourcetrail-0.32.0-full/PROVENANCE.md), and the [requirements checklist](docs/COMPETITION_CHECKLIST.md). Frozen archives retain historical documentation and container labels for evidentiary integrity; use the current guide rather than their inherited 0.28 Compose template.

Repository-root Python code and historical experiments are **not** the terminal Full implementation. Do not run the root service to reproduce Full. No credentials, official request bodies, private evaluation memories, questions, answers, databases or model weights are included in this disclosure. Private account/contact updates and organizer review are separate from the code license.
