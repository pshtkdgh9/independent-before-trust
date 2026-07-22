"""Extract deterministic FEVER claim/wiki evidence candidates for source-pack audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


class FeverSourcePackError(ValueError):
    """Raised when FEVER candidate extraction cannot produce an auditable pack."""


@dataclass(frozen=True)
class CandidateReference:
    source_row_id: int
    label: str
    claim: str
    wiki_page_id: str
    sentence_id: int
    raw_claim_hash: str


def extract_fever_source_pack(
    claims_path: Path, wiki_dir: Path, *, limit: int | None, seed: int
) -> tuple[dict[str, Any], ...]:
    references = _load_candidate_references(claims_path)
    needed_page_ids = {reference.wiki_page_id for reference in references}
    wiki_pages = _load_needed_wiki_pages(wiki_dir, needed_page_ids)

    rows: list[dict[str, Any]] = []
    for reference in references:
        page_lines = wiki_pages.get(reference.wiki_page_id)
        if page_lines is None:
            continue
        evidence_sentence = page_lines.get(reference.sentence_id)
        if evidence_sentence is None:
            continue
        if not evidence_sentence:
            raise FeverSourcePackError(
                f"empty evidence sentence for row {reference.source_row_id} "
                f"{reference.wiki_page_id}:{reference.sentence_id}"
            )
        rows.append(_candidate_row(reference, evidence_sentence))

    if not rows:
        raise FeverSourcePackError("no extractable candidate rows")

    rows = _apply_limit(rows, limit=limit, seed=seed)
    return tuple(rows)


def write_jsonl_atomic(rows: Iterable[Mapping[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=output_path.parent,
            delete=False,
        ) as handle:
            temp_name = handle.name
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        os.replace(temp_name, output_path)
    except Exception:
        if temp_name is not None:
            try:
                Path(temp_name).unlink(missing_ok=True)
            except OSError:
                pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, required=True)
    parser.add_argument("--wiki-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    try:
        rows = extract_fever_source_pack(
            args.claims, args.wiki_dir, limit=args.limit, seed=args.seed
        )
        write_jsonl_atomic(rows, args.output)
    except (OSError, json.JSONDecodeError, FeverSourcePackError) as exc:
        raise SystemExit(f"cannot extract FEVER source pack: {exc}") from exc


def _load_candidate_references(claims_path: Path) -> tuple[CandidateReference, ...]:
    references: list[CandidateReference] = []
    seen_claims: dict[str, int] = {}

    with claims_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            claim = _required_str(row, "claim", line_number)
            if not claim.strip():
                raise FeverSourcePackError(f"empty claim on line {line_number}")
            previous = seen_claims.get(claim)
            if previous is not None:
                raise FeverSourcePackError(
                    f"duplicate claim on lines {previous} and {line_number}"
                )
            seen_claims[claim] = line_number

            reference = _single_evidence_reference(row, line_number)
            if reference is None:
                continue
            page_id, sentence_id = reference
            references.append(
                CandidateReference(
                    source_row_id=_required_int(row, "id", line_number),
                    label=_required_str(row, "label", line_number),
                    claim=claim,
                    wiki_page_id=page_id,
                    sentence_id=sentence_id,
                    raw_claim_hash=_sha256_json(row),
                )
            )

    if not references:
        raise FeverSourcePackError("no candidate rows with exactly one evidence reference")
    return tuple(references)


def _single_evidence_reference(
    row: Mapping[str, Any], line_number: int
) -> tuple[str, int] | None:
    evidence_sets = row.get("evidence")
    if not isinstance(evidence_sets, list):
        raise FeverSourcePackError(f"evidence must be a list on line {line_number}")

    non_null_sets: list[list[Any]] = []
    for evidence_set in evidence_sets:
        if not isinstance(evidence_set, list):
            raise FeverSourcePackError(f"evidence set must be a list on line {line_number}")
        usable = [
            evidence
            for evidence in evidence_set
            if isinstance(evidence, list)
            and len(evidence) >= 4
            and evidence[2] is not None
            and evidence[3] is not None
        ]
        if usable:
            non_null_sets.append(usable)

    if len(non_null_sets) != 1 or len(non_null_sets[0]) != 1:
        return None

    evidence = non_null_sets[0][0]
    page_id = evidence[2]
    sentence_id = evidence[3]
    if not isinstance(page_id, str) or not isinstance(sentence_id, int):
        raise FeverSourcePackError(f"invalid evidence reference on line {line_number}")
    return page_id, sentence_id


def _load_needed_wiki_pages(
    wiki_dir: Path, needed_page_ids: set[str]
) -> dict[str, dict[int, str]]:
    if not wiki_dir.is_dir():
        raise FeverSourcePackError(f"wiki-dir is not a directory: {wiki_dir}")

    remaining = set(needed_page_ids)
    pages: dict[str, dict[int, str]] = {}
    for jsonl_path in sorted(wiki_dir.glob("*.jsonl")):
        if not remaining:
            break
        with jsonl_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not remaining:
                    break
                if not line.strip():
                    continue
                row = json.loads(line)
                page_id = row.get("id")
                if page_id not in remaining:
                    continue
                pages[page_id] = _parse_wiki_lines(row.get("lines"), page_id)
                remaining.remove(page_id)
    return pages


def _parse_wiki_lines(lines: Any, page_id: str) -> dict[int, str]:
    if not isinstance(lines, str):
        raise FeverSourcePackError(f"wiki page {page_id} has non-string lines")

    parsed: dict[int, str] = {}
    for raw_line in lines.splitlines():
        if not raw_line:
            continue
        parts = raw_line.split("\t")
        if len(parts) < 2:
            continue
        try:
            sentence_id = int(parts[0])
        except ValueError as exc:
            raise FeverSourcePackError(
                f"wiki page {page_id} has invalid sentence id {parts[0]!r}"
            ) from exc
        sentence = parts[1].strip()
        if sentence_id in parsed:
            raise FeverSourcePackError(
                f"wiki page {page_id} has duplicate sentence id {sentence_id}"
            )
        parsed[sentence_id] = sentence
    return parsed


def _candidate_row(reference: CandidateReference, evidence_sentence: str) -> dict[str, Any]:
    row = {
        "source_pack_id": (
            f"fever-paper-dev-{reference.source_row_id}-"
            f"{reference.wiki_page_id}-{reference.sentence_id}"
        ),
        "source_row_id": reference.source_row_id,
        "label": reference.label,
        "claim": reference.claim,
        "wiki_page_id": reference.wiki_page_id,
        "sentence_id": reference.sentence_id,
        "evidence_sentence": evidence_sentence,
        "claim_hash": _sha256_text(reference.claim),
        "evidence_sentence_hash": _sha256_text(evidence_sentence),
        "wiki_reference_hash": _sha256_text(
            f"{reference.wiki_page_id}:{reference.sentence_id}"
        ),
        "raw_claim_hash": reference.raw_claim_hash,
    }
    row["candidate_hash"] = _sha256_json(row)
    return row


def _apply_limit(
    rows: list[dict[str, Any]], *, limit: int | None, seed: int
) -> list[dict[str, Any]]:
    if limit is None:
        return rows
    if limit < 0:
        raise FeverSourcePackError("limit must be non-negative")
    if limit >= len(rows):
        return rows
    keyed_rows = list(rows)
    random.Random(seed).shuffle(keyed_rows)
    selected = keyed_rows[:limit]
    return sorted(selected, key=lambda row: row["source_pack_id"])


def _required_str(row: Mapping[str, Any], field: str, line_number: int) -> str:
    value = row.get(field)
    if not isinstance(value, str):
        raise FeverSourcePackError(f"{field} must be a string on line {line_number}")
    return value


def _required_int(row: Mapping[str, Any], field: str, line_number: int) -> int:
    value = row.get(field)
    if not isinstance(value, int):
        raise FeverSourcePackError(f"{field} must be an integer on line {line_number}")
    return value


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_json(row: Mapping[str, Any]) -> str:
    payload = json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return _sha256_text(payload)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    main()
