import unittest
from pathlib import Path

from switching_sde.config.schema import load_experiment_config


class TestConfigSchema(unittest.TestCase):
    def test_load_known_experiment(self):
        cfg = load_experiment_config("id_linear")
        self.assertEqual(cfg.experiment_name, "id_linear")
        self.assertEqual(cfg.drift_family, "ou")
        self.assertIn(cfg.artifact_policy, {"live", "frozen", "auto"})

    def test_invalid_experiment_raises(self):
        with self.assertRaises(Exception):
            load_experiment_config("does_not_exist")


if __name__ == "__main__":
    unittest.main()
