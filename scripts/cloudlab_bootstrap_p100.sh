#!/usr/bin/env bash
set -euo pipefail

repo_dir="${1:-$PWD}"
cd "$repo_dir"

sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install torch==2.5.1 \
  --index-url https://download.pytorch.org/whl/cu121
.venv/bin/python -m pip install -r requirements-cloudlab.txt

.venv/bin/python - <<'PY'
import torch

print(f"torch={torch.__version__}")
print(f"torch_cuda={torch.version.cuda}")
print(f"cuda_available={torch.cuda.is_available()}")
if not torch.cuda.is_available():
    raise SystemExit("CUDA is not available after PyTorch installation")
print(f"device={torch.cuda.get_device_name(0)}")
print(f"capability={torch.cuda.get_device_capability(0)}")
PY

.venv/bin/python -m unittest discover -s tests -v
PATH="$repo_dir/.venv/bin:$PATH" \
  bash scripts/capture_environment.sh results/runs/phi35-pilot/environment-postinstall
touch results/runs/phi35-pilot/SETUP_COMPLETE
