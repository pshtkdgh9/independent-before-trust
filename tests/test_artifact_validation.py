import json
import tempfile
import unittest
from pathlib import Path

from src.lad.pilot import PilotConfig, run_adaptive_paired_pilot
from src.lad.validation import validate_pilot_artifacts


class AlwaysA:
    def generate(self, prompt: str) -> str:
        return "<answer>A</answer>"


class PilotArtifactValidationTests(unittest.TestCase):
    def _build_run(self, root: Path) -> None:
        item = {
            "item_id": "item-1",
            "question": "Choose A or B.",
            "gold_answer": "A",
            "candidate_answers": ["A", "B"],
        }
        config = PilotConfig(
            model_id="fake/model",
            model_revision="deadbeef",
            tokenizer_revision="deadbeef",
            model_license="test-only",
        )
        run_adaptive_paired_pilot([item], AlwaysA(), root, config)
        Path(root, "RUN_COMPLETE").touch()

    def test_accepts_complete_internally_consistent_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            self._build_run(run_dir)

            report = validate_pilot_artifacts(run_dir)

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["counts"]["baseline"], 1)
            self.assertEqual(report["counts"]["generations"], 2)

    def test_rejects_missing_member_of_paired_generation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            self._build_run(run_dir)
            generation_path = run_dir / "generations.jsonl"
            rows = generation_path.read_text(encoding="utf-8").splitlines()
            generation_path.write_text(rows[0] + "\n", encoding="utf-8")

            report = validate_pilot_artifacts(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertIn("generation keys do not match pair keys", report["errors"])

    def test_rejects_correctness_label_that_contradicts_answer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            self._build_run(run_dir)
            generation_path = run_dir / "generations.jsonl"
            rows = [
                json.loads(line)
                for line in generation_path.read_text(encoding="utf-8").splitlines()
            ]
            rows[0]["final_correct"] = not rows[0]["final_correct"]
            generation_path.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                encoding="utf-8",
            )

            report = validate_pilot_artifacts(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertTrue(
                any("final_correct mismatch" in error for error in report["errors"])
            )

    def test_rejects_tampered_condition_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            self._build_run(run_dir)
            metrics_path = run_dir / "metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            metrics["conditions"]["COMMON"]["final_accuracy"] = 999.0
            metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

            report = validate_pilot_artifacts(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertIn(
                "COMMON condition metrics do not reproduce from generations",
                report["errors"],
            )


if __name__ == "__main__":
    unittest.main()
