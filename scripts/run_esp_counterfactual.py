"""Run the ESP counterfactual strength-preservation protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp.core import render_rewrite_prompt, score_cue_preservation
from src.esp.counterfactual import CounterfactualPair, validate_counterfactual_pairs
from src.lad.hf_backend import HuggingFaceBackend


DEFAULT_PAIRS_PATH = Path("data/annotations/esp_counterfactual_pairs_v0.jsonl")
ALLOWED_CONDITIONS = frozenset({"generic", "frame"})


class GenerationBackend(Protocol):
    def generate(self, prompt: str) -> str:
        ...


@dataclass(frozen=True)
class CounterfactualManifestPair:
    record: CounterfactualPair
    source_item_id: str
    attribution: str


@dataclass(frozen=True)
class CounterfactualRunConfig:
    output_dir: Path
    model_path: Path
    model_id: str
    revision: str
    git_commit: str
    condition: str
    seed: int = 1701
    max_new_tokens: int = 96
    dtype: str = "float16"


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_non_empty_dir(path: Path) -> bool:
    return path.is_dir() and any(path.iterdir())


def load_counterfactual_pairs(
    path: Path = DEFAULT_PAIRS_PATH,
) -> list[CounterfactualManifestPair]:
    rows = read_jsonl(path)
    pairs: list[CounterfactualPair] = []
    manifest_pairs: list[CounterfactualManifestPair] = []
    for row in rows:
        pair = CounterfactualPair(
            pair_id=str(row["pair_id"]),
            original_strength=str(row["original_strength"]),
            counterfactual_strength=str(row["counterfactual_strength"]),
            original_source=str(row["original_source"]),
            counterfactual_source=str(row["counterfactual_source"]),
            edit_spans=tuple(str(span) for span in row["edit_spans"]),
            proposition_skeleton=str(row["proposition_skeleton"]),
            counterfactual_proposition_skeleton=(
                str(row["counterfactual_proposition_skeleton"])
                if row.get("counterfactual_proposition_skeleton") is not None
                else None
            ),
            polarity_changed=bool(row.get("polarity_changed", False)),
            material_argument_changed=bool(row.get("material_argument_changed", False)),
        )
        pairs.append(pair)
        manifest_pairs.append(
            CounterfactualManifestPair(
                record=pair,
                source_item_id=str(row["source_item_id"]),
                attribution=str(row["attribution"]),
            )
        )
    validate_counterfactual_pairs(pairs)
    return manifest_pairs


def _variant_rows(pair: CounterfactualManifestPair) -> tuple[dict[str, str], dict[str, str]]:
    record = pair.record
    scope = record.proposition_skeleton
    return (
        {
            "variant": "original",
            "source": record.original_source,
            "assigned_strength": record.original_strength,
            "scope_text": scope,
        },
        {
            "variant": "counterfactual",
            "source": record.counterfactual_source,
            "assigned_strength": record.counterfactual_strength,
            "scope_text": scope,
        },
    )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run_counterfactual_generation(
    *,
    pairs_path: Path = DEFAULT_PAIRS_PATH,
    backend: GenerationBackend,
    config: CounterfactualRunConfig,
) -> dict[str, object]:
    if config.condition not in ALLOWED_CONDITIONS:
        raise ValueError("condition must be one of: frame, generic")
    if _is_non_empty_dir(config.output_dir):
        raise ValueError(f"non-empty output_dir refused: {config.output_dir}")

    pairs = load_counterfactual_pairs(pairs_path)
    rows: list[dict[str, object]] = []
    completed_pair_ids: set[str] = set()
    for pair in pairs:
        pair_rows: list[dict[str, object]] = []
        for variant in _variant_rows(pair):
            annotation = {
                "strength": variant["assigned_strength"],
                "attribution": pair.attribution,
                "scope_text": variant["scope_text"],
            }
            prompt = render_rewrite_prompt(
                variant["source"],
                annotation,
                config.condition,
            )
            output = backend.generate(prompt).strip()
            if not output:
                raise ValueError(f"empty output for pair {pair.record.pair_id}")
            cue_preserved = score_cue_preservation(
                output, variant["assigned_strength"]
            )
            pair_rows.append(
                {
                    "pair_id": pair.record.pair_id,
                    "variant": variant["variant"],
                    "source_item_id": pair.source_item_id,
                    "assigned_strength": variant["assigned_strength"],
                    "prompt": prompt,
                    "raw_output": output,
                    "diagnostic": {"cue_preserved": cue_preserved},
                }
            )
        if len(pair_rows) != 2:
            raise ValueError(f"incomplete pair {pair.record.pair_id}")
        rows.extend(pair_rows)
        completed_pair_ids.add(pair.record.pair_id)

    if len(completed_pair_ids) != len(pairs) or len(rows) != len(pairs) * 2:
        raise ValueError("incomplete counterfactual generations")

    cue_preserved_count = sum(
        bool(row["diagnostic"]["cue_preserved"])
        for row in rows
        if isinstance(row["diagnostic"], dict)
    )
    metrics = {
        "pair_count": len(pairs),
        "row_count": len(rows),
        "cue_bin_preservation_rate": cue_preserved_count / len(rows) if rows else 0.0,
    }
    saved_config = {
        "protocol": "esp-counterfactual-v0",
        "pair_count": len(pairs),
        "generation_count": len(rows),
        "model_id": config.model_id,
        "model_path": str(config.model_path),
        "revision": config.revision,
        "model_revision": config.revision,
        "tokenizer_revision": config.revision,
        "git_commit": config.git_commit,
        "condition": config.condition,
        "seed": config.seed,
        "max_new_tokens": config.max_new_tokens,
        "dtype": config.dtype,
        "pairs_path": str(pairs_path),
        "pairs_sha256": file_sha256(pairs_path),
        "do_sample": False,
        "backend": "HuggingFaceBackend",
    }

    config.output_dir.mkdir(parents=True, exist_ok=True)
    (config.output_dir / "generations.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    _write_json(config.output_dir / "metrics.json", metrics)
    _write_json(config.output_dir / "config.json", saved_config)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS_PATH)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--condition", choices=sorted(ALLOWED_CONDITIONS), required=True)
    parser.add_argument("--seed", type=int, default=1701)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument(
        "--dtype",
        choices=["auto", "float16", "bfloat16", "float32"],
        default="float16",
    )
    args = parser.parse_args()

    config = CounterfactualRunConfig(
        output_dir=args.output_dir,
        model_path=args.model_path,
        model_id=args.model_id,
        revision=args.revision,
        git_commit=args.git_commit,
        condition=args.condition,
        seed=args.seed,
        max_new_tokens=args.max_new_tokens,
        dtype=args.dtype,
    )
    backend = HuggingFaceBackend(
        args.model_path,
        max_new_tokens=args.max_new_tokens,
        seed=args.seed,
        dtype=args.dtype,
    )
    run_counterfactual_generation(pairs_path=args.pairs, backend=backend, config=config)


if __name__ == "__main__":
    main()
