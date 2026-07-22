"""Run the DCEA falsification pilot from a pinned local Hugging Face snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dcea.core import run_pilot
from src.dcea.fixtures import pilot_templates
from src.lad.hf_backend import HuggingFaceBackend


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--max-new-tokens", type=int, default=48)
    parser.add_argument("--dtype", choices=["auto", "float16", "bfloat16", "float32"], default="float16")
    parser.add_argument("--contrastive", action="store_true")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    templates = pilot_templates()
    (args.output_dir / "templates.jsonl").write_text(
        "".join(json.dumps(asdict(item), sort_keys=True) + "\n" for item in templates),
        encoding="utf-8",
    )
    config = {
        "model_id": args.model_id,
        "revision": args.revision,
        "license": args.license,
        "seed": args.seed,
        "max_new_tokens": args.max_new_tokens,
        "dtype": args.dtype,
        "contrastive": args.contrastive,
        "template_count": len(templates),
    }
    (args.output_dir / "config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    backend = HuggingFaceBackend(
        args.model_path,
        max_new_tokens=args.max_new_tokens,
        seed=args.seed,
        dtype=args.dtype,
    )
    run_pilot(templates, backend, args.output_dir, contrastive=args.contrastive)


if __name__ == "__main__":
    main()
