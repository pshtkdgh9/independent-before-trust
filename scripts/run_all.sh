#!/usr/bin/env bash
set -euo pipefail

python -m unittest discover -s tests -v
python -m src.lad.mock_pilot --output-dir results/mock_pilot

echo "Unit tests and non-empirical mock pipeline completed."
echo "No empirical result is produced by this command."
