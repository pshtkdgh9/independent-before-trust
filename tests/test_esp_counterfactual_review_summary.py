import json
import importlib.util
import sys
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[1] / "scripts" / "summarize_esp_counterfactual_reviews.py"
_SPEC = importlib.util.spec_from_file_location("summarize_esp_counterfactual_reviews", _PATH)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
summarize_reviews = _MODULE.summarize_reviews


FIELDS = ("scope_preserved", "strength_preserved", "unsupported_addition", "acceptable_lay_rewrite")


def _write(path: Path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("".join(json.dumps(r) + "\n" for r in rows))


def test_summary_counts_pair_equivariance_and_gate(tmp_path):
    key = []
    a = []
    b = []
    for model in ("phi", "qwen"):
        for condition in ("generic", "frame"):
            for pair in ("p1", "p2"):
                for variant in ("original", "counterfactual"):
                    rid = f"{model}-{condition}-{pair}-{variant}"
                    key.append({"review_id": rid, "run": f"esp-{model}-{condition}", "model_id": model, "condition": condition, "pair_id": pair, "variant": variant})
                    good = condition == "frame" or pair == "p1"
                    row = {"review_id": rid, "scope_preserved": "yes" if good else "no", "strength_preserved": "yes" if good else "no", "unsupported_addition": "no", "acceptable_lay_rewrite": "yes" if good else "no", "rationale": "x"}
                    a.append(row); b.append(dict(row))
    kp, ap, bp = (tmp_path / n for n in ("key.jsonl", "a.jsonl", "b.jsonl"))
    _write(kp, key); _write(ap, a); _write(bp, b)
    result = summarize_reviews(kp, ap, bp, expected_count=16)
    assert result["agreement"]["scope_preserved"] == {"agree": 16, "total": 16, "rate": 1.0, "cohen_kappa": 1.0}
    assert result["runs"]["esp-phi-frame"]["paired_equivariance"] == {"numerator": 2, "denominator": 2, "rate": 1.0}
    assert result["comparisons"]["phi"]["advance"] is True
    assert result["gate"]["advance"] is True
    assert result["evidence_class"] == "model_agent_development_only"
    assert result["human_evidence"] is False


def test_rejects_mismatched_ids_and_bad_domain(tmp_path):
    key = tmp_path / "key.jsonl"; a = tmp_path / "a.jsonl"; b = tmp_path / "b.jsonl"
    _write(key, [{"review_id":"x","run":"r","model_id":"m","condition":"frame","pair_id":"p","variant":"original"}])
    base = {"review_id":"x","scope_preserved":"yes","strength_preserved":"yes","unsupported_addition":"no","acceptable_lay_rewrite":"yes","rationale":"x"}
    _write(a, [base]); _write(b, [{**base, "review_id":"y"}])
    with pytest.raises(ValueError, match="identical review_id"):
        summarize_reviews(key, a, b, expected_count=1)
    _write(b, [{**base, "scope_preserved":"maybe"}])
    with pytest.raises(ValueError, match="scope_preserved"):
        summarize_reviews(key, a, b, expected_count=1)
