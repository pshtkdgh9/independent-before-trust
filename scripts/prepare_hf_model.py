"""Download a pinned Hugging Face snapshot and append its provenance record."""

from __future__ import annotations

import argparse
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from huggingface_hub import snapshot_download

from src.lad.provenance import record_local_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--terms-url", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data_provenance/manifest.jsonl"),
    )
    args = parser.parse_args()

    resolved = snapshot_download(
        repo_id=args.model_id,
        revision=args.revision,
        local_dir=args.output_dir,
    )
    command = " ".join(shlex.quote(part) for part in [
        "python", "scripts/prepare_hf_model.py",
        "--model-id", args.model_id,
        "--revision", args.revision,
        "--license", args.license,
        "--terms-url", args.terms_url,
        "--output-dir", str(args.output_dir),
        "--manifest", str(args.manifest),
    ])
    record_local_snapshot(
        snapshot_dir=Path(resolved),
        manifest_path=args.manifest,
        name=args.model_id,
        source_url=f"https://huggingface.co/{args.model_id}",
        revision=args.revision,
        license_name=args.license,
        terms_url=args.terms_url,
        access_timestamp=datetime.now(timezone.utc).isoformat(),
        download_command=command,
    )


if __name__ == "__main__":
    main()
