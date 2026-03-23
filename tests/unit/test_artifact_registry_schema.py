import tempfile
import unittest
from pathlib import Path

from switching_sde.artifacts.registry import ArtifactRecord, ArtifactRegistry, load_registry, save_registry


class TestArtifactRegistrySchema(unittest.TestCase):
    def test_save_load_roundtrip(self):
        reg = ArtifactRegistry(
            version=1,
            legacy_root="/tmp/legacy",
            generated_at="2026-03-10T12:00:00",
            records=[
                ArtifactRecord(
                    artifact_id="abc",
                    kind="table",
                    scenario="ID",
                    method="m",
                    seed=42,
                    data_version="fixed_v2",
                    split_hash="hash",
                    path="/tmp/a.csv",
                    sha1="123",
                    status="ready",
                )
            ],
        )
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "lock.json"
            save_registry(p, reg)
            loaded = load_registry(p)
            self.assertEqual(len(loaded.records), 1)
            self.assertEqual(loaded.records[0].kind, "table")
            self.assertEqual(loaded.records[0].seed, 42)


if __name__ == "__main__":
    unittest.main()
