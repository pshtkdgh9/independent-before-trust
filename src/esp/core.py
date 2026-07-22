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
