import unittest

from src.lad.statistics import paired_revision_effects


class PairedRevisionEffectsTests(unittest.TestCase):
    def test_computes_within_item_harmful_and_beneficial_effects(self):
        rows = [
            self._row("h1", "COMMON", True, False),
            self._row("h1", "INDEPENDENT", True, True),
            self._row("h2", "COMMON", True, True),
            self._row("h2", "INDEPENDENT", True, True),
            self._row("b1", "COMMON", False, True),
            self._row("b1", "INDEPENDENT", False, False),
        ]

        result = paired_revision_effects(rows, bootstrap_replicates=200, seed=19)

        self.assertEqual(result["harmful_revision"]["paired_n"], 2)
        self.assertEqual(result["harmful_revision"]["common_rate"], 0.5)
        self.assertEqual(result["harmful_revision"]["independent_rate"], 0.0)
        self.assertEqual(result["harmful_revision"]["paired_difference"], 0.5)
        self.assertEqual(result["beneficial_revision"]["paired_n"], 1)
        self.assertEqual(result["beneficial_revision"]["paired_difference"], 1.0)

    def test_excludes_incomplete_parser_pairs_and_reports_them(self):
        rows = [
            self._row("p1", "COMMON", True, None, "missing_answer_tag"),
            self._row("p1", "INDEPENDENT", True, True),
            self._row("p2", "COMMON", True, False),
            self._row("p2", "INDEPENDENT", True, True),
        ]

        result = paired_revision_effects(rows, bootstrap_replicates=50, seed=7)

        self.assertEqual(result["pair_count"], 2)
        self.assertEqual(result["complete_parsed_pair_count"], 1)
        self.assertEqual(result["incomplete_or_failed_pair_count"], 1)
        self.assertEqual(result["harmful_revision"]["paired_n"], 1)

    def test_bootstrap_interval_is_reproducible(self):
        rows = [
            self._row("p1", "COMMON", True, False),
            self._row("p1", "INDEPENDENT", True, True),
            self._row("p2", "COMMON", True, True),
            self._row("p2", "INDEPENDENT", True, False),
        ]

        first = paired_revision_effects(rows, bootstrap_replicates=100, seed=1701)
        second = paired_revision_effects(rows, bootstrap_replicates=100, seed=1701)

        self.assertEqual(first, second)
        self.assertEqual(first["bootstrap_replicates"], 100)
        self.assertEqual(first["bootstrap_seed"], 1701)

    @staticmethod
    def _row(pair_id, condition, initial_correct, final_correct, parse_error=None):
        return {
            "pair_id": pair_id,
            "condition": condition,
            "initial_correct": initial_correct,
            "final_correct": final_correct,
            "parse_error": parse_error,
        }


if __name__ == "__main__":
    unittest.main()
