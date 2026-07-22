"""Build deterministic LAD pilot pairs from pinned BIG-bench source data."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lad.bigbench import build_logical_deduction_items
from src.lad.provenance import sha256_file


def _dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--provenance-log", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    records, summary = build_logical_deduction_items(payload, limit=args.limit)
    summary["seed"] = args.seed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    command = " ".join(shlex.quote(part) for part in [
        "python", "scripts/build_bigbench_pilot.py",
        "--input", str(args.input), "--output", str(args.output),
        "--provenance-log", str(args.provenance_log),
        "--source-url", args.source_url, "--revision", args.revision,
        "--seed", str(args.seed), "--limit", str(args.limit),
    ])
    provenance = {
        **summary,
        "source_url": args.source_url,
        "source_revision": args.revision,
        "source_path": args.input.as_posix(),
        "source_bytes": args.input.stat().st_size,
        "source_sha256": sha256_file(args.input),
        "output_path": args.output.as_posix(),
        "output_bytes": args.output.stat().st_size,
        "output_sha256": sha256_file(args.output),
        "preprocessing_command": command,
        "filtering_decisions": (
            "one task item per unique scenario; deterministic rotating item selection; "
            "no content filtering; no private answer injected during preprocessing"
        ),
        "privacy_or_consent": "synthetic object-order reasoning; no personal data",
        "redistribution": (
            "derived items and runtime pairs releasable with Apache-2.0 attribution"
        ),
    }
    _dump_json(args.provenance_log, provenance)


if __name__ == "__main__":
    main()
