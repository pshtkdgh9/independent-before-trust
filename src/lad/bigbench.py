"""Deterministic BIG-bench logical-deduction pilot construction."""

from __future__ import annotations

import random
import string
from collections import OrderedDict
from typing import Any, Mapping

from .pairs import build_lineage_pair


def _encode_example(example: Mapping[str, Any]) -> tuple[str, str, list[str]]:
    target_scores = example.get("target_scores", {})
    choices = list(target_scores)
    gold_indices = [index for index, choice in enumerate(choices) if target_scores[choice] == 1]
    if len(gold_indices) != 1:
        raise ValueError("each example must contain exactly one gold choice")
    if len(choices) > len(string.ascii_uppercase):
        raise ValueError("too many answer choices")

    labels = list(string.ascii_uppercase[: len(choices)])
    option_lines = [f"({label}) {choice}" for label, choice in zip(labels, choices)]
    question = (
        str(example["input"]).strip()
        + "\n\nWhich option is correct?\nOptions:\n"
        + "\n".join(option_lines)
    )
    return question, labels[gold_indices[0]], labels


def _select_unique_scenarios(
    examples: list[Mapping[str, Any]], limit: int
) -> tuple[list[Mapping[str, Any]], int]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    groups: OrderedDict[str, list[Mapping[str, Any]]] = OrderedDict()
    for example in examples:
        groups.setdefault(str(example["input"]), []).append(example)
    selected = [
        group[group_index % len(group)]
        for group_index, group in enumerate(groups.values())
    ][:limit]
    if len(selected) < limit:
        raise ValueError(
            f"requested {limit} unique scenarios but found only {len(selected)}"
        )
    return selected, len(groups)


def build_logical_deduction_items(
    payload: Mapping[str, Any], *, limit: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Create private-first items without injecting a target model answer."""
    examples = list(payload.get("examples", []))
    selected, unique_scenarios = _select_unique_scenarios(examples, limit)
    items: list[dict[str, Any]] = []
    for index, example in enumerate(selected):
        question, gold, labels = _encode_example(example)
        items.append(
            {
                "item_id": f"bigbench-logical-deduction-{index:04d}",
                "dataset": "google/BIG-bench:logical_deduction/five_objects",
                "source_example_index": examples.index(example),
                "question": question,
                "gold_answer": gold,
                "candidate_answers": labels,
            }
        )
    summary = {
        "artifact_class": "processed-experimental-input",
        "protocol": "adaptive-private-first-v1",
        "source_task": payload.get("name"),
        "source_examples": len(examples),
        "unique_scenarios": unique_scenarios,
        "selected_scenarios": len(selected),
        "output_records": len(items),
        "selection": (
            "preserve source order; choose group_index modulo group size from each "
            "unique input; elicit target-model private answer before pair construction"
        ),
    }
    return items, summary


def build_logical_deduction_pairs(
    payload: Mapping[str, Any], *, seed: int, limit: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Create balanced revision stimuli from unique logical-deduction scenarios."""
    examples = list(payload.get("examples", []))
    selected, unique_scenarios = _select_unique_scenarios(examples, limit)

    rng = random.Random(seed)
    records: list[dict[str, Any]] = []
    for index, example in enumerate(selected):
        question, gold, labels = _encode_example(example)
        distractors = [label for label in labels if label != gold]
        initially_correct = index % 2 == 0
        initial_answer = gold if initially_correct else rng.choice(distractors)
        peer_answer = rng.choice(distractors) if initially_correct else gold
        peer_correct = peer_answer == gold
        base = {
            "pair_id": f"bigbench-logical-deduction-{index:04d}",
            "dataset": "google/BIG-bench:logical_deduction/five_objects",
            "source_example_index": examples.index(example),
            "question": question,
            "gold_answer": gold,
            "target_initial_answer": initial_answer,
            "peer_claims": [peer_answer, peer_answer, peer_answer],
            "peer_correctness": [peer_correct, peer_correct, peer_correct],
            "peer_confidence": [0.8, 0.8, 0.8],
            "message_order": [0, 1, 2],
        }
        records.extend(build_lineage_pair(base, seed=seed + index))

    summary = {
        "artifact_class": "processed-experimental-input",
        "source_task": payload.get("name"),
        "source_examples": len(examples),
        "unique_scenarios": unique_scenarios,
        "selected_scenarios": len(selected),
        "output_records": len(records),
        "seed": seed,
        "selection": (
            "preserve source order; choose group_index modulo group size from each "
            "unique input; alternate initially correct and incorrect targets"
        ),
    }
    return records, summary
