# Context Weave — completed 0.17.1 Smoke

Official Textual Smoke **59.99**, **46/46** completed in **50m 25s**, task `teval_5fab8ab3aa2df587`. Completed `2026-10-10T14:00:46+08:00`. The previous best was **61.77** (0.6.1); change **-1.78**. The target of at least 70 is not met.

This run used local Qwen3.5-4B runtime042, text-embedding-v4, Add16/Search16. No Full or new OpenRouter calls occurred. Frozen source, active runtime, external model files and deployment profile were rechecked after evaluation. [Aggregate result](context-weave-0.17.1-official-smoke.json).

The source archive remains unchanged at commit `553881a93314a32ecd3edacc173358d269252b36`, SHA256 `6e9d1747d5e09f2058ed501549b393c22da73b65412442c35c75cf25922f721e`. The pre-run documentation below is historical; this dated result supersedes its pending-score status.

## Historical pre-run documentation

# Context Weave 0.17.1

Search restores continuity within original messages: after hybrid retrieval and local evidence selection, overlapping selected chunks are merged and ordered by original source offset. Disconnected spans keep their gaps. Different messages retain first-hit relevance order. The selected source text is preserved without adding unselected parent content or generating answers.

Add persists original messages. Local Qwen3.5-4B selects exact source spans for optional indexing weight. If optional local cue selection fails after bounded retries, unchanged original chunks are indexed. This changed Add identity requires a fresh database. Search remains scoped by user and original source.

Actual models: Bailian text-embedding-v4,1024 dimensions; local Qwen3.5-4B with supervised runtime0.4.2 for Add cues and Search planning. Frozen hashes are in local_runtime/MODEL_MANIFEST.json. No OpenRouter calls are enabled. The participant reports organizer permission for a local-model exception; actual models are disclosed here without independently certifying eligibility.

Public validation:50 reused development questions remain38/50 in both arms, with0 wins and0 losses under published AML prompts and a local4B reader/judge. A separately generated24-question long-source panel improves16 to20 correct, with4 wins and0 losses using deterministic identifier checking. These are local proxies, not official scores. Best prior completed official Smoke is61.77 (0.6.1);0.10.0 scored60.31. Official0.17.1 is pending. See EXPERIMENT.json for limitations and checks.

## Reproduce

Use Python3.10 and requirements.txt. Configure credentials privately and settings from env.local.example. Start the frozen local runtime on loopback18095, then API18098 with a fresh database. Add/Search require the configured token. Run `python -m unittest discover -s tests -v`. Keep source, configuration and runtime unchanged during evaluation.

The versioned archive is authoritative; older loose repository files describe earlier releases. The archive excludes credentials, model weights, stored memories and benchmark answers. Source is MIT licensed; dependencies and models retain their licenses. Source continuity and local Add fallback are original changes. Earlier research attribution is in PROVENANCE.md.
