import unittest

from src.lad.lineage import effective_support, validate_paired_intervention
from src.lad.pairs import build_lineage_pair


class PairBuilderTests(unittest.TestCase):
    def test_builds_valid_common_and_independent_records(self):
        base = {
            "pair_id": "case-1",
            "question": "Which answer is supported?",
            "target_initial_answer": "A",
            "peer_claims": ["B", "B", "B"],
            "peer_correctness": [False, False, False],
            "peer_confidence": [0.8, 0.8, 0.8],
            "message_order": [0, 1, 2],
        }

        common, independent = build_lineage_pair(base, seed=7)

        validate_paired_intervention(common, independent)
        self.assertEqual(common["condition"], "COMMON")
        self.assertEqual(independent["condition"], "INDEPENDENT")
        self.assertEqual(len(set(common["source_ids"])), 3)
        self.assertEqual(len(set(independent["source_ids"])), 3)

        common_support = effective_support(
            common["source_ids"], common["source_parents"]
        )
        independent_support = effective_support(
            independent["source_ids"], independent["source_parents"]
        )
        self.assertEqual(common_support.independent_support, 1)
        self.assertEqual(independent_support.independent_support, 3)

    def test_is_deterministic_for_same_seed(self):
        base = {
            "pair_id": "case-2",
            "question": "Q",
            "target_initial_answer": "A",
            "peer_claims": ["B", "B"],
            "peer_correctness": [False, False],
            "peer_confidence": [0.7, 0.7],
            "message_order": [0, 1],
        }

        self.assertEqual(
            build_lineage_pair(base, seed=11), build_lineage_pair(base, seed=11)
        )

    def test_rejects_misaligned_peer_fields(self):
        base = {
            "pair_id": "bad",
            "question": "Q",
            "target_initial_answer": "A",
            "peer_claims": ["B", "B"],
            "peer_correctness": [False],
            "peer_confidence": [0.7, 0.7],
            "message_order": [0, 1],
        }

        with self.assertRaisesRegex(ValueError, "peer fields"):
            build_lineage_pair(base, seed=1)


if __name__ == "__main__":
    unittest.main()
