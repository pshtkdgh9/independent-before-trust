#!/usr/bin/env python
"""Build a condition-blind semantic review packet from ESP generations."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp.core import blind_review_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    args = parser.parse_args()

    annotations = {
        row["item_id"]: row
        for row in map(json.loads, args.annotations.read_text(encoding="utf-8").splitlines())
        if row.get("cue_valid") == "yes"
    }
    packet = []
    key = []
    for path in sorted(args.artifact_root.glob("esp-*/generations.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            generation = json.loads(line)
            item_id = generation["item_id"]
            annotation = annotations[item_id]
            review_id = blind_review_id(item_id, generation["condition"], path.parent.name)
            source = generation["prompt"].split("SOURCE:\n", 1)[1]
            packet.append({
                "review_id": review_id,
                "source": source,
                "gold_strength": annotation["strength"],
                "gold_scope": annotation["scope_text"],
                "gold_attribution": annotation["attribution"],
                "output": generation["raw_output"],
            })
            key.append({
                "review_id": review_id,
                "item_id": item_id,
                "condition": generation["condition"],
                "run": path.parent.name,
            })
    packet.sort(key=lambda row: row["review_id"])
    key.sort(key=lambda row: row["review_id"])
    args.packet.parent.mkdir(parents=True, exist_ok=True)
    args.packet.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in packet) + "\n", encoding="utf-8")
    args.key.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in key) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
