"""Build a blinded source-audit packet from quantity-frame candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.quantity_frame.schema import CandidateItem, SlotName


DEFAULT_CANDIDATES = Path("data/processed/quantity-frame-candidates-v0/candidates.jsonl")
DEFAULT_OUTPUT = Path("results/strong_accept_loop/quantity_frame/audit_packet.jsonl")
DEFAULT_LIMIT = 300
DEFAULT_OVERLAP = 100
CONTEXT_RADIUS = 45
MAX_CONTEXT_CHARS = 220
REVIEWERS = ("reviewer_a", "reviewer_b")
DOCUMENT_IDENTITY_BASIS = "source_text_hash_document_proxy"
DOCUMENT_IDENTITY_LIMITATION = (
    "source datasets lack a stable document id in CandidateItem; "
    "source_text_hash is used as a conservative document proxy"
)


def build_packet(
    *,
    candidates_path: Path,
    output_path: Path,
    per_corpus_limit: int,
    overlap_count: int,
    command: str,
) -> dict[str, Any]:
    candidates = _selected_candidates(candidates_path, per_corpus_limit)
    packet_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        for reviewer in REVIEWERS:
            packet_rows.append(_packet_row(candidate, reviewer))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in packet_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    document_proxies = [candidate.source_text_hash for candidate in candidates]
    document_proxy_reuse_count = len(document_proxies) - len(set(document_proxies))
    return {
        "build_time_utc": _utc_now(),
        "command": command,
        "candidates_path": candidates_path.as_posix(),
        "output_path": output_path.as_posix(),
        "output_bytes": output_path.stat().st_size,
        "output_sha256": _sha256_file(output_path),
        "candidate_items": len(candidates),
        "packet_rows": len(packet_rows),
        "reviewers": list(REVIEWERS),
        "overlap_count_requested": overlap_count,
        "overlap_count_written": len(candidates),
        "document_identity_basis": DOCUMENT_IDENTITY_BASIS,
        "document_identity_limitation": DOCUMENT_IDENTITY_LIMITATION,
        "overlap_document_proxy_disjoint": document_proxy_reuse_count == 0,
        "document_proxy_reuse_count": document_proxy_reuse_count,
        "candidate_development_only": True,
        "model_agent_development_only": True,
        "human_evidence": False,
    }


def _selected_candidates(path: Path, per_corpus_limit: int) -> list[CandidateItem]:
    counts: dict[str, int] = defaultdict(int)
    selected: list[CandidateItem] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        candidate = CandidateItem.from_dict(json.loads(line))
        if counts[candidate.corpus] >= per_corpus_limit:
            continue
        counts[candidate.corpus] += 1
        selected.append(candidate)
    return selected


def _packet_row(candidate: CandidateItem, reviewer: str) -> dict[str, Any]:
    audit_id = "qf-audit-" + _sha256_text(candidate.item_id)[:16]
    frame = candidate.quantity_frame.to_dict()
    return {
        "audit_id": audit_id,
        "review_id": "qf-review-" + _sha256_text(f"{audit_id}:{reviewer}")[:16],
        "reviewer": reviewer,
        "candidate_ref": "qf-source-ref-" + _sha256_text(candidate.item_id)[:16],
        "document_group_hash": "qf-doc-" + candidate.source_text_hash[:16],
        "document_identity_basis": DOCUMENT_IDENTITY_BASIS,
        "document_identity_limitation": DOCUMENT_IDENTITY_LIMITATION,
        "source_record_hash": candidate.source_record_hash,
        "split": candidate.split,
        "source_text_hash": candidate.source_text_hash,
        "target_text_hash": candidate.target_text_hash,
        "source_span": frame["source_span"],
        "source_context": _source_context(candidate.source_text, frame["source_span"]),
        "quantity_frame": {slot.value: frame[slot.value] for slot in SlotName},
        "review_fields": {
            "frame_validity": "unreviewed",
            "slots": {slot.value: "unreviewed" for slot in SlotName},
            "counterfactual_candidate": "unreviewed",
        },
        "candidate_development_only": True,
        "model_agent_development_only": True,
        "human_evidence": False,
        "annotation_status": "pending",
    }


def _source_context(source_text: str, source_span: str) -> str:
    span_start = source_text.find(source_span)
    if span_start < 0:
        return source_span[:MAX_CONTEXT_CHARS]
    span_end = span_start + len(source_span)
    start = max(0, span_start - CONTEXT_RADIUS)
    end = min(len(source_text), span_end + CONTEXT_RADIUS)
    context = source_text[start:end].strip()
    if len(context) <= MAX_CONTEXT_CHARS:
        return context

    overflow = len(context) - MAX_CONTEXT_CHARS
    trim_left = min(max(0, span_start - start), overflow // 2)
    trim_right = overflow - trim_left
    narrowed = context[trim_left : len(context) - trim_right].strip()
    if source_span in narrowed:
        return narrowed
    return source_span[:MAX_CONTEXT_CHARS]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--per-corpus-limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--overlap-count", type=int, default=DEFAULT_OVERLAP)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    command = "python scripts/build_quantity_frame_audit.py " + " ".join(
        sys.argv[1:] if argv is None else argv
    )
    metadata = build_packet(
        candidates_path=args.candidates,
        output_path=args.output,
        per_corpus_limit=args.per_corpus_limit,
        overlap_count=args.overlap_count,
        command=command.strip(),
    )
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
