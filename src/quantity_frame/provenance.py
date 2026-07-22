"""Provenance validation for quantity-frame source acquisition."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


REQUIRED_FIELDS = (
    "name",
    "revision",
    "canonical_url",
    "license",
    "license_url",
    "accessed_utc",
    "raw_path",
    "bytes",
    "sha256",
    "artifact_url",
    "download_command",
    "redistribution",
    "intended_role",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ProvenanceError(ValueError):
    """Raised when a quantity-frame source record is invalid."""


@dataclass(frozen=True)
class SourceRecord:
    name: str
    canonical_url: str
    revision: str
    license: str
    license_url: str
    accessed_utc: str
    raw_path: str
    bytes: int
    sha256: str
    download_command: str
    redistribution: str
    intended_role: str
    artifact_url: str
    source_locator_url: str | None = None
    archive_member: str | None = None
    derived_from_path: str | None = None
    derived_from_sha256: str | None = None
    extraction_command: str | None = None
    google_drive_file_id: str | None = None

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "SourceRecord":
        if not isinstance(row, Mapping):
            raise ProvenanceError("record must be a JSON object")

        for field in REQUIRED_FIELDS:
            if field not in row:
                raise ProvenanceError(f"missing: {field}")

        text_fields = (
            "name",
            "canonical_url",
            "revision",
            "license",
            "license_url",
            "accessed_utc",
            "raw_path",
            "sha256",
            "artifact_url",
            "download_command",
            "redistribution",
            "intended_role",
        )
        for field in text_fields:
            if not _non_empty_text(row[field]):
                raise ProvenanceError(f"{field} must be non-empty text")

        bytes_value = row["bytes"]
        if not isinstance(bytes_value, int) or bytes_value <= 0:
            raise ProvenanceError("bytes must be positive")

        if not UTC_RE.match(str(row["accessed_utc"])):
            raise ProvenanceError("accessed_utc must be UTC YYYY-MM-DDTHH:MM:SSZ")

        sha256 = str(row["sha256"]).lower()
        if not SHA256_RE.match(sha256):
            raise ProvenanceError("sha256 must be lowercase 64-hex")
        optional_text_fields = (
            "source_locator_url",
            "archive_member",
            "derived_from_path",
            "extraction_command",
            "google_drive_file_id",
        )
        for field in optional_text_fields:
            if field in row and not _non_empty_text(row[field]):
                raise ProvenanceError(f"{field} must be non-empty text")

        derived_from_sha256 = row.get("derived_from_sha256")
        if derived_from_sha256 is not None:
            derived_from_sha256 = str(derived_from_sha256).lower()
            if not SHA256_RE.match(derived_from_sha256):
                raise ProvenanceError("derived_from_sha256 must be lowercase 64-hex")

        return cls(
            name=str(row["name"]),
            canonical_url=str(row["canonical_url"]),
            revision=str(row["revision"]),
            license=str(row["license"]),
            license_url=str(row["license_url"]),
            accessed_utc=str(row["accessed_utc"]),
            raw_path=str(row["raw_path"]),
            bytes=bytes_value,
            sha256=sha256,
            download_command=str(row["download_command"]),
            redistribution=str(row["redistribution"]),
            intended_role=str(row["intended_role"]),
            artifact_url=str(row["artifact_url"]),
            source_locator_url=_optional_str(row, "source_locator_url"),
            archive_member=_optional_str(row, "archive_member"),
            derived_from_path=_optional_str(row, "derived_from_path"),
            derived_from_sha256=derived_from_sha256,
            extraction_command=_optional_str(row, "extraction_command"),
            google_drive_file_id=_optional_str(row, "google_drive_file_id"),
        )

    def to_dict(self) -> dict[str, Any]:
        record = {
            "name": self.name,
            "canonical_url": self.canonical_url,
            "revision": self.revision,
            "license": self.license,
            "license_url": self.license_url,
            "accessed_utc": self.accessed_utc,
            "raw_path": self.raw_path,
            "bytes": self.bytes,
            "sha256": self.sha256,
            "artifact_url": self.artifact_url,
            "download_command": self.download_command,
            "redistribution": self.redistribution,
            "intended_role": self.intended_role,
        }
        if self.source_locator_url is not None:
            record["source_locator_url"] = self.source_locator_url
        if self.archive_member is not None:
            record["archive_member"] = self.archive_member
        if self.derived_from_path is not None:
            record["derived_from_path"] = self.derived_from_path
        if self.derived_from_sha256 is not None:
            record["derived_from_sha256"] = self.derived_from_sha256
        if self.extraction_command is not None:
            record["extraction_command"] = self.extraction_command
        if self.google_drive_file_id is not None:
            record["google_drive_file_id"] = self.google_drive_file_id
        return record


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> tuple[SourceRecord, ...]:
    records: list[SourceRecord] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProvenanceError(
                    f"invalid JSON on line {line_number}: {exc.msg}"
                ) from exc
            try:
                records.append(SourceRecord.from_dict(row))
            except ProvenanceError as exc:
                raise ProvenanceError(f"line {line_number}: {exc}") from exc
    return tuple(records)


def verify_manifest(path: Path) -> tuple[int, int]:
    records = load_manifest(path)
    failures = 0
    for record in records:
        raw_path = Path(record.raw_path)
        if not raw_path.is_file():
            failures += 1
            continue
        if raw_path.stat().st_size != record.bytes:
            failures += 1
            continue
        if sha256_file(raw_path) != record.sha256:
            failures += 1
    return len(records), failures


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _optional_str(row: Mapping[str, Any], field: str) -> str | None:
    value = row.get(field)
    return None if value is None else str(value)
