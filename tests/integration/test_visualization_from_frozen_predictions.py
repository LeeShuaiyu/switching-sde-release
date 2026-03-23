import tempfile
import unittest
from pathlib import Path

from switching_sde.config.schema import load_experiment_config
from switching_sde.pipelines.visualize import run_visualization
from tests._legacy_path import detect_legacy_root


class TestVisualizationFromFrozenPredictions(unittest.TestCase):
    def test_frozen_viz_outputs_files(self):
        legacy_root = detect_legacy_root()
        if not (legacy_root / "reports" / "p6_nonlinear_full_v3" / "figures").exists():
            self.skipTest("legacy p6 artifacts missing")
        cfg = load_experiment_config("id_nonlinear")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "figs"
            payload = run_visualization(cfg, mode="frozen", legacy_root=legacy_root, out_dir=out)
            self.assertEqual(payload["mode"], "frozen")
            pngs = list(out.glob("*.png"))
            self.assertTrue(len(pngs) >= 1)


if __name__ == "__main__":
    unittest.main()
