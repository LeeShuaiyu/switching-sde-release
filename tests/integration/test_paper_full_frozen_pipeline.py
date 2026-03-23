import os
import tempfile
import unittest
from pathlib import Path

from switching_sde.pipelines.benchmark import run_benchmark
from tests._legacy_path import detect_legacy_root


class TestPaperFullFrozenPipeline(unittest.TestCase):
    def test_frozen_benchmark_exports_tables(self):
        legacy_root = detect_legacy_root()
        if not (legacy_root / "reports" / "paper_full" / "benchmark_main_table.csv").exists():
            self.skipTest("legacy paper_full artifacts missing")

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "paper_full"
            payload = run_benchmark(suite="paper_full", mode="frozen", legacy_root=legacy_root, output_root=out)
            self.assertEqual(payload["mode"], "frozen")
            self.assertTrue((out / "tables" / "paper_full_main.csv").exists())


if __name__ == "__main__":
    unittest.main()
