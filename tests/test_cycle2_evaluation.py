import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import evaluate_retrieval
from test_contract import FakeEncoder


class CountedEncoder(FakeEncoder):
    calls = 0

    def encode(self, texts, *, query=False):
        self.calls += 1
        return super().encode(texts, query=query)


class Cycle2EvaluationTests(unittest.TestCase):
    def test_new_backend_manifest_resume_and_model_change_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "fixture"
            data.mkdir()
            conversation = {"sample_id": "c1", "speaker_a": "Alice", "speaker_b": "Bob",
                            "sessions": [{"session_index": 0, "date_time": "2026-01-01",
                                          "messages": [{"dia_id": "d1", "speaker": "Alice", "role": "user", "text": "My home is Paris."}]}]}
            question = {"sample_id": "c1", "qa_id": "q1", "category": "fact", "question": "Where is my home?", "evidence": ["d1"]}
            (data / "conversations.jsonl").write_text(json.dumps(conversation) + "\n", encoding="utf-8")
            (data / "questions.jsonl").write_text(json.dumps(question) + "\n", encoding="utf-8")
            output = root / "out"
            env_file = root / "private.env"
            env_file.write_text("AE_EMBEDDING_BACKEND=dashscope\nAE_PLANNER=0\n", encoding="utf-8")
            argv = ["evaluate_retrieval.py", "--env-file", str(env_file), "--data-dir", str(data), "--output", str(output), "--modes", "hybrid_window"]
            encoder = CountedEncoder()
            with patch.dict(os.environ, {"AE_EMBEDDING_BACKEND": "dashscope"}), patch("sys.argv", argv), \
                    patch.object(evaluate_retrieval, "encoder_from_env", return_value=encoder), \
                    patch.object(evaluate_retrieval, "add_indexer_from_env", return_value=None) as indexer_factory, \
                    contextlib.redirect_stdout(io.StringIO()):
                evaluate_retrieval.main()
                self.assertEqual("0", os.environ["AE_PLANNER"])
                calls = encoder.calls
                evaluate_retrieval.main()
                self.assertEqual(calls, encoder.calls)
                metrics = (output / "retrieval_metrics.jsonl").read_text(encoding="utf-8").splitlines()
                self.assertEqual(1, len(metrics))
                self.assertTrue(json.loads(metrics[0])["all_hit"])
                manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(encoder.identity, manifest["encoder_identity"])
                self.assertEqual("dashscope", manifest["embedding_backend"])
                self.assertFalse(manifest["official_score"])
                self.assertIsNone(manifest["add_indexer_identity"])
                changed_indexer = Mock(identity="changed-add-indexing-profile")
                indexer_factory.return_value = changed_indexer
                with self.assertRaisesRegex(ValueError, "different frozen protocol"):
                    evaluate_retrieval.main()
                changed_indexer.enrich.assert_not_called()
                changed_indexer.close.assert_called_once()
                indexer_factory.return_value = None
                encoder.identity = "changed-vector-space"
                with self.assertRaisesRegex(ValueError, "different frozen protocol"):
                    evaluate_retrieval.main()


if __name__ == "__main__":
    unittest.main()
