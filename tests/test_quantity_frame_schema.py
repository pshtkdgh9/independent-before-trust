import json

import pytest

from src.quantity_frame import CandidateItem, NOT_STATED, QuantityFrame, SchemaError, SlotName


VALID_HASH = "a" * 64
OTHER_HASH = "b" * 64
THIRD_HASH = "c" * 64


def representative_frame(**overrides):
    values = {
        "value": "12",
        "denominator_or_base": "100 participants",
        "subgroup": NOT_STATED,
        "time_window": "12 weeks",
        "comparator": "placebo",
        "unit": "Percent",
        "source_span": "12 of 100 participants",
    }
    values.update(overrides)
    return QuantityFrame(**values)


def representative_candidate(**overrides):
    values = {
        "item_id": "cochrane-validation-000001",
        "corpus": "GEM/cochrane-simplification",
        "source_record_hash": VALID_HASH,
        "split": "validation",
        "source_text_hash": OTHER_HASH,
        "target_text_hash": THIRD_HASH,
        "source_text": "In the trial, 12 of 100 participants improved after 12 weeks.",
        "target_text": "Twelve percent improved after 12 weeks.",
        "quantity_frame": representative_frame(),
    }
    values.update(overrides)
    return CandidateItem(**values)


def test_slot_names_are_the_typed_quantity_frame_contract():
    assert [slot.value for slot in SlotName] == [
        "value",
        "denominator_or_base",
        "subgroup",
        "time_window",
        "comparator",
        "unit",
    ]


def test_quantity_frame_requires_value_and_source_span():
    with pytest.raises(SchemaError, match="missing required slot: value"):
        representative_frame(value=NOT_STATED)

    with pytest.raises(SchemaError, match="missing required field: source_span"):
        representative_frame(source_span="")


def test_quantity_frame_serializes_not_stated_slots_explicitly_and_canonicalizes_unit():
    frame = representative_frame()

    assert frame.value == "12"
    assert frame.unit == "percent"
    assert frame.to_dict() == {
        "value": "12",
        "denominator_or_base": "100 participants",
        "subgroup": "not_stated",
        "time_window": "12 weeks",
        "comparator": "placebo",
        "unit": "percent",
        "source_span": "12 of 100 participants",
    }
    assert QuantityFrame.from_dict(frame.to_dict()) == frame
    assert json.loads(json.dumps(frame.to_dict(), sort_keys=True))["subgroup"] == "not_stated"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("denominator_or_base", "", "denominator_or_base must be non-empty text or not_stated"),
        ("time_window", " inferred ", "time_window cannot be inferred"),
        ("unit", "", "unit must be non-empty text or not_stated"),
    ],
)
def test_quantity_frame_rejects_empty_or_inferred_optional_slots(field, value, message):
    with pytest.raises(SchemaError, match=message):
        representative_frame(**{field: value})


def test_quantity_frame_distinguishes_not_stated_from_unknown_and_zero():
    frame = representative_frame(
        value="0",
        denominator_or_base="unknown",
        subgroup="0",
        time_window="not applicable",
        unit="1",
    )

    assert frame.value == "0"
    assert frame.denominator_or_base == "unknown"
    assert frame.subgroup == "0"
    assert frame.time_window == "not applicable"
    assert frame.unit == "1"
    assert frame.to_dict()["unit"] == "1"


def test_quantity_frame_preserves_unknown_unit_as_literal_text():
    frame = representative_frame(unit="unknown")

    assert frame.unit == "unknown"
    assert frame.to_dict()["unit"] == "unknown"


def test_candidate_item_requires_stable_ids_lineage_and_candidate_only_without_verdicts():
    candidate = representative_candidate()

    assert candidate.candidate_only is True
    assert candidate.to_dict() == {
        "item_id": "cochrane-validation-000001",
        "corpus": "GEM/cochrane-simplification",
        "source_record_hash": VALID_HASH,
        "split": "validation",
        "source_text_hash": OTHER_HASH,
        "target_text_hash": THIRD_HASH,
        "source_text": "In the trial, 12 of 100 participants improved after 12 weeks.",
        "target_text": "Twelve percent improved after 12 weeks.",
        "candidate_only": True,
        "quantity_frame": representative_frame().to_dict(),
    }
    assert CandidateItem.from_dict(candidate.to_dict()) == candidate


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("item_id", "", "item_id must be non-empty stable text"),
        ("corpus", "", "corpus must be non-empty text"),
        ("source_record_hash", "abc", "source_record_hash must be lowercase 64-hex"),
        ("source_text_hash", "A" * 64, "source_text_hash must be lowercase 64-hex"),
        ("target_text_hash", "g" * 64, "target_text_hash must be lowercase 64-hex"),
        ("candidate_only", False, "candidate_only must be True"),
    ],
)
def test_candidate_item_rejects_invalid_identity_lineage_or_candidate_flag(field, value, message):
    with pytest.raises(SchemaError, match=message):
        representative_candidate(**{field: value})


@pytest.mark.parametrize(
    "retired_field",
    [
        "topic_id",
        "dataset_id",
        "source_id",
        "content_lineage",
        "lad_source_ids",
        "dcea_source_ids",
        "clep_item_id",
        "esp_pair_id",
        "evidence_state",
    ],
)
def test_candidate_item_rejects_retired_topic_identifiers_and_content_lineage_fields(retired_field):
    row = representative_candidate().to_dict()
    row[retired_field] = "retired"

    with pytest.raises(SchemaError, match=f"retired field: {retired_field}"):
        CandidateItem.from_dict(row)


def test_candidate_item_does_not_overblock_retired_domain_words_in_text():
    candidate = representative_candidate(
        source_text="The LAD artery evidence state was described in the source.",
        target_text="The DCEA, CLEP, and ESP terms appear as ordinary text.",
    )

    assert "LAD artery" in candidate.source_text
    assert CandidateItem.from_dict(candidate.to_dict()) == candidate


@pytest.mark.parametrize("verdict_field", ["audit_verdict", "gold_verdict"])
def test_candidate_item_rejects_audit_or_gold_verdicts(verdict_field):
    row = representative_candidate().to_dict()
    row[verdict_field] = "pass"

    with pytest.raises(SchemaError, match=f"verdict field is not allowed: {verdict_field}"):
        CandidateItem.from_dict(row)


def test_candidate_item_serialization_is_deterministic():
    candidate = representative_candidate()

    assert json.dumps(candidate.to_dict(), sort_keys=True) == json.dumps(
        CandidateItem.from_dict(candidate.to_dict()).to_dict(),
        sort_keys=True,
    )
