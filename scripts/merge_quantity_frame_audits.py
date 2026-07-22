"""Merge completed model-audit shards against the blinded base packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_BASE = Path("results/strong_accept_loop/quantity_frame/audit_packet.jsonl")
DEFAULT_SHARDS = tuple(
    Path("results/strong_accept_loop/quantity_frame/model_audits") / name
    for name in (
        "reviewer_a_part0.jsonl",
        "reviewer_a_part1.jsonl",
        "reviewer_a_part2.jsonl",
        "reviewer_b_part0.jsonl",
        "reviewer_b_part1.jsonl",
        "reviewer_b_part2.jsonl",
    )
)
DEFAULT_OUTPUT = Path(
    "results/strong_accept_loop/quantity_frame/model_audit_packet.jsonl"
)
MUTABLE_FIELDS = {"annotation_status", "review_fields"}
COMPLETED_LABELS = {"yes", "no", "unclear"}
FRAME_SLOTS = {
    "value",
    "denominator_or_base",
    "subgroup",
    "time_window",
    "comparator",
    "unit",
}


def merge(
    *,
    base_path: Path,
    shard_paths: list[Path],
    output_path: Path,
    command: str,
) -> dict[str, Any]:
    base_rows = _read_jsonl(base_path)
    base_by_id = _unique_by_review_id(base_rows, source="base packet")

    shard_rows: list[dict[str, Any]] = []
    for shard_path in shard_paths:
        shard_rows.extend(_read_jsonl(shard_path))
    shard_by_id = _unique_by_review_id(shard_rows, source="audit shards")

    missing = sorted(set(base_by_id) - set(shard_by_id))
    unexpected = sorted(set(shard_by_id) - set(base_by_id))
    if missing:
        raise ValueError(f"missing review_id: {missing[0]}")
    if unexpected:
        raise ValueError(f"unexpected review_id: {unexpected[0]}")

    merged_rows: list[dict[str, Any]] = []
    for base_row in base_rows:
        review_id = str(base_row["review_id"])
        reviewed_row = shard_by_id[review_id]
        _validate_immutable_fields(base_row, reviewed_row, review_id)
        _validate_completed_review(reviewed_row, review_id)
        merged_rows.append(reviewed_row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_bytes = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
        for row in merged_rows
    ).encode("utf-8")
    output_path.write_bytes(output_bytes)
    input_paths = [base_path, *shard_paths]
    return {
        "command": command,
        "base_path": base_path.as_posix(),
        "shard_paths": [path.as_posix() for path in shard_paths],
        "output_path": output_path.as_posix(),
        "input_sha256s": {
            path.as_posix(): _sha256(path.read_bytes()) for path in input_paths
        },
        "output_sha256": _sha256(output_bytes),
        "output_bytes": len(output_bytes),
        "rows": len(merged_rows),
        "model_agent_development_only": True,
        "human_evidence": False,
    }


def _unique_by_review_id(
    rows: list[dict[str, Any]], *, source: str
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        review_id = str(row.get("review_id"))
        if review_id in indexed:
            raise ValueError(f"duplicate review_id in {source}: {review_id}")
        indexed[review_id] = row
    return indexed


def _validate_immutable_fields(
    base_row: dict[str, Any], reviewed_row: dict[str, Any], review_id: str
) -> None:
    fields = (set(base_row) | set(reviewed_row)) - MUTABLE_FIELDS
    for field in sorted(fields):
        if base_row.get(field) != reviewed_row.get(field):
            raise ValueError(f"immutable field changed for {review_id}: {field}")


def _validate_completed_review(row: dict[str, Any], review_id: str) -> None:
    if row.get("annotation_status") != "completed":
        raise ValueError(f"review {review_id} must be completed")
    if row.get("human_evidence") is not False:
        raise ValueError(f"review {review_id} must set human_evidence false")
    if row.get("model_agent_development_only") is not True:
        raise ValueError(
            f"review {review_id} must set model_agent_development_only true"
        )

    review_fields = row.get("review_fields")
    if not isinstance(review_fields, dict):
        raise ValueError(f"invalid review_fields for {review_id}")
    slots = review_fields.get("slots")
    if not isinstance(slots, dict) or set(slots) != FRAME_SLOTS:
        raise ValueError(f"invalid slot fields for {review_id}")
    labels = {
        "frame_validity": review_fields.get("frame_validity"),
        "counterfactual_candidate": review_fields.get("counterfactual_candidate"),
        **{f"slots.{name}": slots[name] for name in sorted(FRAME_SLOTS)},
    }
    for field, label in labels.items():
        if label not in COMPLETED_LABELS:
            raise ValueError(f"invalid label for {review_id}:{field}:{label}")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--shards", nargs="+", type=Path, default=DEFAULT_SHARDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = _parse_args(arguments)
    result = merge(
        base_path=args.base,
        shard_paths=list(args.shards),
        output_path=args.output,
        command="python scripts/merge_quantity_frame_audits.py " + " ".join(arguments),
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
