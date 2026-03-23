import unittest

from switching_sde.artifacts.frozen_loader import suite_table_files, summarize_table


class TestFrozenLoader(unittest.TestCase):
    def test_suite_table_files(self):
        files = suite_table_files("paper_full")
        self.assertIn("main", files)

    def test_summarize_table(self):
        rows = [
            {"a": "1", "b": "x"},
            {"a": "3", "b": "y"},
        ]
        s = summarize_table(rows)
        self.assertEqual(s["num_rows"], 2)
        self.assertAlmostEqual(s["a_mean"], 2.0)


if __name__ == "__main__":
    unittest.main()
