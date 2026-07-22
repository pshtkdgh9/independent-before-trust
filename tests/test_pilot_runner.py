import json
import tempfile
import unittest
from pathlib import Path

from src.lad.pairs import build_lineage_pair
from src.lad.pilot import PilotConfig, parse_answer, run_paired_pilot


class FakeBackend:
    def generate(self, prompt: str) -> str:
        if "is derived from" in prompt:
            return "<answer>B</answer>"
        return "<answer>A</answer>"


class PilotRunnerTests(unittest.TestCase):
    def test_parses_option_label_when_model_repeats_option_text(self):
        answer, error = parse_answer(
            "<answer>E) The black book is the leftmost.</answer>",
            candidates=["A", "B", "C", "D", "E"],
        )

        self.assertEqual(answer, "E")
        self.assertIsNone(error)

    def test_prompt_does_not_leak_condition_label(self):
        from src.lad.pilot import build_revision_prompt

        base = {
            "pair_id": "case-prompt",
            "question": "Q?",
            "gold_answer": "A",
            "target_initial_answer": "A",
            "peer_claims": ["B", "B"],
            "peer_correctness": [False, False],
            "peer_confidence": [0.7, 0.7],
            "message_order": [0, 1],
        }
        common, independent = build_lineage_pair(base, seed=9)

        for record in (common, independent):
            prompt = build_revision_prompt(record)
            self.assertNotIn("COMMON", prompt)
            self.assertNotIn("INDEPENDENT", prompt)

    def test_writes_raw_outputs_metrics_and_reproducibility_config(self):
        base = {
            "pair_id": "case-1",
            "question": "Which option is correct?",
            "gold_answer": "A",
            "target_initial_answer": "A",
            "peer_claims": ["B", "B", "B"],
            "peer_correctness": [False, False, False],
            "peer_confidence": [0.8, 0.8, 0.8],
            "message_order": [0, 1, 2],
        }
        records = list(build_lineage_pair(base, seed=7))
        config = PilotConfig(
            model_id="fake/open-model",
            model_revision="deadbeef",
            tokenizer_revision="deadbeef",
            model_license="test-only",
            seed=17,
            max_new_tokens=16,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_paired_pilot(
                records=records,
                backend=FakeBackend(),
                output_dir=Path(temp_dir),
                config=config,
            )

            raw_path = Path(temp_dir, "generations.jsonl")
            metrics_path = Path(temp_dir, "metrics.json")
            config_path = Path(temp_dir, "config.json")
            self.assertTrue(raw_path.is_file())
            self.assertTrue(metrics_path.is_file())
            self.assertTrue(config_path.is_file())

            rows = [json.loads(line) for line in raw_path.read_text().splitlines()]
            saved_config = json.loads(config_path.read_text())
            self.assertEqual(len(rows), 2)
            self.assertEqual({row["condition"] for row in rows}, {"COMMON", "INDEPENDENT"})
            self.assertTrue(all(row["raw_response"] for row in rows))
            self.assertTrue(all(row["prompt_sha256"] for row in rows))
            self.assertEqual(saved_config["model_revision"], "deadbeef")
            self.assertEqual(result["artifact_class"], "empirical-candidate-unverified")
            self.assertEqual(result["conditions"]["COMMON"]["harmful_revision_rate"], 1.0)
            self.assertEqual(result["conditions"]["INDEPENDENT"]["harmful_revision_rate"], 0.0)
            self.assertEqual(
                result["paired_effects"]["harmful_revision"]["paired_difference"],
                1.0,
            )
            self.assertEqual(
                result["paired_effects"]["effect_direction"],
                "COMMON-minus-INDEPENDENT",
            )

    def test_parse_failures_are_retained_and_counted(self):
        class InvalidBackend:
            def generate(self, prompt: str) -> str:
                return "<answer>Z</answer>"

        base = {
            "pair_id": "case-2",
            "question": "Q?",
            "gold_answer": "A",
            "candidate_answers": ["A", "B"],
            "target_initial_answer": "B",
            "peer_claims": ["A", "A"],
            "peer_correctness": [True, True],
            "peer_confidence": [0.7, 0.7],
            "message_order": [0, 1],
        }
        records = list(build_lineage_pair(base, seed=8))
        config = PilotConfig(
            model_id="fake/invalid",
            model_revision="deadbeef",
            tokenizer_revision="deadbeef",
            model_license="test-only",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            metrics = run_paired_pilot(
                records, InvalidBackend(), Path(temp_dir), config
            )

            self.assertEqual(metrics["conditions"]["COMMON"]["parse_failure_rate"], 1.0)
            self.assertEqual(metrics["conditions"]["INDEPENDENT"]["parse_failure_rate"], 1.0)
            rows = [
                json.loads(line)
                for line in Path(temp_dir, "generations.jsonl").read_text().splitlines()
            ]
            self.assertTrue(all(row["parse_error"] for row in rows))


if __name__ == "__main__":
    unittest.main()
