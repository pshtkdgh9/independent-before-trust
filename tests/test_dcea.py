import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from src.dcea.core import (
    EvidenceTemplate,
    build_intervention_cells,
    render_prompt,
    run_pilot,
    score_generation,
    summarize_cells,
    validate_run,
)
from src.dcea.fixtures import pilot_templates


class DCEATest(unittest.TestCase):
    def setUp(self) -> None:
        self.template = EvidenceTemplate(
            item_id="planet-001",
            query="What year was the Aster probe launched?",
            subject="the Aster probe",
            relation="was launched in",
            original_value="2012",
            counterfactual_value="2017",
            distractor="The probe carried a spectrometer.",
            source_ids=("K7", "M2", "R9"),
        )

    def test_cells_change_only_the_answer_bearing_value(self) -> None:
        cells = build_intervention_cells(self.template)

        singleton_original = cells["singleton_original"]
        singleton_counterfactual = cells["singleton_counterfactual"]
        self.assertEqual(singleton_original.query, singleton_counterfactual.query)
        self.assertEqual(singleton_original.source_ids, singleton_counterfactual.source_ids)
        self.assertEqual(singleton_original.expected_answer, "2012")
        self.assertEqual(singleton_counterfactual.expected_answer, "2017")
        self.assertEqual(
            singleton_original.sources[0].replace("2012", "2017"),
            singleton_counterfactual.sources[0],
        )
        self.assertEqual(singleton_original.sources[1:], singleton_counterfactual.sources[1:])

    def test_template_rejects_non_identifying_intervention(self) -> None:
        with self.assertRaisesRegex(ValueError, "different"):
            EvidenceTemplate(
                item_id="bad",
                query="When?",
                subject="the probe",
                relation="launched in",
                original_value="2012",
                counterfactual_value="2012",
                distractor="Unrelated.",
                source_ids=("A", "B", "C"),
            )

    def test_template_rejects_duplicate_source_ids(self) -> None:
        with self.assertRaisesRegex(ValueError, "unique"):
            EvidenceTemplate(
                item_id="bad",
                query="When?",
                subject="the probe",
                relation="launched in",
                original_value="2012",
                counterfactual_value="2017",
                distractor="Unrelated.",
                source_ids=("A", "A", "C"),
            )

    def test_redundant_cell_has_two_independent_surface_forms(self) -> None:
        cells = build_intervention_cells(self.template)
        redundant = cells["redundant_original"]

        supporting = [source for source in redundant.sources if "2012" in source]
        self.assertEqual(len(supporting), 2)
        self.assertNotEqual(supporting[0], supporting[1])

    def test_score_requires_answer_and_valid_supporting_citation(self) -> None:
        cell = build_intervention_cells(self.template)["singleton_counterfactual"]

        good = score_generation(cell, "ANSWER: 2017\nCITATION: K7")
        wrong_answer = score_generation(cell, "ANSWER: 2012\nCITATION: K7")
        wrong_source = score_generation(cell, "ANSWER: 2017\nCITATION: M2")

        self.assertTrue(good.directional_following)
        self.assertTrue(good.citation_support)
        self.assertFalse(wrong_answer.directional_following)
        self.assertFalse(wrong_source.citation_support)

    def test_summary_reports_redundancy_interaction(self) -> None:
        cells = build_intervention_cells(self.template)
        scored = [
            score_generation(cells["singleton_original"], "ANSWER: 2012\nCITATION: K7"),
            score_generation(cells["singleton_counterfactual"], "ANSWER: 2012\nCITATION: K7"),
            score_generation(cells["redundant_original"], "ANSWER: 2012\nCITATION: K7"),
            score_generation(cells["redundant_counterfactual"], "ANSWER: 2017\nCITATION: K7"),
        ]

        summary = summarize_cells(scored)
        self.assertEqual(summary["singleton_directional_rate"], 0.5)
        self.assertEqual(summary["redundant_directional_rate"], 1.0)
        self.assertEqual(summary["redundancy_interaction"], 0.5)
        self.assertEqual(summary["singleton_counterfactual_following_rate"], 0.0)
        self.assertEqual(summary["redundant_counterfactual_following_rate"], 1.0)
        self.assertEqual(summary["counterfactual_redundancy_interaction"], 1.0)
        self.assertEqual(summary["singleton_pair_flip_rate"], 0.0)
        self.assertEqual(summary["redundant_pair_flip_rate"], 1.0)

    def test_prompt_hides_internal_condition_names(self) -> None:
        cell = build_intervention_cells(self.template)["redundant_counterfactual"]
        prompt = render_prompt(cell, contrastive=True)

        self.assertNotIn("counterfactual", prompt.lower())
        self.assertNotIn("redundant", prompt.lower())
        self.assertIn("[K7]", prompt)
        self.assertIn("ANSWER:", prompt)
        self.assertIn("CITATION:", prompt)

    def test_runner_retains_raw_outputs_and_metrics(self) -> None:
        class EvidenceFollowingBackend:
            def generate(self, prompt: str) -> str:
                answer = "2017" if "2017" in prompt else "2012"
                return f"ANSWER: {answer}\nCITATION: K7"

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            run_pilot([self.template], EvidenceFollowingBackend(), output_dir, contrastive=False)

            generations = [
                json.loads(line)
                for line in (output_dir / "generations.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(len(generations), 4)
            self.assertTrue(all("raw_output" in row for row in generations))
            self.assertEqual(metrics["singleton_directional_rate"], 1.0)
            self.assertEqual(metrics["redundant_directional_rate"], 1.0)

            report = validate_run(output_dir)
            self.assertEqual(report["status"], "pass")

    def test_validator_rejects_tampered_metrics(self) -> None:
        class EvidenceFollowingBackend:
            def generate(self, prompt: str) -> str:
                answer = "2017" if "2017" in prompt else "2012"
                return f"ANSWER: {answer}\nCITATION: K7"

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            run_pilot([self.template], EvidenceFollowingBackend(), output_dir, contrastive=False)
            metrics_path = output_dir / "metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            metrics["singleton_pair_flip_rate"] = 0.0
            metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

            report = validate_run(output_dir)
            self.assertEqual(report["status"], "fail")
            self.assertIn("metrics_mismatch", report["errors"])

    def test_validator_accepts_legacy_metric_subset(self) -> None:
        class EvidenceFollowingBackend:
            def generate(self, prompt: str) -> str:
                answer = "2017" if "2017" in prompt else "2012"
                return f"ANSWER: {answer}\nCITATION: K7"

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            run_pilot([self.template], EvidenceFollowingBackend(), output_dir, contrastive=False)
            metrics_path = output_dir / "metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            del metrics["counterfactual_redundancy_interaction"]
            metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

            self.assertEqual(validate_run(output_dir)["status"], "pass")

    def test_pilot_fixture_has_distinct_balanced_values(self) -> None:
        templates = pilot_templates()
        self.assertGreaterEqual(len(templates), 20)
        self.assertEqual(len({item.item_id for item in templates}), len(templates))
        self.assertTrue(all(item.original_value != item.counterfactual_value for item in templates))


if __name__ == "__main__":
    unittest.main()
