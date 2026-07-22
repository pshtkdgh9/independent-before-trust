"""Integrity checks for completed LAD pilot artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .lineage import effective_support, validate_paired_intervention
from .metrics import aggregate_revision_metrics
from .pilot import build_private_prompt, build_revision_prompt, parse_answer
from .statistics import paired_revision_effects


CORE_FILES = (
    "baseline_generations.jsonl",
    "pairs.jsonl",
    "generations.jsonl",
    "config.json",
    "metrics.json",
)


def _json_lines(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_candidate_answer(
    response: str, candidates: list[str] | None
) -> tuple[str | None, str | None]:
    """Reproduce the runner's candidate-domain normalization exactly."""
    answer, error = parse_answer(response, candidates)
    if error is None and candidates is not None and answer not in candidates:
        return None, "answer_outside_candidates"
    return answer, error


def validate_pilot_artifacts(run_dir: Path) -> dict[str, Any]:
    """Return a machine-readable pass/fail report without altering artifacts."""
    errors: list[str] = []
    missing = [name for name in CORE_FILES if not (run_dir / name).is_file()]
    if not (run_dir / "RUN_COMPLETE").is_file():
        errors.append("RUN_COMPLETE marker is missing")
    if missing:
        errors.append(f"missing core files: {', '.join(missing)}")
        return {"status": "fail", "errors": errors, "run_dir": run_dir.as_posix()}

    baseline = _json_lines(run_dir / "baseline_generations.jsonl")
    pairs = _json_lines(run_dir / "pairs.jsonl")
    generations = _json_lines(run_dir / "generations.jsonl")
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))

    pair_keys = [(str(row["pair_id"]), str(row["condition"])) for row in pairs]
    generation_keys = [
        (str(row["pair_id"]), str(row["condition"])) for row in generations
    ]
    if len(pair_keys) != len(set(pair_keys)):
        errors.append("duplicate pair keys")
    if len(generation_keys) != len(set(generation_keys)):
        errors.append("duplicate generation keys")
    if set(pair_keys) != set(generation_keys):
        errors.append("generation keys do not match pair keys")

    grouped_pairs: dict[str, dict[str, dict[str, Any]]] = {}
    pair_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for row in pairs:
        pair_by_key[(str(row["pair_id"]), str(row["condition"]))] = row
        grouped_pairs.setdefault(str(row["pair_id"]), {})[str(row["condition"])] = row
    for pair_id, conditions in grouped_pairs.items():
        if set(conditions) != {"COMMON", "INDEPENDENT"}:
            errors.append(f"incomplete intervention pair: {pair_id}")
            continue
        try:
            validate_paired_intervention(
                conditions["COMMON"], conditions["INDEPENDENT"]
            )
        except ValueError as exc:
            errors.append(f"invalid intervention pair {pair_id}: {exc}")

    for row in generations:
        key = (str(row["pair_id"]), str(row["condition"]))
        pair = pair_by_key.get(key)
        if pair is None:
            continue
        expected_answer, expected_error = _parse_candidate_answer(
            str(row.get("raw_response", "")), pair.get("candidate_answers")
        )
        if row.get("final_answer") != expected_answer:
            errors.append(f"final_answer mismatch: {key}")
        if row.get("parse_error") != expected_error:
            errors.append(f"parse_error mismatch: {key}")
        expected_initial_correct = pair["target_initial_answer"] == pair["gold_answer"]
        if row.get("initial_correct") != expected_initial_correct:
            errors.append(f"initial_correct mismatch: {key}")
        expected_final_correct = (
            expected_answer == pair["gold_answer"] if expected_answer is not None else None
        )
        if row.get("final_correct") != expected_final_correct:
            errors.append(f"final_correct mismatch: {key}")
        if row.get("initial_answer") != pair["target_initial_answer"]:
            errors.append(f"initial_answer mismatch: {key}")
        if row.get("gold_answer") != pair["gold_answer"]:
            errors.append(f"gold_answer mismatch: {key}")
        support = effective_support(pair["source_ids"], pair["source_parents"])
        expected_support = {
            "nominal_support": support.nominal_support,
            "independent_support": support.independent_support,
            "corroboration_gap": support.corroboration_gap,
        }
        if any(row.get(field) != value for field, value in expected_support.items()):
            errors.append(f"support metrics mismatch: {key}")
        expected_prompt_hash = hashlib.sha256(
            build_revision_prompt(pair).encode("utf-8")
        ).hexdigest()
        if row.get("prompt_sha256") != expected_prompt_hash:
            errors.append(f"revision prompt hash mismatch: {key}")

    representative_pairs = {
        pair_id: conditions.get("COMMON")
        for pair_id, conditions in grouped_pairs.items()
        if conditions.get("COMMON") is not None
    }
    for row in baseline:
        item_id = str(row["item_id"])
        pair = representative_pairs.get(item_id)
        if pair is None:
            errors.append(f"baseline item has no paired record: {item_id}")
            continue
        expected_answer, expected_error = _parse_candidate_answer(
            str(row.get("raw_response", "")), pair.get("candidate_answers")
        )
        if row.get("private_answer") != expected_answer:
            errors.append(f"private_answer mismatch: {item_id}")
        if row.get("parse_error") != expected_error:
            errors.append(f"baseline parse_error mismatch: {item_id}")
        expected_private_correct = (
            expected_answer == pair["gold_answer"] if expected_answer is not None else None
        )
        if row.get("private_correct") != expected_private_correct:
            errors.append(f"private_correct mismatch: {item_id}")
        expected_prompt_hash = hashlib.sha256(
            build_private_prompt(pair).encode("utf-8")
        ).hexdigest()
        if row.get("prompt_sha256") != expected_prompt_hash:
            errors.append(f"private prompt hash mismatch: {item_id}")

    parse_failures = [row for row in baseline + generations if row.get("parse_error")]
    if parse_failures:
        errors.append(f"parse failures present: {len(parse_failures)}")
    malformed_outputs = [
        row for row in baseline + generations if not str(row.get("raw_response", ""))
    ]
    if malformed_outputs:
        errors.append(f"empty raw responses present: {len(malformed_outputs)}")
    invalid_prompt_hashes = [
        row
        for row in baseline + generations
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("prompt_sha256", "")))
    ]
    if invalid_prompt_hashes:
        errors.append(f"invalid prompt hashes present: {len(invalid_prompt_hashes)}")

    parsed_baseline = [row for row in baseline if row.get("parse_error") is None]
    expected_baseline = {
        "n": len(baseline),
        "parsed_n": len(parsed_baseline),
        "parse_failure_rate": (
            (len(baseline) - len(parsed_baseline)) / len(baseline)
            if baseline
            else 0.0
        ),
        "accuracy": (
            sum(bool(row.get("private_correct")) for row in parsed_baseline)
            / len(parsed_baseline)
            if parsed_baseline
            else None
        ),
    }
    if metrics.get("baseline") != expected_baseline:
        errors.append("baseline metrics do not reproduce from generations")
    if metrics.get("paired_item_count") != len(grouped_pairs):
        errors.append("paired item metric count does not match artifact")
    for condition in ("COMMON", "INDEPENDENT"):
        condition_rows = [
            row for row in generations if row.get("condition") == condition
        ]
        parsed_rows = [row for row in condition_rows if row.get("parse_error") is None]
        expected_condition = aggregate_revision_metrics(parsed_rows)
        expected_condition["parse_failure_rate"] = (
            (len(condition_rows) - len(parsed_rows)) / len(condition_rows)
            if condition_rows
            else 0.0
        )
        if metrics.get("conditions", {}).get(condition) != expected_condition:
            errors.append(
                f"{condition} condition metrics do not reproduce from generations"
            )
    recomputed_effects = paired_revision_effects(
        generations,
        bootstrap_replicates=int(
            metrics.get("paired_effects", {}).get("bootstrap_replicates", 10_000)
        ),
        seed=int(metrics.get("paired_effects", {}).get("bootstrap_seed", 1701)),
    )
    if metrics.get("paired_effects") != recomputed_effects:
        errors.append("paired effects do not reproduce from generations")

    hashes = {name: _sha256(run_dir / name) for name in CORE_FILES}
    return {
        "status": "fail" if errors else "pass",
        "run_dir": run_dir.as_posix(),
        "errors": errors,
        "counts": {
            "baseline": len(baseline),
            "pairs": len(pairs),
            "generations": len(generations),
            "paired_items": len(grouped_pairs),
            "parse_failures": len(parse_failures),
        },
        "sha256": hashes,
    }
