"""Closed-label multilingual epistemic-preservation protocol."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Iterable

LANGUAGES = {"en", "ko", "es"}
SPEAKERS = {"ADA", "BRUNO", "CORA", "DIEGO"}
ACTIONS = {"ARRIVE", "APPROVE", "RESIGN", "ATTEND"}
POLARITIES = {"POSITIVE", "NEGATIVE"}
CERTAINTIES = {"POSSIBLE", "PROBABLE", "CERTAIN"}


@dataclass(frozen=True)
class ClosedItem:
    item_id: str
    language: str
    evidence: str
    speaker: str
    action: str
    polarity: str
    certainty: str
    parallel_group: str

    def __post_init__(self) -> None:
        for value, allowed in ((self.language, LANGUAGES), (self.speaker, SPEAKERS), (self.action, ACTIONS), (self.polarity, POLARITIES), (self.certainty, CERTAINTIES)):
            if value not in allowed:
                raise ValueError(f"unsupported closed label: {value}")


def render_prompt(item: ClosedItem, method: str) -> str:
    if method not in {"direct", "translate", "typed"}:
        raise ValueError("unknown method")
    lead = {
        "direct": "Classify the evidence directly.",
        "translate": "Silently translate the evidence into English, then classify it.",
        "typed": "Identify speaker and action first, then polarity and certainty.",
    }[method]
    return (
        f"{lead}\nEVIDENCE ({item.language}): {item.evidence}\n"
        "Allowed SPEAKER labels: ADA, BRUNO, CORA, DIEGO.\n"
        "Allowed ACTION labels: ARRIVE, APPROVE, RESIGN, ATTEND.\n"
        "Allowed POLARITY labels: POSITIVE, NEGATIVE.\n"
        "Allowed CERTAINTY labels: POSSIBLE, PROBABLE, CERTAIN.\n"
        "Return exactly four lines:\nSPEAKER: <label>\nACTION: <label>\nPOLARITY: <label>\nCERTAINTY: <label>"
    )


def parse_output(raw: str) -> dict[str, str] | None:
    values = {}
    for field in ("SPEAKER", "ACTION", "POLARITY", "CERTAINTY"):
        match = re.search(rf"(?im)^{field}:\s*([A-Z]+)\s*$", raw)
        if not match:
            return None
        values[field.lower()] = match.group(1)
    if values["speaker"] not in SPEAKERS or values["action"] not in ACTIONS or values["polarity"] not in POLARITIES or values["certainty"] not in CERTAINTIES:
        return None
    return values


def _score(item: ClosedItem, raw: str) -> dict[str, object]:
    parsed = parse_output(raw)
    expected = {"speaker": item.speaker, "action": item.action, "polarity": item.polarity, "certainty": item.certainty}
    field_scores = {f"{field}_exact": parsed is not None and parsed[field] == value for field, value in expected.items()}
    return {"parsed": parsed, "parse_success": parsed is not None, **field_scores, "exact": parsed == expected}


def _summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    fields = ["parse_success", "speaker_exact", "action_exact", "polarity_exact", "certainty_exact", "exact"]
    def rates(subset: list[dict[str, object]]) -> dict[str, float]:
        return {field: sum(bool(row["score"][field]) for row in subset) / len(subset) if subset else 0.0 for field in fields}
    return {"count": len(rows), **rates(rows), "by_language": {language: rates([row for row in rows if row["item"]["language"] == language]) for language in sorted(LANGUAGES)}}


def run_pilot(items: Iterable[ClosedItem], backend: object, output_dir: Path, *, method: str) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in items:
        prompt = render_prompt(item, method)
        raw = backend.generate(prompt)
        rows.append({"item": asdict(item), "method": method, "prompt": prompt, "raw_output": raw, "score": _score(item, raw)})
    metrics = _summarize(rows)
    (output_dir / "generations.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metrics


def validate_run(output_dir: Path) -> dict[str, object]:
    stored_rows = [json.loads(line) for line in (output_dir / "generations.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    errors = []
    rows = []
    for row in stored_rows:
        score = _score(ClosedItem(**row["item"]), row["raw_output"])
        rows.append({**row, "score": score})
        if score != row["score"] and "score_mismatch" not in errors:
            errors.append("score_mismatch")
    metrics = _summarize(rows)
    if metrics != json.loads((output_dir / "metrics.json").read_text(encoding="utf-8")):
        errors.append("metrics_mismatch")
    return {"status": "pass" if not errors else "fail", "errors": errors, "generation_count": len(rows), "reproduced_metrics": metrics}

