import json
import tempfile
import unittest
from pathlib import Path

from src.lad.mock_pilot import run_mock_pilot


class MockPilotTests(unittest.TestCase):
    def test_writes_valid_non_evidence_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_mock_pilot(Path(temp_dir))

            pair_path = Path(temp_dir, "pairs.jsonl")
            metrics_path = Path(temp_dir, "metrics.json")
            config_path = Path(temp_dir, "config.json")
            self.assertTrue(pair_path.is_file())
            self.assertTrue(metrics_path.is_file())
            self.assertTrue(config_path.is_file())

            pairs = [json.loads(line) for line in pair_path.read_text().splitlines()]
            metrics = json.loads(metrics_path.read_text())
            config = json.loads(config_path.read_text())

            self.assertEqual(len(pairs), 4)
            self.assertEqual({row["condition"] for row in pairs}, {"COMMON", "INDEPENDENT"})
            self.assertEqual(config["artifact_class"], "mock-not-empirical-evidence")
            self.assertEqual(metrics["artifact_class"], "mock-not-empirical-evidence")
            self.assertEqual(result, metrics)


if __name__ == "__main__":
    unittest.main()
