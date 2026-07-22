import json
import tempfile
import unittest
from pathlib import Path

from src.evidence_state.provenance import (
    ProvenanceValidationError,
    load_source_manifest,
    validate_source_manifest_record,
)


FEVER_RECORD = {
    "source_id": "fever-paper-dev-85ebc1ea",
    "source_name": "FEVER paper_dev.jsonl",
    "source_url": "https://fever.ai/download/fever/paper_dev.jsonl",
    "dataset_card_url": (
        "https://huggingface.co/datasets/EleutherAI/fever/tree/"
        "85ebc1eaacc6b6bf0d54719c942b7aad097a1abd"
    ),
    "license_or_terms_url": "https://huggingface.co/datasets/EleutherAI/fever",
    "licenses": ["cc-by-sa-3.0", "gpl-3.0"],
    "retrieved_utc": "2026-07-22T15:59:34Z",
    "revision": "85ebc1eaacc6b6bf0d54719c942b7aad097a1abd",
    "local_path": "data/raw/fever/paper_dev.jsonl",
    "byte_size": 2168767,
    "line_count": 9999,
    "sha256": "41158707810008747946bf23471e82df53e77a513524b9e3ec1c2e674ef5ef8c",
    "raw_record_hash": "41158707810008747946bf23471e82df53e77a513524b9e3ec1c2e674ef5ef8c",
    "transform_script": "src/evidence_state/builder.py",
    "derived_item_hash": "pending-item-builder",
    "redistributable_text": False,
    "download_command": (
        "python scripts/download_public_file.py --url "
        "https://fever.ai/download/fever/paper_dev.jsonl --destination "
        "data/raw/fever/paper_dev.jsonl --artifact-type dataset-source --name "
        "'FEVER paper_dev.jsonl' --revision "
        "85ebc1eaacc6b6bf0d54719c942b7aad097a1abd --license "
        "'cc-by-sa-3.0 OR gpl-3.0' --terms-url "
        "https://huggingface.co/datasets/EleutherAI/fever --manifest "
        "data/evidence_state/source_manifest.jsonl --privacy-or-consent "
        "'public dataset; no private records' --redistribution "
        "'raw claims not redistributed as sufficient evidence text' "
        "--expected-sha256 "
        "41158707810008747946bf23471e82df53e77a513524b9e3ec1c2e674ef5ef8c"
    ),
    "intended_preprocessing": (
        "Use raw FEVER claims only as candidate questions or claim targets; do not "
        "treat raw claims as sufficient evidence text. Build evidence-state items "
        "only after full wiki source provenance is attached."
    ),
    "provenance_boundary": (
        "Raw claims alone are not sufficient evidence text; full wiki source "
        "provenance remains required before item building."
    ),
    "benchmark_claim": False,
}


class EvidenceStateProvenanceTests(unittest.TestCase):
    def test_public_source_requires_auditable_license_and_hash_fields(self):
        record = validate_source_manifest_record(dict(FEVER_RECORD))

        self.assertEqual(record.source_name, "FEVER paper_dev.jsonl")
        self.assertEqual(record.byte_size, 2168767)
        self.assertEqual(
            record.sha256,
            "41158707810008747946bf23471e82df53e77a513524b9e3ec1c2e674ef5ef8c",
        )
        self.assertEqual(
            record.revision, "85ebc1eaacc6b6bf0d54719c942b7aad097a1abd"
        )
        self.assertFalse(record.redistributable_text)
        self.assertFalse(record.benchmark_claim)

    def test_missing_required_fields_are_rejected_with_specific_exclusion_reason(self):
        required_fields = [
            "source_name",
            "source_url",
            "license_or_terms_url",
            "retrieved_utc",
            "raw_record_hash",
            "transform_script",
            "derived_item_hash",
            "redistributable_text",
            "byte_size",
            "sha256",
            "revision",
            "local_path",
            "download_command",
            "intended_preprocessing",
        ]

        for field_name in required_fields:
            with self.subTest(field_name=field_name):
                row = dict(FEVER_RECORD)
                row.pop(field_name)
                with self.assertRaisesRegex(
                    ProvenanceValidationError,
                    f"exclude source: missing required field {field_name}",
                ):
                    validate_source_manifest_record(row)

    def test_rejects_retired_unpublished_or_unlabeled_source_rows(self):
        forbidden_rows = [
            ("old-manuscript-artifact", "exclude source: retired manuscript artifact"),
            ("retired-experiment-output", "exclude source: retired experiment output"),
            ("unpublished-review-packet", "exclude source: unpublished review packet"),
            ("unlabeled-jsonl", "exclude source: unlabeled source jsonl"),
        ]

        for source_type, reason in forbidden_rows:
            with self.subTest(source_type=source_type):
                row = dict(FEVER_RECORD, source_type=source_type)
                with self.assertRaisesRegex(ProvenanceValidationError, reason):
                    validate_source_manifest_record(row)

    def test_rejects_rows_without_license_data(self):
        for override in ({"licenses": []}, {"license_or_terms_url": ""}):
            with self.subTest(override=override):
                row = dict(FEVER_RECORD, **override)
                with self.assertRaisesRegex(
                    ProvenanceValidationError, "exclude source: missing license data"
                ):
                    validate_source_manifest_record(row)

    def test_loads_manifest_jsonl_and_rejects_benchmark_claims(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir, "source_manifest.jsonl")
            good = dict(FEVER_RECORD)
            bad = dict(FEVER_RECORD, source_id="bad-benchmark", benchmark_claim=True)
            manifest.write_text(
                json.dumps(good, sort_keys=True)
                + "\n"
                + json.dumps(bad, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ProvenanceValidationError, "exclude source: benchmark claim is disallowed"
            ):
                load_source_manifest(manifest)

    def test_committed_manifest_records_fever_claims_as_pre_item_source_only(self):
        manifest = Path("data/evidence_state/source_manifest.jsonl")
        records = load_source_manifest(manifest)

        self.assertEqual([record.source_id for record in records], [FEVER_RECORD["source_id"]])
        record = records[0]
        self.assertEqual(record.local_path, "data/raw/fever/paper_dev.jsonl")
        self.assertEqual(record.line_count, 9999)
        self.assertEqual(record.licenses, ("cc-by-sa-3.0", "gpl-3.0"))
        self.assertIn("raw claims alone are not sufficient evidence text", record.provenance_boundary)
        self.assertFalse(record.benchmark_claim)


if __name__ == "__main__":
    unittest.main()
