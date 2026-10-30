import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import httpx
import numpy as np

from adaptive_evidence.core import MemoryStore
from adaptive_evidence.remote_encoder import DashScopeEncoder, EmbeddingError, lossless_segments

ENDPOINT = 'https://embedding.example.test/api/v1/services/embeddings/text-embedding/text-embedding'


def vectors(texts):
    return {'output': {'embeddings': [
        {'text_index': i, 'embedding': [float(i == j) for j in range(64)]}
        for i in range(len(texts))]}}


def too_long():
    return httpx.Response(400, json={'code': 'InvalidParameter',
        'message': '<400> InternalError.Algo.InvalidParameter: Range of input length should be [1, 33000]'})


class EmbeddingLengthRecoveryTests(unittest.TestCase):
    def encoder(self, handler, **kwargs):
        encoder = DashScopeEncoder('synthetic-secret', ENDPOINT, dimensions=64,
            transport=httpx.MockTransport(handler), sleep=lambda _: None, **kwargs)
        self.addCleanup(encoder.close)
        return encoder

    def test_successful_requests_and_existing_database_remain_compatible(self):
        old_path = Path(__file__).resolve().parents[2] / 'context-weave-v320-evidence-budget-20261014/adaptive_evidence/remote_encoder.py'
        spec = importlib.util.spec_from_file_location('original_remote_encoder', old_path)
        old = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)
        calls = []
        def handler(request):
            body = json.loads(request.content)
            calls.append(body)
            return httpx.Response(200, json=vectors(body['input']['texts']))
        before = old.DashScopeEncoder('synthetic-secret', ENDPOINT, dimensions=64,
                                     transport=httpx.MockTransport(handler))
        self.addCleanup(before.close)
        after = self.encoder(handler)
        self.assertEqual(before.identity, after.identity)
        self.assertTrue(np.array_equal(before.encode(['one', 'two'], query=True),
                                       after.encode(['one', 'two'], query=True)))
        self.assertEqual(calls[-2], calls[-1])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'synthetic.db'
            store = MemoryStore(path, before)
            store.add(request_id='r', user_id='synthetic-u', session_id='s',
                      messages=[{'role': 'user', 'content': 'Synthetic archive is in Paris.'}])
            restored = MemoryStore(path, after)
            self.assertIn('Paris', restored.search(user_id='synthetic-u', query='archive')[0]['content'])

    def test_length_recovery_preserves_unicode_all_text_role_and_vector_shape(self):
        original = ('合成档案🙂 archive\n' * 5000) + ' ending-marker'
        accepted = []
        def handler(request):
            body = json.loads(request.content)
            self.assertEqual('query', body['parameters']['text_type'])
            texts = body['input']['texts']
            if any(len(t.encode('utf-8')) > 33000 for t in texts):
                return too_long()
            accepted.extend(texts)
            return httpx.Response(200, json=vectors(texts))
        encoder = self.encoder(handler)
        result = encoder.encode([original], query=True)
        self.assertEqual(original, ''.join(accepted))
        self.assertTrue(all(len(t.encode('utf-8')) <= 7680 for t in accepted))
        self.assertEqual((1, 64), result.shape)
        self.assertAlmostEqual(1, float(np.linalg.norm(result)), places=6)

    def test_failed_batch_isolates_long_item_without_losing_short_items(self):
        accepted = []
        def handler(request):
            texts = json.loads(request.content)['input']['texts']
            if any(len(t) > 33000 for t in texts):
                return too_long()
            accepted.extend(texts)
            return httpx.Response(200, json=vectors(texts))
        texts = ['first', 'long synthetic ' * 3000, 'last']
        result = self.encoder(handler).encode(texts)
        self.assertEqual((3, 64), result.shape)
        self.assertEqual(''.join(texts), ''.join(accepted))

    def test_unrelated_400_remains_fail_closed_and_private(self):
        for body in ({'code': 'InvalidParameter', 'message': 'synthetic-secret private-input'},
                     {'code': 'synthetic-secret', 'message': 'Range of input length should be [1, 33000]'},
                     {'code': 'DataInspectionFailed', 'message': 'private-input'}):
            encoder = self.encoder(lambda _: httpx.Response(400, json=body))
            with self.assertRaises(EmbeddingError) as ctx:
                encoder.encode(['private-input'])
            self.assertNotIn('private-input', str(ctx.exception))
            self.assertNotIn('synthetic-secret', str(ctx.exception))
            self.assertEqual(1, encoder.usage()['requests'])

    def test_recovery_is_bounded_by_request_budget(self):
        def handler(request):
            texts = json.loads(request.content)['input']['texts']
            return too_long() if len(texts[0]) > 33000 else httpx.Response(200, json=vectors(texts))
        encoder = self.encoder(handler, batch_size=1, max_requests=2)
        with self.assertRaisesRegex(EmbeddingError, 'budget'):
            encoder.encode(['synthetic ' * 8000])
        self.assertEqual(2, encoder.usage()['requests'])

    def test_unsplittable_length_error_is_not_retried_forever(self):
        encoder = self.encoder(lambda _: too_long())
        with self.assertRaisesRegex(EmbeddingError, 'input_length'):
            encoder.encode(['small input'])
        self.assertEqual(1, encoder.usage()['requests'])

    def test_segmentation_preserves_whitespace_and_codepoint_boundaries(self):
        original = ' ' * 16000 + ('abc🙂中文\n' * 4000) + ' ' * 16000
        pieces = lossless_segments(original, 7680)
        self.assertEqual(original, ''.join(pieces))
        self.assertTrue(all(piece.strip() for piece in pieces))


if __name__ == '__main__':
    unittest.main()
