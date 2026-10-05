import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

import preflight
from adaptive_evidence import api
from adaptive_evidence.remote_encoder import DashScopeEncoder
from test_remote_encoder import ENDPOINT, result


SETTINGS = {"MEMORY_API_KEY": "test-memory-key", "DASHSCOPE_API_KEY": "test-provider-key",
            "AE_EMBEDDING_URL": ENDPOINT, "AE_EMBEDDING_BACKEND": "dashscope", "AE_PLANNER": "0"}


class PreflightTests(unittest.TestCase):
    def test_missing_config_report_is_offline_and_has_no_secrets(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(httpx.Client, "post", side_effect=AssertionError("network")):
            report = preflight.configuration_report()
            self.assertFalse(report["ready_for_live_probe"])
            self.assertEqual(3, len(report["missing_environment"]))
        with patch.dict(os.environ, SETTINGS, clear=True), patch.object(httpx.Client, "post", side_effect=AssertionError("network")):
            report = preflight.configuration_report()
            self.assertTrue(report["ready_for_live_probe"])
            self.assertEqual("not_run", report["live_probe"])
            self.assertNotIn("test-provider-key", json.dumps(report))

    def test_bad_placeholder_or_local_backend_not_ready(self):
        for changes in ({"AE_EMBEDDING_URL": "https://{WorkspaceId}.example.test/"},
                        {"AE_EMBEDDING_BACKEND": "bge"}, {"AE_LOCAL_NO_AUTH": "1"}):
            with patch.dict(os.environ, {**SETTINGS, **changes}, clear=True):
                self.assertFalse(preflight.configuration_report()["ready_for_live_probe"])

    def test_live_probe_exercises_production_lifespan_with_mock_provider(self):
        requests = []
        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            return httpx.Response(200, json=result(len(body["input"]["texts"])))
        encoder = DashScopeEncoder("test", ENDPOINT, dimensions=64, transport=httpx.MockTransport(handler))
        with patch.dict(os.environ, SETTINGS, clear=True), patch.object(api, "encoder_from_env", return_value=encoder):
            report = preflight.live_probe()
        self.assertEqual("passed", report["live_probe"])
        self.assertTrue(encoder.client.is_closed)
        self.assertGreater(len(requests), 5)
        self.assertEqual(0, api.get_store.cache_info().currsize)
        self.assertEqual({"document", "query"}, {r["parameters"]["text_type"] for r in requests})

    def test_environment_file_is_data_not_shell_code(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            path = Path(tmp) / ".env"
            path.write_text('# comment\nMEMORY_API_KEY="literal-$(not-executed)"\nAE_PLANNER=0\n', encoding="utf-8")
            preflight.load_env(path)
            self.assertEqual("literal-$(not-executed)", os.environ["MEMORY_API_KEY"])


if __name__ == "__main__":
    unittest.main()
