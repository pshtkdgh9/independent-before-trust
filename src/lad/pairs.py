"""Construction of paired source-dependence interventions."""

import random
import string
from copy import deepcopy
from typing import Mapping

from .lineage import validate_paired_intervention


def _source_label(rng: random.Random, used: set[str]) -> str:
    while True:
        label = "src-" + "".join(rng.choices(string.ascii_lowercase + string.digits, k=8))
        if label not in used:
            used.add(label)
            return label


def build_lineage_pair(base: Mapping, seed: int) -> tuple[dict, dict]:
    """Create records that differ only in their source-lineage fields."""
    peer_fields = (
        "peer_claims",
        "peer_correctness",
        "peer_confidence",
        "message_order",
    )
    lengths = {len(base[field]) for field in peer_fields}
    if len(lengths) != 1:
        raise ValueError("peer fields must have equal lengths")

    peer_count = lengths.pop()
    if peer_count < 2:
        raise ValueError("paired intervention requires at least two peers")

    rng = random.Random(seed)
    used: set[str] = set()

    shared_root = _source_label(rng, used)
    common_ids = [_source_label(rng, used) for _ in range(peer_count)]
    common_parents = {shared_root: []}
    common_parents.update({source_id: [shared_root] for source_id in common_ids})

    independent_ids = [_source_label(rng, used) for _ in range(peer_count)]
    independent_parents = {source_id: [] for source_id in independent_ids}

    common = deepcopy(dict(base))
    common.update(
        condition="COMMON",
        source_ids=common_ids,
        source_parents=common_parents,
    )
    independent = deepcopy(dict(base))
    independent.update(
        condition="INDEPENDENT",
        source_ids=independent_ids,
        source_parents=independent_parents,
    )
    validate_paired_intervention(common, independent)
    return common, independent
