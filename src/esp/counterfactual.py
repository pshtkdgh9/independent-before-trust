"""Counterfactual uncertainty-pair records for ESP validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CounterfactualPair:
    pair_id: str
    original_strength: str
    counterfactual_strength: str
    original_source: str
    counterfactual_source: str
    edit_spans: tuple[str, ...]
    proposition_skeleton: str
    counterfactual_proposition_skeleton: str | None = None
    polarity_changed: bool = False
    material_argument_changed: bool = False


_ALLOWED_STRENGTH_TRANSITIONS = frozenset(
    {
        ("possible", "likely"),
        ("likely", "possible"),
        ("suggestive", "likely"),
        ("likely", "suggestive"),
    }
)


def validate_counterfactual_pairs(
    pairs: Iterable[CounterfactualPair],
) -> list[CounterfactualPair]:
    """Return pairs in input order after deterministic validation."""
    validated = list(pairs)
    seen_pair_ids: set[str] = set()
    for pair in validated:
        if pair.pair_id in seen_pair_ids:
            raise ValueError(f"counterfactual unique pair IDs violated: {pair.pair_id}")
        seen_pair_ids.add(pair.pair_id)

        transition = (pair.original_strength, pair.counterfactual_strength)
        if transition not in _ALLOWED_STRENGTH_TRANSITIONS:
            raise ValueError(
                "counterfactual adjacent strength transition required: "
                f"{pair.original_strength} -> {pair.counterfactual_strength}"
            )

        original_source = pair.original_source.strip()
        counterfactual_source = pair.counterfactual_source.strip()
        if not original_source or not counterfactual_source:
            raise ValueError("counterfactual pair source strings must be non-empty")

        if original_source == counterfactual_source:
            raise ValueError("original and counterfactual sources must differ")

        if len(pair.edit_spans) != 1 or not pair.edit_spans[0].strip():
            raise ValueError("counterfactual pair must declare exactly one edit span")

        counterfactual_skeleton = (
            pair.counterfactual_proposition_skeleton
            if pair.counterfactual_proposition_skeleton is not None
            else pair.proposition_skeleton
        )
        if pair.proposition_skeleton != counterfactual_skeleton:
            raise ValueError("counterfactual pair must keep proposition_skeleton unchanged")

        if pair.polarity_changed:
            raise ValueError("counterfactual pair must reject polarity changes")

        if pair.material_argument_changed:
            raise ValueError("counterfactual pair must reject material argument changes")

    return validated


__all__ = ["CounterfactualPair", "validate_counterfactual_pairs"]
