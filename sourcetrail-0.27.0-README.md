# SourceTrail 0.27.0 release

The exact source for the SourceTrail submission is in `sourcetrail-0.27.0-source.zip`; repository-root code can represent another version. Extract the archive and follow its README.md and OPERATIONS.md.

Archive SHA-256: `18b0e6b5706b43572b8a61ef674bb44285c9a5890eaf454d8f7bbdbd89bed5f8`. Per-file checksums are included in the archive.

# SourceTrail 0.27.0

Requested division: Open-source Methods (the current application form labels its non-industry option Academic leaderboard). Evaluation type: Textual Memory.

Original code author/copyright: 王子铭 (Giorno-Banana); MIT. SourceTrail is the submission name for this frozen Context Weave 0.27.0 implementation. Method sources, original authors and historical changes are retained in PROVENANCE.md. This release removes generative Add indexing and ReFind-inspired Search planning; it retains raw-source hybrid retrieval and neighboring source windows. No upstream implementation or prompt was copied for this change.

Add LLM: none. Search LLM: none. Answer generation is owned/configured by the external AML evaluator. Embedding: text-embedding-v4, 1024 dimensions, batches of up to 10. The no-generative-LLM configuration and its embedding provider are disclosed for official eligibility review; this document does not claim an exemption from the non-industry model rule.

The publicly reachable synchronous Add/Search service uses FastAPI, SQLite WAL, X-Api-Key and HTTPS. Proposed platform concurrency: Add 16 / Search 16. Request-id idempotency, user isolation, atomic Add persistence and immediate search after successful Add are supported. Use a new database for reproduction and preserve any existing evaluation database. Reproduction and run commands are in README.md and OPERATIONS.md; env.example contains only placeholders.

Validation: 35 automated tests, live synthetic embedding-provider preflight, and 16 deployed HTTP checks covering authentication, idempotency, conflicts, immediate retrieval, isolation and concurrent requests. Synthetic checks are not official scores or Full-throughput measurements. There is no official score for this release.

All executable source and configuration templates match the frozen deployed 0.27.0 package byte-for-byte. Only README.md, OPERATIONS.md and this submission description have been updated for the new submission name. SHA256SUMS.json covers the published release files.
