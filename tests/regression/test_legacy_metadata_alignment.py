import json
import unittest
from pathlib import Path

from tests._legacy_path import detect_legacy_root


class TestLegacyMetadataAlignment(unittest.TestCase):
    def test_eval_json_contains_data_version_and_split_hash(self):
        legacy_root = detect_legacy_root()
        folder = legacy_root / "reports" / "p6_nonlinear_full_v3" / "raw" / "eval_json"
        if not folder.exists():
            self.skipTest("legacy p6 eval_json folder missing")
        files = sorted(folder.glob("*_test.json"))
        self.assertTrue(files)
        with files[0].open("r", encoding="utf-8") as f:
            payload = json.load(f)
        self.assertIn("data_version", payload)
        self.assertIn("split_hash", payload)
        self.assertTrue(str(payload.get("data_version", "")).startswith("fixed_"))


if __name__ == "__main__":
    unittest.main()
