#!/usr/bin/env bash
set -euo pipefail

repo_dir="${1:-$PWD}"
run_root="${2:-results/runs/dcea-pilot}"
cd "$repo_dir"

run_model() {
  local label="$1"
  local model_path="$2"
  local model_id="$3"
  local revision="$4"
  local license_name="$5"
  local mode="$6"
  local output_dir="$run_root/$label-$mode"
  local contrastive_flag=()
  if [[ "$mode" == "contrastive" ]]; then
    contrastive_flag=(--contrastive)
  fi
  mkdir -p "$output_dir"
  date --utc --iso-8601=seconds >"$output_dir/run-started-utc.txt"
  git rev-parse HEAD >"$output_dir/run-git-commit.txt"
  .venv/bin/python scripts/run_dcea_pilot.py \
    --output-dir "$output_dir" \
    --model-path "$model_path" \
    --model-id "$model_id" \
    --revision "$revision" \
    --license "$license_name" \
    --seed 1701 \
    --max-new-tokens 48 \
    --dtype float16 \
    "${contrastive_flag[@]}"
  date --utc --iso-8601=seconds >"$output_dir/run-completed-utc.txt"
  touch "$output_dir/RUN_COMPLETE"
}

for mode in ordinary contrastive; do
  run_model \
    phi35 \
    models/phi-3.5-mini-instruct-ccf028f \
    microsoft/Phi-3.5-mini-instruct \
    ccf028fc8e1b3ab750a7c55b22792f57ba69f216 \
    MIT \
    "$mode"
  run_model \
    qwen25 \
    models/qwen2.5-1.5b-instruct-989aa79 \
    Qwen/Qwen2.5-1.5B-Instruct \
    989aa7980e4cf806f80c7fef2b1adb7bc71aa306 \
    Apache-2.0 \
    "$mode"
done
