import unittest

from src.lad.bigbench import build_logical_deduction_items, build_logical_deduction_pairs
from src.lad.lineage import validate_paired_intervention


class BigBenchPairTests(unittest.TestCase):
    def test_builds_private_first_items_without_injected_initial_answers(self):
        payload = {
            "name": "five_objects",
            "examples": [
                {"input": "Scenario one.", "target_scores": {"x": 1, "y": 0}},
                {"input": "Scenario two.", "target_scores": {"m": 0, "n": 1}},
            ],
        }

        items, summary = build_logical_deduction_items(payload, limit=2)

        self.assertEqual(len(items), 2)
        self.assertNotIn("target_initial_answer", items[0])
        self.assertEqual(items[0]["candidate_answers"], ["A", "B"])
        self.assertEqual(summary["protocol"], "adaptive-private-first-v1")

    def test_builds_one_counterbalanced_pair_per_unique_scenario(self):
        payload = {
            "name": "five_objects",
            "examples": [
                {
                    "input": "Scenario one.",
                    "target_scores": {"choice x": 1, "choice y": 0},
                },
                {
                    "input": "Scenario one.",
                    "target_scores": {"choice x": 0, "choice y": 1},
                },
                {
                    "input": "Scenario two.",
                    "target_scores": {"choice m": 0, "choice n": 1},
                },
            ],
        }

        records, summary = build_logical_deduction_pairs(payload, seed=17, limit=2)

        self.assertEqual(len(records), 4)
        self.assertEqual(summary["source_examples"], 3)
        self.assertEqual(summary["unique_scenarios"], 2)
        self.assertEqual(summary["selected_scenarios"], 2)
        self.assertEqual(summary["output_records"], 4)
        by_pair = {}
        for record in records:
            by_pair.setdefault(record["pair_id"], {})[record["condition"]] = record
            self.assertIn("Options:", record["question"])
            self.assertIn(record["gold_answer"], {"A", "B"})
            self.assertEqual(len(record["peer_claims"]), 3)
        for pair in by_pair.values():
            validate_paired_intervention(pair["COMMON"], pair["INDEPENDENT"])

        bases = [pair["COMMON"] for pair in by_pair.values()]
        self.assertEqual(
            {row["target_initial_answer"] == row["gold_answer"] for row in bases},
            {True, False},
        )

    def test_is_deterministic(self):
        payload = {
            "name": "five_objects",
            "examples": [
                {"input": "S1", "target_scores": {"x": 1, "y": 0}},
                {"input": "S2", "target_scores": {"x": 0, "y": 1}},
            ],
        }
        self.assertEqual(
            build_logical_deduction_pairs(payload, seed=3, limit=2),
            build_logical_deduction_pairs(payload, seed=3, limit=2),
        )

    def test_rejects_ambiguous_gold(self):
        payload = {
            "name": "bad",
            "examples": [
                {"input": "S", "target_scores": {"x": 1, "y": 1}},
            ],
        }
        with self.assertRaisesRegex(ValueError, "exactly one gold"):
            build_logical_deduction_pairs(payload, seed=1, limit=1)


if __name__ == "__main__":
    unittest.main()
