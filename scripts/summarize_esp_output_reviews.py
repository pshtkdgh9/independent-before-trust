#!/usr/bin/env python
"""Summarize two condition-blind ESP development audits."""

import argparse
import json
from collections import defaultdict
from pathlib import Path


FIELDS = ("strength_preserved", "scope_preserved", "unsupported_addition", "acceptable_lay_rewrite")


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--review-a", type=Path, required=True)
    parser.add_argument("--review-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    key_rows = read_jsonl(args.key)
    reviews = {"a": read_jsonl(args.review_a), "b": read_jsonl(args.review_b)}
    key = {row["review_id"]: row for row in key_rows}
    if len(key) != len(key_rows):
        raise ValueError("duplicate review_id in key")
    for name, rows in reviews.items():
        if [row["review_id"] for row in rows] != [row["review_id"] for row in key_rows]:
            raise ValueError(f"review {name} does not match key order")

    by_id = {name: {row["review_id"]: row for row in rows} for name, rows in reviews.items()}
    summary = {"items": len(key_rows), "agreement": {}, "by_run": {}}
    for field in FIELDS:
        summary["agreement"][field] = sum(
            by_id["a"][rid][field] == by_id["b"][rid][field] for rid in key
        ) / len(key)

    grouped = defaultdict(list)
    for row in key_rows:
        grouped[row["run"]].append(row["review_id"])
    for run, ids in sorted(grouped.items()):
        result = {"items": len(ids)}
        for reviewer in ("a", "b"):
            result[reviewer] = {
                field: {
                    label: sum(by_id[reviewer][rid][field] == label for rid in ids)
                    for label in ("yes", "no", "unclear")
                }
                for field in FIELDS
            }
        result["strict_consensus"] = {
            "strength_preserved_yes": sum(
                by_id["a"][rid]["strength_preserved"] == "yes"
                and by_id["b"][rid]["strength_preserved"] == "yes" for rid in ids
            ),
            "scope_preserved_yes": sum(
                by_id["a"][rid]["scope_preserved"] == "yes"
                and by_id["b"][rid]["scope_preserved"] == "yes" for rid in ids
            ),
            "unsupported_addition_either_yes": sum(
                by_id["a"][rid]["unsupported_addition"] == "yes"
                or by_id["b"][rid]["unsupported_addition"] == "yes" for rid in ids
            ),
            "acceptable_both_yes": sum(
                by_id["a"][rid]["acceptable_lay_rewrite"] == "yes"
                and by_id["b"][rid]["acceptable_lay_rewrite"] == "yes" for rid in ids
            ),
        }
        summary["by_run"][run] = result
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
