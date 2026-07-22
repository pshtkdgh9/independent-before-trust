import json
import importlib.util
import zipfile
from io import BytesIO
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
        "artifact_url": "https://example.test/validation.json",
        "download_command": "python scripts/acquire_quantity_frame_sources.py",
        "redistribution": "metadata only; raw corpus remains git-ignored",
        "intended_role": "development prevalence estimation",
    }


def test_source_record_requires_revision():
    with pytest.raises(ProvenanceError, match="missing: revision"):
        SourceRecord.from_dict({"name": "cochrane"})


def test_source_record_requires_artifact_url(tmp_path):
    row = complete_record(tmp_path)
    del row["artifact_url"]

    with pytest.raises(ProvenanceError, match="missing: artifact_url"):
        SourceRecord.from_dict(row)


def test_source_record_validates_required_fields_and_canonical_sha(tmp_path):
    record = SourceRecord.from_dict(complete_record(tmp_path))

    assert record.sha256 == "a" * 64
    assert record.bytes > 0


def test_source_record_preserves_archive_lineage_fields(tmp_path):
    row = complete_record(tmp_path)
    row.update(
        {
            "source_locator_url": "https://huggingface.co/datasets/example/resolve/rev/loader.py",
            "archive_member": "val.json",
            "derived_from_path": "data/raw/example/archive.zip",
            "derived_from_sha256": "b" * 64,
            "extraction_command": "python scripts/acquire_quantity_frame_sources.py",
            "google_drive_file_id": "1abc",
        }
    )

    assert SourceRecord.from_dict(row).to_dict() == {
        **row,
        "sha256": "a" * 64,
    }


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


def test_download_replaces_stale_existing_file_after_hash_mismatch(tmp_path, monkeypatch):
    destination = tmp_path / "artifact.txt"
    destination.write_text("stale", encoding="utf-8")
    fresh = b"fresh"
    import hashlib

    class Response:
        def __enter__(self):
            return BytesIO(fresh)

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(acquire_quantity_frame_sources.urllib.request, "urlopen", lambda *args, **kwargs: Response())

    acquire_quantity_frame_sources.download(
        "https://example.test/artifact.txt",
        destination,
        expected_sha256=hashlib.sha256(fresh).hexdigest(),
    )

    assert destination.read_bytes() == fresh


def test_download_reuses_existing_file_only_when_hash_matches(tmp_path, monkeypatch):
    destination = tmp_path / "artifact.txt"
    destination.write_bytes(b"fresh")
    expected = acquire_quantity_frame_sources.sha256_file(destination)

    def fail_urlopen(*args, **kwargs):
        raise AssertionError("matching existing file should not be downloaded")

    monkeypatch.setattr(acquire_quantity_frame_sources.urllib.request, "urlopen", fail_urlopen)

    acquire_quantity_frame_sources.download(
        "https://example.test/artifact.txt",
        destination,
        expected_sha256=expected,
    )

    assert destination.read_bytes() == b"fresh"


def test_extract_member_rejects_ambiguous_suffix_matches(tmp_path):
    archive_path = tmp_path / "archive.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("a/val.json", "{}")
        archive.writestr("b/val.json", "{}")

    with pytest.raises(ValueError, match="ambiguous archive member"):
        acquire_quantity_frame_sources.extract_member(
            archive_path,
            "val.json",
            tmp_path / "val.json",
        )


def test_sources_use_stable_google_drive_locator_not_volatile_url():
    drive_sources = [
        source
        for source in acquire_quantity_frame_sources.SOURCES
        if "google_drive_file_id" in source
    ]

    assert drive_sources
    for source in drive_sources:
        assert source["google_drive_file_id"] == "1WKW8BAqluOlXrpy1B9mV3j3CtAK3JdnE"
        assert "drive.usercontent.google.com" not in str(source["artifact_url"])
        assert "confirm=" not in str(source["artifact_url"])
        assert "uuid=" not in str(source["artifact_url"])
        assert "at=" not in str(source["artifact_url"])


def test_repository_manifest_verifies_four_quantity_frame_artifacts():
    records = SourceRecord.from_dict
    manifest_records = [
        records(json.loads(line))
        for line in Path("data_provenance/quantity_frame_manifest.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    missing = [
        record.raw_path
        for record in manifest_records
        if not Path(record.raw_path).is_file()
    ]
    if missing:
        pytest.skip(f"raw quantity-frame artifacts absent: {', '.join(missing)}")

    assert (
        verify_manifest(Path("data_provenance/quantity_frame_manifest.jsonl"))
        == (4, 0)
    )
