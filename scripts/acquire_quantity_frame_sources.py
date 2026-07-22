"""Acquire and verify pinned quantity-frame source artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.quantity_frame.provenance import (
    SourceRecord,
    sha256_file,
    verify_manifest,
)


ACCESS_TIME = "2026-07-23T00:00:00Z"
DEFAULT_MANIFEST_PATH = Path("data_provenance/quantity_frame_manifest.jsonl")
SOURCES = (
    {
        "name": "GEM/cochrane-simplification validation",
        "canonical_url": "https://huggingface.co/datasets/GEM/cochrane-simplification",
        "artifact_url": "https://huggingface.co/datasets/GEM/cochrane-simplification/resolve/75a92ae445171fa1b7641a229bfe3c77c0d8723d/validation.json",
        "revision": "75a92ae445171fa1b7641a229bfe3c77c0d8723d",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "raw_path": "data/raw/quantity_frame/cochrane-simplification/75a92ae445171fa1b7641a229bfe3c77c0d8723d/validation.json",
        "redistribution": "metadata, script, and hashes only; raw corpus remains git-ignored",
        "intended_role": "source acquisition for development prevalence estimation; no preprocessing",
    },
    {
        "name": "tomasg25/scientific_lay_summarisation eLife validation",
        "canonical_url": "https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation",
        "artifact_url": "https://drive.usercontent.google.com/download?id=1WKW8BAqluOlXrpy1B9mV3j3CtAK3JdnE&export=download&authuser=1&confirm=t&uuid=1332bc11-7cbf-4c4d-8561-85621060f397&at=APZUnTVLLKAGVSBpQlYKojrJ57xb%3A1716450570186",
        "source_locator_url": "https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation/resolve/9e109befb07bfb993843991d09b8aa6ee40b9267/scientific_lay_summarisation.py",
        "revision": "9e109befb07bfb993843991d09b8aa6ee40b9267",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "archive_path": "data/raw/quantity_frame/scientific_lay_summarisation/9e109befb07bfb993843991d09b8aa6ee40b9267/elife_archive.zip",
        "archive_member": "val.json",
        "raw_path": "data/raw/quantity_frame/scientific_lay_summarisation/9e109befb07bfb993843991d09b8aa6ee40b9267/elife_val.json",
        "redistribution": "metadata, script, hashes, and acquisition command only; raw corpus remains git-ignored",
        "intended_role": "source acquisition for development prevalence estimation; no preprocessing",
    },
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="JSONL manifest path to write or verify",
    )
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    if args.verify_only:
        verified, failures = verify_manifest(args.manifest)
        print(f"verified_sources={verified} failures={failures}")
        return 0 if failures == 0 else 1

    records = []
    for source in SOURCES:
        raw_path = Path(str(source["raw_path"]))
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        if "archive_path" in source:
            archive_path = Path(str(source["archive_path"]))
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            download(str(source["artifact_url"]), archive_path)
            extract_member(
                archive_path,
                str(source["archive_member"]),
                raw_path,
            )
        else:
            download(str(source["artifact_url"]), raw_path)
        record = SourceRecord.from_dict(
            {
                "name": source["name"],
                "canonical_url": source["canonical_url"],
                "revision": source["revision"],
                "license": source["license"],
                "license_url": source["license_url"],
                "accessed_utc": ACCESS_TIME,
                "raw_path": raw_path.as_posix(),
                "bytes": raw_path.stat().st_size,
                "sha256": sha256_file(raw_path),
                "artifact_url": source["artifact_url"],
                "download_command": (
                    f"python scripts/acquire_quantity_frame_sources.py --manifest {args.manifest.as_posix()}"
                ),
                "redistribution": source["redistribution"],
                "intended_role": source["intended_role"],
            }
        )
        records.append(record)

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    print(f"acquired_sources={len(records)} manifest={args.manifest.as_posix()}")
    return 0


def download(url: str, destination: Path) -> None:
    if destination.is_file() and destination.stat().st_size > 0:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "codex-provenance/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        with destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)


def extract_member(archive_path: Path, member_name: str, destination: Path) -> None:
    with zipfile.ZipFile(archive_path) as archive:
        matches = [name for name in archive.namelist() if name.endswith(member_name)]
        if not matches:
            raise FileNotFoundError(f"{member_name} not found in {archive_path}")
        with archive.open(matches[0]) as source, destination.open("wb") as target:
            shutil.copyfileobj(source, target)


if __name__ == "__main__":
    raise SystemExit(main())
