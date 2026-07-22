import unittest

from src.esp.core import (
    annotation_agreement,
    blind_review_id,
    build_pilot_items,
    extract_uncertainty_frames,
    validate_annotations,
    render_rewrite_prompt,
    score_cue_preservation,
)
from src.esp.counterfactual import CounterfactualPair, validate_counterfactual_pairs


class ESPTests(unittest.TestCase):
    def test_blind_review_id_is_stable_and_hides_condition(self):
        first = blind_review_id("esp-0001-00", "frame")
        self.assertEqual(first, blind_review_id("esp-0001-00", "frame"))
        self.assertNotEqual(first, blind_review_id("esp-0001-00", "generic"))
        self.assertNotEqual(
            blind_review_id("esp-0001-00", "frame", "esp-phi-frame"),
            blind_review_id("esp-0001-00", "frame", "esp-qwen-frame"),
        )
        self.assertNotIn("frame", first)

    def test_extracts_cue_and_sentence_scope_without_matching_substrings(self):
        text = (
            "The treatment may reduce symptoms in adults. "
            "The mayor reported the result. It is unknown whether children benefit."
        )

        frames = extract_uncertainty_frames(text)

        self.assertEqual([frame.cue for frame in frames], ["may", "unknown whether"])
        self.assertEqual(
            frames[0].scope,
            "The treatment may reduce symptoms in adults.",
        )
        self.assertEqual(frames[0].strength, "possible")
        self.assertEqual(frames[1].strength, "unknown")

    def test_builds_deterministic_natural_text_items_and_preserves_sources(self):
        records = [
            {
                "article": "We found a clear effect. It may depend on temperature.",
                "summary": "The effect could change with temperature.",
                "title": "Temperature study",
                "year": "2024",
            },
            {
                "article": "It is unknown whether the result generalizes.",
                "summary": "Researchers do not yet know if it applies elsewhere.",
                "title": "Generalization study",
                "year": "2023",
            },
        ]

        items = build_pilot_items(records, limit=2)

        self.assertEqual([item.item_id for item in items], ["esp-0000-00", "esp-0001-00"])
        self.assertEqual(items[0].source_text, records[0]["article"])
        self.assertEqual(items[0].reference_summary, records[0]["summary"])
        self.assertEqual(items[1].frame.cue, "unknown whether")

    def test_limits_source_to_abstract_when_sections_are_available(self):
        records = [
            {
                "article": "The effect may be small.\nThe discussion might be long.",
                "summary": "The effect may be limited.",
                "section_headings": ["Abstract", "Discussion"],
            }
        ]

        item = build_pilot_items(records, limit=1)[0]

        self.assertEqual(item.source_text, "The effect may be small.")
        self.assertNotIn("discussion", item.source_text.lower())

    def test_rejects_annotation_ids_that_do_not_match_manifest_order(self):
        with self.assertRaisesRegex(ValueError, "item IDs"):
            validate_annotations(
                ["esp-0000-00", "esp-0001-00"],
                [{"item_id": "esp-0001-00"}, {"item_id": "esp-0000-00"}],
            )

    def test_reports_exact_label_agreement_without_scoring_scope_as_exact(self):
        left = [
            {
                "item_id": "a",
                "cue_valid": "yes",
                "strength": "possible",
                "attribution": "authors",
                "retain_in_lay_rewrite": "yes",
                "scope_text": "may help adults",
            },
            {
                "item_id": "b",
                "cue_valid": "no",
                "strength": "not_epistemic",
                "attribution": "authors",
                "retain_in_lay_rewrite": "no",
                "scope_text": "",
            },
        ]
        right = [dict(row) for row in left]
        right[0]["scope_text"] = "help adults"
        right[1]["cue_valid"] = "yes"

        report = annotation_agreement(left, right)

        self.assertEqual(report["items"], 2)
        self.assertEqual(report["exact_agreement"]["cue_valid"], 0.5)
        self.assertEqual(report["exact_agreement"]["strength"], 1.0)
        self.assertNotIn("scope_text", report["exact_agreement"])

    def test_frame_prompt_exposes_frame_but_direct_prompt_does_not(self):
        annotation = {
            "scope_text": "the treatment may help adults",
            "strength": "possible",
            "attribution": "authors",
        }
        direct = render_rewrite_prompt("The treatment may help adults.", annotation, "direct")
        framed = render_rewrite_prompt("The treatment may help adults.", annotation, "frame")
        self.assertNotIn("FRAME", direct)
        self.assertIn("STRENGTH=possible", framed)

    def test_cue_score_distinguishes_preserved_strength(self):
        self.assertTrue(score_cue_preservation("It might help adults.", "possible"))
        self.assertFalse(score_cue_preservation("It helps adults.", "possible"))

    def test_counterfactual_pair_records_are_validated_and_immutable(self):
        pair = CounterfactualPair(
            pair_id="esp-cf-0001",
            original_strength="possible",
            counterfactual_strength="likely",
            original_source="The result may reduce symptoms.",
            counterfactual_source="The result likely reduces symptoms.",
            edit_spans=("may -> likely",),
            proposition_skeleton="The result {strength} reduce symptoms.",
        )

        self.assertEqual(validate_counterfactual_pairs([pair]), [pair])
        with self.assertRaisesRegex(AttributeError, "cannot assign"):
            pair.original_strength = "likely"

    def test_counterfactual_pair_validation_rejects_invalid_records(self):
        valid = {
            "pair_id": "esp-cf-0001",
            "original_strength": "possible",
            "counterfactual_strength": "likely",
            "original_source": "The result may reduce symptoms.",
            "counterfactual_source": "The result likely reduces symptoms.",
            "edit_spans": ("may -> likely",),
            "proposition_skeleton": "The result {strength} reduce symptoms.",
        }
        cases = [
            ("unique pair IDs", {"pair_id": "esp-cf-0001"}, [CounterfactualPair(**valid)]),
            ("adjacent strength", {"counterfactual_strength": "suggestive"}, []),
            ("differ", {"counterfactual_source": valid["original_source"]}, []),
            ("exactly one edit span", {"edit_spans": ("may -> likely", "reduce -> improve")}, []),
            ("exactly one edit span", {"edit_spans": ("",)}, []),
            ("proposition_skeleton", {"counterfactual_proposition_skeleton": "Symptoms are reduced."}, []),
            ("source strings", {"original_source": ""}, []),
            ("polarity changes", {"polarity_changed": True}, []),
            ("material argument changes", {"material_argument_changed": True}, []),
        ]

        for pattern, overrides, prefix in cases:
            fields = dict(valid)
            fields.update(overrides)
            with self.subTest(pattern=pattern):
                with self.assertRaisesRegex(ValueError, pattern):
                    validate_counterfactual_pairs([*prefix, CounterfactualPair(**fields)])


if __name__ == "__main__":
    unittest.main()
