import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from src.quantity_frame import CandidateItem, retrieve_candidates


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "build_quantity_frame_candidates.py"
)
SCRIPT_SPEC = importlib.util.spec_from_file_location(
    "build_quantity_frame_candidates", SCRIPT_PATH
)
assert SCRIPT_SPEC and SCRIPT_SPEC.loader
build_quantity_frame_candidates = importlib.util.module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(build_quantity_frame_candidates)


@pytest.mark.parametrize(
    ("text", "cue_type", "span"),
    [
        ("Treatment helped 18% after 6 months.", "percentage", "18%"),
        ("Treatment helped 12 of 100 participants.", "fraction", "12 of 100"),
        ("There were 42 deaths compared with placebo.", "count", "42 deaths"),
        ("Patients received 3.2 mg versus 1.4 mg.", "unit", "3.2 mg"),
        ("Pain improved after 6 months.", "time_window", "after 6 months"),
        ("Symptoms improved versus placebo.", "comparison", "versus placebo"),
    ],
)
def test_retrieve_candidates_finds_conservative_quantity_and_context_cues(
    text, cue_type, span
):
    records = retrieve_candidates(text)

    assert any(record.cue_type == cue_type and record.text == span for record in records)


def test_retrieve_candidates_suppresses_duplicates_and_preserves_source_order():
    records = retrieve_candidates(
        "18% improved. After 6 months, 18% improved versus placebo."
    )

    assert [record.text for record in records] == [
        "18%",
        "After 6 months",
        "versus placebo",
    ]


def test_retrieve_candidates_excludes_obvious_years_citations_and_section_numbers():
    records = retrieve_candidates("In 2020, section 3.2 cited [12] without results.")

    assert records == ()


def test_retrieve_candidates_reports_exclusion_reasons():
    diagnostics = build_quantity_frame_candidates.scan_text("In 2020, see [12].")

    assert diagnostics.candidates == ()
    assert diagnostics.exclusions == {
        "year_without_quantity_context": 1,
        "citation_number_without_quantity_context": 1,
    }


def _manifest_record(tmp_path, name, raw_path):
    data = raw_path.read_bytes()
    return {
        "name": name,
        "canonical_url": "https://example.test/dataset",
        "revision": "abc123",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "accessed_utc": "2026-07-23T00:00:00Z",
        "raw_path": raw_path.as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "artifact_url": "https://example.test/artifact.json",
        "download_command": "download",
        "redistribution": "metadata only; raw corpus remains git-ignored",
        "intended_role": "test fixture",
    }


def _write_manifest(tmp_path, cochrane_path, elife_path):
    manifest = tmp_path / "manifest.jsonl"
    rows = [
        _manifest_record(tmp_path, "GEM/cochrane-simplification validation", cochrane_path),
        _manifest_record(
            tmp_path,
            "tomasg25/scientific_lay_summarisation eLife validation",
            elife_path,
        ),
    ]
    manifest.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    return manifest


def test_builder_writes_candidate_only_items_with_hash_lineage_and_no_verdicts(tmp_path):
    cochrane_path = tmp_path / "validation.json"
    elife_path = tmp_path / "elife_val.json"
    cochrane_path.write_text(
        json.dumps(
            [
                {
                    "gem_id": "c1",
                    "doi": "10.1/example",
                    "source": "12 of 100 participants improved versus placebo.",
                    "target": "Twelve of one hundred improved.",
                }
            ]
        ),
        encoding="utf-8",
    )
    elife_path.write_text(
        json.dumps(
            [
                {
                    "id": "e1",
                    "abstract": "The dose was 3.2 mg after 6 months.",
                    "summary": "The dose was measured later.",
                }
            ]
        ),
        encoding="utf-8",
    )
    manifest = _write_manifest(tmp_path, cochrane_path, elife_path)
    output = tmp_path / "candidates.jsonl"
    metadata = tmp_path / "candidate_build.json"

    result = build_quantity_frame_candidates.build(
        manifest_path=manifest,
        output_path=output,
        metadata_path=metadata,
        per_corpus_limit=300,
        command="test command",
    )

    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    for row in rows:
        candidate = CandidateItem.from_dict(row)
        assert candidate.candidate_only is True
        assert "audit_verdict" not in row
        assert "gold_verdict" not in row
        assert row["source_record_hash"]
        assert row["source_text_hash"] == hashlib.sha256(
            row["source_text"].encode("utf-8")
        ).hexdigest()
        assert row["target_text_hash"] == hashlib.sha256(
            row["target_text"].encode("utf-8")
        ).hexdigest()

    assert result["candidate_only"] is True
    assert result["human_evidence"] is False
    assert result["experimental_claim"] is False
    assert "source_text" not in json.dumps(result)
    assert "target_text" not in json.dumps(result)


def test_builder_creates_metadata_parent_directory(tmp_path):
    cochrane_path = tmp_path / "validation.json"
    elife_path = tmp_path / "elife_val.json"
    cochrane_path.write_text(
        json.dumps(
            [
                {
                    "gem_id": "c1",
                    "source": "12 of 100 participants improved versus placebo.",
                    "target": "Twelve of one hundred improved.",
                }
            ]
        ),
        encoding="utf-8",
    )
    elife_path.write_text(
        json.dumps(
            [
                {
                    "id": "e1",
                    "abstract": "The dose was 3.2 mg after 6 months.",
                    "summary": "The dose was measured later.",
                }
            ]
        ),
        encoding="utf-8",
    )
    manifest = _write_manifest(tmp_path, cochrane_path, elife_path)
    metadata = tmp_path / "nested" / "candidate_build.json"

    build_quantity_frame_candidates.build(
        manifest_path=manifest,
        output_path=tmp_path / "candidates.jsonl",
        metadata_path=metadata,
        per_corpus_limit=300,
        command="test command",
    )

    assert metadata.is_file()


def test_builder_skips_duplicates_applies_per_corpus_limits_and_is_deterministic(tmp_path):
    cochrane_path = tmp_path / "validation.json"
    elife_path = tmp_path / "elife_val.json"
    cochrane_path.write_text(
        json.dumps(
            [
                {"gem_id": "c1", "source": "10% improved.", "target": "Ten percent."},
                {"gem_id": "c1b", "source": "10% improved.", "target": "Ten percent."},
                {"gem_id": "c2", "source": "20% improved.", "target": "Twenty percent."},
            ]
        ),
        encoding="utf-8",
    )
    elife_path.write_text(
        json.dumps(
            [
                {"id": "e1", "abstract": "1.2 mg versus placebo.", "summary": "Dose."},
                {"id": "e2", "abstract": "2.4 mg after 2 weeks.", "summary": "Dose."},
            ]
        ),
        encoding="utf-8",
    )
    manifest = _write_manifest(tmp_path, cochrane_path, elife_path)
    output = tmp_path / "candidates.jsonl"
    metadata = tmp_path / "candidate_build.json"

    first = build_quantity_frame_candidates.build(
        manifest_path=manifest,
        output_path=output,
        metadata_path=metadata,
        per_corpus_limit=1,
        command="test command",
    )
    second = build_quantity_frame_candidates.build(
        manifest_path=manifest,
        output_path=output,
        metadata_path=metadata,
        per_corpus_limit=1,
        command="test command",
    )

    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert [row["source_text"] for row in rows] == [
        "10% improved.",
        "1.2 mg versus placebo.",
    ]
    assert len({row["item_id"] for row in rows}) == 2
    assert all(row["item_id"].startswith("qf-candidate-") for row in rows)
    assert first["corpora"]["GEM/cochrane-simplification"]["duplicates_skipped"] == 1
    assert first["corpora"]["GEM/cochrane-simplification"]["candidates_written"] == 1
    assert first["corpora"]["tomasg25/scientific_lay_summarisation"]["candidates_written"] == 1
    assert first["output_sha256"] == second["output_sha256"]
    assert first["deterministic_second_run_sha256"] == first["output_sha256"]
