from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BUILDER_PATH = _ROOT / "scripts" / "build_esp_counterfactual_blind_review.py"
_PAIRS_PATH = _ROOT / "data" / "annotations" / "esp_counterfactual_pairs_v0.jsonl"
_ARTIFACT_ROOT = (
    _ROOT
    / "results"
    / "strong_accept_loop"
    / "cloudlab_artifacts"
    / "esp-counterfactual-b1d8635"
)

_BUILDER_SPEC = importlib.util.spec_from_file_location(
    "build_esp_counterfactual_blind_review", _BUILDER_PATH
)
assert _BUILDER_SPEC and _BUILDER_SPEC.loader
builder = importlib.util.module_from_spec(_BUILDER_SPEC)
sys.modules[_BUILDER_SPEC.name] = builder
_BUILDER_SPEC.loader.exec_module(builder)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class ESPCounterfactualBlindReviewTests(unittest.TestCase):
    def test_build_is_deterministic_and_writes_sorted_packet_and_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            first_packet = temp_path / "first_packet.jsonl"
            first_key = temp_path / "first_key.jsonl"
            second_packet = temp_path / "second_packet.jsonl"
            second_key = temp_path / "second_key.jsonl"

            first = builder.build_blind_review_packet(
                artifact_root=_ARTIFACT_ROOT,
                pairs_path=_PAIRS_PATH,
                packet_path=first_packet,
                key_path=first_key,
            )
            second = builder.build_blind_review_packet(
                artifact_root=_ARTIFACT_ROOT,
                pairs_path=_PAIRS_PATH,
                packet_path=second_packet,
                key_path=second_key,
            )

            self.assertEqual(first, second)
            self.assertEqual(first_packet.read_bytes(), second_packet.read_bytes())
            self.assertEqual(first_key.read_bytes(), second_key.read_bytes())
            self.assertEqual([row["review_id"] for row in first["packet"]], sorted(row["review_id"] for row in first["packet"]))
            self.assertEqual([row["review_id"] for row in first["key"]], sorted(row["review_id"] for row in first["key"]))

    def test_packet_has_112_unique_opaque_ids_and_hides_internal_labels(self):
        result = builder.build_blind_review_packet(
            artifact_root=_ARTIFACT_ROOT,
            pairs_path=_PAIRS_PATH,
        )
        packet = result["packet"]
        key = result["key"]
        review_ids = [row["review_id"] for row in packet]

        self.assertEqual(len(packet), 112)
        self.assertEqual(len(key), 112)
        self.assertEqual(len(set(review_ids)), 112)
        self.assertEqual({row["review_id"] for row in key}, set(review_ids))
        self.assertEqual(
            set(packet[0]),
            {
                "review_id",
                "source_sentence",
                "target_strength",
                "target_scope",
                "attribution",
                "output",
            },
        )

        key_by_review_id = {row["review_id"]: row for row in key}
        forbidden_values: set[str] = {"original", "counterfactual", "generic", "frame"}
        for key_row in key:
            forbidden_values.update(
                str(key_row[field])
                for field in (
                    "run",
                    "model_id",
                    "condition",
                    "pair_id",
                    "variant",
                    "source_item_id",
                )
            )

        for packet_row in packet:
            self.assertTrue(str(packet_row["review_id"]).startswith("esp-cf-review-"))
            self.assertTrue(str(packet_row["source_sentence"]).strip())
            self.assertTrue(str(packet_row["output"]).strip())
            serialized = json.dumps(packet_row, ensure_ascii=False)
            self.assertNotIn(str(key_by_review_id[packet_row["review_id"]]["run"]), serialized)
            for forbidden in forbidden_values:
                self.assertNotIn(forbidden, str(packet_row["review_id"]))
            for forbidden in forbidden_values:
                if forbidden in {"original", "counterfactual"}:
                    continue
                self.assertNotIn(forbidden, serialized)

    def test_rejects_incomplete_run_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_root = Path(temp_dir) / "artifacts"
            shutil.copytree(_ARTIFACT_ROOT, artifact_root)
            shutil.rmtree(artifact_root / "esp-qwen-frame")

            with self.assertRaisesRegex(ValueError, "expected exactly 4 runs"):
                builder.build_blind_review_packet(
                    artifact_root=artifact_root,
                    pairs_path=_PAIRS_PATH,
                )

    def test_rejects_missing_generation_row(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_root = Path(temp_dir) / "artifacts"
            shutil.copytree(_ARTIFACT_ROOT, artifact_root)
            generations_path = artifact_root / "esp-qwen-generic" / "generations.jsonl"
            rows = _read_jsonl(generations_path)
            _write_jsonl(generations_path, rows[:-1])

            with self.assertRaisesRegex(ValueError, "expected 28 rows"):
                builder.build_blind_review_packet(
                    artifact_root=artifact_root,
                    pairs_path=_PAIRS_PATH,
                )

    def test_rejects_tampered_strength_and_source_item_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_root = Path(temp_dir) / "artifacts"
            shutil.copytree(_ARTIFACT_ROOT, artifact_root)
            generations_path = artifact_root / "esp-qwen-generic" / "generations.jsonl"
            rows = _read_jsonl(generations_path)
            rows[0]["assigned_strength"] = "possible"
            rows[1]["source_item_id"] = "esp-wrong-source"
            _write_jsonl(generations_path, rows)

            with self.assertRaisesRegex(ValueError, "assigned_strength mismatch.*source_item_id mismatch"):
                builder.build_blind_review_packet(
                    artifact_root=artifact_root,
                    pairs_path=_PAIRS_PATH,
                )

    def test_cli_writes_actual_packet_and_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            packet_path = temp_path / "packet.jsonl"
            key_path = temp_path / "key.jsonl"

            result = subprocess.run(
                [
                    sys.executable,
                    str(_BUILDER_PATH),
                    "--artifact-root",
                    str(_ARTIFACT_ROOT),
                    "--pairs",
                    str(_PAIRS_PATH),
                    "--packet",
                    str(packet_path),
                    "--key",
                    str(key_path),
                ],
                cwd=temp_path,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(len(_read_jsonl(packet_path)), 112)
            self.assertEqual(len(_read_jsonl(key_path)), 112)


if __name__ == "__main__":
    unittest.main()
