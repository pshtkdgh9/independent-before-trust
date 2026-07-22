#!/usr/bin/env bash
set -euo pipefail

repo_dir="${1:-$PWD}"
cd "$repo_dir"

run_dir="${2:-results/runs/phi35-pilot}"
mkdir -p "$run_dir"
date --utc --iso-8601=seconds >"$run_dir/run-started-utc.txt"
git rev-parse HEAD >"$run_dir/run-git-commit.txt"

.venv/bin/python scripts/download_public_file.py \
  --url https://raw.githubusercontent.com/google/BIG-bench/092b196c1f8f14a54bbc62f24759d43bde46dd3b/bigbench/benchmark_tasks/logical_deduction/five_objects/task.json \
  --destination data/raw/bigbench/092b196c/logical_deduction_five_objects.json \
  --artifact-type dataset-source \
  --name google/BIG-bench:logical_deduction/five_objects \
  --revision 092b196c1f8f14a54bbc62f24759d43bde46dd3b \
  --license Apache-2.0 \
  --terms-url https://github.com/google/BIG-bench/blob/092b196c1f8f14a54bbc62f24759d43bde46dd3b/LICENSE \
  --expected-sha256 552dec4d5067bdbe033e78e80fdf1f5a8061d17b385379b8ec5104fa17d07918

.venv/bin/python scripts/build_bigbench_pilot.py \
  --input data/raw/bigbench/092b196c/logical_deduction_five_objects.json \
  --output data/processed/lad-pilot-v1/items.jsonl \
  --provenance-log results/strong_accept_loop/provenance_logs/bigbench_logical_deduction_preprocessing.json \
  --source-url https://raw.githubusercontent.com/google/BIG-bench/092b196c1f8f14a54bbc62f24759d43bde46dd3b/bigbench/benchmark_tasks/logical_deduction/five_objects/task.json \
  --revision 092b196c1f8f14a54bbc62f24759d43bde46dd3b \
  --seed 1701 \
  --limit 50

.venv/bin/python scripts/prepare_hf_model.py \
  --model-id microsoft/Phi-3.5-mini-instruct \
  --revision ccf028fc8e1b3ab750a7c55b22792f57ba69f216 \
  --license MIT \
  --terms-url https://huggingface.co/microsoft/Phi-3.5-mini-instruct/blob/ccf028fc8e1b3ab750a7c55b22792f57ba69f216/LICENSE \
  --output-dir models/phi-3.5-mini-instruct-ccf028f

.venv/bin/python scripts/run_cloudlab_pilot.py \
  --items data/processed/lad-pilot-v1/items.jsonl \
  --output-dir "$run_dir" \
  --model-path models/phi-3.5-mini-instruct-ccf028f \
  --model-id microsoft/Phi-3.5-mini-instruct \
  --revision ccf028fc8e1b3ab750a7c55b22792f57ba69f216 \
  --license MIT \
  --seed 1701 \
  --max-new-tokens 64 \
  --dtype float16 \
  --trust-remote-code

date --utc --iso-8601=seconds >"$run_dir/run-completed-utc.txt"
touch "$run_dir/RUN_COMPLETE"
