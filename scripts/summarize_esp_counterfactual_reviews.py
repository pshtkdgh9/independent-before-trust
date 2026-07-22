#!/usr/bin/env python
"""Summarize two blinded model-agent ESP counterfactual reviews."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "strong_accept_loop" / "esp_counterfactual"
FIELDS = ("scope_preserved", "strength_preserved", "unsupported_addition", "acceptable_lay_rewrite")
DOMAIN = {"yes", "no", "unclear"}


def _read(path: Path, kind: str) -> list[dict]:
    if not path.is_file(): raise ValueError(f"missing {kind}: {path}")
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip(): raise ValueError(f"{kind} line {number} is blank")
        try: row = json.loads(line)
        except json.JSONDecodeError as exc: raise ValueError(f"{kind} line {number} is not JSON: {exc.msg}") from exc
        if not isinstance(row, dict): raise ValueError(f"{kind} line {number} is not an object")
        rows.append(row)
    return rows


def _index(rows: list[dict], kind: str, expected: int, review: bool = False) -> dict[str, dict]:
    if len(rows) != expected: raise ValueError(f"{kind} expected {expected} rows, found {len(rows)}")
    out = {}
    for i, row in enumerate(rows, 1):
        rid = row.get("review_id")
        if not isinstance(rid, str) or not rid.strip() or rid in out: raise ValueError(f"{kind} line {i} invalid or duplicate review_id")
        if review:
            for field in FIELDS:
                if row.get(field) not in DOMAIN: raise ValueError(f"{kind} line {i} invalid {field}: {row.get(field)!r}")
        else:
            for field in ("run", "model_id", "condition", "pair_id", "variant"):
                if not isinstance(row.get(field), str) or not row[field].strip(): raise ValueError(f"{kind} line {i} invalid {field}")
            if row["condition"] not in {"generic", "frame"} or row["variant"] not in {"original", "counterfactual"}: raise ValueError(f"{kind} line {i} invalid condition or variant")
        out[rid] = row
    return out


def _metric(n: int, d: int) -> dict: return {"numerator": n, "denominator": d, "rate": n / d if d else None}


def _kappa(xs: list[str], ys: list[str]) -> float | None:
    n = len(xs); observed = sum(x == y for x, y in zip(xs, ys)) / n
    cx, cy = Counter(xs), Counter(ys)
    expected = sum(cx[v] * cy[v] for v in DOMAIN) / (n * n)
    return None if expected == 1 else (observed - expected) / (1 - expected)


def summarize_reviews(key_path: Path, reviewer_a_path: Path, reviewer_b_path: Path, *, expected_count: int = 112) -> dict:
    key = _index(_read(key_path, "key"), "key", expected_count)
    a = _index(_read(reviewer_a_path, "reviewer_a"), "reviewer_a", expected_count, True)
    b = _index(_read(reviewer_b_path, "reviewer_b"), "reviewer_b", expected_count, True)
    if set(key) != set(a) or set(key) != set(b): raise ValueError("key and reviewers must contain identical review_id sets")
    agreement = {}
    for field in FIELDS:
        xs, ys = [a[x][field] for x in key], [b[x][field] for x in key]
        agree = sum(x == y for x, y in zip(xs, ys))
        agreement[field] = {"agree": agree, "total": expected_count, "rate": agree / expected_count, "cohen_kappa": _kappa(xs, ys)}
    grouped = defaultdict(list)
    for rid, meta in key.items(): grouped[meta["run"]].append((rid, meta))
    runs = {}
    if len(grouped) != 4: raise ValueError(f"expected 4 runs, found {len(grouped)}")
    for run, items in sorted(grouped.items()):
        model_ids = {m["model_id"] for _, m in items}; conditions = {m["condition"] for _, m in items}
        if len(model_ids) != 1 or len(conditions) != 1: raise ValueError(f"run {run} has inconsistent metadata")
        if expected_count == 112 and len(items) != 28: raise ValueError(f"run {run} expected 28 rows, found {len(items)}")
        stats = {"model_id": next(iter(model_ids)), "condition": next(iter(conditions)), "rows": len(items)}
        for field in FIELDS:
            n = sum(a[r][field] == b[r][field] == "yes" for r, _ in items)
            stats[field + "_strict_yes"] = _metric(n, len(items))
        pairs = defaultdict(dict)
        for rid, meta in items:
            if meta["variant"] in pairs[meta["pair_id"]]: raise ValueError(f"duplicate pair variant in {run}")
            pairs[meta["pair_id"]][meta["variant"]] = rid
        if any(set(v) != {"original", "counterfactual"} for v in pairs.values()): raise ValueError(f"run {run} incomplete pair variants")
        if expected_count == 112 and len(pairs) != 14: raise ValueError(f"run {run} expected 14 pairs, found {len(pairs)}")
        eq = sum(all(a[r][f] == b[r][f] == "yes" for r in variants.values() for f in ("scope_preserved", "strength_preserved")) for variants in pairs.values())
        stats["paired_equivariance"] = _metric(eq, len(pairs)); runs[run] = stats
    by_model = defaultdict(dict)
    for run, stats in runs.items(): by_model[stats["model_id"]][stats["condition"]] = stats
    comparisons = {}
    for model, cells in by_model.items():
        if set(cells) != {"generic", "frame"}: raise ValueError(f"model {model} lacks generic/frame cells")
        g, f = cells["generic"], cells["frame"]
        eq_better = f["paired_equivariance"]["rate"] > g["paired_equivariance"]["rate"]
        unsupported_not_worse = f["unsupported_addition_strict_yes"]["rate"] <= g["unsupported_addition_strict_yes"]["rate"]
        acceptable_not_worse = f["acceptable_lay_rewrite_strict_yes"]["rate"] >= g["acceptable_lay_rewrite_strict_yes"]["rate"]
        comparisons[model] = {"generic_run": next(r for r,s in runs.items() if s is g), "frame_run": next(r for r,s in runs.items() if s is f), "paired_equivariance": {"generic": g["paired_equivariance"], "frame": f["paired_equivariance"], "frame_minus_generic_rate": f["paired_equivariance"]["rate"] - g["paired_equivariance"]["rate"]}, "unsupported_addition_strict_yes": {"generic": g["unsupported_addition_strict_yes"], "frame": f["unsupported_addition_strict_yes"]}, "acceptable_lay_rewrite_strict_yes": {"generic": g["acceptable_lay_rewrite_strict_yes"], "frame": f["acceptable_lay_rewrite_strict_yes"]}, "frame_strictly_better_equivariance": eq_better, "frame_not_worse_unsupported_additions": unsupported_not_worse, "frame_not_worse_acceptable_rate": acceptable_not_worse, "advance": eq_better and unsupported_not_worse and acceptable_not_worse}
    advance = len(comparisons) == 2 and all(x["advance"] for x in comparisons.values())
    return {"schema_version": 1, "evidence_class": "model_agent_development_only", "human_evidence": False, "row_count": expected_count, "agreement": agreement, "runs": runs, "comparisons": comparisons, "gate": {"advance": advance, "rule": "frame paired equivariance must be strictly greater than generic in both model families; frame strict-consensus unsupported-addition rate must be no greater; frame strict-consensus acceptable rate must be no lower"}}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--key", type=Path, default=BASE / "blind_key.jsonl"); p.add_argument("--reviewer-a", type=Path, default=BASE / "reviewer_a_v1.jsonl"); p.add_argument("--reviewer-b", type=Path, default=BASE / "reviewer_b_v1.jsonl"); p.add_argument("--output", type=Path, default=BASE / "review_summary_v1.json")
    args = p.parse_args()
    try: result = summarize_reviews(args.key, args.reviewer_a, args.reviewer_b)
    except ValueError as exc: print(str(exc), file=sys.stderr); raise SystemExit(1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "advance": result["gate"]["advance"]}, sort_keys=True))


if __name__ == "__main__": main()
