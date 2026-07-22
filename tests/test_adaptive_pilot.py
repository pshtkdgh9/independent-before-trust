import json
import tempfile
import unittest
from pathlib import Path

from src.lad.pilot import PilotConfig, run_adaptive_paired_pilot


class AdaptiveBackend:
    def generate(self, prompt: str) -> str:
        if "No peer messages" in prompt:
            if "item-one" in prompt:
                return "<answer>A</answer>"
            return "<answer>B</answer>"
        if "is derived from" in prompt:
            return "<answer>B</answer>"
        return "<answer>A</answer>"


class AdaptivePilotTests(unittest.TestCase):
    def test_elicits_private_answer_before_constructing_paired_revision(self):
        items = [
            {
                "item_id": "one",
                "question": "item-one\nOptions:\n(A) x\n(B) y",
                "gold_answer": "A",
                "candidate_answers": ["A", "B"],
            },
            {
                "item_id": "two",
                "question": "item-two\nOptions:\n(A) x\n(B) y",
                "gold_answer": "A",
                "candidate_answers": ["A", "B"],
            },
        ]
        config = PilotConfig(
            model_id="fake/adaptive",
            model_revision="abc",
            tokenizer_revision="abc",
            model_license="test-only",
            seed=23,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            metrics = run_adaptive_paired_pilot(
                items, AdaptiveBackend(), Path(temp_dir), config
            )

            baseline = [
                json.loads(line)
                for line in Path(temp_dir, "baseline_generations.jsonl")
                .read_text()
                .splitlines()
            ]
            pairs = [
                json.loads(line)
                for line in Path(temp_dir, "pairs.jsonl").read_text().splitlines()
            ]
            self.assertEqual([row["private_answer"] for row in baseline], ["A", "B"])
            self.assertEqual(len(pairs), 4)
            for row in pairs[:2]:
                self.assertEqual(row["target_initial_answer"], "A")
                self.assertEqual(row["peer_claims"], ["B", "B", "B"])
            for row in pairs[2:]:
                self.assertEqual(row["target_initial_answer"], "B")
                self.assertEqual(row["peer_claims"], ["A", "A", "A"])
            self.assertEqual(metrics["baseline"]["parse_failure_rate"], 0.0)
            self.assertEqual(metrics["baseline"]["accuracy"], 0.5)
            self.assertEqual(metrics["paired_item_count"], 2)

    def test_invalid_private_answer_is_retained_but_not_paired(self):
        class InvalidBackend:
            def generate(self, prompt: str) -> str:
                return "<answer>Z</answer>"

        items = [{
            "item_id": "bad",
            "question": "Q\nOptions:\n(A) x\n(B) y",
            "gold_answer": "A",
            "candidate_answers": ["A", "B"],
        }]
        config = PilotConfig("fake", "abc", "abc", "test")
        with tempfile.TemporaryDirectory() as temp_dir:
            metrics = run_adaptive_paired_pilot(
                items, InvalidBackend(), Path(temp_dir), config
            )
            self.assertEqual(metrics["baseline"]["parse_failure_rate"], 1.0)
            self.assertEqual(metrics["paired_item_count"], 0)
            row = json.loads(
                Path(temp_dir, "baseline_generations.jsonl").read_text().strip()
            )
            self.assertEqual(row["parse_error"], "answer_outside_candidates")


if __name__ == "__main__":
    unittest.main()
