# Frozen source release 0.68.0

Original author: Giorno-Banana. License: MIT. This is a candidate from the exact official 0.32.0 / 68.67 source; it has no new official score yet and does not replace the incumbent. Historical root code stays for provenance. Use the versioned source archive and SHA256 manifest.

The archive retains the tested API component version 0.32.0 intentionally. The release version is 0.68.0. Only non-document multiple-choice relevance ranking changes: original pretrained BAAI/bge-reranker-v2-m3, query-only, weight 0.25, original top6 anchors protected, at most64 scoring candidates. Returned evidence is always original source text. Add/Search make zero generative calls. Open/document paths preserve 0.32 behavior.

## Reproduce

Unzip context-weave-0.68.0-source.zip into an empty directory. Verify SHA256SUMS and the adjacent source manifest. Read REPRO_068.txt and RELEASE_RUNTIME.json. Install requirements-reranker.txt with the recorded Python/CUDA runtime. Obtain the original BAAI/bge-reranker-v2-m3 snapshot at revision953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e; the code verifies its file hashes. Set AE_RERANKER_MODEL to that local folder, AE_MODE=choice_m3_anchors and AE_CONTEXT_CHARS=24000. Configure authenticated Add/Search and text-embedding-v4,1024dimensions,batch10 using env.example; supply credentials privately. Run python -m uvicorn adaptive_evidence.api:app. Never include credentials in public files.

## Local comparison and limits

Fixed48 development+48holdout cases per available benchmark family, all original12 slices retained and separately gated. Six available families: LoCoMo, LongMemEval, BEAM, CLBench, PersonaMem v1 and v2. ScriptMem adapter and native scorer exist;96 selected cases are unavailable because original scripts were not released/available. They are excluded from end-to-end denominators.

Development final macro accuracy43.4028%->44.7917%; holdout46.5278%->47.2222%. All1152pairedgrades valid. Every family accuracy and available annotated retrieval/input recall passed nonregression; original12 slices also passed. These local scores are not official Smoke scores.

Research used the same local Qwen3.5-4B Q4_K_M for Answer and Judge under pinned llama.cpp CUDA, temperature0,seed20261021,no thinking,512outputtokens. Answer input limit4096 actual runtime tokens; native Judge4096 or11776 with full prompts/rubrics retained. A new replication fixed HF4096-vs-llama.cpp4101 token accounting using authoritative server templates/token IDs and exact-prefix clipping of final overflow. Earlier failed records were preserved, never repaired. Native publisher scoring is retained, with schema-constrained output. Exact raw inference caches were reused only for identical requests; parsed grades were regenerated.

This is historically exposed public data with a small shared Answer/Judge, not blind confirmatory data. Development and holdout paired bootstrap intervals include zero. The local gates justify a Smoke check, not a guaranteed official improvement. Only a strictly higher completed official Smoke may replace68.67. No new Full, account, or key is created by this release.
