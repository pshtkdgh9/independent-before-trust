import unittest

from src.esp.core import build_pilot_items, extract_uncertainty_frames


class ESPTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
