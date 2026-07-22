"""Validate a completed ESP counterfactual run and write validation.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp.core import render_rewrite_prompt, score_cue_preservation
from src.esp.counterfactual import CounterfactualPair, validate_counterfactual_pairs


DEFAULT_PAIRS_PATH = Path("data/annotations/esp_counterfactual_pairs_v0.jsonl")
EXPECTED_PAIR_COUNT = 14
EXPECTED_GENERATION_COUNT = 28
PROTOCOL = "esp-counterfactual-v0"
_INTERNAL_LABEL_RE = re.compile(
    r"\b(?:variant|condition|original|counterfactual)\s*:", re.IGNORECASE
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_inventory(
    run_dir: Path, *, exclude_path: Path | None = None
) -> dict[str, dict[str, object]]:
    files: dict[str, dict[str, object]] = {}
    excluded = exclude_path.resolve() if exclude_path is not None else None
    for path in sorted(p for p in run_dir.rglob("*") if p.is_file()):
        if excluded is not None and path.resolve() == excluded:
            continue
        relative = path.relative_to(run_dir).as_posix()
        files[relative] = {"bytes": path.stat().st_size, "sha256": _sha256(path)}
    return files


def _read_required_json(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing {label}")
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


def _read_jsonl(path: Path, errors: list[str], label: str) -> list[dict[str, Any]]:
    if not path.is_file():
        errors.append(f"missing {label}")
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            errors.append(f"{label} contains blank line {line_number}")
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


def _load_manifest(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    rows = _read_jsonl(path, errors, "pair manifest")
    pairs: list[CounterfactualPair] = []
    for row in rows:
        try:
            pairs.append(
                CounterfactualPair(
                    pair_id=str(row["pair_id"]),
                    original_strength=str(row["original_strength"]),
                    counterfactual_strength=str(row["counterfactual_strength"]),
                    original_source=str(row["original_source"]),
                    counterfactual_source=str(row["counterfactual_source"]),
                    edit_spans=tuple(str(span) for span in row["edit_spans"]),
                    proposition_skeleton=str(row["proposition_skeleton"]),
                    counterfactual_proposition_skeleton=(
                        str(row["counterfactual_proposition_skeleton"])
                        if row.get("counterfactual_proposition_skeleton") is not None
                        else None
                    ),
                    polarity_changed=bool(row.get("polarity_changed", False)),
                    material_argument_changed=bool(
                        row.get("material_argument_changed", False)
                    ),
                )
            )
        except KeyError as exc:
            errors.append(f"pair manifest missing field {exc.args[0]}")
    try:
        validate_counterfactual_pairs(pairs)
    except ValueError as exc:
        errors.append(str(exc))
    if len(rows) != EXPECTED_PAIR_COUNT:
        errors.append(
            f"pair manifest count mismatch: expected {EXPECTED_PAIR_COUNT}, found {len(rows)}"
        )
    return rows


def _expected_rows(manifest: list[dict[str, Any]], condition: str) -> list[dict[str, Any]]:
    expected: list[dict[str, Any]] = []
    for pair in manifest:
        variants = (
            (
                "original",
                str(pair["original_source"]),
                str(pair["original_strength"]),
            ),
            (
                "counterfactual",
                str(pair["counterfactual_source"]),
                str(pair["counterfactual_strength"]),
            ),
        )
        for variant, source, strength in variants:
            annotation = {
                "strength": strength,
                "attribution": str(pair["attribution"]),
                "scope_text": str(pair["proposition_skeleton"]),
            }
            expected.append(
                {
                    "pair_id": str(pair["pair_id"]),
                    "variant": variant,
                    "source_item_id": str(pair["source_item_id"]),
                    "assigned_strength": strength,
                    "prompt": render_rewrite_prompt(source, annotation, condition),
                }
            )
    return expected


def _append_config_errors(
    config: dict[str, Any],
    metrics: dict[str, Any],
    manifest_sha256: str,
    expected_git_commit: str | None,
    expected_model_id: str | None,
    expected_revision: str | None,
    expected_condition: str | None,
    errors: list[str],
) -> None:
    required_config = {
        "protocol": PROTOCOL,
        "pair_count": EXPECTED_PAIR_COUNT,
        "generation_count": EXPECTED_GENERATION_COUNT,
        "pairs_sha256": manifest_sha256,
    }
    for key, expected in required_config.items():
        if config.get(key) != expected:
            if key == "pairs_sha256":
                errors.append("config pairs_sha256 does not match manifest")
            else:
                errors.append(f"config {key} mismatch: {config.get(key)!r}")
    if config.get("revision") != config.get("model_revision"):
        errors.append("config revision and model_revision differ")
    if config.get("revision") != config.get("tokenizer_revision"):
        errors.append("config revision and tokenizer_revision differ")
    if expected_git_commit is not None and config.get("git_commit") != expected_git_commit:
        errors.append(f"config git_commit mismatch: {config.get('git_commit')}")
    if expected_model_id is not None and config.get("model_id") != expected_model_id:
        errors.append(f"config model_id mismatch: {config.get('model_id')}")
    if expected_revision is not None and config.get("revision") != expected_revision:
        errors.append(f"config revision mismatch: {config.get('revision')}")
    if expected_condition is not None and config.get("condition") != expected_condition:
        errors.append(f"config condition mismatch: {config.get('condition')}")
    if metrics.get("pair_count") != EXPECTED_PAIR_COUNT:
        errors.append(f"metrics pair_count mismatch: {metrics.get('pair_count')!r}")
    if metrics.get("row_count") != EXPECTED_GENERATION_COUNT:
        errors.append(f"metrics row_count mismatch: {metrics.get('row_count')!r}")


def _validate_generation_rows(
    rows: list[dict[str, Any]],
    expected_rows: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, object]:
    if len(rows) != EXPECTED_GENERATION_COUNT:
        errors.append(
            "generation row count mismatch: "
            f"expected {EXPECTED_GENERATION_COUNT}, found {len(rows)}"
        )
    actual_order = [(row.get("pair_id"), row.get("variant")) for row in rows]
    expected_order = [(row["pair_id"], row["variant"]) for row in expected_rows]
    if actual_order != expected_order:
        errors.append("generation rows do not match manifest pair order")

    cue_preserved_count = 0
    for index, expected in enumerate(expected_rows):
        if index >= len(rows):
            continue
        row = rows[index]
        pair_id = expected["pair_id"]
        variant = expected["variant"]
        for key in ("pair_id", "variant", "source_item_id", "assigned_strength"):
            if row.get(key) != expected[key]:
                errors.append(
                    f"{key} mismatch for {pair_id} {variant}: {row.get(key)!r}"
                )
        if row.get("prompt") != expected["prompt"]:
            errors.append(f"prompt mismatch for {pair_id} {variant}")
        prompt = row.get("prompt")
        if isinstance(prompt, str) and _INTERNAL_LABEL_RE.search(prompt):
            errors.append(f"prompt leaks internal label for {pair_id} {variant}")
        raw_output = row.get("raw_output")
        if not isinstance(raw_output, str) or not raw_output.strip():
            errors.append(f"empty raw_output for {pair_id} {variant}")
            recomputed_cue = False
        else:
            recomputed_cue = score_cue_preservation(raw_output, expected["assigned_strength"])
        diagnostic = row.get("diagnostic")
        if not isinstance(diagnostic, dict):
            errors.append(f"diagnostic missing for {pair_id} {variant}")
        elif diagnostic.get("cue_preserved") != recomputed_cue:
            errors.append(f"diagnostic cue_preserved mismatch for {pair_id} {variant}")
        cue_preserved_count += int(recomputed_cue)

    denominator = len(rows) if rows else 0
    return {
        "pair_count": EXPECTED_PAIR_COUNT,
        "row_count": len(rows),
        "cue_bin_preservation_rate": (
            cue_preserved_count / denominator if denominator else 0.0
        ),
    }


def validate_esp_counterfactual_run(
    run_dir: Path,
    *,
    pairs_path: Path = DEFAULT_PAIRS_PATH,
    expected_git_commit: str | None = None,
    expected_model_id: str | None = None,
    expected_revision: str | None = None,
    expected_condition: str | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    run_dir = Path(run_dir)
    pairs_path = Path(pairs_path)
    files = (
        _file_inventory(run_dir, exclude_path=output_path) if run_dir.is_dir() else {}
    )
    if not run_dir.is_dir():
        errors.append(f"run directory missing: {run_dir}")

    if not (run_dir / "RUN_COMPLETE").is_file():
        errors.append("missing RUN_COMPLETE")
    run_git_commit = ""
    commit_path = run_dir / "run-git-commit.txt"
    if commit_path.is_file():
        run_git_commit = commit_path.read_text(encoding="utf-8").strip()
    else:
        errors.append("missing run-git-commit.txt")
    if expected_git_commit is not None and run_git_commit != expected_git_commit:
        errors.append(f"run-git-commit.txt mismatch: {run_git_commit}")

    manifest_sha256 = _sha256(pairs_path) if pairs_path.is_file() else ""
    if not manifest_sha256:
        errors.append(f"pair manifest missing: {pairs_path}")
    manifest = _load_manifest(pairs_path, errors) if manifest_sha256 else []
    config = _read_required_json(run_dir / "config.json", errors, "config.json")
    metrics = _read_required_json(run_dir / "metrics.json", errors, "metrics.json")
    rows = _read_jsonl(run_dir / "generations.jsonl", errors, "generations.jsonl")

    condition = str(config.get("condition") or expected_condition or "")
    if condition not in {"generic", "frame"}:
        errors.append(f"unsupported condition: {condition!r}")
    expected = _expected_rows(manifest, condition) if manifest and condition else []
    recomputed_metrics = _validate_generation_rows(rows, expected, errors)
    _append_config_errors(
        config,
        metrics,
        manifest_sha256,
        expected_git_commit,
        expected_model_id,
        expected_revision,
        expected_condition,
        errors,
    )
    if metrics != recomputed_metrics:
        errors.append("metrics do not reproduce from generations")

    report: dict[str, Any] = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "counts": {"pairs": len(manifest), "generations": len(rows)},
        "config": {
            "condition": config.get("condition"),
            "git_commit": config.get("git_commit"),
            "model_id": config.get("model_id"),
            "pairs_sha256": config.get("pairs_sha256"),
            "revision": config.get("revision"),
        },
        "hashes": {"pairs_sha256": manifest_sha256},
        "files": files,
        "recomputed_metrics": recomputed_metrics,
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-git-commit")
    parser.add_argument("--expected-model-id")
    parser.add_argument("--expected-revision")
    parser.add_argument("--expected-condition", choices=("generic", "frame"))
    args = parser.parse_args()

    output = args.output or args.run_dir / "validation.json"
    report = validate_esp_counterfactual_run(
        args.run_dir,
        pairs_path=args.pairs,
        expected_git_commit=args.expected_git_commit,
        expected_model_id=args.expected_model_id,
        expected_revision=args.expected_revision,
        expected_condition=args.expected_condition,
        output_path=output,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
