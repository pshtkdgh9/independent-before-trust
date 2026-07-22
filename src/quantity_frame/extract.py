"""Conservative quantity-candidate retrieval for source/target pairs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SpanRecord:
    text: str
    start: int
    end: int
    cue_type: str


@dataclass(frozen=True)
class ScanDiagnostics:
    candidates: tuple[SpanRecord, ...]
    exclusions: dict[str, int]


PERCENT_RE = re.compile(
    r"(?<!\w)\d+(?:\.\d+)?\s?(?:%|\bpercent\b)", re.IGNORECASE
)
FRACTION_RE = re.compile(r"\b\d+(?:\.\d+)?\s+of\s+\d+(?:\.\d+)?\b", re.IGNORECASE)
UNIT_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:mg|g|kg|ml|l|mmol|weeks?|months?|years?|days?|hours?)\b",
    re.IGNORECASE,
)
COUNT_RE = re.compile(
    r"\b\d+\s+(?:participants?|patients?|people|cases?|deaths?|events?|trials?|studies?)\b",
    re.IGNORECASE,
)
TIME_RE = re.compile(
    r"\b(?:after|before|within|over|during|at)\s+\d+(?:\.\d+)?\s*(?:days?|weeks?|months?|years?|hours?)\b",
    re.IGNORECASE,
)
COMPARISON_RE = re.compile(
    r"\b(?:versus|vs\.?|compared with|compared to)\s+(?:placebo|control|usual care|baseline|[a-z][a-z-]+)\b",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
CITATION_RE = re.compile(r"\[\s*\d+\s*\]")
SECTION_RE = re.compile(r"\b\d+(?:\.\d+)+\b")


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("fraction", FRACTION_RE),
    ("percentage", PERCENT_RE),
    ("unit", UNIT_RE),
    ("count", COUNT_RE),
    ("time_window", TIME_RE),
    ("comparison", COMPARISON_RE),
)


def retrieve_candidates(text: str) -> tuple[SpanRecord, ...]:
    """Return deterministic quantity/cue spans without semantic slot binding."""
    return scan_text(text).candidates


def scan_text(text: str) -> ScanDiagnostics:
    if not isinstance(text, str) or not text.strip():
        return ScanDiagnostics((), {"empty_text": 1})

    spans = sorted(_iter_spans(text), key=lambda span: (span.start, span.end, span.cue_type))
    deduped: list[SpanRecord] = []
    seen_text: set[str] = set()
    occupied: list[tuple[int, int]] = []
    for span in spans:
        canonical = _canonical_span(span.text)
        if canonical in seen_text:
            continue
        if any(span.start >= start and span.end <= end for start, end in occupied):
            continue
        seen_text.add(canonical)
        occupied.append((span.start, span.end))
        deduped.append(span)

    exclusions = _exclusion_reasons(text, bool(deduped))
    return ScanDiagnostics(tuple(deduped), exclusions)


def _iter_spans(text: str) -> Iterable[SpanRecord]:
    for cue_type, pattern in PATTERNS:
        for match in pattern.finditer(text):
            matched = _clean_span(match.group(0))
            if not matched:
                continue
            yield SpanRecord(matched, match.start(), match.end(), cue_type)


def _exclusion_reasons(text: str, has_candidates: bool) -> dict[str, int]:
    if has_candidates:
        return {}

    exclusions: dict[str, int] = {}
    year_count = len(YEAR_RE.findall(text))
    citation_count = len(CITATION_RE.findall(text))
    section_count = len(SECTION_RE.findall(text))
    if year_count:
        exclusions["year_without_quantity_context"] = year_count
    if citation_count:
        exclusions["citation_number_without_quantity_context"] = citation_count
    if section_count:
        exclusions["section_number_without_quantity_context"] = section_count
    if not exclusions:
        exclusions["no_quantity_evidence"] = 1
    return exclusions


def _clean_span(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" ,.;:()"))


def _canonical_span(value: str) -> str:
    return _clean_span(value).lower()
