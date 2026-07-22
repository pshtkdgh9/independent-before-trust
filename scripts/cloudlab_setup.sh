#!/usr/bin/env bash
set -euo pipefail

repo_dir="${1:-$PWD}"
venv_dir="${repo_dir}/.venv"

cd "$repo_dir"
python3 -m venv "$venv_dir"
source "$venv_dir/bin/activate"
python -m pip install --upgrade pip setuptools wheel

echo "Record nvidia-smi and choose the matching official PyTorch wheel before continuing."
echo "Then run: python -m pip install -r requirements-cloudlab.txt"
echo "Finally run: python -m unittest discover -s tests -v"
