"""Deterministic outcome metrics for paired LAD experiments."""

from typing import Iterable, Mapping


def classify_revision(initial_correct: bool, final_correct: bool) -> str:
    if initial_correct and not final_correct:
        return "harmful"
    if not initial_correct and final_correct:
        return "beneficial"
    if initial_correct:
        return "stable_correct"
    return "stable_incorrect"


def aggregate_revision_metrics(rows: Iterable[Mapping[str, bool]]) -> dict[str, float]:
    records = list(rows)
    initially_correct = sum(bool(row["initial_correct"]) for row in records)
    initially_incorrect = len(records) - initially_correct
    harmful = sum(
        classify_revision(row["initial_correct"], row["final_correct"]) == "harmful"
        for row in records
    )
    beneficial = sum(
        classify_revision(row["initial_correct"], row["final_correct"])
        == "beneficial"
        for row in records
    )
    final_correct = sum(bool(row["final_correct"]) for row in records)

    return {
        "n": len(records),
        "initially_correct_n": initially_correct,
        "initially_incorrect_n": initially_incorrect,
        "harmful_revision_rate": (
            harmful / initially_correct if initially_correct else 0.0
        ),
        "beneficial_revision_rate": (
            beneficial / initially_incorrect if initially_incorrect else 0.0
        ),
        "final_accuracy": final_correct / len(records) if records else 0.0,
    }
