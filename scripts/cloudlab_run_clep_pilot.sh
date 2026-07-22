#!/usr/bin/env bash
set -euo pipefail

repo_dir=${1:-/users/SangSong/independent-before-trust}
output_root=${2:-/users/SangSong/clep-pilot}
phi_path=${PHI_PATH:-/users/SangSong/models/microsoft--Phi-3.5-mini-instruct/ccf028fc8e1b3ab750a7c55b22792f57ba69f216}
qwen_path=${QWEN_PATH:-/users/SangSong/models/Qwen--Qwen2.5-1.5B-Instruct/989aa7980e4cf806f80c7fef2b1adb7bc71aa306}

cd "$repo_dir"
commit=$(git rev-parse HEAD)
mkdir -p "$output_root"

for method in direct translate typed; do
  python scripts/run_clep_pilot.py --output-dir "$output_root/phi-$method" --model-path "$phi_path" --model-id microsoft/Phi-3.5-mini-instruct --revision ccf028fc8e1b3ab750a7c55b22792f57ba69f216 --license MIT --method "$method"
  python scripts/run_clep_pilot.py --output-dir "$output_root/qwen-$method" --model-path "$qwen_path" --model-id Qwen/Qwen2.5-1.5B-Instruct --revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 --license Apache-2.0 --method "$method"
done
printf '%s\n' "$commit" > "$output_root/EXECUTION_COMMIT"
date -u +%FT%TZ > "$output_root/RUN_COMPLETE"
