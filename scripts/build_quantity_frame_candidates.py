"""Build deterministic quantity-frame candidate-only records."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.quantity_frame.extract import SpanRecord, scan_text
from src.quantity_frame.provenance import SourceRecord, load_manifest, sha256_file
from src.quantity_frame.schema import NOT_STATED, CandidateItem, QuantityFrame


COCHRANE_NAME = "GEM/cochrane-simplification validation"
ELIFE_NAME = "tomasg25/scientific_lay_summarisation eLife validation"
DEFAULT_MANIFEST = Path("data_provenance/quantity_frame_manifest.jsonl")
DEFAULT_OUTPUT = Path("data/processed/quantity-frame-candidates-v0/candidates.jsonl")
DEFAULT_METADATA = Path("results/strong_accept_loop/quantity_frame/candidate_build.json")
DEFAULT_LIMIT = 300
CORPUS_NAMES = {
    COCHRANE_NAME: "GEM/cochrane-simplification",
    ELIFE_NAME: "tomasg25/scientific_lay_summarisation",
}


def build(
    *,
    manifest_path: Path,
    output_path: Path,
    metadata_path: Path,
    per_corpus_limit: int,
    command: str,
    deterministic_second_run_sha256: str | None = None,
) -> dict[str, Any]:
    records = _selected_source_records(manifest_path)
    corpus_stats: dict[str, dict[str, Any]] = {}
    candidates: list[CandidateItem] = []
    seen_pairs: set[tuple[str, str, str]] = set()

    for name in (COCHRANE_NAME, ELIFE_NAME):
        source_record = records[name]
        raw_rows = _load_json_rows(Path(source_record.raw_path))
        stats = {
            "source_record_hash": _source_record_hash(source_record),
            "revision": source_record.revision,
            "raw_path": source_record.raw_path,
            "raw_sha256": source_record.sha256,
            "rows_read": len(raw_rows),
            "candidate_rows_found": 0,
            "candidates_written": 0,
            "duplicates_skipped": 0,
            "exclusions": {},
        }

        for row_index, row in enumerate(raw_rows):
            source_text, target_text = _texts_for_record(name, row)
            if not source_text or not target_text:
                stats["exclusions"] = _merge_exclusions(
                    stats["exclusions"], {"missing_text": 1}
                )
                continue

            diagnostics = scan_text(source_text)
            stats["exclusions"] = _merge_exclusions(
                stats["exclusions"], diagnostics.exclusions
            )
            if not diagnostics.candidates:
                continue

            stats["candidate_rows_found"] += 1
            pair_key = (name, source_text, target_text)
            if pair_key in seen_pairs:
                stats["duplicates_skipped"] += 1
                continue
            seen_pairs.add(pair_key)

            if stats["candidates_written"] >= per_corpus_limit:
                stats["exclusions"] = _merge_exclusions(
                    stats["exclusions"], {"per_corpus_limit": 1}
                )
                continue

            candidates.append(
                _candidate_item(
                    corpus=CORPUS_NAMES[name],
                    source_record=source_record,
                    source_text=source_text,
                    target_text=target_text,
                    span=diagnostics.candidates[0],
                )
            )
            stats["candidates_written"] += 1

        corpus_stats[CORPUS_NAMES[name]] = stats

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for candidate in candidates:
            handle.write(
                json.dumps(candidate.to_dict(), ensure_ascii=False, sort_keys=True)
                + "\n"
            )

    output_sha256 = sha256_file(output_path)
    metadata = {
        "build_time_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "git_commit": _git_commit(),
        "command": command,
        "manifest_path": manifest_path.as_posix(),
        "source_revisions": {
            CORPUS_NAMES[name]: {
                "revision": record.revision,
                "raw_path": record.raw_path,
                "raw_sha256": record.sha256,
                "source_record_hash": _source_record_hash(record),
            }
            for name, record in records.items()
        },
        "corpora": corpus_stats,
        "total_rows_read": sum(stats["rows_read"] for stats in corpus_stats.values()),
        "total_candidates_found": sum(
            stats["candidate_rows_found"] for stats in corpus_stats.values()
        ),
        "total_candidates_written": len(candidates),
        "total_duplicates_skipped": sum(
            stats["duplicates_skipped"] for stats in corpus_stats.values()
        ),
        "output_path": output_path.as_posix(),
        "output_bytes": output_path.stat().st_size,
        "output_sha256": output_sha256,
        "deterministic_second_run_sha256": deterministic_second_run_sha256
        or output_sha256,
        "candidate_only": True,
        "human_evidence": False,
        "experimental_claim": False,
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def _selected_source_records(manifest_path: Path) -> dict[str, SourceRecord]:
    records = {record.name: record for record in load_manifest(manifest_path)}
    missing = [name for name in (COCHRANE_NAME, ELIFE_NAME) if name not in records]
    if missing:
        raise ValueError(f"missing source records: {', '.join(missing)}")
    return {name: records[name] for name in (COCHRANE_NAME, ELIFE_NAME)}


def _load_json_rows(path: Path) -> list[Mapping[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [row for row in rows if isinstance(row, Mapping)]


def _texts_for_record(name: str, row: Mapping[str, Any]) -> tuple[str | None, str | None]:
    if name == COCHRANE_NAME:
        return _text(row.get("source")), _text(row.get("target"))
    if name == ELIFE_NAME:
        return _join_text(row.get("abstract")), _join_text(row.get("summary"))
    raise ValueError(f"unsupported corpus: {name}")


def _candidate_item(
    *,
    corpus: str,
    source_record: SourceRecord,
    source_text: str,
    target_text: str,
    span: SpanRecord,
) -> CandidateItem:
    source_text_hash = _text_hash(source_text)
    target_text_hash = _text_hash(target_text)
    item_seed = "\n".join((corpus, source_text_hash, target_text_hash))
    return CandidateItem(
        item_id=f"qf-candidate-{_sha256_text(item_seed)[:16]}",
        corpus=corpus,
        source_record_hash=_source_record_hash(source_record),
        split="validation",
        source_text_hash=source_text_hash,
        target_text_hash=target_text_hash,
        source_text=source_text,
        target_text=target_text,
        quantity_frame=_quantity_frame(span),
    )


def _quantity_frame(span: SpanRecord) -> QuantityFrame:
    value = _first_number(span.text) or span.text
    unit = _unit_for_span(span)
    denominator = NOT_STATED
    if span.cue_type == "fraction":
        denominator = span.text.split(" of ", 1)[1]
    return QuantityFrame(
        value=value,
        denominator_or_base=denominator,
        unit=unit,
        time_window=span.text if span.cue_type == "time_window" else NOT_STATED,
        comparator=span.text if span.cue_type == "comparison" else NOT_STATED,
        source_span=span.text,
    )


def _unit_for_span(span: SpanRecord) -> str:
    if span.cue_type == "percentage":
        return "percent"
    if span.cue_type == "count":
        parts = span.text.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else NOT_STATED
    if span.cue_type == "unit":
        parts = span.text.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else NOT_STATED
    return NOT_STATED


def _first_number(text: str) -> str | None:
    import re

    match = re.search(r"\d+(?:\.\d+)?", text)
    return None if match is None else match.group(0)


def _join_text(value: Any) -> str | None:
    if isinstance(value, list):
        return " ".join(str(part).strip() for part in value if str(part).strip())
    return _text(value)


def _text(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return " ".join(value.split())


def _merge_exclusions(left: Mapping[str, int], right: Mapping[str, int]) -> dict[str, int]:
    counts = Counter(left)
    counts.update(right)
    return dict(sorted(counts.items()))


def _source_record_hash(record: SourceRecord) -> str:
    return _sha256_text(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True))


def _text_hash(text: str) -> str:
    return _sha256_text(text)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--per-corpus-limit", type=int, default=DEFAULT_LIMIT)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    command = "python scripts/build_quantity_frame_candidates.py " + " ".join(
        sys.argv[1:] if argv is None else argv
    )
    first = build(
        manifest_path=args.manifest,
        output_path=args.output,
        metadata_path=args.metadata,
        per_corpus_limit=args.per_corpus_limit,
        command=command.strip(),
    )
    second = build(
        manifest_path=args.manifest,
        output_path=args.output,
        metadata_path=args.metadata,
        per_corpus_limit=args.per_corpus_limit,
        command=command.strip(),
        deterministic_second_run_sha256=first["output_sha256"],
    )
    print(
        "wrote "
        f"{second['total_candidates_written']} candidates to {second['output_path']} "
        f"sha256={second['output_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
