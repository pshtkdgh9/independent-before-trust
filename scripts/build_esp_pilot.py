"""Build a deterministic ESP candidate manifest from a pinned Parquet split."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp.core import build_pilot_items


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--source-revision", required=True)
    args = parser.parse_args()

    table = pq.read_table(args.input)
    records = table.to_pylist()
    items = build_pilot_items(records, limit=args.limit)
    if len(items) < args.limit:
        raise ValueError(f"requested {args.limit} items but extracted {len(items)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for item in items:
            handle.write(json.dumps(asdict(item), ensure_ascii=False, sort_keys=True) + "\n")

    report = {
        "source_path": args.input.as_posix(),
        "source_revision": args.source_revision,
        "source_bytes": args.input.stat().st_size,
        "source_sha256": sha256_file(args.input),
        "source_records": table.num_rows,
        "selection": "source order; abstract section only; first fixed-lexicon frames",
        "limit": args.limit,
        "output_path": args.output.as_posix(),
        "output_bytes": args.output.stat().st_size,
        "output_sha256": sha256_file(args.output),
    }
    report_path = args.output.with_suffix(".provenance.json")
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
