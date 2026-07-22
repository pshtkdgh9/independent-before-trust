from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

_RUNNER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_esp_counterfactual.py"
_SPEC = importlib.util.spec_from_file_location("run_esp_counterfactual", _RUNNER_PATH)
assert _SPEC and _SPEC.loader
runner = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = runner
_SPEC.loader.exec_module(runner)

CounterfactualRunConfig = runner.CounterfactualRunConfig
load_counterfactual_pairs = runner.load_counterfactual_pairs
run_counterfactual_generation = runner.run_counterfactual_generation


class FakeBackend:
    def __init__(self, outputs: list[str] | None = None) -> None:
        self.outputs = list(outputs or [])
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if self.outputs:
            return self.outputs.pop(0)
        if "STRENGTH=likely" in prompt:
            return "The result is likely useful."
        return "The result may be useful."


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def valid_pair(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "pair_id": "esp-cf-v0-0001",
        "source_item_id": "esp-0001-00",
        "original_strength": "possible",
        "counterfactual_strength": "likely",
        "attribution": "authors",
        "original_source": "The result may reduce symptoms.",
        "counterfactual_source": "The result likely reduces symptoms.",
        "edit_spans": ["may=>likely"],
        "proposition_skeleton": "The result reduces symptoms.",
        "counterfactual_proposition_skeleton": "The result reduces symptoms.",
        "polarity_changed": False,
        "material_argument_changed": False,
    }
    row.update(overrides)
    return row


class ESPCounterfactualRunnerTests(unittest.TestCase):
    def test_loads_default_pair_file_into_validated_counterfactual_records(self):
        pairs = load_counterfactual_pairs()

        self.assertGreater(len(pairs), 0)
        self.assertEqual(pairs[0].record.pair_id, "esp-cf-v0-0001")
        self.assertEqual(pairs[0].source_item_id, "esp-0005-03")
        self.assertEqual(pairs[0].attribution, "authors")

    def test_writes_two_rows_per_pair_in_original_then_counterfactual_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pairs_path = temp_path / "pairs.jsonl"
            write_jsonl(pairs_path, [valid_pair()])
            config = CounterfactualRunConfig(
                output_dir=temp_path / "out",
                model_path=Path("models/fake"),
                model_id="fake/model",
                revision="abc123",
                condition="frame",
                seed=17,
                max_new_tokens=32,
                git_commit="feedface",
            )

            metrics = run_counterfactual_generation(
                pairs_path=pairs_path,
                backend=FakeBackend(),
                config=config,
            )

            rows = [
                json.loads(line)
                for line in (config.output_dir / "generations.jsonl").read_text().splitlines()
            ]
            saved_config = json.loads((config.output_dir / "config.json").read_text())
            saved_metrics = json.loads((config.output_dir / "metrics.json").read_text())

            self.assertEqual([(row["pair_id"], row["variant"]) for row in rows], [
                ("esp-cf-v0-0001", "original"),
                ("esp-cf-v0-0001", "counterfactual"),
            ])
            self.assertEqual([row["assigned_strength"] for row in rows], ["possible", "likely"])
            self.assertEqual({row["source_item_id"] for row in rows}, {"esp-0001-00"})
            self.assertTrue(all(row["raw_output"] for row in rows))
            self.assertTrue(all("cue_preserved" in row["diagnostic"] for row in rows))
            self.assertEqual(saved_config["protocol"], "esp-counterfactual-v0")
            self.assertEqual(saved_config["pair_count"], 1)
            self.assertEqual(saved_config["generation_count"], 2)
            self.assertEqual(saved_config["dtype"], "float16")
            self.assertEqual(saved_config["git_commit"], "feedface")
            self.assertEqual(
                saved_config["pairs_sha256"],
                hashlib.sha256(pairs_path.read_bytes()).hexdigest(),
            )
            self.assertFalse(saved_config["do_sample"])
            self.assertEqual(saved_config["backend"], "HuggingFaceBackend")
            self.assertEqual(saved_config["tokenizer_revision"], "abc123")
            self.assertEqual(saved_metrics, metrics)
            self.assertEqual(saved_metrics["row_count"], 2)
            self.assertEqual(saved_metrics["pair_count"], 1)
            self.assertEqual(saved_metrics["cue_bin_preservation_rate"], 1.0)

    def test_prompts_preserve_frame_fields_without_leaking_labels(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pairs_path = temp_path / "pairs.jsonl"
            write_jsonl(pairs_path, [valid_pair()])
            backend = FakeBackend()

            run_counterfactual_generation(
                pairs_path=pairs_path,
                backend=backend,
                config=CounterfactualRunConfig(
                    output_dir=temp_path / "out",
                    model_path=Path("models/fake"),
                    model_id="fake/model",
                    revision="abc123",
                    condition="frame",
                    git_commit="feedface",
                ),
            )

            self.assertEqual(len(backend.prompts), 2)
            self.assertIn("STRENGTH=possible", backend.prompts[0])
            self.assertIn("STRENGTH=likely", backend.prompts[1])
            for prompt in backend.prompts:
                self.assertIn("ATTRIBUTION=authors", prompt)
                self.assertIn("SCOPE=The result reduces symptoms.", prompt)
                self.assertNotIn("condition", prompt.lower())
                self.assertNotIn("variant", prompt.lower())
                self.assertNotIn("original", prompt.lower())
                self.assertNotIn("counterfactual", prompt.lower())

    def test_rejects_empty_output_instead_of_writing_incomplete_pair(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pairs_path = temp_path / "pairs.jsonl"
            write_jsonl(pairs_path, [valid_pair()])
            output_dir = temp_path / "out"

            with self.assertRaisesRegex(ValueError, "empty output"):
                run_counterfactual_generation(
                    pairs_path=pairs_path,
                    backend=FakeBackend(["usable rewrite", "   "]),
                    config=CounterfactualRunConfig(
                        output_dir=output_dir,
                        model_path=Path("models/fake"),
                        model_id="fake/model",
                        revision="abc123",
                        condition="generic",
                        git_commit="feedface",
                    ),
                )

            self.assertFalse((output_dir / "generations.jsonl").exists())
            self.assertFalse((output_dir / "RUN_COMPLETE").exists())

    def test_rejects_non_empty_output_dir_before_generation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pairs_path = temp_path / "pairs.jsonl"
            write_jsonl(pairs_path, [valid_pair()])
            output_dir = temp_path / "out"
            output_dir.mkdir()
            (output_dir / "generations.jsonl").write_text("stale\n", encoding="utf-8")
            backend = FakeBackend()

            with self.assertRaisesRegex(ValueError, "non-empty output_dir"):
                run_counterfactual_generation(
                    pairs_path=pairs_path,
                    backend=backend,
                    config=CounterfactualRunConfig(
                        output_dir=output_dir,
                        model_path=Path("models/fake"),
                        model_id="fake/model",
                        revision="abc123",
                        condition="generic",
                        git_commit="feedface",
                    ),
                )

            self.assertEqual(backend.prompts, [])
            self.assertEqual(
                (output_dir / "generations.jsonl").read_text(encoding="utf-8"),
                "stale\n",
            )

    def test_rejects_unsupported_condition_before_generation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pairs_path = temp_path / "pairs.jsonl"
            write_jsonl(pairs_path, [valid_pair()])
            backend = FakeBackend()

            with self.assertRaisesRegex(ValueError, "condition"):
                run_counterfactual_generation(
                    pairs_path=pairs_path,
                    backend=backend,
                    config=CounterfactualRunConfig(
                        output_dir=temp_path / "out",
                        model_path=Path("models/fake"),
                        model_id="fake/model",
                        revision="abc123",
                        condition="direct",
                        git_commit="feedface",
                    ),
                )

            self.assertEqual(backend.prompts, [])


if __name__ == "__main__":
    unittest.main()
