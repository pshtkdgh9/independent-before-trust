from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, Tuple

from src.evidence_state.schema import EvidenceItem


UNCERTAINTY_CUES = ("maybe", "possibly", "unknown", "unclear", "not sure")


class EvidenceStateBuildError(ValueError):
    """Raised when source material is not ready for item construction."""


def build_evidence_state_items(
    source_pack_rows: Iterable[Mapping[str, Any]],
) -> Tuple[EvidenceItem, ...]:
    items: list[EvidenceItem] = []
    for row_number, row in enumerate(source_pack_rows, start=1):
        source = _validate_source_pack_row(row, row_number)
        items.extend(_build_insufficiency_pair(source))
        items.extend(_build_conflict_pair(source))
    return tuple(sorted(items, key=lambda item: item.item_id))


def load_source_pack_jsonl(path: Path) -> Tuple[Mapping[str, Any], ...]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise EvidenceStateBuildError(
                    f"invalid JSON in source pack line {line_number}: {exc.msg}"
                ) from exc
    if not rows:
        raise EvidenceStateBuildError("source pack is empty; no evidence synthesized")
    return tuple(rows)


def write_items_jsonl(items: Sequence[EvidenceItem], output_path: Path) -> None:
    text = items_to_jsonl(items)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text + ("\n" if text else ""), encoding="utf-8", newline="\n")


def items_to_jsonl(items: Sequence[EvidenceItem]) -> str:
    rows = [_item_to_row(item) for item in sorted(items, key=lambda item: item.item_id)]
    return "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)


def _build_insufficiency_pair(source: Mapping[str, Any]) -> Tuple[EvidenceItem, ...]:
    pair_id = f"{source['source_pack_id']}:insufficiency"
    index = source["required_premise_index"]
    evidence = tuple(source["evidence_sentences"])
    insufficient_evidence = evidence[:index] + evidence[index + 1 :]
    removed = evidence[index]

    return (
        _make_item(
            source=source,
            pair_id=pair_id,
            pair_kind="insufficiency",
            evidence_state="sufficient",
            expected_action="proceed",
            evidence=evidence,
            intervention_kind="restore_required_premise",
            evidence_index=index,
            expected_directional_flip="proceed_to_retrieve",
            extra_intervention={"restored_sentence_hash": _sha256_text(removed)},
        ),
        _make_item(
            source=source,
            pair_id=pair_id,
            pair_kind="insufficiency",
            evidence_state="insufficient",
            expected_action="retrieve",
            evidence=insufficient_evidence,
            intervention_kind="remove_required_premise",
            evidence_index=index,
            expected_directional_flip="proceed_to_retrieve",
            extra_intervention={"removed_sentence_hash": _sha256_text(removed)},
        ),
    )


def _build_conflict_pair(source: Mapping[str, Any]) -> Tuple[EvidenceItem, ...]:
    pair_id = f"{source['source_pack_id']}:conflict"
    index = source["required_premise_index"]
    evidence = tuple(source["evidence_sentences"])
    original = evidence[index]
    incompatible = source["incompatible_sentence"]
    conflict_index = len(evidence)
    conflict_evidence = evidence + (incompatible,)

    return (
        _make_item(
            source=source,
            pair_id=pair_id,
            pair_kind="conflict",
            evidence_state="sufficient",
            expected_action="proceed",
            evidence=evidence,
            intervention_kind="remove_conflicting_sentence",
            evidence_index=conflict_index,
            expected_directional_flip="proceed_to_abstain",
            extra_intervention={"target_sentence_hash": _sha256_text(original)},
        ),
        _make_item(
            source=source,
            pair_id=pair_id,
            pair_kind="conflict",
            evidence_state="conflict",
            expected_action="abstain",
            evidence=conflict_evidence,
            intervention_kind="add_conflicting_sentence",
            evidence_index=conflict_index,
            expected_directional_flip="proceed_to_abstain",
            extra_intervention={
                "original_sentence_hash": _sha256_text(original),
                "incompatible_sentence_hash": _sha256_text(incompatible),
            },
        ),
    )


def _make_item(
    *,
    source: Mapping[str, Any],
    pair_id: str,
    pair_kind: str,
    evidence_state: str,
    expected_action: str,
    evidence: Tuple[str, ...],
    intervention_kind: str,
    evidence_index: int,
    expected_directional_flip: str,
    extra_intervention: Mapping[str, str],
) -> EvidenceItem:
    item_id = f"{pair_id}:{evidence_state}"
    source_links = (
        {
            "source_id": source["source_id"],
            "source_url": source["source_url"],
        },
    )
    item_payload = {
        "item_id": item_id,
        "pair_id": pair_id,
        "question": source["question"],
        "evidence": list(evidence),
        "answer": source["answer"],
        "evidence_state": evidence_state,
        "expected_action": expected_action,
        "source_ids": [source["source_id"]],
        "source_links": source_links,
        "expected_directional_flip": expected_directional_flip,
    }
    item_hash = _sha256_json(item_payload)
    intervention = {
        "kind": intervention_kind,
        "field": "evidence",
        "evidence_index": evidence_index,
        "pair_kind": pair_kind,
        "answer_hash": _sha256_text(source["answer"]),
        "item_hash": item_hash,
        "source_links": source_links,
        "expected_directional_flip": expected_directional_flip,
        **extra_intervention,
    }
    return EvidenceItem(
        item_id=item_id,
        pair_id=pair_id,
        question=source["question"],
        evidence=evidence,
        answer=source["answer"],
        evidence_state=evidence_state,
        expected_action=expected_action,
        intervention=intervention,
        source_ids=(source["source_id"],),
    )


def _item_to_row(item: EvidenceItem) -> Mapping[str, Any]:
    return {
        "item_id": item.item_id,
        "pair_id": item.pair_id,
        "question": item.question,
        "evidence": list(item.evidence),
        "answer": item.answer,
        "evidence_state": item.evidence_state,
        "expected_action": item.expected_action,
        "intervention": dict(item.intervention),
        "source_ids": list(item.source_ids),
        "item_hash": item.intervention["item_hash"],
        "source_links": list(item.intervention["source_links"]),
        "expected_directional_flip": item.intervention["expected_directional_flip"],
    }


def _validate_source_pack_row(row: Mapping[str, Any], row_number: int) -> Mapping[str, Any]:
    if not isinstance(row, Mapping):
        raise EvidenceStateBuildError(f"source pack row {row_number} must be an object")
    if row.get("source_material_sufficient") is not True:
        raise EvidenceStateBuildError(
            f"source pack row {row_number} refused: source_material_sufficient=false"
        )
    if row.get("auditable") is not True:
        raise EvidenceStateBuildError(f"source pack row {row_number} refused: unauditable")

    required_text_fields = (
        "source_pack_id",
        "source_id",
        "source_url",
        "question",
        "answer",
        "incompatible_sentence",
    )
    for field_name in required_text_fields:
        _require_text(row, field_name, row_number)

    evidence = row.get("evidence_sentences")
    if not isinstance(evidence, list) or len(evidence) < 2:
        raise EvidenceStateBuildError(
            f"source pack row {row_number} requires at least two evidence_sentences"
        )
    for index, sentence in enumerate(evidence):
        if not isinstance(sentence, str) or not sentence.strip():
            raise EvidenceStateBuildError(
                f"source pack row {row_number} evidence_sentences[{index}] is empty"
            )
        _reject_uncertainty_cues(sentence, row_number)

    required_index = row.get("required_premise_index")
    if (
        not isinstance(required_index, int)
        or required_index < 0
        or required_index >= len(evidence)
    ):
        raise EvidenceStateBuildError(
            f"source pack row {row_number} has invalid required_premise_index"
        )

    incompatible = str(row["incompatible_sentence"])
    _reject_uncertainty_cues(incompatible, row_number)
    if incompatible in evidence:
        raise EvidenceStateBuildError(
            f"source pack row {row_number} incompatible_sentence must add new evidence"
        )

    return {
        **row,
        "evidence_sentences": tuple(str(sentence) for sentence in evidence),
        "required_premise_index": required_index,
    }


def _require_text(row: Mapping[str, Any], field_name: str, row_number: int) -> None:
    if not isinstance(row.get(field_name), str) or not row[field_name].strip():
        raise EvidenceStateBuildError(
            f"source pack row {row_number} missing non-empty {field_name}"
        )


def _reject_uncertainty_cues(text: str, row_number: int) -> None:
    lowered = text.lower()
    if any(cue in lowered for cue in UNCERTAINTY_CUES):
        raise EvidenceStateBuildError(
            f"source pack row {row_number} contains artificial uncertainty cue"
        )


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_json(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=list)
    return _sha256_text(payload)
