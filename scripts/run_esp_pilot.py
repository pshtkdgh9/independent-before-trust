"""Run one deterministic ESP prompt condition on a pinned local model."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp.core import render_rewrite_prompt, score_cue_preservation, validate_annotations
from src.lad.hf_backend import HuggingFaceBackend


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--condition", choices=["direct", "generic", "frame"], required=True)
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    args = parser.parse_args()

    items = read_jsonl(args.items)
    annotations = read_jsonl(args.annotations)
    validate_annotations([str(row["item_id"]) for row in items], annotations)
    selected = [(item, ann) for item, ann in zip(items, annotations) if ann["cue_valid"] == "yes"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    config = {**vars(args), "items": str(args.items), "annotations": str(args.annotations), "model_path": str(args.model_path), "eligible_items": len(selected), "protocol": "esp-v0-development"}
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    backend = HuggingFaceBackend(args.model_path, max_new_tokens=args.max_new_tokens, seed=args.seed, dtype="float16")
    rows = []
    for item, annotation in selected:
        prompt = render_rewrite_prompt(str(item["frame"]["scope"]), annotation, args.condition)
        output = backend.generate(prompt)
        rows.append({"item_id": item["item_id"], "condition": args.condition, "prompt": prompt, "raw_output": output, "strength": annotation["strength"], "cue_preserved_diagnostic": score_cue_preservation(output, str(annotation["strength"]))})
    (args.output_dir / "generations.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    metrics = {"items": len(rows), "cue_preservation_diagnostic": sum(bool(row["cue_preserved_diagnostic"]) for row in rows) / len(rows)}
    (args.output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
