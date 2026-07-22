"""Typed prompts, scoring, and integrity validation for CLEP pilots."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Iterable


LANGUAGES = {"en", "ko", "es"}
POLARITIES = {"positive", "negative"}
CERTAINTIES = {"possible", "probable", "certain"}


@dataclass(frozen=True)
class EpistemicItem:
    item_id: str
    language: str
    evidence: str
    speaker: str
    proposition: str
    polarity: str
    certainty: str
    parallel_group: str

    def __post_init__(self) -> None:
        if self.language not in LANGUAGES:
            raise ValueError("unsupported language")
        if self.polarity not in POLARITIES:
            raise ValueError("unsupported polarity")
        if self.certainty not in CERTAINTIES:
            raise ValueError("unsupported certainty")


def render_prompt(item: EpistemicItem, method: str) -> str:
    if method not in {"direct", "translate", "typed"}:
        raise ValueError("unknown method")
    instruction = {
        "direct": "Read the evidence and report its meaning in English.",
        "translate": "Translate the evidence into English, then report its meaning.",
        "typed": "Extract the epistemic fields before writing the English report.",
    }[method]
    return (
        f"{instruction}\nEVIDENCE ({item.language}): {item.evidence}\n"
        "Return exactly two lines. Use only possible, probable, or certain for certainty; "
        "use positive or negative for polarity.\n"
        'TUPLE: {"speaker":"...","proposition":"...","polarity":"...","certainty":"..."}\n'
        "REPORT: <one English sentence>"
    )


def parse_typed_output(raw_text: str) -> dict[str, str] | None:
    match = re.search(r"(?im)^TUPLE:\s*(\{.*\})\s*$", raw_text)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    keys = {"speaker", "proposition", "polarity", "certainty"}
    if set(value) != keys or not all(isinstance(value[key], str) for key in keys):
        return None
    if value["polarity"] not in POLARITIES or value["certainty"] not in CERTAINTIES:
        return None
    return value


def _score(item: EpistemicItem, raw_output: str) -> dict[str, object]:
    parsed = parse_typed_output(raw_output)
    return {
        "parsed": parsed,
        "parse_success": parsed is not None,
        "speaker_exact": parsed is not None and parsed["speaker"].casefold() == item.speaker.casefold(),
        "proposition_exact": parsed is not None and parsed["proposition"].casefold() == item.proposition.casefold(),
        "polarity_exact": parsed is not None and parsed["polarity"] == item.polarity,
        "certainty_exact": parsed is not None and parsed["certainty"] == item.certainty,
        "all_fields_exact": parsed is not None
        and parsed["speaker"].casefold() == item.speaker.casefold()
        and parsed["proposition"].casefold() == item.proposition.casefold()
        and parsed["polarity"] == item.polarity
        and parsed["certainty"] == item.certainty,
    }


def _summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    fields = ["parse_success", "speaker_exact", "proposition_exact", "polarity_exact", "certainty_exact", "all_fields_exact"]
    count = len(rows)
    result: dict[str, object] = {field: sum(bool(row["score"][field]) for row in rows) / count if count else 0.0 for field in fields}
    result["count"] = count
    result["by_language"] = {
        language: {
            field: sum(bool(row["score"][field]) for row in rows if row["item"]["language"] == language)
            / sum(1 for row in rows if row["item"]["language"] == language)
            for field in fields
        }
        for language in sorted({str(row["item"]["language"]) for row in rows})
    }
    return result


def run_pilot(items: Iterable[EpistemicItem], backend: object, output_dir: Path, *, method: str) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in items:
        prompt = render_prompt(item, method)
        raw_output = backend.generate(prompt)
        rows.append({"item": asdict(item), "method": method, "prompt": prompt, "raw_output": raw_output, "score": _score(item, raw_output)})
    metrics = _summarize(rows)
    (output_dir / "generations.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metrics


def validate_run(output_dir: Path) -> dict[str, object]:
    rows = [json.loads(line) for line in (output_dir / "generations.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    errors = []
    reproduced = []
    for row in rows:
        item = EpistemicItem(**row["item"])
        score = _score(item, row["raw_output"])
        reproduced.append({**row, "score": score})
        if score != row["score"] and "score_mismatch" not in errors:
            errors.append("score_mismatch")
        if not score["parse_success"] and "parse_failures" not in errors:
            errors.append("parse_failures")
    metrics = _summarize(reproduced)
    stored = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    if metrics != stored:
        errors.append("metrics_mismatch")
    return {"status": "pass" if not errors else "fail", "errors": errors, "generation_count": len(rows), "reproduced_metrics": metrics}

