#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH="$1"
MODEL_ID="$2"
REVISION="$3"
ITEMS="$4"
ANNOTATIONS="$5"
OUTPUT_ROOT="$6"

for condition in direct generic frame; do
  python scripts/run_esp_pilot.py \
    --items "$ITEMS" \
    --annotations "$ANNOTATIONS" \
    --output-dir "$OUTPUT_ROOT/$condition" \
    --model-path "$MODEL_PATH" \
    --model-id "$MODEL_ID" \
    --revision "$REVISION" \
    --condition "$condition"
done
