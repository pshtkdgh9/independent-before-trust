#!/usr/bin/env bash
set -euo pipefail
repo_dir=${1:-/users/SangSong/clep-code}
output_root=${2:-/users/SangSong/clep-v2-pilot}
phi_path=${PHI_PATH:?set PHI_PATH}
qwen_path=${QWEN_PATH:?set QWEN_PATH}
cd "$repo_dir"
mkdir -p "$output_root"
for method in direct translate typed; do
  python scripts/run_clep_v2_pilot.py --output-dir "$output_root/phi-$method" --model-path "$phi_path" --model-id microsoft/Phi-3.5-mini-instruct --revision ccf028fc8e1b3ab750a7c55b22792f57ba69f216 --license MIT --method "$method"
  python scripts/run_clep_v2_pilot.py --output-dir "$output_root/qwen-$method" --model-path "$qwen_path" --model-id Qwen/Qwen2.5-1.5B-Instruct --revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 --license Apache-2.0 --method "$method"
done
git rev-parse HEAD > "$output_root/EXECUTION_COMMIT"
date -u +%FT%TZ > "$output_root/RUN_COMPLETE"
