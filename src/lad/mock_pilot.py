"""Generate a deterministic mock artifact for testing the LAD pipeline.

The generated values are synthetic and must never be cited as empirical evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .metrics import aggregate_revision_metrics
from .pairs import build_lineage_pair


ARTIFACT_CLASS = "mock-not-empirical-evidence"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run_mock_pilot(output_dir: Path) -> dict[str, Any]:
    """Exercise pair construction and metric aggregation with synthetic inputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    base_cases = [
        {
            "pair_id": "mock-001",
            "question": "Which answer is supported?",
            "target_initial_answer": "A",
            "peer_claims": ["B", "B", "B"],
            "peer_correctness": [False, False, False],
            "peer_confidence": [0.8, 0.8, 0.8],
            "message_order": [0, 1, 2],
        },
        {
            "pair_id": "mock-002",
            "question": "Which answer is supported?",
            "target_initial_answer": "B",
            "peer_claims": ["A", "A", "A"],
            "peer_correctness": [True, True, True],
            "peer_confidence": [0.7, 0.7, 0.7],
            "message_order": [0, 1, 2],
        },
    ]
    pairs = [
        record
        for index, base_case in enumerate(base_cases)
        for record in build_lineage_pair(base_case, seed=1701 + index)
    ]

    with (output_dir / "pairs.jsonl").open("w", encoding="utf-8") as handle:
        for record in pairs:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    # These outcomes are deliberately synthetic. They exist only to verify that
    # condition-stratified aggregation and artifact serialization work end to end.
    mock_outcomes = {
        "COMMON": [
            {"initial_correct": True, "final_correct": False},
            {"initial_correct": False, "final_correct": False},
        ],
        "INDEPENDENT": [
            {"initial_correct": True, "final_correct": True},
            {"initial_correct": False, "final_correct": True},
        ],
    }
    metrics: dict[str, Any] = {
        "artifact_class": ARTIFACT_CLASS,
        "conditions": {
            condition: aggregate_revision_metrics(rows)
            for condition, rows in mock_outcomes.items()
        },
        "warning": "Synthetic pipeline check; not empirical evidence and not citable.",
    }
    config = {
        "artifact_class": ARTIFACT_CLASS,
        "case_count": len(base_cases),
        "pair_seed_start": 1701,
        "warning": "Synthetic pipeline check; not empirical evidence and not citable.",
    }
    _write_json(output_dir / "metrics.json", metrics)
    _write_json(output_dir / "config.json", config)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run_mock_pilot(args.output_dir)


if __name__ == "__main__":
    main()
