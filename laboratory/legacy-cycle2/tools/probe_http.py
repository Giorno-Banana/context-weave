"""Exercise a running Add/Search API with synthetic data, never official jobs.

Writes isolated probe users and can verify their persistence after a restart.
Only MEMORY_API_KEY is sent to the target; provider keys remain local.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import statistics
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from preflight import load_env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recover-from", type=Path)
    args = parser.parse_args()
    url = urlsplit(args.base_url)
    if (url.username or url.password or url.query or url.fragment or not url.hostname
            or url.scheme not in {"http", "https"}
            or (url.scheme == "http" and url.hostname not in {"127.0.0.1", "localhost", "::1"})):
        parser.error("Use HTTPS, or loopback HTTP, without URL credentials, query or fragment")
    load_env(args.env_file)
    key = os.getenv("MEMORY_API_KEY", "")
    if not key:
        parser.error("MEMORY_API_KEY is required")
    fixture = "network-probe-" + uuid.uuid4().hex
    if args.recover_from:
        previous = json.loads(args.recover_from.read_text(encoding="utf-8-sig"))
        if previous.get("status") != "passed":
            parser.error("Recovery requires a successful earlier probe")
        fixture = previous["fixture_id"]
    base = args.base_url.rstrip("/")
    headers = {"X-Api-Key": key}
    checks = []
    timings = []
    report = {"base_url": base, "fixture_id": fixture, "transport": "network HTTP",
              "phase": "recover" if args.recover_from else "write",
              "synthetic_data_only": True, "official_smoke": False, "official_full": False}

    def check(condition, stage):
        if not condition:
            raise RuntimeError(stage)
        checks.append(stage)

    with httpx.Client(timeout=60, follow_redirects=False) as client:
        def request(path, body=None, auth=headers):
            before = time.perf_counter()
            if body is None:
                response = client.get(base + path)
            else:
                response = client.post(base + path, json=body, headers=auth)
            timings.append({"path": path, "status": response.status_code,
                            "ms": (time.perf_counter() - before) * 1000})
            return response

        def query(suffix, text, expected, forbidden=None, auth=headers):
            response = request("/search", {"user_id": fixture + suffix,
                               "query": text, "top_k": 1, "options": ["train", "ferry"]}, auth)
            check(response.status_code == 200, "search" + suffix)
            hits = response.json()["data"]
            check(len(hits) == 1 and expected in hits[0]["content"]
                  and (forbidden is None or forbidden not in hits[0]["content"]),
                  "evidence_and_scope" + suffix)

        try:
            health = request("/health")
            check(health.status_code == 200, "health")
            report["health"] = health.json()
            if args.recover_from:
                query("-a", "Where did I move?", "Berlin")
                query("-b", "What is my travel preference?", "ferry", "train")
                check(True, "recovered_after_process_restart")
            else:
                a = {"request_id": "r1", "user_id": fixture + "-a", "session_id": "s1",
                     "messages": [{"role": "user", "content": "My travel preference is train. I live in Paris."}]}
                b = {**a, "user_id": fixture + "-b",
                     "messages": [{"role": "user", "content": "My travel preference is ferry. I live in Tokyo."}]}
                check(request("/add", a, {}).status_code == 401, "missing_auth")
                check(request("/add", a, {"X-Api-Key": "invalid-probe-key"}).status_code == 401, "wrong_auth")
                for body in (a, b):
                    response = request("/add", body)
                    check(response.status_code == 200 and response.json() == {
                        "success": True, "request_id": body["request_id"],
                        "user_id": body["user_id"], "session_id": body["session_id"]}, "add_ids")
                check(request("/add", a).status_code == 200, "idempotent_retry")
                conflict = {**a, "messages": [{"role": "user", "content": "Conflicting retry."}]}
                check(request("/add", conflict).status_code == 409, "conflict")
                query("-a", "What is my travel preference?", "train", "ferry")
                query("-b", "What is my travel preference?", "ferry", "train", {"Authorization": "Bearer " + key})
                empty = request("/search", {"user_id": fixture + "-empty", "query": "home", "top_k": 1})
                check(empty.status_code == 200 and empty.json() == {"data": []}, "empty_scope")
                invalid = request("/search", {"user_id": fixture + "-a", "query": "home", "top_k": 0})
                check(invalid.status_code == 422 and "home" not in invalid.text, "private_validation_error")
                update = {**a, "request_id": "r2", "session_id": "s2",
                          "messages": [{"role": "user", "timestamp": 1767225600000, "content": "I moved to Berlin."}]}
                check(request("/add", update).status_code == 200, "streaming_add")
                query("-a", "Where did I move?", "Berlin", auth={"Authorization": "Token " + key})
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(query, "-a", "Where did I move?", "Berlin"),
                               pool.submit(query, "-b", "What is my travel preference?", "ferry", "train")]
                    for future in futures:
                        future.result()
                check(True, "two_concurrent_searches")
            report["status"] = "passed"
        except Exception as error:
            report.update(status="failed", error_type=type(error).__name__)
            if isinstance(error, RuntimeError):
                report["failed_check"] = str(error)
    report["checks"] = checks
    report["http_requests"] = len(timings)
    report["timings"] = timings
    successful_searches = [t["ms"] for t in timings if t["path"] == "/search" and t["status"] == 200]
    report["median_search_ms"] = statistics.median(successful_searches) if successful_searches else None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "timings"}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
