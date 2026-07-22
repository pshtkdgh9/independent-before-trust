"""Deterministic candidate extraction for the ESP feasibility pilot."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class UncertaintyFrame:
    cue: str
    strength: str
    scope: str
    start: int
    end: int


@dataclass(frozen=True)
class PilotItem:
    item_id: str
    title: str
    year: str
    source_text: str
    reference_summary: str
    frame: UncertaintyFrame


_CUES = (
    (re.compile(r"\bunknown whether\b", re.IGNORECASE), "unknown"),
    (re.compile(r"\bunclear whether\b", re.IGNORECASE), "unknown"),
    (re.compile(r"\bmay\b", re.IGNORECASE), "possible"),
    (re.compile(r"\bmight\b", re.IGNORECASE), "possible"),
    (re.compile(r"\bcould\b", re.IGNORECASE), "possible"),
    (re.compile(r"\bsuggests?\b", re.IGNORECASE), "suggestive"),
    (re.compile(r"\blikely\b", re.IGNORECASE), "likely"),
)


def _sentence_spans(text: str) -> Iterable[tuple[int, int, str]]:
    for match in re.finditer(r"\S(?:.*?\S)?(?:[.!?](?=\s|$)|$)", text, re.DOTALL):
        sentence = match.group(0).strip()
        if sentence:
            yield match.start(), match.end(), sentence


def extract_uncertainty_frames(text: str) -> list[UncertaintyFrame]:
    frames: list[UncertaintyFrame] = []
    for sentence_start, _, sentence in _sentence_spans(text):
        matches: list[tuple[int, int, str, str]] = []
        for pattern, strength in _CUES:
            for match in pattern.finditer(sentence):
                matches.append((match.start(), match.end(), match.group(0).lower(), strength))
        for start, end, cue, strength in sorted(matches):
            frames.append(
                UncertaintyFrame(
                    cue=cue,
                    strength=strength,
                    scope=sentence,
                    start=sentence_start + start,
                    end=sentence_start + end,
                )
            )
    return frames


def build_pilot_items(
    records: Iterable[Mapping[str, object]], *, limit: int
) -> list[PilotItem]:
    items: list[PilotItem] = []
    for record_index, record in enumerate(records):
        article = str(record.get("article") or "")
        headings = record.get("section_headings") or []
        source_text = article
        if headings and str(headings[0]).strip().lower() == "abstract":
            source_text = article.split("\n", 1)[0].strip()
        reference_summary = str(record.get("summary") or "")
        for frame_index, frame in enumerate(extract_uncertainty_frames(source_text)):
            items.append(
                PilotItem(
                    item_id=f"esp-{record_index:04d}-{frame_index:02d}",
                    title=str(record.get("title") or ""),
                    year=str(record.get("year") or ""),
                    source_text=source_text,
                    reference_summary=reference_summary,
                    frame=frame,
                )
            )
            if len(items) >= limit:
                return items
    return items


def validate_annotations(
    manifest_item_ids: list[str], annotations: list[Mapping[str, object]]
) -> None:
    annotation_ids = [str(row.get("item_id") or "") for row in annotations]
    if annotation_ids != manifest_item_ids:
        raise ValueError("annotation item IDs do not match manifest order")


def annotation_agreement(
    left: list[Mapping[str, object]], right: list[Mapping[str, object]]
) -> dict[str, object]:
    left_ids = [str(row.get("item_id") or "") for row in left]
    validate_annotations(left_ids, right)
    fields = ("cue_valid", "strength", "attribution", "retain_in_lay_rewrite")
    item_count = len(left)
    exact = {
        field: (
            sum(str(a.get(field)) == str(b.get(field)) for a, b in zip(left, right))
            / item_count
            if item_count
            else 0.0
        )
        for field in fields
    }
    return {"items": item_count, "exact_agreement": exact}
