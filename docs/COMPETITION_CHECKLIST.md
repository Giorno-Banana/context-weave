# Current-rule checklist (verified2026-10-31, UTC+8)

Sources: [participation rules](https://agentmemories.ai/rules), [API guide](https://agentmemories.ai/api-guide), [user documentation](https://agentmemories.ai/zh-cn/docs). Material deadline:2026-10-31 23:59UTC+8. Evaluation stop:2026-11-04 23:59UTC+8. This is a participant audit, not organizer certification.

| Requirement | Evidence / remaining verification |
|---|---|
| System/version/category/team | SourceTrail0.32.0, Textual, Open-source Methods; current teamQhc‘s team; account fields updated separately |
| Contact and team details | Private organizer records must identify current contact; do not infer contact identity from historical source copyright |
| Public repository and fixed commit | Original fixed commit plus unchanged terminal recovery archive, readable tree and per-file hashes; use the immutable disclosure commit |
| Model requirements | text-embedding-v4,1024dimensions; no generative LLM component in Add/Search; external evaluator owns Answer |
| Method and all changes | PROVENANCE.md through0.32 plus FULL_RECOVERY.md; recovery explicitly identified as a behavioral change |
| Authentication and live capacity | SUBMISSION.md and OPERATIONS.md; original registered root endpoints, X-Api-Key, declared16/16, top_k100 |
| Contract and isolation | Frozen synthetic suite; source-only evidence, atomic/idempotent Add, user_id isolation, roles/timestamps, stable IDs and budgets |
| Matching account Smoke | Official eligibility API reports passed, teval_a35e6262923680e0,63.68 |
| Full completion | Official GET succeeded9,602/9,602, teval_6c99618ea0916224,52.79; platform-side duplicate/hash completeness requires organizer review |
| Terminal source vs originally declared source | Recovery changes3files; disclosed, not silently called identical; organizer acceptance remains unverified |
| Active service/source identity | Verify exact terminal source hashes, private profile hash and recovery health marker after any restoration;2xxalone is insufficient |
| Secrets and official-data exclusion | Publication allowlist and private-value scan; no official inputs/answers/databases or private keys included |
| Data retention | Delete data/derived copies within30days; Full deadline2026-11-15 03:02:32UTC+8; shared DB may have earlier tasks; actual scheduled/completed purge must be tracked privately |
| Public display | Framework SourceTrail; public method/code/result aggregates only; private contact/teacher/key material excluded from this repository |
| Final publication review | Successful Full is necessary but insufficient. Organizer must verify version, pipeline/dataset hashes, complete unique results, recovery acceptance and publication eligibility |

Do not claim fully reviewed compliance until remaining organizer/retention/contact checks are resolved. Do not rerun Full, replace the evaluation source with a later experiment, or treat Smoke/local scores as Full.
