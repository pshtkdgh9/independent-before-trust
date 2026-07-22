import json
import importlib.util
from pathlib import Path

import pytest

from src.quantity_frame.provenance import (
    ProvenanceError,
    SourceRecord,
    verify_manifest,
)


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "acquire_quantity_frame_sources.py"
SCRIPT_SPEC = importlib.util.spec_from_file_location(
    "acquire_quantity_frame_sources", SCRIPT_PATH
)
assert SCRIPT_SPEC and SCRIPT_SPEC.loader
acquire_quantity_frame_sources = importlib.util.module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(acquire_quantity_frame_sources)


def complete_record(tmp_path: Path) -> dict[str, object]:
    raw_file = tmp_path / "validation.json"
    raw_file.write_text('{"rows": []}\n', encoding="utf-8")
    return {
        "name": "GEM/cochrane-simplification validation",
        "canonical_url": "https://huggingface.co/datasets/GEM/cochrane-simplification",
        "revision": "4cb746692aa0964a4a1073e70fc8e2eab004f50a",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "accessed_utc": "2026-07-23T00:00:00Z",
        "raw_path": raw_file.as_posix(),
        "bytes": raw_file.stat().st_size,
        "sha256": "A" * 64,
        "download_command": "python scripts/acquire_quantity_frame_sources.py",
        "redistribution": "metadata only; raw corpus remains git-ignored",
        "intended_role": "development prevalence estimation",
    }


def test_source_record_requires_revision():
    with pytest.raises(ProvenanceError, match="missing: revision"):
        SourceRecord.from_dict({"name": "cochrane"})


def test_source_record_validates_required_fields_and_canonical_sha(tmp_path):
    record = SourceRecord.from_dict(complete_record(tmp_path))

    assert record.sha256 == "a" * 64
    assert record.bytes > 0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("sha256", "z" * 64, "sha256 must be lowercase 64-hex"),
        ("bytes", 0, "bytes must be positive"),
        ("accessed_utc", "2026-07-23", "accessed_utc must be UTC"),
        ("intended_role", "", "intended_role must be non-empty text"),
    ],
)
def test_source_record_rejects_invalid_values(tmp_path, field, value, message):
    row = complete_record(tmp_path)
    row[field] = value

    with pytest.raises(ProvenanceError, match=message):
        SourceRecord.from_dict(row)


def test_verify_manifest_rehashes_local_sources(tmp_path):
    row = complete_record(tmp_path)
    raw_path = Path(row["raw_path"])
    import hashlib

    row["sha256"] = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")

    assert verify_manifest(manifest) == (1, 0)


def test_acquire_cli_verifies_selected_manifest(tmp_path, monkeypatch, capsys):
    row = complete_record(tmp_path)
    raw_path = Path(row["raw_path"])
    import hashlib

    row["sha256"] = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    manifest = tmp_path / "selected_manifest.jsonl"
    manifest.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "acquire_quantity_frame_sources.py",
            "--manifest",
            manifest.as_posix(),
            "--verify-only",
        ],
    )

    assert acquire_quantity_frame_sources.main() == 0
    assert "verified_sources=1 failures=0" in capsys.readouterr().out
