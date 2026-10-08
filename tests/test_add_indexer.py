import concurrent.futures
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import closing

import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch

from adaptive_evidence.add_indexer import AddIndexerError, OpenRouterAddIndexer, candidates
from adaptive_evidence.api import app, get_store
from adaptive_evidence.core import MemoryStore
from test_contract import FakeEncoder


def response(chunks, **updates):
    body = {"model": "openai/gpt-4o-mini", "choices": [{"finish_reason": "stop",
            "message": {"content": json.dumps(chunks)}}],
            "usage": {"prompt_tokens": 23, "completion_tokens": 11}}
    body.update(updates)
    return body


def valid_handler(request):
    user = json.loads(json.loads(request.content)["messages"][1]["content"])
    chunks = {key: {"first": 0, "second": -1, "third": -1} for key in reversed(user)}
    return httpx.Response(200, json=response(chunks))


class AddIndexerTests(unittest.TestCase):
    def indexer(self, handler=valid_handler, **options):
        result = OpenRouterAddIndexer("fake-private-key", transport=httpx.MockTransport(handler),
                                      sleep=lambda _: None, **options)
        self.addCleanup(result.close)
        return result

    def test_actual_route_batch_order_and_verbatim_indexing(self):
        requests = []
        def handler(request):
            requests.append(request)
            body = json.loads(request.content)
            self.assertEqual("https://openrouter.ai/api/v1/chat/completions", str(request.url))
            self.assertEqual("Bearer fake-private-key", request.headers["Authorization"])
            self.assertEqual("openai/gpt-4o-mini", body["model"])
            self.assertEqual(["openai"], body["provider"]["only"])
            self.assertFalse(body["provider"]["allow_fallbacks"])
            self.assertTrue(body["provider"]["require_parameters"])
            self.assertEqual("json_schema", body["response_format"]["type"])
            return valid_handler(request)
        model = self.indexer(handler)
        texts = [f"Memory {i}: Luna moved to Berlin on May 7." for i in range(11)]
        indexed = model.enrich(texts)
        self.assertEqual(2, len(requests))
        self.assertEqual([text + "\n" + candidates(text)[0] for text in texts], indexed)
        self.assertEqual(11, model.usage()["validated_chunks"])
        self.assertEqual(46, model.usage()["prompt_tokens"])
        self.assertEqual([], model.enrich([]))

    def test_hallucinated_cross_chunk_and_duplicate_ids_rejected(self):
        values = [
            {"c0": {"first": "invented fact", "second": -1, "third": -1}, "c1": {"first": 0, "second": -1, "third": -1}},
            {"c0": {"first": 999, "second": -1, "third": -1}, "c1": {"first": 0, "second": -1, "third": -1}},
            {"c0": {"first": True, "second": -1, "third": -1}, "c1": {"first": 0, "second": -1, "third": -1}},
            {"c0": {"first": 0, "second": -1, "third": -1}},
        ]
        for value in values:
            with self.subTest(value=value):
                model = self.indexer(lambda _, v=value: httpx.Response(200, json=response(v)), max_attempts=1)
                with self.assertRaises(AddIndexerError):
                    model.enrich(["Alice lives in Paris", "Bob lives in Berlin"])

    def test_auth_redirect_and_wrong_model_fail_without_source_or_key_leak(self):
        for status in (401, 403, 302):
            with self.subTest(status=status):
                model = self.indexer(lambda _, s=status: httpx.Response(s, text="fake-private-key private-source"))
                with self.assertRaises(AddIndexerError) as error:
                    model.enrich(["private-source"])
                self.assertEqual(1, model.usage()["requests"])
                self.assertNotIn("fake-private-key", str(error.exception))
                self.assertNotIn("private-source", str(error.exception))
        model = self.indexer(lambda _: httpx.Response(200, json=response(
            [{"id": 0, "quotes": []}], model="a-different-model")), max_attempts=1)
        with self.assertRaises(AddIndexerError):
            model.enrich(["private-source"])

    def test_retry_budget_and_truncated_output_abort(self):
        count = iter((429, 503, 200))
        model = self.indexer(lambda r: valid_handler(r) if (s := next(count)) == 200 else httpx.Response(s))
        self.assertEqual(["Paris\nParis"], model.enrich(["Paris"]))
        self.assertEqual(3, model.usage()["requests"])
        limited = self.indexer(lambda _: httpx.Response(429), max_requests=1)
        with self.assertRaises(AddIndexerError):
            limited.enrich(["Paris"])
        self.assertEqual(1, limited.usage()["requests"])
        truncated = self.indexer(lambda _: httpx.Response(200, json=response([], choices=[
            {"finish_reason": "length", "message": {"content": "{}"}}])), max_attempts=1)
        with self.assertRaises(AddIndexerError):
            truncated.enrich(["Paris"])

    def test_index_cues_are_used_but_never_returned_and_retry_is_idempotent(self):
        class RecordingEncoder(FakeEncoder):
            documents = []
            def encode(self, texts, *, query=False):
                if not query:
                    self.documents.extend(texts)
                return super().encode(texts, query=query)
        with tempfile.TemporaryDirectory() as tmp:
            model = self.indexer()
            encoder = RecordingEncoder()
            store = MemoryStore(Path(tmp) / "m.db", encoder, add_indexer=model)
            payload = dict(user_id="alice", request_id="r", session_id="s",
                           messages=[{"role": "user", "content": "Luna likes the blue wand."}])
            with concurrent.futures.ThreadPoolExecutor(8) as pool:
                results = list(pool.map(lambda _: store.add(**payload), range(8)))
            self.assertEqual(1, sum(results))
            self.assertEqual(1, model.usage()["requests"])
            self.assertEqual("Luna likes the blue wand.\nLuna likes the blue wand.", encoder.documents[0])
            hit = store.search(user_id="alice", query="Luna wand", top_k=1)[0]
            self.assertEqual("[user] Luna likes the blue wand.", hit["content"])
            self.assertNotIn("index_text", hit)
            self.assertEqual([], store.search(user_id="bob", query="Luna wand"))
            with self.assertRaises(ValueError):
                MemoryStore(Path(tmp) / "m.db", encoder)

    def test_failed_add_is_atomic_and_api_returns_sanitized_503(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = self.indexer(lambda _: httpx.Response(503, text="private-source fake-private-key"), max_attempts=1)
            store = MemoryStore(Path(tmp) / "m.db", FakeEncoder(), add_indexer=model)
            app.dependency_overrides[get_store] = lambda: store
            self.addCleanup(app.dependency_overrides.clear)
            with patch.dict("os.environ", {"MEMORY_API_KEY": "synthetic-api-key"}):
                client = TestClient(app)
                result = client.post("/add", headers={"X-Api-Key": "synthetic-api-key"}, json={
                    "user_id": "u", "request_id": "r", "session_id": "s",
                    "messages": [{"role": "user", "content": "private-source"}]})
                self.assertEqual(503, result.status_code)
                self.assertNotIn("private-source", result.text)
                self.assertEqual("openai/gpt-4o-mini", client.get("/health").json()["add_llm"])
            with closing(store.connect()) as db:
                self.assertEqual(0, db.execute("SELECT count(*) FROM requests").fetchone()[0])
                self.assertEqual(0, db.execute("SELECT count(*) FROM sources").fetchone()[0])

    def test_span_selection_preserves_whitespace_unicode_and_length(self):
        text = ("Maya  Chen\tvisit cafe\u0301 and café. 日期：十一月十八日。 " * 30)[:980]
        spans = candidates(text)
        self.assertEqual(text, "".join(spans))
        self.assertTrue(all(0 < len(s) <= 96 and s in text for s in spans))
        model = self.indexer()
        self.assertEqual([text + "\n" + spans[0]], model.enrich([text]))

    def test_failed_later_batch_resumes_after_restart_and_remains_invisible(self):
        state = {"fail": True, "calls": []}
        def handler(request):
            data = json.loads(json.loads(request.content)["messages"][1]["content"])
            text = data["c0"]["0"]
            state["calls"].append(text)
            if text.startswith("Memory 8") and state["fail"]:
                return httpx.Response(503)
            return valid_handler(request)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.db"
            model = self.indexer(handler, max_attempts=1)
            store = MemoryStore(path, FakeEncoder(), add_indexer=model)
            payload = dict(user_id="u", request_id="r", session_id="s", messages=[
                {"role": "user", "content": f"Memory {i}: unique fact."} for i in range(16)])
            with self.assertRaises(AddIndexerError):
                store.add(**payload)
            self.assertEqual([], store.search(user_id="u", query="fact"))
            with self.assertRaises(ValueError):
                store.add(**{**payload, "session_id": "changed"})
            state["fail"] = False
            restarted = MemoryStore(path, FakeEncoder(), add_indexer=model)
            self.assertEqual(16, restarted.add(**payload))
            self.assertEqual(3, len(state["calls"]))
            self.assertEqual(0, restarted.add(**payload))
            with closing(restarted.connect()) as db:
                self.assertEqual(0, db.execute("SELECT COUNT(*) FROM add_batches").fetchone()[0])
                self.assertEqual(0, db.execute("SELECT COUNT(*) FROM pending_adds").fetchone()[0])
            # Same request in a different user scope must call the model again.
            restarted.add(**{**payload, "user_id": "other"})
            self.assertEqual(5, len(state["calls"]))

    def test_embedding_failure_reuses_cached_llm_and_purge_removes_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = self.indexer()
            encoder = FakeEncoder()
            encoder.fail = True
            store = MemoryStore(Path(tmp) / "m.db", encoder, add_indexer=model)
            payload = dict(user_id="u", request_id="r", session_id="s",
                           messages=[{"role": "user", "content": "Remember Maya  Chen."}])
            with self.assertRaises(RuntimeError):
                store.add(**payload)
            self.assertEqual(1, model.usage()["requests"])
            encoder.fail = False
            store.add(**payload)
            self.assertEqual(1, model.usage()["requests"])
            encoder.fail = True
            with self.assertRaises(RuntimeError):
                store.add(**{**payload, "request_id": "r2"})
            store.purge_user("u")
            with closing(store.connect()) as db:
                for table in ("pending_adds", "add_batches", "sources", "requests", "chunks"):
                    self.assertEqual(0, db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0])

    def test_failure_log_omits_secret_and_source(self):
        model = self.indexer(lambda _: httpx.Response(401, text="fake-private-key private-source"))
        with self.assertLogs("adaptive_evidence.add_indexer", level="WARNING") as capture:
            with self.assertRaises(AddIndexerError):
                model.enrich(["private-source"])
        self.assertIn("status=401", "".join(capture.output))
        self.assertNotIn("fake-private-key", "".join(capture.output))
        self.assertNotIn("private-source", "".join(capture.output))


if __name__ == "__main__":
    unittest.main()
