from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from src.esp.core import render_rewrite_prompt, score_cue_preservation

_ROOT = Path(__file__).resolve().parents[1]
_RUNNER_PATH = _ROOT / "scripts" / "run_esp_counterfactual.py"
_VALIDATOR_PATH = _ROOT / "scripts" / "validate_esp_counterfactual.py"
_EXPECTED_COMMIT = "b1d86358eac24a757fb631d5c4342869d9c177e6"

_RUNNER_SPEC = importlib.util.spec_from_file_location("run_esp_counterfactual", _RUNNER_PATH)
assert _RUNNER_SPEC and _RUNNER_SPEC.loader
runner = importlib.util.module_from_spec(_RUNNER_SPEC)
sys.modules[_RUNNER_SPEC.name] = runner
_RUNNER_SPEC.loader.exec_module(runner)

_VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "validate_esp_counterfactual", _VALIDATOR_PATH
)
assert _VALIDATOR_SPEC and _VALIDATOR_SPEC.loader
validator = importlib.util.module_from_spec(_VALIDATOR_SPEC)
sys.modules[_VALIDATOR_SPEC.name] = validator
_VALIDATOR_SPEC.loader.exec_module(validator)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _build_complete_run(run_dir: Path, *, condition: str = "frame") -> None:
    pairs = runner.load_counterfactual_pairs()
    rows: list[dict[str, object]] = []
    for pair in pairs:
        variants = (
            (
                "original",
                pair.record.original_source,
                pair.record.original_strength,
            ),
            (
                "counterfactual",
                pair.record.counterfactual_source,
                pair.record.counterfactual_strength,
            ),
        )
        for variant, source, strength in variants:
            annotation = {
                "strength": strength,
                "attribution": pair.attribution,
                "scope_text": pair.record.proposition_skeleton,
            }
            output = (
                "The finding is likely preserved."
                if strength == "likely"
                else "The finding may be preserved."
                if strength == "possible"
                else "The findings suggest preservation."
            )
            rows.append(
                {
                    "pair_id": pair.record.pair_id,
                    "variant": variant,
                    "source_item_id": pair.source_item_id,
                    "assigned_strength": strength,
                    "prompt": render_rewrite_prompt(source, annotation, condition),
                    "raw_output": output,
                    "diagnostic": {
                        "cue_preserved": score_cue_preservation(output, strength)
                    },
                }
            )
    cue_count = sum(bool(row["diagnostic"]["cue_preserved"]) for row in rows)
    run_dir.mkdir(parents=True)
    (run_dir / "RUN_COMPLETE").write_text("", encoding="utf-8")
    (run_dir / "run-started-utc.txt").write_text("2026-07-22T00:00:00Z\n", encoding="utf-8")
    (run_dir / "run-completed-utc.txt").write_text("2026-07-22T00:01:00Z\n", encoding="utf-8")
    (run_dir / "run-git-commit.txt").write_text(_EXPECTED_COMMIT + "\n", encoding="utf-8")
    _write_jsonl(run_dir / "generations.jsonl", rows)
    _write_json(
        run_dir / "metrics.json",
        {
            "pair_count": 14,
            "row_count": 28,
            "cue_bin_preservation_rate": cue_count / len(rows),
        },
    )
    _write_json(
        run_dir / "config.json",
        {
            "backend": "HuggingFaceBackend",
            "condition": condition,
            "do_sample": False,
            "dtype": "float16",
            "generation_count": 28,
            "git_commit": _EXPECTED_COMMIT,
            "max_new_tokens": 96,
            "model_id": "test/model",
            "model_path": "models/test",
            "model_revision": "revision-1",
            "pair_count": 14,
            "pairs_path": "data/annotations/esp_counterfactual_pairs_v0.jsonl",
            "pairs_sha256": hashlib.sha256(
                (runner.DEFAULT_PAIRS_PATH).read_bytes()
            ).hexdigest(),
            "protocol": "esp-counterfactual-v0",
            "revision": "revision-1",
            "seed": 1701,
            "tokenizer_revision": "revision-1",
        },
    )


class ESPCounterfactualValidationTests(unittest.TestCase):
    def _validate(self, run_dir: Path, **kwargs: object) -> dict[str, object]:
        return validator.validate_esp_counterfactual_run(
            run_dir,
            pairs_path=runner.DEFAULT_PAIRS_PATH,
            expected_git_commit=_EXPECTED_COMMIT,
            expected_model_id=kwargs.pop("expected_model_id", "test/model"),
            expected_revision=kwargs.pop("expected_revision", "revision-1"),
            expected_condition=kwargs.pop("expected_condition", "frame"),
            **kwargs,
        )

    def test_accepts_valid_fixture_and_writes_validation_json_with_file_hashes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            _build_complete_run(run_dir)

            report = self._validate(run_dir, output_path=run_dir / "validation.json")

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["counts"], {"pairs": 14, "generations": 28})
            self.assertEqual(report["recomputed_metrics"]["pair_count"], 14)
            self.assertEqual(report["recomputed_metrics"]["row_count"], 28)
            self.assertEqual(report["hashes"]["pairs_sha256"], report["config"]["pairs_sha256"])
            self.assertGreater(report["files"]["generations.jsonl"]["bytes"], 0)
            self.assertEqual(
                report["files"]["generations.jsonl"]["sha256"],
                hashlib.sha256((run_dir / "generations.jsonl").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                json.loads((run_dir / "validation.json").read_text(encoding="utf-8")),
                report,
            )
            second_report = self._validate(run_dir, output_path=run_dir / "validation.json")
            self.assertNotIn("validation.json", second_report["files"])
            self.assertEqual(second_report, report)

    def test_rejects_tampered_metrics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            _build_complete_run(run_dir)
            metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
            metrics["cue_bin_preservation_rate"] = 0.0
            _write_json(run_dir / "metrics.json", metrics)

            report = self._validate(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertIn("metrics do not reproduce from generations", report["errors"])

    def test_rejects_missing_generation_row(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            _build_complete_run(run_dir)
            rows = (run_dir / "generations.jsonl").read_text(encoding="utf-8").splitlines()
            (run_dir / "generations.jsonl").write_text("\n".join(rows[:-1]) + "\n", encoding="utf-8")

            report = self._validate(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertIn("generation row count mismatch: expected 28, found 27", report["errors"])
            self.assertIn("generation rows do not match manifest pair order", report["errors"])

    def test_rejects_missing_complete_marker_and_wrong_commit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            _build_complete_run(run_dir)
            (run_dir / "RUN_COMPLETE").unlink()
            (run_dir / "run-git-commit.txt").write_text("deadbeef\n", encoding="utf-8")

            report = self._validate(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertIn("missing RUN_COMPLETE", report["errors"])
            self.assertIn("run-git-commit.txt mismatch: deadbeef", report["errors"])

    def test_rejects_manifest_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            _build_complete_run(run_dir)
            config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
            config["pairs_sha256"] = "0" * 64
            _write_json(run_dir / "config.json", config)

            report = self._validate(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertIn("config pairs_sha256 does not match manifest", report["errors"])

    def test_rejects_empty_raw_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            _build_complete_run(run_dir)
            rows = [
                json.loads(line)
                for line in (run_dir / "generations.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            rows[3]["raw_output"] = " "
            _write_jsonl(run_dir / "generations.jsonl", rows)

            report = self._validate(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertIn("empty raw_output for esp-cf-v0-0002 counterfactual", report["errors"])

    def test_rejects_prompt_label_leakage_for_condition(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            _build_complete_run(run_dir)
            rows = [
                json.loads(line)
                for line in (run_dir / "generations.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            rows[0]["prompt"] += "\nVariant: original"
            _write_jsonl(run_dir / "generations.jsonl", rows)

            report = self._validate(run_dir)

            self.assertEqual(report["status"], "fail")
            self.assertIn(
                "prompt mismatch for esp-cf-v0-0001 original", report["errors"]
            )
            self.assertIn(
                "prompt leaks internal label for esp-cf-v0-0001 original", report["errors"]
            )


if __name__ == "__main__":
    unittest.main()
