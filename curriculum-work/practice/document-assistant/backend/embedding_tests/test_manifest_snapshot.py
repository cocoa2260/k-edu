"""Dependency-free regression for provenance snapshots, not semantic model tests."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from retrieval.encoder import profile_hash
from retrieval.index import LocalIndex, ProfileMismatch


class BoundaryEncoder:
    def __init__(self):
        self.profile = dict(model_id='nonsemantic-boundary-fixture', revision='v1',
                            dimension=2, normalized=True, max_tokens=512)

    def encode(self, texts, kind):
        return [[1.0, 0.0] for _ in texts]


class ManifestSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name)/'index.sqlite'
        self.encoder = BoundaryEncoder()
        self.document = dict(id='A', version='v1', access='staff', current=True,
                             title='meal', text='meal cap 30000')
        self.index = LocalIndex.create(self.path, self.encoder, [self.document])

    def tearDown(self):
        self.index.close()
        self.folder.cleanup()

    def test_later_profile_change_cannot_rewrite_earlier_evidence(self):
        before = self.index.manifest()
        self.encoder.profile['max_tokens'] = 128
        self.assertEqual(before['profile']['max_tokens'], 512)
        self.assertEqual(profile_hash(before['profile']), before['profile_sha256'])
        with self.assertRaises(ProfileMismatch):
            LocalIndex(self.path, self.encoder)

    def test_reader_modifying_snapshot_cannot_change_live_encoder(self):
        before = self.index.manifest()
        before['profile']['max_tokens'] = 128
        self.assertEqual(self.encoder.profile['max_tokens'], 512)
        self.assertEqual(self.index.search('meal')['hits'][0]['doc_id'], 'A')

    def test_lifecycle_snapshots_and_result_context_remain_independent(self):
        selected = self.index.search('meal')
        before = self.index.manifest()
        updated = deepcopy(self.document)
        updated.update(version='v2', text='meal cap 35000')
        self.index.upsert(updated)
        middle = self.index.manifest()
        self.index.delete('A')
        after = self.index.manifest()
        self.assertEqual(before['documents'][0]['version'], 'v1')
        self.assertEqual(middle['documents'][0]['version'], 'v2')
        self.assertEqual((before['total_chunks'], middle['total_chunks'], after['total_chunks']), (1, 1, 0))
        self.assertEqual((before['generation'], middle['generation'], after['generation']), (1, 2, 3))
        self.assertEqual(self.index.search('meal')['hits'], [])
        from retrieval.index import StaleSelection
        with self.assertRaises(StaleSelection):
            self.index.context(selected)


if __name__=='__main__':
    unittest.main()
