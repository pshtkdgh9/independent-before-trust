"""Acquire and verify pinned quantity-frame source artifacts."""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import re
import shutil
import sys
import urllib.parse
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
ELIFE_DRIVE_FILE_ID = "1WKW8BAqluOlXrpy1B9mV3j3CtAK3JdnE"
SOURCES = (
    {
        "name": "GEM/cochrane-simplification validation",
        "canonical_url": "https://huggingface.co/datasets/GEM/cochrane-simplification",
        "artifact_url": "https://huggingface.co/datasets/GEM/cochrane-simplification/resolve/75a92ae445171fa1b7641a229bfe3c77c0d8723d/validation.json",
        "revision": "75a92ae445171fa1b7641a229bfe3c77c0d8723d",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "raw_path": "data/raw/quantity_frame/cochrane-simplification/75a92ae445171fa1b7641a229bfe3c77c0d8723d/validation.json",
        "expected_sha256": "18c883a77ff20f718b71c05251146d9648022f277cd4dc345b43820cd6ba2d5f",
        "redistribution": "metadata, script, and hashes only; raw corpus remains git-ignored",
        "intended_role": "source acquisition for development prevalence estimation; no preprocessing",
    },
    {
        "name": "tomasg25/scientific_lay_summarisation loader",
        "canonical_url": "https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation",
        "artifact_url": "https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation/resolve/9e109befb07bfb993843991d09b8aa6ee40b9267/scientific_lay_summarisation.py",
        "revision": "9e109befb07bfb993843991d09b8aa6ee40b9267",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "raw_path": "data/raw/quantity_frame/scientific_lay_summarisation/9e109befb07bfb993843991d09b8aa6ee40b9267/scientific_lay_summarisation.py",
        "expected_sha256": "07adb618266d5caf198815d61d338e1f23d2bab8b7afd3833a615cf37314e260",
        "redistribution": "metadata, script, hashes, and acquisition command only; raw corpus remains git-ignored",
        "intended_role": "loader provenance for Google Drive archive locator; no preprocessing",
    },
    {
        "name": "tomasg25/scientific_lay_summarisation eLife Google Drive archive",
        "canonical_url": "https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation",
        "artifact_url": f"https://drive.google.com/file/d/{ELIFE_DRIVE_FILE_ID}/view",
        "google_drive_file_id": ELIFE_DRIVE_FILE_ID,
        "source_locator_url": "https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation/resolve/9e109befb07bfb993843991d09b8aa6ee40b9267/scientific_lay_summarisation.py",
        "revision": "9e109befb07bfb993843991d09b8aa6ee40b9267",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "raw_path": "data/raw/quantity_frame/scientific_lay_summarisation/9e109befb07bfb993843991d09b8aa6ee40b9267/elife_archive.zip",
        "expected_sha256": "b0d11e4475f5ffd6a8c1875f7b6b2a6be3c4afc67c4682c2dbf43a1611a8e1a0",
        "redistribution": "metadata, script, hashes, and acquisition command only; raw corpus remains git-ignored",
        "intended_role": "bulk archive source acquisition for validation split extraction; no preprocessing",
    },
    {
        "name": "tomasg25/scientific_lay_summarisation eLife validation",
        "canonical_url": "https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation",
        "artifact_url": f"https://drive.google.com/file/d/{ELIFE_DRIVE_FILE_ID}/view#member=val.json",
        "google_drive_file_id": ELIFE_DRIVE_FILE_ID,
        "source_locator_url": "https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation/resolve/9e109befb07bfb993843991d09b8aa6ee40b9267/scientific_lay_summarisation.py",
        "revision": "9e109befb07bfb993843991d09b8aa6ee40b9267",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "archive_path": "data/raw/quantity_frame/scientific_lay_summarisation/9e109befb07bfb993843991d09b8aa6ee40b9267/elife_archive.zip",
        "archive_expected_sha256": "b0d11e4475f5ffd6a8c1875f7b6b2a6be3c4afc67c4682c2dbf43a1611a8e1a0",
        "archive_member": "val.json",
        "raw_path": "data/raw/quantity_frame/scientific_lay_summarisation/9e109befb07bfb993843991d09b8aa6ee40b9267/elife_val.json",
        "expected_sha256": "24fe7b98f04d2e6e5a80dda26ba241d5742de0f02c9e13a33121cabd98e9aeed",
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
            ensure_archive_artifact(source, archive_path)
            actual_member = extract_member(
                archive_path,
                str(source["archive_member"]),
                raw_path,
            )
        else:
            ensure_source_artifact(source, raw_path)
            actual_member = None
        row = {
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
        if row["sha256"] != source["expected_sha256"]:
            raise RuntimeError(f"unexpected sha256 for {raw_path}")
        for field in ("source_locator_url", "google_drive_file_id"):
            if field in source:
                row[field] = source[field]
        if "archive_path" in source:
            row["archive_member"] = actual_member
            row["derived_from_path"] = Path(str(source["archive_path"])).as_posix()
            row["derived_from_sha256"] = sha256_file(Path(str(source["archive_path"])))
            row["extraction_command"] = (
                f"python scripts/acquire_quantity_frame_sources.py --manifest {args.manifest.as_posix()}"
            )
        record = SourceRecord.from_dict(row)
        records.append(record)

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    print(f"acquired_sources={len(records)} manifest={args.manifest.as_posix()}")
    return 0


def ensure_source_artifact(source: dict[str, object], destination: Path) -> None:
    expected_sha256 = str(source["expected_sha256"])
    if "google_drive_file_id" in source:
        download_google_drive(
            str(source["google_drive_file_id"]),
            destination,
            expected_sha256,
        )
        return
    download(str(source["artifact_url"]), destination, expected_sha256)


def ensure_archive_artifact(source: dict[str, object], destination: Path) -> None:
    expected_sha256 = str(source["archive_expected_sha256"])
    if "google_drive_file_id" in source:
        download_google_drive(
            str(source["google_drive_file_id"]),
            destination,
            expected_sha256,
        )
        return
    download(str(source["artifact_url"]), destination, expected_sha256)


def download(url: str, destination: Path, expected_sha256: str) -> None:
    expected_sha256 = expected_sha256.lower()
    if destination.is_file() and sha256_file(destination) == expected_sha256:
        return
    temp_path = destination.with_name(f"{destination.name}.tmp")
    request = urllib.request.Request(url, headers={"User-Agent": "codex-provenance/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        with temp_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    if sha256_file(temp_path) != expected_sha256:
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(f"downloaded sha256 mismatch for {destination}")
    temp_path.replace(destination)


def download_google_drive(file_id: str, destination: Path, expected_sha256: str) -> None:
    expected_sha256 = expected_sha256.lower()
    if destination.is_file() and sha256_file(destination) == expected_sha256:
        return

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    response = _open_drive_response(opener, file_id)
    token = _drive_confirm_token(cookie_jar)
    if token is None:
        token = _drive_confirm_token_from_url(getattr(response, "url", ""))
    if token is not None:
        response.close()
        response = _open_drive_response(opener, file_id, confirm=token)

    temp_path = destination.with_name(f"{destination.name}.tmp")
    with response:
        with temp_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    if sha256_file(temp_path) != expected_sha256:
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(f"downloaded sha256 mismatch for {destination}")
    temp_path.replace(destination)


def _open_drive_response(opener, file_id: str, confirm: str | None = None):
    query = {"export": "download", "id": file_id}
    if confirm is not None:
        query["confirm"] = confirm
    url = f"https://drive.google.com/uc?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(url, headers={"User-Agent": "codex-provenance/1.0"})
    return opener.open(request, timeout=120)


def _drive_confirm_token(cookie_jar: http.cookiejar.CookieJar) -> str | None:
    for cookie in cookie_jar:
        if cookie.name.startswith("download_warning"):
            return cookie.value
    return None


def _drive_confirm_token_from_url(url: str) -> str | None:
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    values = query.get("confirm")
    if values:
        return values[0]
    match = re.search(r"confirm=([0-9A-Za-z_-]+)", url)
    return None if match is None else match.group(1)


def extract_member(archive_path: Path, member_name: str, destination: Path) -> str:
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if member_name in names:
            matches = [member_name]
        else:
            matches = [name for name in names if name.endswith(f"/{member_name}")]
        if not matches:
            raise FileNotFoundError(f"{member_name} not found in {archive_path}")
        if len(matches) > 1:
            raise ValueError(f"ambiguous archive member {member_name} in {archive_path}")
        with archive.open(matches[0]) as source, destination.open("wb") as target:
            shutil.copyfileobj(source, target)
        return matches[0]


if __name__ == "__main__":
    raise SystemExit(main())
