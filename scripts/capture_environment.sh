#!/usr/bin/env bash
set -euo pipefail

output_dir="${1:?usage: capture_environment.sh OUTPUT_DIR}"
mkdir -p "$output_dir"

python --version >"$output_dir/python.txt" 2>&1
python -m pip freeze >"$output_dir/pip-freeze.txt"
uname -a >"$output_dir/uname.txt"
nvidia-smi -q >"$output_dir/nvidia-smi.txt"
git rev-parse HEAD >"$output_dir/git-commit.txt"
git status --short >"$output_dir/git-status.txt"
