# MemMachine recall exploratory Smoke

This release starts from the exact official Context Weave 0.32.0 source (historical Smoke 68.67). Its only retrieval change preserves the baseline Search stream as an unchanged prefix and appends exact previous-1/next-2 raw episodes within the same Add/session using spare Search character budget. The MemMachine paper motivates this bounded episode window; the implementation is independent. Summaries, profile extraction, additional rerankers, Answer prompts and agent logic are unchanged.

The release label is 0.69.0. Python source metadata remains 0.32.0 to preserve the exact tested source identities; runtime mode is explicitly `memmachine_recall`. The versioned archive is the authoritative source for this release, rather than the historical repository root.

The fixed development retrieval study completed 288 cases and 68 source tests. LoCoMo Search recall increased from 76.5248% to 81.8440%, complete evidence hits 30 to 33, with three gains and no losses. BEAM and LongMemEval tied. All 4096-token packed Answer inputs were unchanged. Final-answer gains, holdout gains and official gains have not been established.

The user explicitly authorized one exploratory Textual Smoke as a one-time exception to the local score gates. The permanent gates remain unchanged, Full is not authorized, and this release cannot automatically replace the incumbent.

The service uses the existing production embedding settings, exact raw sources, authentication, and a 24000-character Search budget. Credentials, datasets, generated answers, private profiles and databases are excluded from the source archive.
