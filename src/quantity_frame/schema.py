"""Typed schema for quantity-frame candidate records."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


HASH_RE = re.compile(r"^[0-9a-f]{64}$")
RETIRED_CANDIDATE_FIELDS = frozenset(
    {
        "topic_id",
        "dataset_id",
        "source_id",
        "content_lineage",
        "lad_source_ids",
        "dcea_source_ids",
        "clep_item_id",
        "esp_pair_id",
        "evidence_state",
    }
)
VERDICT_FIELDS = frozenset({"audit_verdict", "gold_verdict"})
UNIT_ALIASES = {
    "%": "percent",
    "percent": "percent",
}


class SchemaError(ValueError):
    """Raised when a quantity-frame schema record is invalid."""


class SlotName(str, Enum):
    VALUE = "value"
    DENOMINATOR_OR_BASE = "denominator_or_base"
    SUBGROUP = "subgroup"
    TIME_WINDOW = "time_window"
    COMPARATOR = "comparator"
    UNIT = "unit"


class NotStated(str, Enum):
    NOT_STATED = "not_stated"


NOT_STATED = NotStated.NOT_STATED


@dataclass(frozen=True)
class QuantityFrame:
    value: str
    source_span: str
    denominator_or_base: str | NotStated = NOT_STATED
    subgroup: str | NotStated = NOT_STATED
    time_window: str | NotStated = NOT_STATED
    comparator: str | NotStated = NOT_STATED
    unit: str | NotStated = NOT_STATED

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _required_text(self.value, "value"))
        object.__setattr__(
            self, "source_span", _required_text(self.source_span, "source_span")
        )
        for slot in (
            SlotName.DENOMINATOR_OR_BASE,
            SlotName.SUBGROUP,
            SlotName.TIME_WINDOW,
            SlotName.COMPARATOR,
        ):
            object.__setattr__(
                self,
                slot.value,
                _optional_slot(getattr(self, slot.value), slot.value),
            )
        object.__setattr__(self, "unit", _unit_slot(self.unit))

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "QuantityFrame":
        if not isinstance(row, Mapping):
            raise SchemaError("quantity_frame must be a JSON object")
        _reject_unknown_fields(
            row,
            {
                "value",
                "denominator_or_base",
                "subgroup",
                "time_window",
                "comparator",
                "unit",
                "source_span",
            },
        )
        for field in ("value", "source_span"):
            if field not in row:
                message = (
                    f"missing required slot: {field}"
                    if field == "value"
                    else f"missing required field: {field}"
                )
                raise SchemaError(message)
        return cls(
            value=row["value"],
            denominator_or_base=row.get("denominator_or_base", NOT_STATED),
            subgroup=row.get("subgroup", NOT_STATED),
            time_window=row.get("time_window", NOT_STATED),
            comparator=row.get("comparator", NOT_STATED),
            unit=row.get("unit", NOT_STATED),
            source_span=row["source_span"],
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "value": self.value,
            "denominator_or_base": _serialize_slot(self.denominator_or_base),
            "subgroup": _serialize_slot(self.subgroup),
            "time_window": _serialize_slot(self.time_window),
            "comparator": _serialize_slot(self.comparator),
            "unit": _serialize_slot(self.unit),
            "source_span": self.source_span,
        }


@dataclass(frozen=True)
class CandidateItem:
    item_id: str
    corpus: str
    source_record_hash: str
    split: str
    source_text_hash: str
    target_text_hash: str
    source_text: str
    target_text: str
    quantity_frame: QuantityFrame
    candidate_only: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "item_id", _candidate_item_id(self.item_id, "item_id")
        )
        for field in ("corpus", "split", "source_text", "target_text"):
            object.__setattr__(
                self,
                field,
                _non_empty_text(getattr(self, field), f"{field} must be non-empty text"),
            )
        object.__setattr__(
            self,
            "source_record_hash",
            _hash(self.source_record_hash, "source_record_hash"),
        )
        object.__setattr__(
            self,
            "source_text_hash",
            _text_hash(self.source_text_hash, "source_text_hash", self.source_text),
        )
        object.__setattr__(
            self,
            "target_text_hash",
            _text_hash(self.target_text_hash, "target_text_hash", self.target_text),
        )
        if self.candidate_only is not True:
            raise SchemaError("candidate_only must be True")
        if not isinstance(self.quantity_frame, QuantityFrame):
            if isinstance(self.quantity_frame, Mapping):
                object.__setattr__(
                    self,
                    "quantity_frame",
                    QuantityFrame.from_dict(self.quantity_frame),
                )
            else:
                raise SchemaError("quantity_frame must be a QuantityFrame")

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "CandidateItem":
        if not isinstance(row, Mapping):
            raise SchemaError("candidate item must be a JSON object")
        for field in sorted(RETIRED_CANDIDATE_FIELDS):
            if field in row:
                raise SchemaError(f"retired field: {field}")
        for field in sorted(VERDICT_FIELDS):
            if field in row:
                raise SchemaError(f"verdict field is not allowed: {field}")
        _reject_unknown_fields(
            row,
            {
                "item_id",
                "corpus",
                "source_record_hash",
                "split",
                "source_text_hash",
                "target_text_hash",
                "source_text",
                "target_text",
                "candidate_only",
                "quantity_frame",
            },
        )
        for field in (
            "item_id",
            "corpus",
            "source_record_hash",
            "split",
            "source_text_hash",
            "target_text_hash",
            "source_text",
            "target_text",
            "quantity_frame",
        ):
            if field not in row:
                raise SchemaError(f"missing required field: {field}")
        return cls(
            item_id=row["item_id"],
            corpus=row["corpus"],
            source_record_hash=row["source_record_hash"],
            split=row["split"],
            source_text_hash=row["source_text_hash"],
            target_text_hash=row["target_text_hash"],
            source_text=row["source_text"],
            target_text=row["target_text"],
            candidate_only=row.get("candidate_only", True),
            quantity_frame=QuantityFrame.from_dict(row["quantity_frame"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "corpus": self.corpus,
            "source_record_hash": self.source_record_hash,
            "split": self.split,
            "source_text_hash": self.source_text_hash,
            "target_text_hash": self.target_text_hash,
            "source_text": self.source_text,
            "target_text": self.target_text,
            "candidate_only": True,
            "quantity_frame": self.quantity_frame.to_dict(),
        }


def _required_text(value: Any, field: str) -> str:
    if value is NOT_STATED:
        raise SchemaError(_missing_required_message(field))
    text = _non_empty_text(value, _missing_required_message(field))
    if _is_not_stated(text):
        raise SchemaError(_missing_required_message(field))
    return text


def _missing_required_message(field: str) -> str:
    if field == "source_span":
        return "missing required field: source_span"
    return f"missing required slot: {field}"


def _candidate_item_id(value: Any, field: str) -> str:
    return _non_empty_text(value, f"{field} must be non-empty stable text")


def _non_empty_text(value: Any, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(message)
    return value.strip()


def _optional_slot(value: Any, field: str) -> str | NotStated:
    if value is NOT_STATED:
        return NOT_STATED
    text = _non_empty_text(value, f"{field} must be non-empty text or not_stated")
    if _is_not_stated(text):
        return NOT_STATED
    if text.lower() == "inferred":
        raise SchemaError(f"{field} cannot be inferred")
    return text


def _unit_slot(value: Any) -> str | NotStated:
    if value is NOT_STATED:
        return NOT_STATED
    text = _non_empty_text(value, "unit must be non-empty text or not_stated")
    if _is_not_stated(text):
        return NOT_STATED
    if text.lower() == "inferred":
        raise SchemaError("unit cannot be inferred")
    canonical = UNIT_ALIASES.get(text.lower())
    return canonical if canonical is not None else text


def _is_not_stated(value: Any) -> bool:
    return value is NOT_STATED or value == NOT_STATED.value


def _serialize_slot(value: str | NotStated) -> str:
    return NOT_STATED.value if value is NOT_STATED else str(value)


def _hash(value: Any, field: str) -> str:
    text = _non_empty_text(value, f"{field} must be lowercase 64-hex")
    if not HASH_RE.match(text):
        raise SchemaError(f"{field} must be lowercase 64-hex")
    return text


def _text_hash(value: Any, field: str, text: str) -> str:
    digest = _hash(value, field)
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if digest != expected:
        raise SchemaError(f"{field} mismatch")
    return digest


def _reject_unknown_fields(row: Mapping[str, Any], allowed: set[str]) -> None:
    for field in sorted(set(row) - allowed):
        raise SchemaError(f"unknown field: {field}")
