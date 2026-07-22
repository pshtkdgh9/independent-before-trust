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
  local partial_dir="${output_dir}.partial"
  if [[ -e "$output_dir" ]]; then
    echo "Refusing to reuse existing output directory: $output_dir" >&2
    exit 1
  fi
  if [[ -e "$partial_dir" ]]; then
    echo "Refusing to reuse existing partial directory: $partial_dir" >&2
    exit 1
  fi
  local run_started_utc
  local git_commit
  run_started_utc="$(date --utc --iso-8601=seconds)"
  git_commit="$(git rev-parse HEAD)"
  mkdir -p "$partial_dir"
  .venv/bin/python scripts/run_esp_counterfactual.py \
    --pairs data/annotations/esp_counterfactual_pairs_v0.jsonl \
    --output-dir "$partial_dir" \
    --model-path "$model_path" \
    --model-id "$model_id" \
    --revision "$revision" \
    --git-commit "$git_commit" \
    --condition "$condition" \
    --seed 1701 \
    --max-new-tokens 96 \
    --dtype float16
  printf '%s\n' "$run_started_utc" >"$partial_dir/run-started-utc.txt"
  printf '%s\n' "$git_commit" >"$partial_dir/run-git-commit.txt"
  date --utc --iso-8601=seconds >"$partial_dir/run-completed-utc.txt"
  touch "$partial_dir/RUN_COMPLETE"
  mv "$partial_dir" "$output_dir"
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
