import unittest

from src.lad.metrics import aggregate_revision_metrics, classify_revision


class RevisionClassificationTests(unittest.TestCase):
    def test_marks_correct_to_incorrect_as_harmful(self):
        self.assertEqual(classify_revision(True, False), "harmful")

    def test_marks_incorrect_to_correct_as_beneficial(self):
        self.assertEqual(classify_revision(False, True), "beneficial")

    def test_distinguishes_stable_correct_and_stable_incorrect(self):
        self.assertEqual(classify_revision(True, True), "stable_correct")
        self.assertEqual(classify_revision(False, False), "stable_incorrect")


class RevisionAggregationTests(unittest.TestCase):
    def test_reports_rates_with_eligible_denominators(self):
        rows = [
            {"initial_correct": True, "final_correct": False},
            {"initial_correct": True, "final_correct": True},
            {"initial_correct": False, "final_correct": True},
            {"initial_correct": False, "final_correct": False},
            {"initial_correct": False, "final_correct": False},
        ]

        result = aggregate_revision_metrics(rows)

        self.assertEqual(result["n"], 5)
        self.assertEqual(result["initially_correct_n"], 2)
        self.assertEqual(result["initially_incorrect_n"], 3)
        self.assertEqual(result["harmful_revision_rate"], 0.5)
        self.assertAlmostEqual(result["beneficial_revision_rate"], 1 / 3)
        self.assertEqual(result["final_accuracy"], 0.4)


if __name__ == "__main__":
    unittest.main()
