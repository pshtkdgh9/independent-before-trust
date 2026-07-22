"""Download one immutable public file atomically and append provenance."""

from __future__ import annotations

import argparse
import os
import shlex
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lad.provenance import record_downloaded_file, sha256_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--artifact-type", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--terms-url", required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data_provenance/manifest.jsonl"),
    )
    args = parser.parse_args()

    args.destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=args.destination.name + ".", dir=args.destination.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        with urllib.request.urlopen(args.url) as response, temporary_path.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        actual_sha256 = sha256_file(temporary_path)
        if args.expected_sha256 and actual_sha256 != args.expected_sha256:
            raise ValueError(
                f"checksum mismatch: expected {args.expected_sha256}, got {actual_sha256}"
            )
        temporary_path.replace(args.destination)
    finally:
        temporary_path.unlink(missing_ok=True)

    command_parts = [
        "python", "scripts/download_public_file.py", "--url", args.url,
        "--destination", str(args.destination), "--artifact-type", args.artifact_type,
        "--name", args.name, "--revision", args.revision, "--license", args.license,
        "--terms-url", args.terms_url, "--manifest", str(args.manifest),
    ]
    if args.expected_sha256:
        command_parts.extend(["--expected-sha256", args.expected_sha256])
    record_downloaded_file(
        file_path=args.destination,
        manifest_path=args.manifest,
        artifact_type=args.artifact_type,
        name=args.name,
        source_url=args.url,
        revision=args.revision,
        license_name=args.license,
        terms_url=args.terms_url,
        access_timestamp=datetime.now(timezone.utc).isoformat(),
        download_command=" ".join(shlex.quote(part) for part in command_parts),
    )


if __name__ == "__main__":
    main()
