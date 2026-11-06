# Run the terminal Full source

These instructions supplement the frozen source without modifying it. Use Python3.10–3.12 with SQLite FTS5. Install the pinned requirements from the exact release tree in a fresh virtual environment.

```powershell
cd releases/sourcetrail-0.32.0-full
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item env.example .env
# Edit .env privately: MEMORY_API_KEY, DASHSCOPE_API_KEY, AE_EMBEDDING_URL.
# Use the participant's text-embedding-v4 provider endpoint, not a chat endpoint.
# Set AE_DATABASE to a fresh isolated absolute path; never reuse the official DB for tests.
.\start_local.ps1 -Port 18532 -PythonPath .\.venv\Scripts\python.exe -EnvFile @('.env')
```

Keep `AE_EMBEDDING_BACKEND=dashscope`, dimensions1024,batch10, `AE_MODE=query_document_evidence`, `AE_CONTEXT_CHARS=24000`. The launcher forces generative Add/Search flags off. API keys are different credentials: the service needs the participant Memory System Key and embedding provider key; an AML Eval Key is not needed by the memory implementation.

For an offline synthetic regression run from this release directory:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

71 frozen tests passed at recovery. The compatibility test also loads the supplied sibling directory `../context-weave-v320-evidence-budget-20261014/`; keep that original tree beside the recovery tree. The unchanged standalone recovery ZIP does not include this sibling; extract the original archive into that sibling directory if using ZIPs rather than the Git checkout. Reproduction test results are recorded separately from historical tests and scores. `python preflight.py --env-file .env --live` sends synthetic data to the configured paid embedding provider and uses temporary isolated storage; run only under the operator's authorized provider budget. Do not send or inspect official evaluation records in diagnostics.

## API and capacity

The application provides authenticated POST `/add` and `/search`, plus unauthenticated GET `/health`. Configure the base URL and any HTTPS access in the independent runtime. The expected terminal-source health marker is `embedding_length_recovery=provider-confirmed-lossless-v1`, version0.32.0, embedding text-embedding-v4, zero generative calls, raw_source Add and query_document_evidence Search. A2xx health check alone does not prove the correct source.

Successful Add returns success=true plus the exact request_id/user_id/session_id. Search returns a JSON object containing ranked data records with stable nonempty id/content, at most requested top_k (maximum100); an empty result is data=[]. Timestamp units are source Unix milliseconds. Authentication failures return401; validation422; duplicate-payload conflicts409; embedding failures503 with Retry-After. Access logs are disabled; the application records only path/status/duration and sanitized provider categories, not request bodies or IDs.

Declared Add/Search concurrency is16/16. Upstream embedding batches are serialized, so actual latency depends on input length and provider limits. Historical configuration uses60s per upstream attempt,3 attempts and no fixed process request budget; these are upstream limits, not an end-to-end API timeout. Provider-confirmed length recovery may issue extra segment calls. The organizer currently permits up to30minutes per Add/Search request; the operator must provision proxy timeouts and capacity accordingly, without implying the service enforces a30minute internal deadline. Maintain one Uvicorn worker and persistent writable storage. Do not promise a measured throughput SLA.

## Persistence, isolation and retention

Never change official source/profile or clear data during an active/uncertain evaluation. Preserve pending requests and idempotency state during restarts. Use separate databases for local tests; never copy official data into a public artifact.

Limit access to necessary operators. Delete official data and derived copies within30days after each task ends unless the organizer has given prior written permission. This includes SQLite main/WAL/SHM files, vector/cache backups and copied evaluation bodies. Data from multiple tasks follows the earliest applicable retention deadline. Full deadline:2026-11-15 03:02:32 UTC+8. Retain only sanitized operational counts, hashes and aggregate score evidence where permitted. Arrange an actual bounded deletion procedure before that deadline; this document is not an automated purge or a completed-deletion attestation.

The release archive retains its original container templates and file identities. Use the launcher above for this independent reproduction workflow.
