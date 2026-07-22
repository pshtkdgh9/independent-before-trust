"""Predeclared source-audit gate for quantity-frame pilots."""

from __future__ import annotations

from dataclasses import dataclass


SOURCE_GATE_THRESHOLDS = {
    "valid": 100,
    "corpora": 2,
    "denominator": 30,
    "comparator": 30,
    "counterfactual": 60,
}


@dataclass(frozen=True)
class SourceGateResult:
    advance: bool
    status: str
    counts: dict[str, int]
    failures: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "advance": self.advance,
            "status": self.status,
            "counts": dict(self.counts),
            "failures": list(self.failures),
        }


def evaluate_source_gate(
    *,
    valid: int,
    corpora: int,
    denominator: int,
    comparator: int,
    counterfactual: int,
) -> SourceGateResult:
    """Evaluate the immutable pre-GPU source gate thresholds."""
    counts = {
        "valid": _non_negative_int(valid, "valid"),
        "corpora": _non_negative_int(corpora, "corpora"),
        "denominator": _non_negative_int(denominator, "denominator"),
        "comparator": _non_negative_int(comparator, "comparator"),
        "counterfactual": _non_negative_int(counterfactual, "counterfactual"),
    }
    failures = tuple(
        f"{field}<{threshold}"
        for field, threshold in SOURCE_GATE_THRESHOLDS.items()
        if counts[field] < threshold
    )
    return SourceGateResult(
        advance=not failures,
        status="pass" if not failures else "fail",
        counts=counts,
        failures=failures,
    )


def _non_negative_int(value: int, field: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value
