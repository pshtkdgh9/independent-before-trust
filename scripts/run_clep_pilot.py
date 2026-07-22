"""Run one CLEP model/method cell from a pinned local Hugging Face snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.clep.core import run_pilot, validate_run
from src.clep.fixtures import pilot_items
from src.lad.hf_backend import HuggingFaceBackend


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--method", choices=["direct", "translate", "typed"], required=True)
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--dtype", choices=["auto", "float16", "bfloat16", "float32"], default="float16")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    items = pilot_items()
    (args.output_dir / "items.jsonl").write_text(
        "".join(json.dumps(asdict(item), ensure_ascii=False, sort_keys=True) + "\n" for item in items),
        encoding="utf-8",
    )
    config = vars(args).copy()
    config["output_dir"] = str(args.output_dir)
    config["model_path"] = str(args.model_path)
    config["item_count"] = len(items)
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    backend = HuggingFaceBackend(args.model_path, max_new_tokens=args.max_new_tokens, seed=args.seed, dtype=args.dtype)
    run_pilot(items, backend, args.output_dir, method=args.method)
    report = validate_run(args.output_dir)
    (args.output_dir / "integrity_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
