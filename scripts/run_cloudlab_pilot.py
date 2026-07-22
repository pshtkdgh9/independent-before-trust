"""Run the LAD paired pilot from a pinned local Hugging Face snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lad.hf_backend import HuggingFaceBackend
from src.lad.pilot import PilotConfig, run_adaptive_paired_pilot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--dtype", choices=["auto", "float16", "bfloat16", "float32"], default="bfloat16")
    parser.add_argument("--trust-remote-code", action="store_true")
    args = parser.parse_args()

    records = [
        json.loads(line)
        for line in args.items.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    config = PilotConfig(
        model_id=args.model_id,
        model_revision=args.revision,
        tokenizer_revision=args.revision,
        model_license=args.license,
        seed=args.seed,
        max_new_tokens=args.max_new_tokens,
        dtype=args.dtype,
    )
    backend = HuggingFaceBackend(
        args.model_path,
        max_new_tokens=args.max_new_tokens,
        seed=args.seed,
        dtype=args.dtype,
        trust_remote_code=args.trust_remote_code,
    )
    run_adaptive_paired_pilot(records, backend, args.output_dir, config)


if __name__ == "__main__":
    main()
