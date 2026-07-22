"""Deterministic source-lineage operations used by LAD experiments."""

from dataclasses import dataclass
from typing import Mapping, Sequence


class LineageCycleError(ValueError):
    """Raised when a source-lineage graph contains a cycle."""


@dataclass(frozen=True)
class SupportSummary:
    nominal_support: int
    independent_support: int
    corroboration_gap: float


def lineage_roots(
    source_id: str,
    parents: Mapping[str, Sequence[str]],
    _active: frozenset[str] = frozenset(),
) -> set[str]:
    """Return root sources reachable from ``source_id``."""
    if source_id in _active:
        raise LineageCycleError(f"cycle detected at source {source_id!r}")

    direct_parents = tuple(parents.get(source_id, ()))
    if not direct_parents:
        return {source_id}

    active = _active | {source_id}
    roots: set[str] = set()
    for parent in direct_parents:
        roots.update(lineage_roots(parent, parents, active))
    return roots


def effective_support(
    source_ids: Sequence[str], parents: Mapping[str, Sequence[str]]
) -> SupportSummary:
    """Summarize nominal support and distinct root-source support."""
    roots: set[str] = set()
    for source_id in source_ids:
        roots.update(lineage_roots(source_id, parents))

    nominal = len(source_ids)
    independent = len(roots)
    gap = 0.0 if nominal == 0 else (nominal - independent) / nominal
    return SupportSummary(nominal, independent, gap)


def validate_paired_intervention(common: Mapping, independent: Mapping) -> None:
    """Ensure a COMMON/INDEPENDENT pair differs only in lineage fields."""
    if common.get("condition") != "COMMON":
        raise ValueError("first record must use COMMON condition")
    if independent.get("condition") != "INDEPENDENT":
        raise ValueError("second record must use INDEPENDENT condition")

    lineage_fields = {"condition", "source_ids", "source_parents"}
    all_fields = set(common) | set(independent)
    for field in sorted(all_fields - lineage_fields):
        if common.get(field) != independent.get(field):
            raise ValueError(f"paired invariant changed: {field}")

    common_support = effective_support(
        common.get("source_ids", ()), common.get("source_parents", {})
    )
    independent_support = effective_support(
        independent.get("source_ids", ()), independent.get("source_parents", {})
    )
    if common_support.nominal_support != independent_support.nominal_support:
        raise ValueError("paired invariant changed: nominal support")
    if common_support.independent_support >= independent_support.independent_support:
        raise ValueError("COMMON must have fewer independent roots than INDEPENDENT")
