from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple


ALLOWED_EVIDENCE_STATES = ("sufficient", "insufficient", "conflict")
ALLOWED_ROUTER_ACTIONS = ("clarify", "retrieve", "abstain")
ALLOWED_INTERVENTION_KINDS = (
    "add_conflicting_sentence",
    "remove_conflicting_sentence",
    "remove_required_premise",
    "restore_required_premise",
)
ALLOWED_INTERVENTION_FIELDS = ("evidence",)


class EvidenceStateValidationError(ValueError):
    """Raised when an evidence-state record violates the schema contract."""


@dataclass(frozen=True)
class EvidenceItem:
    item_id: str
    pair_id: str
    question: str
    evidence: Tuple[str, ...]
    answer: str
    evidence_state: str
    expected_action: str
    intervention: Mapping[str, object]
    source_ids: Tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text("item_id", self.item_id)
        _require_text("pair_id", self.pair_id)
        _require_text("question", self.question)
        _require_text("answer", self.answer)
        _require_text_sequence("evidence", self.evidence)
        _require_text_sequence("source_ids", self.source_ids)
        _require_allowed(
            "evidence_state", self.evidence_state, ALLOWED_EVIDENCE_STATES
        )
        _require_allowed(
            "expected_action", self.expected_action, ALLOWED_ROUTER_ACTIONS
        )
        _validate_intervention(self.intervention)


@dataclass(frozen=True)
class EvidencePair:
    pair_id: str
    first: EvidenceItem
    second: EvidenceItem

    def __post_init__(self) -> None:
        _require_text("pair_id", self.pair_id)
        if self.first.pair_id != self.pair_id or self.second.pair_id != self.pair_id:
            raise EvidenceStateValidationError("pair_id must match both items")
        if self.first.question != self.second.question:
            raise EvidenceStateValidationError("paired items must keep the same question")
        if self.first.evidence_state == self.second.evidence_state:
            raise EvidenceStateValidationError(
                "paired items must use different evidence_state values"
            )
        if self.first.answer != self.second.answer:
            raise EvidenceStateValidationError(
                "only evidence_state may differ outside explicit evidence intervention"
            )
        if self.first.source_ids != self.second.source_ids:
            raise EvidenceStateValidationError(
                "only evidence_state may differ outside explicit evidence intervention"
            )

    @property
    def question(self) -> str:
        return self.first.question

    @property
    def evidence_states(self) -> Tuple[str, str]:
        return (self.first.evidence_state, self.second.evidence_state)


def _require_text(field_name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceStateValidationError(f"{field_name} must be non-empty text")


def _require_text_sequence(field_name: str, value: Tuple[str, ...]) -> None:
    if not isinstance(value, tuple) or not value:
        raise EvidenceStateValidationError(f"{field_name} must be a non-empty tuple")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise EvidenceStateValidationError(
                f"{field_name}[{index}] must be non-empty text"
            )


def _require_allowed(field_name: str, value: str, allowed: Tuple[str, ...]) -> None:
    if value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise EvidenceStateValidationError(
            f"{field_name} must be one of {allowed_text}"
        )


def _validate_intervention(intervention: Mapping[str, object]) -> None:
    if not isinstance(intervention, Mapping):
        raise EvidenceStateValidationError("intervention must be a mapping")
    if "kind" not in intervention:
        raise EvidenceStateValidationError("intervention.kind is required")
    if "field" not in intervention:
        raise EvidenceStateValidationError("intervention.field is required")

    kind = intervention["kind"]
    field = intervention["field"]
    _require_allowed("intervention.kind", kind, ALLOWED_INTERVENTION_KINDS)
    if field not in ALLOWED_INTERVENTION_FIELDS:
        raise EvidenceStateValidationError("intervention.field must be evidence")

    if "evidence_index" in intervention:
        index = intervention["evidence_index"]
        if not isinstance(index, int) or index < 0:
            raise EvidenceStateValidationError(
                "intervention.evidence_index must be a non-negative integer"
            )
