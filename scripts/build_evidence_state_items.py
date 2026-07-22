"""Build evidence-state paired items from an audited source-pack JSONL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evidence_state.builder import (
    EvidenceStateBuildError,
    build_evidence_state_items,
    load_source_pack_jsonl,
    write_items_jsonl,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pack", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        rows = load_source_pack_jsonl(args.source_pack)
        items = build_evidence_state_items(rows)
        write_items_jsonl(items, args.output)
    except (OSError, EvidenceStateBuildError) as exc:
        raise SystemExit(f"cannot build evidence-state items: {exc}") from exc


if __name__ == "__main__":
    main()
