"""Machine-readable provenance records for downloaded model snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _append_record(manifest_path: Path, record: dict[str, Any]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def record_downloaded_file(
    *,
    file_path: Path,
    manifest_path: Path,
    artifact_type: str,
    name: str,
    source_url: str,
    revision: str,
    license_name: str,
    terms_url: str,
    access_timestamp: str,
    download_command: str,
    privacy_or_consent: str,
    redistribution: str,
) -> dict[str, Any]:
    """Append provenance for one immutable downloaded source file."""
    if not file_path.is_file():
        raise ValueError(f"downloaded file does not exist: {file_path}")
    record: dict[str, Any] = {
        "artifact_type": artifact_type,
        "name": name,
        "source_url": source_url,
        "access_timestamp": access_timestamp,
        "revision": revision,
        "license": license_name,
        "terms_url": terms_url,
        "local_path": file_path.as_posix(),
        "bytes": file_path.stat().st_size,
        "sha256": sha256_file(file_path),
        "download_command": download_command,
        "privacy_or_consent": privacy_or_consent,
        "redistribution": redistribution,
    }
    _append_record(manifest_path, record)
    return record


def record_local_snapshot(
    *,
    snapshot_dir: Path,
    manifest_path: Path,
    name: str,
    source_url: str,
    revision: str,
    license_name: str,
    terms_url: str,
    access_timestamp: str,
    download_command: str | None = None,
) -> dict[str, Any]:
    """Append checksums for an immutable local Hugging Face snapshot."""
    if not snapshot_dir.is_dir():
        raise ValueError(f"snapshot directory does not exist: {snapshot_dir}")

    files = []
    for path in sorted(item for item in snapshot_dir.rglob("*") if item.is_file()):
        files.append(
            {
                "path": path.relative_to(snapshot_dir).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    if not files:
        raise ValueError("snapshot contains no files")

    record: dict[str, Any] = {
        "artifact_type": "huggingface-model-snapshot",
        "name": name,
        "source_url": source_url,
        "access_timestamp": access_timestamp,
        "revision": revision,
        "license": license_name,
        "terms_url": terms_url,
        "snapshot_path": snapshot_dir.as_posix(),
        "download_command": download_command,
        "preprocessing": "none",
        "redistribution": "weights not redistributed; users fetch from source",
        "files": files,
        "total_bytes": sum(item["bytes"] for item in files),
    }
    _append_record(manifest_path, record)
    return record
