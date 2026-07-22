"""Paired statistical summaries for LAD generation artifacts."""

from __future__ import annotations

import random
from typing import Any, Iterable, Mapping


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _effect_summary(
    outcomes: list[tuple[int, int]], *, replicates: int, rng: random.Random
) -> dict[str, Any]:
    paired_n = len(outcomes)
    if paired_n == 0:
        return {
            "paired_n": 0,
            "common_rate": None,
            "independent_rate": None,
            "paired_difference": None,
            "bootstrap_95_ci": None,
        }

    common_rate = sum(common for common, _ in outcomes) / paired_n
    independent_rate = sum(independent for _, independent in outcomes) / paired_n
    differences = [common - independent for common, independent in outcomes]
    bootstrap = []
    for _ in range(replicates):
        sampled = [differences[rng.randrange(paired_n)] for _ in range(paired_n)]
        bootstrap.append(sum(sampled) / paired_n)
    return {
        "paired_n": paired_n,
        "common_rate": common_rate,
        "independent_rate": independent_rate,
        "paired_difference": common_rate - independent_rate,
        "bootstrap_95_ci": [
            _percentile(bootstrap, 0.025),
            _percentile(bootstrap, 0.975),
        ],
    }


def paired_revision_effects(
    rows: Iterable[Mapping[str, Any]],
    *,
    bootstrap_replicates: int = 10_000,
    seed: int = 1701,
) -> dict[str, Any]:
    """Estimate COMMON-minus-INDEPENDENT revision effects by resampling pairs."""
    if bootstrap_replicates <= 0:
        raise ValueError("bootstrap_replicates must be positive")

    pairs: dict[str, dict[str, Mapping[str, Any]]] = {}
    for row in rows:
        pair_id = str(row["pair_id"])
        condition = str(row["condition"])
        if condition not in {"COMMON", "INDEPENDENT"}:
            raise ValueError(f"unknown condition: {condition}")
        pair = pairs.setdefault(pair_id, {})
        if condition in pair:
            raise ValueError(f"duplicate {condition} row for {pair_id}")
        pair[condition] = row

    complete: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
    for pair_id, pair in pairs.items():
        if set(pair) != {"COMMON", "INDEPENDENT"}:
            continue
        common, independent = pair["COMMON"], pair["INDEPENDENT"]
        if common["initial_correct"] != independent["initial_correct"]:
            raise ValueError(f"paired initial state changed: {pair_id}")
        if (
            common.get("parse_error") is None
            and independent.get("parse_error") is None
            and common.get("final_correct") is not None
            and independent.get("final_correct") is not None
        ):
            complete.append((common, independent))

    harmful = [
        (int(not common["final_correct"]), int(not independent["final_correct"]))
        for common, independent in complete
        if common["initial_correct"]
    ]
    beneficial = [
        (int(common["final_correct"]), int(independent["final_correct"]))
        for common, independent in complete
        if not common["initial_correct"]
    ]
    rng = random.Random(seed)
    return {
        "pair_count": len(pairs),
        "complete_parsed_pair_count": len(complete),
        "incomplete_or_failed_pair_count": len(pairs) - len(complete),
        "bootstrap_replicates": bootstrap_replicates,
        "bootstrap_seed": seed,
        "effect_direction": "COMMON-minus-INDEPENDENT",
        "harmful_revision": _effect_summary(
            harmful, replicates=bootstrap_replicates, rng=rng
        ),
        "beneficial_revision": _effect_summary(
            beneficial, replicates=bootstrap_replicates, rng=rng
        ),
    }
