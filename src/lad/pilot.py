"""Paired open-model pilot runner for Lineage-Aware Deliberation."""

from __future__ import annotations

import hashlib
import json
import platform
import random
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol

from .lineage import effective_support, validate_paired_intervention
from .metrics import aggregate_revision_metrics
from .pairs import build_lineage_pair
from .statistics import paired_revision_effects


ARTIFACT_CLASS = "empirical-candidate-unverified"
ANSWER_PATTERN = re.compile(r"<answer>\s*([^<>\n]+?)\s*</answer>", re.IGNORECASE)
OPEN_ANSWER_PATTERN = re.compile(r"<answer>\s*([^<>\n]+)", re.IGNORECASE)


class GenerationBackend(Protocol):
    def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class PilotConfig:
    model_id: str
    model_revision: str
    tokenizer_revision: str
    model_license: str
    seed: int = 1701
    max_new_tokens: int = 64
    temperature: float = 0.0
    dtype: str = "auto"
    quantization: str = "none"
    prompt_version: str = "lad-pilot-v1"


def _json_dump(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _root_description(record: Mapping[str, Any]) -> list[str]:
    parents = record["source_parents"]
    descriptions = []
    for source_id in record["source_ids"]:
        direct = parents.get(source_id, [])
        if direct:
            descriptions.append(f"{source_id} is derived from {', '.join(direct)}")
        else:
            descriptions.append(f"{source_id} is an independent root source")
    return descriptions


def build_revision_prompt(record: Mapping[str, Any]) -> str:
    """Render an auditable prompt whose only paired difference is lineage metadata."""
    messages = []
    for index in record["message_order"]:
        messages.append(
            "- source={source}; claim={claim}; stated_confidence={confidence}".format(
                source=record["source_ids"][index],
                claim=record["peer_claims"][index],
                confidence=record["peer_confidence"][index],
            )
        )
    lineage = "\n".join(f"- {item}" for item in _root_description(record))
    return (
        "You are revising an answer after seeing peer evidence. Source lineage indicates "
        "whether messages ultimately rely on shared or independent roots.\n"
        f"Question: {record['question']}\n"
        f"Your private answer: {record['target_initial_answer']}\n"
        "Peer messages:\n"
        + "\n".join(messages)
        + "\nSource lineage:\n"
        + lineage
        + "\nReturn only the final answer inside <answer>...</answer>."
    )


def parse_answer(
    response: str, candidates: Iterable[str] | None = None
) -> tuple[str | None, str | None]:
    match = ANSWER_PATTERN.search(response)
    candidate_list = [str(candidate) for candidate in candidates or []]
    if match:
        answer = match.group(1).strip()
    else:
        open_match = OPEN_ANSWER_PATTERN.search(response)
        if open_match:
            answer = open_match.group(1).strip()
        elif candidate_list:
            answer = response.strip().splitlines()[0].strip()
        else:
            return None, "missing_answer_tag"
    if not answer:
        return None, "empty_answer"
    if candidate_list:
        exact = [candidate for candidate in candidate_list if answer == candidate]
        if exact:
            return exact[0], None
        prefixed = [
            candidate
            for candidate in candidate_list
            if re.match(
                rf"^(?:\(\s*{re.escape(candidate)}\s*\)|"
                rf"{re.escape(candidate)}(?:\s*[\)\].:\-]|\s*$))",
                answer,
                flags=re.IGNORECASE,
            )
        ]
        if len(prefixed) == 1:
            return prefixed[0], None
    return answer, None


def build_private_prompt(item: Mapping[str, Any]) -> str:
    return (
        "Answer the question independently. No peer messages or source-lineage "
        "information are available.\n"
        f"Question: {item['question']}\n"
        "Return only the final option label inside <answer>...</answer>."
    )


def _validate_records(records: list[Mapping[str, Any]]) -> None:
    by_pair: dict[str, dict[str, Mapping[str, Any]]] = {}
    required = {
        "pair_id",
        "question",
        "gold_answer",
        "target_initial_answer",
        "peer_claims",
        "peer_correctness",
        "peer_confidence",
        "message_order",
        "condition",
        "source_ids",
        "source_parents",
    }
    for record in records:
        missing = required - set(record)
        if missing:
            raise ValueError(f"record missing fields: {sorted(missing)}")
        pair = by_pair.setdefault(str(record["pair_id"]), {})
        condition = str(record["condition"])
        if condition in pair:
            raise ValueError(f"duplicate {condition} record for {record['pair_id']}")
        pair[condition] = record
    for pair_id, pair in by_pair.items():
        if set(pair) != {"COMMON", "INDEPENDENT"}:
            raise ValueError(f"incomplete paired intervention: {pair_id}")
        validate_paired_intervention(pair["COMMON"], pair["INDEPENDENT"])


def run_paired_pilot(
    records: Iterable[Mapping[str, Any]],
    backend: GenerationBackend,
    output_dir: Path,
    config: PilotConfig,
) -> dict[str, Any]:
    """Run and serialize a paired pilot without discarding parser failures."""
    materialized = list(records)
    _validate_records(materialized)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_config = asdict(config)
    saved_config.update(
        artifact_class=ARTIFACT_CLASS,
        python_version=platform.python_version(),
        platform=platform.platform(),
        record_count=len(materialized),
    )
    _json_dump(output_dir / "config.json", saved_config)

    generation_rows: list[dict[str, Any]] = []
    generation_path = output_dir / "generations.jsonl"
    with generation_path.open("w", encoding="utf-8") as handle:
        for record in materialized:
            prompt = build_revision_prompt(record)
            started = time.perf_counter()
            raw_response = backend.generate(prompt)
            elapsed = time.perf_counter() - started
            candidates = record.get("candidate_answers")
            final_answer, parse_error = parse_answer(raw_response, candidates)
            if (
                parse_error is None
                and candidates is not None
                and final_answer not in candidates
            ):
                parse_error = "answer_outside_candidates"
                final_answer = None
            support = effective_support(record["source_ids"], record["source_parents"])
            row = {
                "artifact_class": ARTIFACT_CLASS,
                "pair_id": record["pair_id"],
                "condition": record["condition"],
                "initial_answer": record["target_initial_answer"],
                "gold_answer": record["gold_answer"],
                "final_answer": final_answer,
                "initial_correct": record["target_initial_answer"]
                == record["gold_answer"],
                "final_correct": (
                    final_answer == record["gold_answer"]
                    if final_answer is not None
                    else None
                ),
                "parse_error": parse_error,
                "raw_response": raw_response,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "generation_seconds": elapsed,
                "nominal_support": support.nominal_support,
                "independent_support": support.independent_support,
                "corroboration_gap": support.corroboration_gap,
            }
            generation_rows.append(row)
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()

    conditions: dict[str, Any] = {}
    for condition in ("COMMON", "INDEPENDENT"):
        rows = [row for row in generation_rows if row["condition"] == condition]
        parsed = [row for row in rows if row["parse_error"] is None]
        summary = aggregate_revision_metrics(parsed)
        summary["parse_failure_rate"] = (
            (len(rows) - len(parsed)) / len(rows) if rows else 0.0
        )
        conditions[condition] = summary

    metrics = {
        "artifact_class": ARTIFACT_CLASS,
        "conditions": conditions,
        "paired_effects": paired_revision_effects(
            generation_rows, bootstrap_replicates=10_000, seed=config.seed
        ),
        "warning": (
            "Candidate experimental artifact; requires provenance, integrity, and "
            "analysis validation before supporting a manuscript claim."
        ),
    }
    _json_dump(output_dir / "metrics.json", metrics)
    return metrics


def run_adaptive_paired_pilot(
    items: Iterable[Mapping[str, Any]],
    backend: GenerationBackend,
    output_dir: Path,
    config: PilotConfig,
) -> dict[str, Any]:
    """Elicit actual private answers, then construct lineage-only revision pairs."""
    materialized = list(items)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(config.seed)

    baseline_rows: list[dict[str, Any]] = []
    pair_records: list[dict[str, Any]] = []
    baseline_path = output_dir / "baseline_generations.jsonl"
    with baseline_path.open("w", encoding="utf-8") as handle:
        seen_ids: set[str] = set()
        for index, item in enumerate(materialized):
            required = {"item_id", "question", "gold_answer", "candidate_answers"}
            missing = required - set(item)
            if missing:
                raise ValueError(f"item missing fields: {sorted(missing)}")
            item_id = str(item["item_id"])
            if item_id in seen_ids:
                raise ValueError(f"duplicate item_id: {item_id}")
            seen_ids.add(item_id)
            candidates = list(item["candidate_answers"])
            if item["gold_answer"] not in candidates:
                raise ValueError(f"gold answer outside candidates: {item_id}")

            prompt = build_private_prompt(item)
            started = time.perf_counter()
            raw_response = backend.generate(prompt)
            elapsed = time.perf_counter() - started
            private_answer, parse_error = parse_answer(raw_response, candidates)
            if parse_error is None and private_answer not in candidates:
                parse_error = "answer_outside_candidates"
                private_answer = None
            baseline_row = {
                "artifact_class": ARTIFACT_CLASS,
                "item_id": item_id,
                "gold_answer": item["gold_answer"],
                "private_answer": private_answer,
                "private_correct": (
                    private_answer == item["gold_answer"]
                    if private_answer is not None
                    else None
                ),
                "parse_error": parse_error,
                "raw_response": raw_response,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "generation_seconds": elapsed,
            }
            baseline_rows.append(baseline_row)
            handle.write(json.dumps(baseline_row, sort_keys=True) + "\n")
            handle.flush()

            if private_answer is None:
                continue
            distractors = [answer for answer in candidates if answer != item["gold_answer"]]
            if not distractors:
                raise ValueError(f"item requires at least one distractor: {item_id}")
            peer_answer = (
                rng.choice(distractors)
                if private_answer == item["gold_answer"]
                else item["gold_answer"]
            )
            base = {
                "pair_id": item_id,
                "dataset": item.get("dataset", "unspecified"),
                "source_example_index": item.get("source_example_index"),
                "question": item["question"],
                "gold_answer": item["gold_answer"],
                "candidate_answers": candidates,
                "target_initial_answer": private_answer,
                "peer_claims": [peer_answer, peer_answer, peer_answer],
                "peer_correctness": [
                    peer_answer == item["gold_answer"],
                    peer_answer == item["gold_answer"],
                    peer_answer == item["gold_answer"],
                ],
                "peer_confidence": [0.8, 0.8, 0.8],
                "message_order": [0, 1, 2],
            }
            pair_records.extend(build_lineage_pair(base, seed=config.seed + index))

    with (output_dir / "pairs.jsonl").open("w", encoding="utf-8") as handle:
        for record in pair_records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    # Alternate which condition is generated first to avoid a systematic order effect.
    execution_records: list[dict[str, Any]] = []
    for index in range(0, len(pair_records), 2):
        pair = pair_records[index : index + 2]
        execution_records.extend(pair if (index // 2) % 2 == 0 else list(reversed(pair)))
    metrics = run_paired_pilot(
        execution_records, backend, output_dir, config
    )
    parsed_baseline = [row for row in baseline_rows if row["parse_error"] is None]
    baseline_metrics = {
        "n": len(baseline_rows),
        "parsed_n": len(parsed_baseline),
        "parse_failure_rate": (
            (len(baseline_rows) - len(parsed_baseline)) / len(baseline_rows)
            if baseline_rows
            else 0.0
        ),
        "accuracy": (
            sum(bool(row["private_correct"]) for row in parsed_baseline)
            / len(parsed_baseline)
            if parsed_baseline
            else 0.0
        ),
    }
    metrics["baseline"] = baseline_metrics
    metrics["paired_item_count"] = len(pair_records) // 2
    metrics["protocol"] = "adaptive-private-first-v1"
    _json_dump(output_dir / "metrics.json", metrics)
    return metrics
