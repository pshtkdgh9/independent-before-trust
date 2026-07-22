import unittest

from src.lad.lineage import (
    LineageCycleError,
    effective_support,
    lineage_roots,
    validate_paired_intervention,
)


class LineageRootsTests(unittest.TestCase):
    def test_collapses_derived_sources_to_one_root(self):
        parents = {
            "article-a": (),
            "summary-a1": ("article-a",),
            "summary-a2": ("article-a",),
        }

        self.assertEqual(lineage_roots("summary-a1", parents), {"article-a"})
        self.assertEqual(lineage_roots("summary-a2", parents), {"article-a"})

    def test_rejects_lineage_cycles(self):
        parents = {"a": ("b",), "b": ("a",)}

        with self.assertRaises(LineageCycleError):
            lineage_roots("a", parents)


class EffectiveSupportTests(unittest.TestCase):
    def test_counts_shared_root_once(self):
        parents = {
            "source-a": (),
            "restatement-a1": ("source-a",),
            "restatement-a2": ("source-a",),
            "source-b": (),
        }

        result = effective_support(
            ["restatement-a1", "restatement-a2", "source-b"], parents
        )

        self.assertEqual(result.nominal_support, 3)
        self.assertEqual(result.independent_support, 2)
        self.assertAlmostEqual(result.corroboration_gap, 1 / 3)


class PairedInterventionTests(unittest.TestCase):
    def test_accepts_pair_that_differs_only_in_lineage(self):
        common = {
            "pair_id": "p1",
            "condition": "COMMON",
            "question": "Q",
            "target_initial_answer": "A",
            "peer_claims": ["B", "B"],
            "peer_correctness": [False, False],
            "peer_confidence": [0.9, 0.9],
            "message_order": [0, 1],
            "source_ids": ["s1a", "s1b"],
            "source_parents": {"root": [], "s1a": ["root"], "s1b": ["root"]},
        }
        independent = {
            **common,
            "condition": "INDEPENDENT",
            "source_ids": ["s2", "s3"],
            "source_parents": {"s2": [], "s3": []},
        }

        validate_paired_intervention(common, independent)

    def test_rejects_pair_with_changed_claim_content(self):
        common = {
            "pair_id": "p1",
            "condition": "COMMON",
            "question": "Q",
            "target_initial_answer": "A",
            "peer_claims": ["B", "B"],
            "peer_correctness": [False, False],
            "peer_confidence": [0.9, 0.9],
            "message_order": [0, 1],
            "source_ids": ["s1", "s1"],
            "source_parents": {"s1": []},
        }
        independent = {
            **common,
            "condition": "INDEPENDENT",
            "peer_claims": ["B", "C"],
            "source_ids": ["s2", "s3"],
            "source_parents": {"s2": [], "s3": []},
        }

        with self.assertRaisesRegex(ValueError, "peer_claims"):
            validate_paired_intervention(common, independent)


if __name__ == "__main__":
    unittest.main()
