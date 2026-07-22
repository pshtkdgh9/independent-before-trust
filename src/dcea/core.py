"""Controlled interventions and deterministic metrics for DCEA pilots."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Iterable


@dataclass(frozen=True)
class EvidenceTemplate:
    item_id: str
    query: str
    subject: str
    relation: str
    original_value: str
    counterfactual_value: str
    distractor: str
    source_ids: tuple[str, str, str]

    def __post_init__(self) -> None:
        if self.original_value == self.counterfactual_value:
            raise ValueError("original and counterfactual values must be different")
        if len(set(self.source_ids)) != len(self.source_ids):
            raise ValueError("source identifiers must be unique")


@dataclass(frozen=True)
class InterventionCell:
    item_id: str
    condition: str
    query: str
    sources: tuple[str, ...]
    source_ids: tuple[str, ...]
    supporting_source_ids: tuple[str, ...]
    expected_answer: str
    redundancy: bool


@dataclass(frozen=True)
class GenerationScore:
    item_id: str
    condition: str
    redundancy: bool
    expected_answer: str
    parsed_answer: str | None
    parsed_citation: str | None
    directional_following: bool
    citation_valid: bool
    citation_support: bool


def _fact(template: EvidenceTemplate, value: str, paraphrase: bool = False) -> str:
    if paraphrase:
        return f"Launch records date {template.subject}'s departure to {value}."
    return f"{template.subject.capitalize()} {template.relation} {value}."


def _cell(template: EvidenceTemplate, value: str, redundant: bool) -> InterventionCell:
    ids = template.source_ids
    sources = [_fact(template, value), template.distractor]
    supporting_ids = [ids[0]]
    if redundant:
        sources.append(_fact(template, value, paraphrase=True))
        supporting_ids.append(ids[2])
    condition = f"{'redundant' if redundant else 'singleton'}_{'original' if value == template.original_value else 'counterfactual'}"
    used_ids = ids if redundant else ids[:2]
    return InterventionCell(
        item_id=template.item_id,
        condition=condition,
        query=template.query,
        sources=tuple(sources),
        source_ids=tuple(used_ids),
        supporting_source_ids=tuple(supporting_ids),
        expected_answer=value,
        redundancy=redundant,
    )


def build_intervention_cells(template: EvidenceTemplate) -> dict[str, InterventionCell]:
    return {
        "singleton_original": _cell(template, template.original_value, False),
        "singleton_counterfactual": _cell(template, template.counterfactual_value, False),
        "redundant_original": _cell(template, template.original_value, True),
        "redundant_counterfactual": _cell(template, template.counterfactual_value, True),
    }


def score_generation(cell: InterventionCell, raw_text: str) -> GenerationScore:
    answer_match = re.search(r"(?im)^ANSWER:\s*(\S.*?)\s*$", raw_text)
    citation_match = re.search(r"(?im)^CITATION:\s*([A-Za-z0-9_-]+)\s*$", raw_text)
    answer = answer_match.group(1).strip() if answer_match else None
    citation = citation_match.group(1) if citation_match else None
    valid = citation in cell.source_ids if citation else False
    return GenerationScore(
        item_id=cell.item_id,
        condition=cell.condition,
        redundancy=cell.redundancy,
        expected_answer=cell.expected_answer,
        parsed_answer=answer,
        parsed_citation=citation,
        directional_following=answer == cell.expected_answer,
        citation_valid=valid,
        citation_support=valid and citation in cell.supporting_source_ids,
    )


def render_prompt(cell: InterventionCell, *, contrastive: bool) -> str:
    source_lines = "\n".join(
        f"[{source_id}] {source}"
        for source_id, source in zip(cell.source_ids, cell.sources)
    )
    instruction = (
        "Use the supplied sources even if they differ from what you remember. "
        "The answer and citation must track the source text."
        if contrastive
        else "Answer using the supplied sources."
    )
    return (
        f"{instruction}\n\nSOURCES\n{source_lines}\n\n"
        f"QUESTION\n{cell.query}\n\n"
        "Return exactly two lines:\nANSWER: <answer>\nCITATION: <source id>"
    )


def run_pilot(
    templates: Iterable[EvidenceTemplate],
    backend: object,
    output_dir: Path,
    *,
    contrastive: bool,
) -> dict[str, float]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    scores: list[GenerationScore] = []
    for template in templates:
        for cell in build_intervention_cells(template).values():
            prompt = render_prompt(cell, contrastive=contrastive)
            raw_output = backend.generate(prompt)
            score = score_generation(cell, raw_output)
            rows.append(
                {
                    "cell": asdict(cell),
                    "prompt": prompt,
                    "raw_output": raw_output,
                    "score": asdict(score),
                }
            )
            scores.append(score)
    metrics = summarize_cells(scores)
    (output_dir / "generations.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metrics


def summarize_cells(scores: Iterable[GenerationScore]) -> dict[str, float]:
    groups: dict[bool, list[GenerationScore]] = {False: [], True: []}
    by_pair: dict[tuple[str, bool], dict[str, GenerationScore]] = {}
    for score in scores:
        groups[score.redundancy].append(score)
        intervention = "counterfactual" if score.condition.endswith("counterfactual") else "original"
        by_pair.setdefault((score.item_id, score.redundancy), {})[intervention] = score

    def rate(rows: list[GenerationScore]) -> float:
        return sum(row.directional_following for row in rows) / len(rows) if rows else 0.0

    singleton = rate(groups[False])
    redundant = rate(groups[True])

    def counterfactual_rate(redundancy: bool) -> float:
        rows = [row for row in groups[redundancy] if row.condition.endswith("counterfactual")]
        return rate(rows)

    def flip_rate(redundancy: bool) -> float:
        pairs = [
            pair
            for (item_id, is_redundant), pair in by_pair.items()
            if is_redundant == redundancy
            and "original" in pair
            and "counterfactual" in pair
        ]
        if not pairs:
            return 0.0
        flips = sum(
            pair["original"].parsed_answer != pair["counterfactual"].parsed_answer
            for pair in pairs
        )
        return flips / len(pairs)

    return {
        "singleton_directional_rate": singleton,
        "redundant_directional_rate": redundant,
        "redundancy_interaction": redundant - singleton,
        "singleton_counterfactual_following_rate": counterfactual_rate(False),
        "redundant_counterfactual_following_rate": counterfactual_rate(True),
        "singleton_pair_flip_rate": flip_rate(False),
        "redundant_pair_flip_rate": flip_rate(True),
    }
