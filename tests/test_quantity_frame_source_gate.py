import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Optional

from src.quantity_frame import SourceGateResult, evaluate_source_gate


BUILD_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "build_quantity_frame_audit.py"
)
SUMMARY_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "summarize_quantity_frame_audit.py"
)


def _load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _candidate(
    *,
    item_id: str,
    corpus: str,
    source_text: str,
    target_text: str,
    frame: dict[str, str],
) -> dict[str, object]:
    return {
        "item_id": item_id,
        "corpus": corpus,
        "source_record_hash": "a" * 64,
        "split": "validation",
        "source_text_hash": _hash(source_text),
        "target_text_hash": _hash(target_text),
        "source_text": source_text,
        "target_text": target_text,
        "candidate_only": True,
        "quantity_frame": frame,
    }


def _frame(**overrides: str) -> dict[str, str]:
    frame = {
        "value": "12",
        "denominator_or_base": "100 participants",
        "subgroup": "not_stated",
        "time_window": "12 weeks",
        "comparator": "placebo",
        "unit": "percent",
        "source_span": "12 of 100 participants",
    }
    frame.update(overrides)
    return frame


def _review_row(
    *,
    audit_id: str,
    reviewer: str,
    source_record_hash: str = "a" * 64,
    frame: Optional[dict[str, str]] = None,
    frame_validity: str = "yes",
    denominator_or_base: str = "yes",
    comparator: str = "yes",
    counterfactual_candidate: str = "yes",
    annotation_status: str = "completed",
) -> dict[str, object]:
    slots = {slot: "yes" for slot in _frame() if slot != "source_span"}
    slots["denominator_or_base"] = denominator_or_base
    slots["comparator"] = comparator
    return {
        "audit_id": audit_id,
        "review_id": f"{audit_id}-{reviewer}",
        "reviewer": reviewer,
        "source_record_hash": source_record_hash,
        "document_group_hash": "qf-doc-" + _hash(audit_id)[:16],
        "document_identity_basis": "source_text_hash_document_proxy",
        "document_identity_limitation": (
            "source datasets lack a stable document id in CandidateItem; "
            "source_text_hash is used as a conservative document proxy"
        ),
        "quantity_frame": frame or _frame(),
        "review_fields": {
            "frame_validity": frame_validity,
            "slots": slots,
            "counterfactual_candidate": counterfactual_candidate,
        },
        "annotation_status": annotation_status,
    }


def test_source_gate_rejects_thin_comparator_support():
    result = evaluate_source_gate(
        valid=120,
        corpora=2,
        denominator=40,
        comparator=29,
        counterfactual=80,
    )

    assert result.advance is False
    assert "comparator<30" in result.failures


def test_source_gate_requires_all_pre_gpu_thresholds():
    result = evaluate_source_gate(
        valid=100,
        corpora=2,
        denominator=30,
        comparator=30,
        counterfactual=60,
    )

    assert result == SourceGateResult(
        advance=True,
        status="pass",
        counts={
            "valid": 100,
            "corpora": 2,
            "denominator": 30,
            "comparator": 30,
            "counterfactual": 60,
        },
        failures=(),
    )


def test_audit_packet_uses_opaque_ids_bounded_context_and_full_slot_template(tmp_path):
    build_quantity_frame_audit = _load_script(BUILD_SCRIPT, "build_quantity_frame_audit")
    candidates = tmp_path / "candidates.jsonl"
    output = tmp_path / "audit_packet.jsonl"
    rows = [
        _candidate(
            item_id="qf-candidate-alpha",
            corpus="corpus-a",
            source_text=(
                "Intro sentence that should not all be copied. "
                "Document A says 12 of 100 participants improved after 12 weeks "
                "versus placebo for adults. "
                "Trailing sentence that should not all be copied."
            ),
            target_text="A lay summary.",
            frame=_frame(),
        ),
        _candidate(
            item_id="qf-candidate-beta",
            corpus="corpus-b",
            source_text="Document B says 3.2 mg versus placebo.",
            target_text="Another lay summary.",
            frame=_frame(value="3.2", denominator_or_base="not_stated", source_span="3.2 mg"),
        ),
    ]
    candidates.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    result = build_quantity_frame_audit.build_packet(
        candidates_path=candidates,
        output_path=output,
        per_corpus_limit=10,
        overlap_count=1,
        command="test command",
    )

    packet_rows = [
        json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()
    ]
    assert len(packet_rows) == 4
    assert result["candidate_development_only"] is True
    assert result["model_agent_development_only"] is True
    assert result["human_evidence"] is False
    assert result["document_identity_basis"] == "source_text_hash_document_proxy"
    assert result["document_identity_limitation"] == (
        "source datasets lack a stable document id in CandidateItem; "
        "source_text_hash is used as a conservative document proxy"
    )
    assert result["overlap_document_proxy_disjoint"] is True
    assert "corpus" not in json.dumps(packet_rows)
    assert "condition" not in json.dumps(packet_rows)
    assert all("source_text" not in row for row in packet_rows)
    assert all("target_text" not in row for row in packet_rows)
    assert "Intro sentence that should not all be copied" not in json.dumps(packet_rows)
    assert all(row["audit_id"].startswith("qf-audit-") for row in packet_rows)
    assert all(row["reviewer"] in {"reviewer_a", "reviewer_b"} for row in packet_rows)
    assert all(row["document_group_hash"].startswith("qf-doc-") for row in packet_rows)
    assert {row["document_identity_basis"] for row in packet_rows} == {
        "source_text_hash_document_proxy"
    }
    assert {row["document_identity_limitation"] for row in packet_rows} == {
        "source datasets lack a stable document id in CandidateItem; "
        "source_text_hash is used as a conservative document proxy"
    }
    for row in packet_rows:
        assert row["source_span"] in row["source_context"]
        assert len(row["source_context"]) <= 220
        assert row["source_context"] != rows[0]["source_text"]
    assert {row["review_fields"]["frame_validity"] for row in packet_rows} == {
        "unreviewed"
    }
    for slot in (
        "value",
        "denominator_or_base",
        "subgroup",
        "time_window",
        "comparator",
        "unit",
    ):
        assert {row["review_fields"]["slots"][slot] for row in packet_rows} == {
            "unreviewed"
        }


def test_builder_marks_reused_document_proxy_in_overlap_as_not_disjoint(tmp_path):
    build_quantity_frame_audit = _load_script(BUILD_SCRIPT, "build_quantity_frame_audit")
    source_text = "The same source says 12 of 100 participants improved versus placebo."
    candidates = tmp_path / "candidates.jsonl"
    output = tmp_path / "audit_packet.jsonl"
    candidates.write_text(
        "".join(
            json.dumps(row, sort_keys=True) + "\n"
            for row in [
                _candidate(
                    item_id="qf-candidate-1",
                    corpus="corpus-a",
                    source_text=source_text,
                    target_text="A target.",
                    frame=_frame(),
                ),
                _candidate(
                    item_id="qf-candidate-2",
                    corpus="corpus-b",
                    source_text=source_text,
                    target_text="Another target.",
                    frame=_frame(source_span="versus placebo"),
                ),
            ]
        ),
        encoding="utf-8",
    )

    result = build_quantity_frame_audit.build_packet(
        candidates_path=candidates,
        output_path=output,
        per_corpus_limit=10,
        overlap_count=2,
        command="test command",
    )

    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert result["overlap_document_proxy_disjoint"] is False
    assert result["document_proxy_reuse_count"] == 1
    assert len({row["document_group_hash"] for row in rows}) == 1


def test_summary_preserves_disagreements_and_pending_gate_without_annotations(tmp_path):
    build_quantity_frame_audit = _load_script(BUILD_SCRIPT, "build_quantity_frame_audit")
    summarize_quantity_frame_audit = _load_script(
        SUMMARY_SCRIPT, "summarize_quantity_frame_audit"
    )
    candidates = tmp_path / "candidates.jsonl"
    packet = tmp_path / "audit_packet.jsonl"
    gate = tmp_path / "source_gate.json"
    candidates.write_text(
        "".join(
            json.dumps(row, sort_keys=True) + "\n"
            for row in [
                _candidate(
                    item_id="qf-candidate-1",
                    corpus="corpus-a",
                    source_text="A: 12 of 100 participants improved.",
                    target_text="A target.",
                    frame=_frame(),
                ),
                _candidate(
                    item_id="qf-candidate-2",
                    corpus="corpus-b",
                    source_text="B: 30% improved versus control.",
                    target_text="B target.",
                    frame=_frame(value="30", source_span="30%"),
                ),
            ]
        ),
        encoding="utf-8",
    )
    build_quantity_frame_audit.build_packet(
        candidates_path=candidates,
        output_path=packet,
        per_corpus_limit=10,
        overlap_count=1,
        command="test command",
    )
    result = summarize_quantity_frame_audit.summarize(
        packet_path=packet,
        output_path=gate,
        command="summary command",
    )

    assert result["status"] == "pending_annotation"
    assert result["advance"] is False
    assert result["human_evidence"] is False
    assert result["model_agent_development_only"] is True
    assert result["document_identity"] == {
        "basis": "source_text_hash_document_proxy",
        "limitation": (
            "source datasets lack a stable document id in CandidateItem; "
            "source_text_hash is used as a conservative document proxy"
        ),
        "document_proxy_reuse_count": 0,
        "overlap_document_proxy_disjoint": True,
    }
    assert result["raw_disagreements"] == []
    assert result["integrity_failures"]
    assert set(result["agreement_by_field"]) == {
        "frame_validity",
        "value",
        "denominator_or_base",
        "subgroup",
        "time_window",
        "comparator",
        "unit",
        "counterfactual_candidate",
    }
    assert result["source_gate"]["failures"]
    assert json.loads(gate.read_text(encoding="utf-8")) == result


def test_summary_includes_counterfactual_disagreements(tmp_path):
    summarize_quantity_frame_audit = _load_script(
        SUMMARY_SCRIPT, "summarize_quantity_frame_audit"
    )
    packet = tmp_path / "audit_packet.jsonl"
    gate = tmp_path / "source_gate.json"
    base = {
        "audit_id": "qf-audit-alpha",
        "review_id": "qf-review-a",
        "reviewer": "reviewer_a",
        "source_record_hash": "a" * 64,
        "document_group_hash": "qf-doc-" + "b" * 16,
        "quantity_frame": _frame(),
        "review_fields": {
            "frame_validity": "yes",
            "slots": {slot: "yes" for slot in _frame() if slot != "source_span"},
            "counterfactual_candidate": "yes",
        },
        "annotation_status": "completed",
    }
    other = json.loads(json.dumps(base))
    other["review_id"] = "qf-review-b"
    other["reviewer"] = "reviewer_b"
    other["review_fields"]["counterfactual_candidate"] = "no"
    packet.write_text(
        json.dumps(base, sort_keys=True) + "\n" + json.dumps(other, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = summarize_quantity_frame_audit.summarize(
        packet_path=packet,
        output_path=gate,
        command="summary command",
    )

    assert result["agreement_by_field"]["counterfactual_candidate"] == {
        "agreement": 0.0,
        "agreements": 0,
        "comparable": 1,
    }
    assert result["raw_disagreements"] == [
        {
            "audit_id": "qf-audit-alpha",
            "field": "counterfactual_candidate",
            "labels": {"reviewer_a": "yes", "reviewer_b": "no"},
        }
    ]


def test_summary_rejects_100_single_reviewer_positive_rows(tmp_path):
    summarize_quantity_frame_audit = _load_script(
        SUMMARY_SCRIPT, "summarize_quantity_frame_audit"
    )
    packet = tmp_path / "audit_packet.jsonl"
    gate = tmp_path / "source_gate.json"
    rows = [
        _review_row(
            audit_id=f"qf-audit-{index:03d}",
            reviewer="reviewer_a",
            source_record_hash=("a" if index < 50 else "b") * 64,
        )
        for index in range(100)
    ]
    packet.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    result = summarize_quantity_frame_audit.summarize(
        packet_path=packet,
        output_path=gate,
        command="summary command",
    )

    assert result["advance"] is False
    assert result["source_gate"]["counts"]["valid"] == 0
    assert any("missing_reviewer:qf-audit-000:reviewer_b" in failure for failure in result["integrity_failures"])
    assert any(
        issue["field"] == "integrity" and "missing_reviewer:qf-audit-000:reviewer_b" in issue["issues"]
        for issue in result["raw_disagreements"]
    )


def test_summary_rejects_duplicate_reviewer_rows(tmp_path):
    summarize_quantity_frame_audit = _load_script(
        SUMMARY_SCRIPT, "summarize_quantity_frame_audit"
    )
    packet = tmp_path / "audit_packet.jsonl"
    gate = tmp_path / "source_gate.json"
    rows = [
        _review_row(audit_id="qf-audit-dup", reviewer="reviewer_a"),
        _review_row(audit_id="qf-audit-dup", reviewer="reviewer_a"),
        _review_row(audit_id="qf-audit-dup", reviewer="reviewer_b"),
    ]
    packet.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    result = summarize_quantity_frame_audit.summarize(
        packet_path=packet,
        output_path=gate,
        command="summary command",
    )

    assert result["advance"] is False
    assert result["source_gate"]["counts"]["valid"] == 0
    assert "duplicate_reviewer:qf-audit-dup:reviewer_a" in result["integrity_failures"]


def test_summary_rejects_invalid_closed_vocabulary_labels(tmp_path):
    summarize_quantity_frame_audit = _load_script(
        SUMMARY_SCRIPT, "summarize_quantity_frame_audit"
    )
    packet = tmp_path / "audit_packet.jsonl"
    gate = tmp_path / "source_gate.json"
    rows = [
        _review_row(audit_id="qf-audit-label", reviewer="reviewer_a", frame_validity="maybe"),
        _review_row(audit_id="qf-audit-label", reviewer="reviewer_b"),
    ]
    packet.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    result = summarize_quantity_frame_audit.summarize(
        packet_path=packet,
        output_path=gate,
        command="summary command",
    )

    assert result["advance"] is False
    assert result["source_gate"]["counts"]["valid"] == 0
    assert "invalid_label:qf-audit-label:reviewer_a:frame_validity:maybe" in result[
        "integrity_failures"
    ]


def test_slot_disagreement_prevents_denominator_and_comparator_counts(tmp_path):
    summarize_quantity_frame_audit = _load_script(
        SUMMARY_SCRIPT, "summarize_quantity_frame_audit"
    )
    packet = tmp_path / "audit_packet.jsonl"
    gate = tmp_path / "source_gate.json"
    rows = [
        _review_row(
            audit_id="qf-audit-slot",
            reviewer="reviewer_a",
            denominator_or_base="yes",
            comparator="yes",
        ),
        _review_row(
            audit_id="qf-audit-slot",
            reviewer="reviewer_b",
            denominator_or_base="no",
            comparator="no",
        ),
    ]
    packet.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    result = summarize_quantity_frame_audit.summarize(
        packet_path=packet,
        output_path=gate,
        command="summary command",
    )

    assert result["source_gate"]["counts"]["valid"] == 1
    assert result["source_gate"]["counts"]["denominator"] == 0
    assert result["source_gate"]["counts"]["comparator"] == 0
    assert {
        disagreement["field"]
        for disagreement in result["raw_disagreements"]
        if disagreement["audit_id"] == "qf-audit-slot"
    } >= {"denominator_or_base", "comparator"}
