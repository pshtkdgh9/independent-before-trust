# Lineage-Aware Deliberation

This repository is the independent research workspace for an EACL 2027 / later ACL-family submission on source dependence in language-agent deliberation. The central question is whether repeated evidence derived from one source is mistaken for independent corroboration.

The repository contains no supported empirical headline result yet. Current claims in `results/strong_accept_loop/evidence_map.md` are hypotheses.

## Local verification

```bash
python -m unittest discover -s tests -v
```

## CloudLab target

- Wisconsin `d7525`
- Ubuntu 22.04
- one NVIDIA A30 24 GB
- Python 3.10+

After cloning, run `bash scripts/cloudlab_setup.sh`. Record `nvidia-smi`, OS, Python, and CUDA details before installing the PyTorch wheel recommended by the official PyTorch selector. Then install `requirements-cloudlab.txt` and run the tests.

The first ungated pilot model is `microsoft/Phi-3.5-mini-instruct` under the MIT license. Always download an immutable revision and checksum the local snapshot:

```bash
python scripts/download_public_file.py \
  --url https://raw.githubusercontent.com/google/BIG-bench/092b196c1f8f14a54bbc62f24759d43bde46dd3b/bigbench/benchmark_tasks/logical_deduction/five_objects/task.json \
  --destination data/raw/bigbench/092b196c/logical_deduction_five_objects.json \
  --artifact-type dataset-source \
  --name google/BIG-bench:logical_deduction/five_objects \
  --revision 092b196c1f8f14a54bbc62f24759d43bde46dd3b \
  --license Apache-2.0 \
  --terms-url https://github.com/google/BIG-bench/blob/092b196c1f8f14a54bbc62f24759d43bde46dd3b/LICENSE \
  --expected-sha256 552dec4d5067bdbe033e78e80fdf1f5a8061d17b385379b8ec5104fa17d07918
python scripts/build_bigbench_pilot.py \
  --input data/raw/bigbench/092b196c/logical_deduction_five_objects.json \
  --output data/processed/lad-pilot-v1/items.jsonl \
  --provenance-log results/strong_accept_loop/provenance_logs/bigbench_logical_deduction_preprocessing.json \
  --source-url https://raw.githubusercontent.com/google/BIG-bench/092b196c1f8f14a54bbc62f24759d43bde46dd3b/bigbench/benchmark_tasks/logical_deduction/five_objects/task.json \
  --revision 092b196c1f8f14a54bbc62f24759d43bde46dd3b \
  --seed 1701 --limit 50
bash scripts/capture_environment.sh results/runs/phi35-pilot/environment
python scripts/prepare_hf_model.py \
  --model-id microsoft/Phi-3.5-mini-instruct \
  --revision ccf028fc8e1b3ab750a7c55b22792f57ba69f216 \
  --license MIT \
  --terms-url https://huggingface.co/microsoft/Phi-3.5-mini-instruct/blob/ccf028fc8e1b3ab750a7c55b22792f57ba69f216/LICENSE \
  --output-dir models/phi-3.5-mini-instruct-ccf028f
python scripts/run_cloudlab_pilot.py \
  --items data/processed/lad-pilot-v1/items.jsonl \
  --output-dir results/runs/phi35-pilot \
  --model-path models/phi-3.5-mini-instruct-ccf028f \
  --model-id microsoft/Phi-3.5-mini-instruct \
  --revision ccf028fc8e1b3ab750a7c55b22792f57ba69f216 \
  --license MIT \
  --trust-remote-code
python scripts/validate_pilot_artifacts.py \
  --run-dir results/runs/phi35-pilot \
  --output results/runs/phi35-pilot/integrity-report.json
```

`run_cloudlab_pilot.py` first elicits each model's actual private answer, then constructs a matched COMMON/INDEPENDENT pair around that fixed answer. It retains baseline generations, runtime pair manifests, revision responses, and parser failures. Outputs are labeled `empirical-candidate-unverified`; they become evidence only after provenance, invariant, and analysis validation.

Do not add a Hugging Face token to the repository. Use `huggingface-cli login` only when a selected model requires account acceptance, and prefer models downloadable without gated credentials.

## Research integrity

- The already-submitted journal paper is not reused as manuscript text, claims, results, or evidence.
- Local reference PDFs are background material only and are inventoried under `results/strong_accept_loop/reference_inventory.tsv`.
- New public datasets/models must be recorded with URL, license/terms, revision, bytes, checksum, command, preprocessing, and storage path before use.
- Supplied evidence context is not described as RAG unless a retriever is run and evaluated end to end.
