import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "merge_quantity_frame_audits.py"
SCRIPT_SPEC = importlib.util.spec_from_file_location(
    "merge_quantity_frame_audits", SCRIPT_PATH
)
merge_quantity_frame_audits = importlib.util.module_from_spec(SCRIPT_SPEC)
assert SCRIPT_SPEC.loader is not None
SCRIPT_SPEC.loader.exec_module(merge_quantity_frame_audits)


def _base_row(review_id: str, reviewer: str) -> dict:
    return {
        "annotation_status": "pending",
        "audit_id": "audit-1",
        "candidate_development_only": True,
        "candidate_ref": "candidate-1",
        "document_group_hash": "document-1",
        "document_identity_basis": "source_text_hash_document_proxy",
        "document_identity_limitation": "document proxy",
        "human_evidence": False,
        "model_agent_development_only": True,
        "quantity_frame": {
            "value": "10",
            "denominator_or_base": "20",
            "subgroup": "not_stated",
            "time_window": "not_stated",
            "comparator": "not_stated",
            "unit": "%",
        },
        "review_fields": {
            "frame_validity": "unreviewed",
            "slots": {
                "value": "unreviewed",
                "denominator_or_base": "unreviewed",
                "subgroup": "unreviewed",
                "time_window": "unreviewed",
                "comparator": "unreviewed",
                "unit": "unreviewed",
            },
            "counterfactual_candidate": "unreviewed",
        },
        "review_id": review_id,
        "reviewer": reviewer,
        "source_context": "10 of 20 participants",
        "source_record_hash": "record-hash",
        "source_span": "10 of 20",
        "source_text_hash": "source-hash",
        "split": "validation",
        "target_text_hash": "target-hash",
    }


def _completed(row: dict, label: str = "yes") -> dict:
    result = json.loads(json.dumps(row))
    result["annotation_status"] = "completed"
    result["review_fields"] = {
        "frame_validity": label,
        "slots": {name: label for name in row["quantity_frame"]},
        "counterfactual_candidate": label,
    }
    return result


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _merge(tmp_path: Path, base_rows: list[dict], shard_rows: list[list[dict]]):
    base_path = tmp_path / "base.jsonl"
    output_path = tmp_path / "merged.jsonl"
    _write_jsonl(base_path, base_rows)
    shard_paths = []
    for index, rows in enumerate(shard_rows):
        shard_path = tmp_path / f"shard-{index}.jsonl"
        _write_jsonl(shard_path, rows)
        shard_paths.append(shard_path)
    result = merge_quantity_frame_audits.merge(
        base_path=base_path,
        shard_paths=shard_paths,
        output_path=output_path,
        command="test merge",
    )
    return result, output_path


def test_merge_preserves_base_order_and_reports_deterministic_metadata(tmp_path):
    first = _base_row("review-1", "reviewer_a")
    second = _base_row("review-2", "reviewer_b")

    result, output_path = _merge(
        tmp_path, [first, second], [[_completed(second)], [_completed(first)]]
    )

    output_rows = [json.loads(line) for line in output_path.read_text().splitlines()]
    assert [row["review_id"] for row in output_rows] == ["review-1", "review-2"]
    assert result["rows"] == 2
    assert result["human_evidence"] is False
    assert result["model_agent_development_only"] is True
    assert result["output_sha256"]
    assert len(result["input_sha256s"]) == 3


@pytest.mark.parametrize(
    ("shards", "message"),
    [
        (lambda a, b: [[a]], "missing review_id"),
        (lambda a, b: [[a, a, b]], "duplicate review_id"),
        (
            lambda a, b: [[a, b, _completed(_base_row("unexpected", "reviewer_a"))]],
            "unexpected review_id",
        ),
    ],
)
def test_merge_rejects_non_exact_review_id_coverage(tmp_path, shards, message):
    first = _base_row("review-1", "reviewer_a")
    second = _base_row("review-2", "reviewer_b")

    with pytest.raises(ValueError, match=message):
        _merge(tmp_path, [first, second], shards(_completed(first), _completed(second)))


def test_merge_rejects_immutable_field_or_reviewer_change(tmp_path):
    base = _base_row("review-1", "reviewer_a")
    changed = _completed(base)
    changed["source_span"] = "changed"

    with pytest.raises(ValueError, match="immutable field changed.*source_span"):
        _merge(tmp_path, [base], [[changed]])

    changed = _completed(base)
    changed["reviewer"] = "reviewer_b"
    with pytest.raises(ValueError, match="immutable field changed.*reviewer"):
        _merge(tmp_path, [base], [[changed]])


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda row: row.update(annotation_status="pending"), "must be completed"),
        (
            lambda row: row["review_fields"].update(frame_validity="maybe"),
            "invalid label",
        ),
        (lambda row: row.update(human_evidence=True), "immutable field changed"),
        (
            lambda row: row.update(model_agent_development_only=False),
            "immutable field changed",
        ),
    ],
)
def test_merge_rejects_incomplete_invalid_or_non_model_rows(tmp_path, mutate, message):
    base = _base_row("review-1", "reviewer_a")
    completed = _completed(base)
    mutate(completed)

    with pytest.raises(ValueError, match=message):
        _merge(tmp_path, [base], [[completed]])
