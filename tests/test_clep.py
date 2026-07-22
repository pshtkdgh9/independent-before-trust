import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.clep.core import EpistemicItem, parse_typed_output, run_pilot, validate_run
from src.clep.fixtures import pilot_items


class CLEPTest(unittest.TestCase):
    def test_fixture_is_parallel_and_balanced(self) -> None:
        items = pilot_items()
        self.assertGreaterEqual(len(items), 12)
        self.assertEqual(len({item.item_id for item in items}), len(items))
        self.assertEqual({item.language for item in items}, {"en", "ko", "es"})
        self.assertEqual({item.certainty for item in items}, {"possible", "probable", "certain"})
        self.assertEqual({item.polarity for item in items}, {"positive", "negative"})

    def test_item_rejects_unknown_labels(self) -> None:
        with self.assertRaises(ValueError):
            EpistemicItem("x", "fr", "text", "Ada", "arrive", "positive", "certain", "g")

    def test_parser_requires_all_typed_fields(self) -> None:
        parsed = parse_typed_output(
            'TUPLE: {"speaker":"Ada","proposition":"arrive","polarity":"negative","certainty":"possible"}\nREPORT: Ada may not arrive.'
        )
        self.assertEqual(parsed["speaker"], "Ada")
        self.assertEqual(parsed["polarity"], "negative")
        self.assertIsNone(parse_typed_output("REPORT: Ada may not arrive."))

    def test_runner_and_validator_recompute_metrics(self) -> None:
        class Backend:
            def generate(self, prompt: str) -> str:
                return 'TUPLE: {"speaker":"Ada","proposition":"arrive","polarity":"negative","certainty":"possible"}\nREPORT: Ada may not arrive.'

        item = EpistemicItem("x-en", "en", "Ada may not arrive.", "Ada", "arrive", "negative", "possible", "g1")
        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            run_pilot([item], Backend(), output_dir, method="typed")
            self.assertEqual(validate_run(output_dir)["status"], "pass")
            metrics_path = output_dir / "metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            metrics["all_fields_exact"] = 0.0
            metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
            self.assertEqual(validate_run(output_dir)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
