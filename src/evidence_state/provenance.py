from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Tuple


REQUIRED_FIELDS = (
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
)
RETIRED_SOURCE_REASONS = {
    "old-manuscript-artifact": "retired manuscript artifact",
    "retired-experiment-output": "retired experiment output",
    "unpublished-review-packet": "unpublished review packet",
    "unlabeled-jsonl": "unlabeled source jsonl",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ProvenanceValidationError(ValueError):
    """Raised when a source cannot be admitted into evidence-state provenance."""


@dataclass(frozen=True)
class SourceManifestRecord:
    source_id: str
    source_name: str
    source_url: str
    license_or_terms_url: str
    licenses: Tuple[str, ...]
    retrieved_utc: str
    raw_record_hash: str
    transform_script: str
    derived_item_hash: str
    redistributable_text: bool
    byte_size: int
    sha256: str
    revision: str
    local_path: str
    download_command: str
    intended_preprocessing: str
    provenance_boundary: str
    benchmark_claim: bool
    line_count: int | None = None
    dataset_card_url: str | None = None


def validate_source_manifest_record(
    row: Mapping[str, Any],
) -> SourceManifestRecord:
    if not isinstance(row, Mapping):
        _exclude("row must be a JSON object")

    source_type = row.get("source_type")
    if source_type in RETIRED_SOURCE_REASONS:
        _exclude(RETIRED_SOURCE_REASONS[str(source_type)])

    for field_name in REQUIRED_FIELDS:
        if field_name not in row:
            _exclude(f"missing required field {field_name}")

    if row.get("benchmark_claim") is True:
        _exclude("benchmark claim is disallowed")

    licenses = _licenses(row.get("licenses"))
    if not licenses or not _text(row.get("license_or_terms_url")):
        _exclude("missing license data")

    source_id = row.get("source_id", "")
    if not _text(source_id):
        _exclude("missing required field source_id")

    sha256 = str(row["sha256"]).lower()
    raw_record_hash = str(row["raw_record_hash"]).lower()
    if not SHA256_RE.match(sha256):
        _exclude("sha256 must be a lowercase 64-character hex digest")
    if not SHA256_RE.match(raw_record_hash) and raw_record_hash != "pending-item-builder":
        _exclude("raw_record_hash must be a lowercase 64-character hex digest")

    if not UTC_RE.match(str(row["retrieved_utc"])):
        _exclude("retrieved_utc must be UTC in YYYY-MM-DDTHH:MM:SSZ form")

    byte_size = row["byte_size"]
    if not isinstance(byte_size, int) or byte_size <= 0:
        _exclude("byte_size must be a positive integer")

    line_count = row.get("line_count")
    if line_count is not None and (
        not isinstance(line_count, int) or line_count <= 0
    ):
        _exclude("line_count must be a positive integer")

    redistributable_text = row["redistributable_text"]
    if not isinstance(redistributable_text, bool):
        _exclude("redistributable_text must be true or false")

    for field_name in (
        "source_name",
        "source_url",
        "revision",
        "local_path",
        "download_command",
        "transform_script",
        "derived_item_hash",
        "intended_preprocessing",
    ):
        if not _text(row[field_name]):
            _exclude(f"{field_name} must be non-empty text")

    return SourceManifestRecord(
        source_id=str(source_id),
        source_name=str(row["source_name"]),
        source_url=str(row["source_url"]),
        license_or_terms_url=str(row["license_or_terms_url"]),
        licenses=licenses,
        retrieved_utc=str(row["retrieved_utc"]),
        raw_record_hash=raw_record_hash,
        transform_script=str(row["transform_script"]),
        derived_item_hash=str(row["derived_item_hash"]),
        redistributable_text=redistributable_text,
        byte_size=byte_size,
        sha256=sha256,
        revision=str(row["revision"]),
        local_path=str(row["local_path"]),
        download_command=str(row["download_command"]),
        intended_preprocessing=str(row["intended_preprocessing"]),
        provenance_boundary=str(row.get("provenance_boundary", "")),
        benchmark_claim=bool(row.get("benchmark_claim", False)),
        line_count=line_count,
        dataset_card_url=_optional_text(row.get("dataset_card_url")),
    )


def load_source_manifest(manifest_path: Path) -> Tuple[SourceManifestRecord, ...]:
    records = []
    with manifest_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProvenanceValidationError(
                    f"exclude source: invalid JSON on line {line_number}: {exc.msg}"
                ) from exc
            records.append(validate_source_manifest_record(row))
    return tuple(records)


def _licenses(value: Any) -> Tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    licenses = []
    for item in value:
        if not _text(item):
            return ()
        licenses.append(str(item))
    return tuple(licenses)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not _text(value):
        _exclude("optional URL fields must be non-empty text when present")
    return str(value)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _exclude(reason: str) -> None:
    raise ProvenanceValidationError(f"exclude source: {reason}")
