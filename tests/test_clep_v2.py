import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.clep_v2.core import ClosedItem, parse_output, run_pilot, validate_run
from src.clep_v2.fixtures import pilot_items


class CLEPV2Test(unittest.TestCase):
    def test_fixture_has_complete_parallel_groups(self) -> None:
        items = pilot_items()
        self.assertGreaterEqual(len(items), 24)
        groups = {}
        for item in items:
            groups.setdefault(item.parallel_group, set()).add(item.language)
        self.assertTrue(all(languages == {"en", "ko", "es"} for languages in groups.values()))

    def test_parser_accepts_only_closed_labels(self) -> None:
        parsed = parse_output("SPEAKER: ADA\nACTION: ARRIVE\nPOLARITY: NEGATIVE\nCERTAINTY: POSSIBLE")
        self.assertEqual(parsed["action"], "ARRIVE")
        self.assertIsNone(parse_output("SPEAKER: ADA\nACTION: MAY NOT ARRIVE\nPOLARITY: NEGATIVE\nCERTAINTY: POSSIBLE"))

    def test_integrity_recomputes_from_raw_output(self) -> None:
        class Backend:
            def generate(self, prompt: str) -> str:
                return "SPEAKER: ADA\nACTION: ARRIVE\nPOLARITY: NEGATIVE\nCERTAINTY: POSSIBLE"

        item = ClosedItem("x", "en", "Ada may not arrive.", "ADA", "ARRIVE", "NEGATIVE", "POSSIBLE", "g")
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            run_pilot([item], Backend(), path, method="direct")
            self.assertEqual(validate_run(path)["status"], "pass")
            metrics_path = path / "metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            metrics["exact"] = 0.0
            metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
            self.assertEqual(validate_run(path)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
