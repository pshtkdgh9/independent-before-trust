import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.evidence_state.builder import (
    EvidenceStateBuildError,
    build_evidence_state_items,
    items_to_jsonl,
)


VALID_SOURCE_PACK_ROW = {
    "source_pack_id": "fever-wiki-example-1",
    "source_id": "wiki-page-ada-award-2026-07-23",
    "source_url": "https://example.org/wiki/Ada_Award",
    "source_material_sufficient": True,
    "auditable": True,
    "question": "Who won the 2024 Example Award?",
    "answer": "Ada Lovelace",
    "evidence_sentences": [
        "The 2024 Example Award ceremony was held in Paris.",
        "Ada Lovelace won the 2024 Example Award.",
        "The prize committee announced the result after the final vote.",
    ],
    "required_premise_index": 1,
    "incompatible_sentence": "Grace Hopper won the 2024 Example Award.",
}


class EvidenceStateBuilderTests(unittest.TestCase):
    def test_builds_insufficiency_pair_by_removing_exactly_one_required_premise(self):
        items = build_evidence_state_items([dict(VALID_SOURCE_PACK_ROW)])

        sufficient = _item(items, "insufficiency", "sufficient")
        insufficient = _item(items, "insufficiency", "insufficient")

        self.assertEqual(sufficient.question, insufficient.question)
        self.assertEqual(sufficient.answer, insufficient.answer)
        self.assertEqual(sufficient.source_ids, insufficient.source_ids)
        self.assertEqual(sufficient.expected_action, "proceed")
        self.assertEqual(insufficient.expected_action, "retrieve")
        self.assertEqual(insufficient.intervention["kind"], "remove_required_premise")
        self.assertEqual(insufficient.intervention["field"], "evidence")
        self.assertEqual(insufficient.intervention["evidence_index"], 1)
        self.assertEqual(
            insufficient.intervention["removed_sentence_hash"],
            _sha("Ada Lovelace won the 2024 Example Award."),
        )
        self.assertEqual(
            tuple(s for s in sufficient.evidence if s not in insufficient.evidence),
            ("Ada Lovelace won the 2024 Example Award.",),
        )
        self.assertEqual(
            insufficient.evidence,
            (
                "The 2024 Example Award ceremony was held in Paris.",
                "The prize committee announced the result after the final vote.",
            ),
        )

    def test_builds_conflict_pair_by_adding_exactly_one_incompatible_sentence(self):
        items = build_evidence_state_items([dict(VALID_SOURCE_PACK_ROW)])

        sufficient = _item(items, "conflict", "sufficient")
        conflict = _item(items, "conflict", "conflict")

        self.assertEqual(sufficient.question, conflict.question)
        self.assertEqual(sufficient.answer, conflict.answer)
        self.assertEqual(sufficient.expected_action, "proceed")
        self.assertEqual(conflict.expected_action, "abstain")
        self.assertEqual(len(conflict.evidence), len(sufficient.evidence) + 1)
        self.assertEqual(conflict.evidence[:-1], sufficient.evidence)
        self.assertEqual(
            sufficient.evidence[1], "Ada Lovelace won the 2024 Example Award."
        )
        self.assertEqual(
            conflict.evidence[-1], "Grace Hopper won the 2024 Example Award."
        )
        self.assertEqual(conflict.intervention["kind"], "add_conflicting_sentence")
        self.assertEqual(conflict.intervention["field"], "evidence")
        self.assertEqual(conflict.intervention["evidence_index"], 3)
        self.assertEqual(
            conflict.intervention["original_sentence_hash"],
            _sha("Ada Lovelace won the 2024 Example Award."),
        )
        self.assertEqual(
            conflict.intervention["incompatible_sentence_hash"],
            _sha("Grace Hopper won the 2024 Example Award."),
        )

    def test_sufficient_controls_have_stable_answer_hashes_and_no_uncertainty_cues(self):
        items = build_evidence_state_items([dict(VALID_SOURCE_PACK_ROW)])
        sufficient_items = [item for item in items if item.evidence_state == "sufficient"]

        self.assertEqual(len(sufficient_items), 2)
        self.assertEqual({item.answer for item in sufficient_items}, {"Ada Lovelace"})
        self.assertEqual({item.expected_action for item in sufficient_items}, {"proceed"})
        for item in sufficient_items:
            self.assertNotRegex(
                " ".join(item.evidence).lower(),
                r"\b(maybe|possibly|unknown|unclear|not sure)\b",
            )
            self.assertIn("item_hash", item.intervention)
            self.assertEqual(item.intervention["answer_hash"], _sha("Ada Lovelace"))

    def test_jsonl_output_has_stable_ids_hashes_source_links_and_directional_flips(self):
        items = build_evidence_state_items([dict(VALID_SOURCE_PACK_ROW)])
        rows = [json.loads(line) for line in items_to_jsonl(items).splitlines()]

        self.assertEqual([row["item_id"] for row in rows], sorted(row["item_id"] for row in rows))
        self.assertEqual(len({row["item_hash"] for row in rows}), 4)
        self.assertEqual(
            {row["source_links"][0]["source_url"] for row in rows},
            {"https://example.org/wiki/Ada_Award"},
        )
        flips = {row["pair_id"]: row["expected_directional_flip"] for row in rows}
        self.assertEqual(
            flips,
            {
                "fever-wiki-example-1:conflict": "proceed_to_abstain",
                "fever-wiki-example-1:insufficiency": "proceed_to_retrieve",
            },
        )

    def test_refuses_source_pack_without_explicit_incompatible_sentence(self):
        row = dict(VALID_SOURCE_PACK_ROW)
        del row["incompatible_sentence"]

        with self.assertRaisesRegex(EvidenceStateBuildError, "incompatible_sentence"):
            build_evidence_state_items([row])

    def test_refuses_source_pack_rows_without_sufficient_or_auditable_source_material(self):
        for override, message in (
            ({"source_material_sufficient": False}, "source_material_sufficient=false"),
            ({"auditable": False}, "unauditable"),
        ):
            with self.subTest(override=override):
                row = dict(VALID_SOURCE_PACK_ROW, **override)
                with self.assertRaisesRegex(EvidenceStateBuildError, message):
                    build_evidence_state_items([row])

    def test_cli_fails_clearly_without_ready_source_pack_and_does_not_write_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_pack = Path(temp_dir, "source-pack.jsonl")
            output = Path(temp_dir, "items.jsonl")
            row = dict(VALID_SOURCE_PACK_ROW, source_material_sufficient=False)
            source_pack.write_text(json.dumps(row) + "\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_evidence_state_items.py",
                    "--source-pack",
                    str(source_pack),
                    "--output",
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source_material_sufficient=false", result.stderr)
            self.assertFalse(output.exists())


def _item(items, pair_kind, evidence_state):
    matches = [
        item
        for item in items
        if item.intervention["pair_kind"] == pair_kind
        and item.evidence_state == evidence_state
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one {pair_kind}/{evidence_state} item, got {len(matches)}"
        )
    return matches[0]


def _sha(text):
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    unittest.main()
