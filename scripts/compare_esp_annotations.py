"""Validate two independent ESP annotation files and report agreement."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp.core import annotation_agreement, validate_annotations


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = read_jsonl(args.manifest)
    left = read_jsonl(args.left)
    right = read_jsonl(args.right)
    item_ids = [str(row["item_id"]) for row in manifest]
    validate_annotations(item_ids, left)
    validate_annotations(item_ids, right)
    report = annotation_agreement(left, right)
    report["disagreements"] = {
        field: [
            str(a["item_id"])
            for a, b in zip(left, right)
            if str(a.get(field)) != str(b.get(field))
        ]
        for field in ("cue_valid", "strength", "attribution", "retain_in_lay_rewrite")
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
