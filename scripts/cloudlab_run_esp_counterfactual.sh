#!/usr/bin/env bash
set -e

repo_dir="${1:-$PWD}"
run_root="${2:-results/runs/esp-counterfactual-v0}"
cd "$repo_dir"

run_condition() {
  local label="$1"
  local model_path="$2"
  local model_id="$3"
  local revision="$4"
  local condition="$5"
  local output_dir="$run_root/$label-$condition"
  mkdir -p "$output_dir"
  date --utc --iso-8601=seconds >"$output_dir/run-started-utc.txt"
  git rev-parse HEAD >"$output_dir/run-git-commit.txt"
  .venv/bin/python scripts/run_esp_counterfactual.py \
    --pairs data/annotations/esp_counterfactual_pairs_v0.jsonl \
    --output-dir "$output_dir" \
    --model-path "$model_path" \
    --model-id "$model_id" \
    --revision "$revision" \
    --condition "$condition" \
    --seed 1701 \
    --max-new-tokens 96 \
    --dtype float16
  date --utc --iso-8601=seconds >"$output_dir/run-completed-utc.txt"
  touch "$output_dir/RUN_COMPLETE"
}

for condition in generic frame; do
  run_condition \
    esp-phi \
    models/phi-3.5-mini-instruct-ccf028f \
    microsoft/Phi-3.5-mini-instruct \
    ccf028fc8e1b3ab750a7c55b22792f57ba69f216 \
    "$condition"
done

for condition in generic frame; do
  run_condition \
    esp-qwen \
    models/qwen2.5-1.5b-instruct-989aa79 \
    Qwen/Qwen2.5-1.5B-Instruct \
    989aa7980e4cf806f80c7fef2b1adb7bc71aa306 \
    "$condition"
done
