"""Summarize blinded quantity-frame source audits and write the source gate."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.quantity_frame.decision import evaluate_source_gate
from src.quantity_frame.schema import NOT_STATED, SlotName


DEFAULT_PACKET = Path("results/strong_accept_loop/quantity_frame/audit_packet.jsonl")
DEFAULT_OUTPUT = Path("results/strong_accept_loop/quantity_frame/source_gate.json")
EXPECTED_REVIEWERS = ("reviewer_a", "reviewer_b")
AGREEMENT_FIELDS = (
    "frame_validity",
    *tuple(slot.value for slot in SlotName),
    "counterfactual_candidate",
)
PENDING_STATUS = "pending"
COMPLETED_STATUS = "completed"
VALID_STATUSES = {PENDING_STATUS, COMPLETED_STATUS}
PENDING_LABELS = {"unreviewed"}
COMPLETED_LABELS = {"yes", "no", "unclear"}
POSITIVE_LABEL = "yes"


def summarize(*, packet_path: Path, output_path: Path, command: str) -> dict[str, Any]:
    packet_rows = _read_jsonl(packet_path)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in packet_rows:
        grouped[str(row["audit_id"])].append(row)

    integrity_by_id = _integrity_by_audit_id(grouped)
    integrity_failures = [
        issue for audit_id in sorted(integrity_by_id) for issue in integrity_by_id[audit_id]
    ]
    agreement_by_field = {
        field: _agreement_for_field(
            rows_by_id=grouped, integrity_by_id=integrity_by_id, field=field
        )
        for field in AGREEMENT_FIELDS
    }
    raw_disagreements = _raw_disagreements(grouped, integrity_by_id)
    counts = _gate_counts(grouped, integrity_by_id)
    gate = evaluate_source_gate(**counts)
    pending = any(row.get("annotation_status") == PENDING_STATUS for row in packet_rows)
    integrity_failed = bool(integrity_failures)
    status = "pending_annotation" if pending else gate.status
    if integrity_failed and not pending:
        status = "integrity_fail"
    result = {
        "build_time_utc": _utc_now(),
        "command": command,
        "packet_path": packet_path.as_posix(),
        "status": status,
        "advance": False if pending or integrity_failed else gate.advance,
        "human_evidence": False,
        "model_agent_development_only": True,
        "candidate_development_only": True,
        "items": len(grouped),
        "packet_rows": len(packet_rows),
        "document_identity": _document_identity(packet_rows),
        "integrity_failures": integrity_failures,
        "agreement_by_field": agreement_by_field,
        "raw_disagreements": raw_disagreements,
        "source_gate": gate.to_dict()
        if not pending and not integrity_failed
        else {
            **gate.to_dict(),
            "status": status,
            "advance": False,
            "failures": _gate_failures(
                pending=pending,
                integrity_failed=integrity_failed,
                integrity_failures=integrity_failures,
                gate_failures=gate.failures,
            ),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def _gate_failures(
    *,
    pending: bool,
    integrity_failed: bool,
    integrity_failures: list[str],
    gate_failures: tuple[str, ...],
) -> list[str]:
    failures: list[str] = []
    if pending:
        failures.append("annotations_pending")
    if integrity_failed:
        failures.extend(integrity_failures)
    failures.extend(gate_failures)
    return failures


def _document_identity(packet_rows: list[dict[str, Any]]) -> dict[str, Any]:
    item_document_groups = {
        str(row["audit_id"]): str(row["document_group_hash"]) for row in packet_rows
    }
    document_proxy_reuse_count = len(item_document_groups) - len(
        set(item_document_groups.values())
    )
    basis = {
        row.get("document_identity_basis", "unknown") for row in packet_rows
    } or {"unknown"}
    limitation = {
        row.get("document_identity_limitation", "unknown") for row in packet_rows
    } or {"unknown"}
    return {
        "basis": sorted(basis)[0],
        "limitation": sorted(limitation)[0],
        "document_proxy_reuse_count": document_proxy_reuse_count,
        "overlap_document_proxy_disjoint": document_proxy_reuse_count == 0,
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _agreement_for_field(
    *,
    rows_by_id: dict[str, list[dict[str, Any]]],
    integrity_by_id: dict[str, list[str]],
    field: str,
) -> dict[str, Any]:
    comparable = 0
    agreements = 0
    for audit_id, rows in rows_by_id.items():
        pair = _strict_pair(rows, integrity_by_id[audit_id])
        if pair is None:
            continue
        labels = [_field_label(row, field) for row in pair.values()]
        reviewed = [label for label in labels if label != "unreviewed"]
        if len(reviewed) < 2:
            continue
        comparable += 1
        if len(set(reviewed)) == 1:
            agreements += 1
    return {
        "comparable": comparable,
        "agreements": agreements,
        "agreement": None if comparable == 0 else agreements / comparable,
    }


def _raw_disagreements(
    rows_by_id: dict[str, list[dict[str, Any]]],
    integrity_by_id: dict[str, list[str]],
) -> list[dict[str, Any]]:
    disagreements: list[dict[str, Any]] = []
    for audit_id, rows in sorted(rows_by_id.items()):
        disagreement_issues = [
            issue
            for issue in integrity_by_id[audit_id]
            if not issue.startswith("annotation_status:")
        ]
        if disagreement_issues:
            disagreements.append(
                {
                    "audit_id": audit_id,
                    "field": "integrity",
                    "issues": disagreement_issues,
                }
            )
        pair = _strict_pair(rows, integrity_by_id[audit_id])
        if pair is None:
            continue
        for field in AGREEMENT_FIELDS:
            labels = {
                str(row["reviewer"]): _field_label(row, field)
                for row in pair.values()
                if _field_label(row, field) != "unreviewed"
            }
            if len(labels) >= 2 and len(set(labels.values())) > 1:
                disagreements.append(
                    {
                        "audit_id": audit_id,
                        "field": field,
                        "labels": labels,
                    }
                )
    return disagreements


def _gate_counts(
    rows_by_id: dict[str, list[dict[str, Any]]],
    integrity_by_id: dict[str, list[str]],
) -> dict[str, int]:
    valid_ids: set[str] = set()
    denominator = 0
    comparator = 0
    counterfactual = 0
    corpus_hashes: set[str] = set()
    for audit_id, rows in rows_by_id.items():
        pair = _strict_pair(rows, integrity_by_id[audit_id])
        if pair is None:
            continue
        row = pair[EXPECTED_REVIEWERS[0]]
        corpus_hashes.add(str(row["source_record_hash"]))
        if not _positive_consensus(pair, "frame_validity"):
            continue
        valid_ids.add(audit_id)
        frame = row["quantity_frame"]
        if frame["denominator_or_base"] != NOT_STATED.value and _positive_consensus(
            pair, "denominator_or_base"
        ):
            denominator += 1
        if frame["comparator"] != NOT_STATED.value and _positive_consensus(
            pair, "comparator"
        ):
            comparator += 1
        if _positive_consensus(pair, "counterfactual_candidate"):
            counterfactual += 1
    return {
        "valid": len(valid_ids),
        "corpora": len(corpus_hashes),
        "denominator": denominator,
        "comparator": comparator,
        "counterfactual": counterfactual,
    }


def _positive_consensus(pair: dict[str, dict[str, Any]], field: str) -> bool:
    return all(_field_label(pair[reviewer], field) == POSITIVE_LABEL for reviewer in EXPECTED_REVIEWERS)


def _strict_pair(
    rows: list[dict[str, Any]], integrity_failures: list[str]
) -> dict[str, dict[str, Any]] | None:
    if integrity_failures:
        return None
    pair = {str(row["reviewer"]): row for row in rows}
    if tuple(sorted(pair)) != EXPECTED_REVIEWERS:
        return None
    return pair


def _integrity_by_audit_id(
    rows_by_id: dict[str, list[dict[str, Any]]]
) -> dict[str, list[str]]:
    return {
        audit_id: _integrity_failures_for_audit(audit_id, rows)
        for audit_id, rows in rows_by_id.items()
    }


def _integrity_failures_for_audit(
    audit_id: str, rows: list[dict[str, Any]]
) -> list[str]:
    failures: list[str] = []
    reviewer_counts = Counter(str(row.get("reviewer")) for row in rows)
    for reviewer in sorted(set(reviewer_counts) - set(EXPECTED_REVIEWERS)):
        failures.append(f"unexpected_reviewer:{audit_id}:{reviewer}")
    for reviewer in EXPECTED_REVIEWERS:
        count = reviewer_counts.get(reviewer, 0)
        if count == 0:
            failures.append(f"missing_reviewer:{audit_id}:{reviewer}")
        if count > 1:
            failures.append(f"duplicate_reviewer:{audit_id}:{reviewer}")

    for row in rows:
        reviewer = str(row.get("reviewer"))
        status = row.get("annotation_status")
        if status not in VALID_STATUSES:
            failures.append(f"invalid_annotation_status:{audit_id}:{reviewer}:{status}")
        elif status != COMPLETED_STATUS:
            failures.append(f"annotation_status:{audit_id}:{reviewer}:{status}")
        allowed = COMPLETED_LABELS if status == COMPLETED_STATUS else PENDING_LABELS
        for field in AGREEMENT_FIELDS:
            label = _field_label(row, field)
            if label not in allowed:
                failures.append(f"invalid_label:{audit_id}:{reviewer}:{field}:{label}")
    return failures


def _field_label(row: dict[str, Any], field: str) -> object:
    review_fields = row.get("review_fields", {})
    if field == "frame_validity":
        return review_fields.get("frame_validity", "unreviewed")
    if field == "counterfactual_candidate":
        return review_fields.get("counterfactual_candidate", "unreviewed")
    return review_fields.get("slots", {}).get(field, "unreviewed")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    command = "python scripts/summarize_quantity_frame_audit.py " + " ".join(
        sys.argv[1:] if argv is None else argv
    )
    result = summarize(
        packet_path=args.packet,
        output_path=args.output,
        command=command.strip(),
    )
    print(json.dumps({"status": result["status"], "advance": result["advance"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
