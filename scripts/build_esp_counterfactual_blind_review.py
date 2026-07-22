#!/usr/bin/env python
"""Build a blind-review packet for ESP counterfactual generations."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAIRS_PATH = REPO_ROOT / "data" / "annotations" / "esp_counterfactual_pairs_v0.jsonl"
DEFAULT_ARTIFACT_ROOT = (
    REPO_ROOT
    / "results"
    / "strong_accept_loop"
    / "cloudlab_artifacts"
    / "esp-counterfactual-b1d8635"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "results" / "strong_accept_loop" / "esp_counterfactual"
DEFAULT_PACKET_PATH = DEFAULT_OUTPUT_DIR / "blind_packet.jsonl"
DEFAULT_KEY_PATH = DEFAULT_OUTPUT_DIR / "blind_key.jsonl"
EXPECTED_RUNS = 4
EXPECTED_PAIR_COUNT = 14
EXPECTED_ROWS_PER_RUN = 28
EXPECTED_VARIANTS = ("original", "counterfactual")
PACKET_FIELDS = (
    "review_id",
    "source_sentence",
    "target_strength",
    "target_scope",
    "attribution",
    "output",
)


def _read_json(path: Path, label: str, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing {label}: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label} is not strict JSON: {exc.msg}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{label} must be a JSON object")
        return {}
    return payload


def _read_jsonl(path: Path, label: str, errors: list[str]) -> list[dict[str, Any]]:
    if not path.is_file():
        errors.append(f"missing {label}: {path}")
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            errors.append(f"{label} line {line_number} is blank")
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{label} line {line_number} is not strict JSON: {exc.msg}")
            continue
        if not isinstance(row, dict):
            errors.append(f"{label} line {line_number} must be a JSON object")
            continue
        rows.append(row)
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _review_id(run: str, pair_id: str, variant: str, seed: int = 1701) -> str:
    payload = f"{seed}:{run}:{pair_id}:{variant}".encode("utf-8")
    return "esp-cf-review-" + hashlib.sha256(payload).hexdigest()[:16]


def _source_from_prompt(prompt: object) -> str:
    if not isinstance(prompt, str) or "SOURCE:\n" not in prompt:
        return ""
    return prompt.rsplit("SOURCE:\n", 1)[1]


def _load_pairs(pairs_path: Path, errors: list[str]) -> dict[str, dict[str, Any]]:
    rows = _read_jsonl(pairs_path, "pair manifest", errors)
    if len(rows) != EXPECTED_PAIR_COUNT:
        errors.append(
            f"pair manifest count mismatch: expected {EXPECTED_PAIR_COUNT}, found {len(rows)}"
        )

    pairs: dict[str, dict[str, Any]] = {}
    required = (
        "pair_id",
        "source_item_id",
        "original_strength",
        "counterfactual_strength",
        "attribution",
        "original_source",
        "counterfactual_source",
        "proposition_skeleton",
    )
    for row_number, row in enumerate(rows, 1):
        missing = [field for field in required if field not in row]
        if missing:
            errors.append(
                f"pair manifest row {row_number} missing fields: {', '.join(missing)}"
            )
            continue
        pair_id = str(row["pair_id"])
        if pair_id in pairs:
            errors.append(f"duplicate pair_id in manifest: {pair_id}")
            continue
        pairs[pair_id] = row
    return pairs


def _expected_variant(pair: dict[str, Any], variant: str) -> dict[str, str]:
    prefix = "original" if variant == "original" else "counterfactual"
    return {
        "source_sentence": str(pair[f"{prefix}_source"]),
        "target_strength": str(pair[f"{prefix}_strength"]),
        "source_item_id": str(pair["source_item_id"]),
        "target_scope": str(pair["proposition_skeleton"]),
        "attribution": str(pair["attribution"]),
    }


def _run_dirs(artifact_root: Path, errors: list[str]) -> list[Path]:
    if not artifact_root.is_dir():
        errors.append(f"artifact root missing: {artifact_root}")
        return []
    run_dirs = sorted(
        path
        for path in artifact_root.iterdir()
        if path.is_dir() and (path / "generations.jsonl").is_file()
    )
    if len(run_dirs) != EXPECTED_RUNS:
        errors.append(f"expected exactly 4 runs, found {len(run_dirs)}")
    return run_dirs


def _validate_run(
    run_dir: Path,
    pairs: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    run = run_dir.name
    config = _read_json(run_dir / "config.json", f"{run} config.json", errors)
    model_id = str(config.get("model_id") or "")
    condition = str(config.get("condition") or "")
    if not model_id:
        errors.append(f"{run} config missing model_id")
    if condition not in {"generic", "frame"}:
        errors.append(f"{run} unsupported condition: {condition!r}")
    if config.get("pair_count") != EXPECTED_PAIR_COUNT:
        errors.append(f"{run} config pair_count mismatch: {config.get('pair_count')!r}")
    if config.get("generation_count") != EXPECTED_ROWS_PER_RUN:
        errors.append(
            f"{run} config generation_count mismatch: {config.get('generation_count')!r}"
        )

    rows = _read_jsonl(run_dir / "generations.jsonl", f"{run} generations.jsonl", errors)
    if len(rows) != EXPECTED_ROWS_PER_RUN:
        errors.append(f"{run} expected 28 rows, found {len(rows)}")

    seen: set[tuple[str, str]] = set()
    packet: list[dict[str, Any]] = []
    key: list[dict[str, Any]] = []
    for row_number, row in enumerate(rows, 1):
        pair_id = str(row.get("pair_id") or "")
        variant = str(row.get("variant") or "")
        row_label = f"{run} row {row_number}"
        if pair_id not in pairs:
            errors.append(f"{row_label} unknown pair_id: {pair_id!r}")
            continue
        if variant not in EXPECTED_VARIANTS:
            errors.append(f"{row_label} invalid variant: {variant!r}")
            continue
        pair_variant = (pair_id, variant)
        if pair_variant in seen:
            errors.append(f"{row_label} duplicate pair+variant: {pair_id} {variant}")
            continue
        seen.add(pair_variant)

        expected = _expected_variant(pairs[pair_id], variant)
        assigned_strength = row.get("assigned_strength")
        source_item_id = row.get("source_item_id")
        if assigned_strength != expected["target_strength"]:
            errors.append(
                f"{row_label} assigned_strength mismatch for {pair_id} {variant}: {assigned_strength!r}"
            )
        if source_item_id != expected["source_item_id"]:
            errors.append(
                f"{row_label} source_item_id mismatch for {pair_id} {variant}: {source_item_id!r}"
            )
        prompt_source = _source_from_prompt(row.get("prompt"))
        if prompt_source != expected["source_sentence"]:
            errors.append(f"{row_label} source sentence mismatch for {pair_id} {variant}")
        raw_output = row.get("raw_output")
        if not isinstance(raw_output, str) or not raw_output.strip():
            errors.append(f"{row_label} empty raw_output for {pair_id} {variant}")
            raw_output = ""

        review_id = _review_id(run, pair_id, variant)
        packet.append(
            {
                "review_id": review_id,
                "source_sentence": expected["source_sentence"],
                "target_strength": expected["target_strength"],
                "target_scope": expected["target_scope"],
                "attribution": expected["attribution"],
                "output": raw_output,
            }
        )
        key.append(
            {
                "review_id": review_id,
                "run": run,
                "model_id": model_id,
                "condition": condition,
                "pair_id": pair_id,
                "variant": variant,
                "source_item_id": expected["source_item_id"],
            }
        )

    expected_pairs = {
        (pair_id, variant) for pair_id in pairs for variant in EXPECTED_VARIANTS
    }
    missing = sorted(expected_pairs - seen)
    if missing:
        errors.append(
            f"{run} missing pair+variant rows: "
            + ", ".join(f"{pair_id} {variant}" for pair_id, variant in missing)
        )
    return packet, key


def build_blind_review_packet(
    *,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
    pairs_path: Path = DEFAULT_PAIRS_PATH,
    packet_path: Path | None = None,
    key_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    errors: list[str] = []
    pairs = _load_pairs(Path(pairs_path), errors)
    packet: list[dict[str, Any]] = []
    key: list[dict[str, Any]] = []

    for run_dir in _run_dirs(Path(artifact_root), errors):
        run_packet, run_key = _validate_run(run_dir, pairs, errors)
        packet.extend(run_packet)
        key.extend(run_key)

    review_ids = [row["review_id"] for row in packet]
    if len(review_ids) != len(set(review_ids)):
        errors.append("review_id values are not unique")
    if len(packet) != EXPECTED_RUNS * EXPECTED_ROWS_PER_RUN:
        errors.append(
            f"packet row count mismatch: expected 112, found {len(packet)}"
        )
    if len(key) != EXPECTED_RUNS * EXPECTED_ROWS_PER_RUN:
        errors.append(f"key row count mismatch: expected 112, found {len(key)}")
    if errors:
        raise ValueError("; ".join(errors))

    packet.sort(key=lambda row: str(row["review_id"]))
    key.sort(key=lambda row: str(row["review_id"]))
    if packet_path is not None:
        _write_jsonl(Path(packet_path), packet)
    if key_path is not None:
        _write_jsonl(Path(key_path), key)
    return {"packet": packet, "key": key}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS_PATH)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET_PATH)
    parser.add_argument("--key", type=Path, default=DEFAULT_KEY_PATH)
    args = parser.parse_args()

    try:
        result = build_blind_review_packet(
            artifact_root=args.artifact_root,
            pairs_path=args.pairs,
            packet_path=args.packet,
            key_path=args.key,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
    print(
        json.dumps(
            {
                "packet": str(args.packet),
                "key": str(args.key),
                "rows": len(result["packet"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
