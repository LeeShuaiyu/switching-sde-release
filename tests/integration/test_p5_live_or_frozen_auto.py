import tempfile
import unittest
from pathlib import Path

from switching_sde.config.schema import load_experiment_config
from switching_sde.pipelines.evaluate import run_eval
from tests._legacy_path import detect_legacy_root


class TestP5LiveOrFrozenAuto(unittest.TestCase):
    def test_auto_mode_returns_payload(self):
        legacy_root = detect_legacy_root()
        if not (legacy_root / "reports" / "p5" / "raw" / "eval_json").exists():
            self.skipTest("legacy p5 artifacts missing")
        cfg = load_experiment_config("ood_linear_s1")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            payload = run_eval(cfg, mode="auto", legacy_root=legacy_root, out_dir=out)
            self.assertIn(payload.get("mode"), {"live", "frozen"})
            self.assertTrue(any(p.name.endswith(".json") for p in out.glob("*.json")))


if __name__ == "__main__":
    unittest.main()
