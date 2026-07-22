# Data Provenance Register

One pilot source has been downloaded and transformed. The pinned model snapshot has been downloaded on CloudLab and a compatibility-fixed inference run is in progress, but no result has been promoted to evidence. The local reference inventory remains checksummed in `reference_inventory.tsv`.

## Pilot dataset

| Item | Value |
|---|---|
| Name | BIG-bench `logical_deduction/five_objects` |
| Canonical repository | <https://github.com/google/BIG-bench> |
| Exact source URL | <https://raw.githubusercontent.com/google/BIG-bench/092b196c1f8f14a54bbc62f24759d43bde46dd3b/bigbench/benchmark_tasks/logical_deduction/five_objects/task.json> |
| Immutable revision | `092b196c1f8f14a54bbc62f24759d43bde46dd3b` |
| License/terms | Apache-2.0; <https://github.com/google/BIG-bench/blob/092b196c1f8f14a54bbc62f24759d43bde46dd3b/LICENSE> |
| Access timestamp | `2026-07-22T07:24:01.837228+00:00` |
| Raw path | `data/raw/bigbench/092b196c/logical_deduction_five_objects.json` |
| Raw bytes | 305,889 |
| Raw SHA-256 | `552dec4d5067bdbe033e78e80fdf1f5a8061d17b385379b8ec5104fa17d07918` |
| Processed path | `data/processed/lad-pilot-v1/items.jsonl` |
| Processed records | 50 private-first items selected from 100 unique scenarios / 500 source examples |
| Processed bytes | 35,141 |
| Processed SHA-256 | `6d4af279528c92518c92032c62cf4ead91fc7e0bcf1059b3f53e1c2533cdf407` |
| Detailed preprocessing record | `results/strong_accept_loop/provenance_logs/bigbench_logical_deduction_preprocessing.json` |
| Privacy/consent | Synthetic object-order reasoning; no personal data expected |
| Redistribution | Derived items/runtime pairs may be released with upstream Apache-2.0 attribution and notices |

Preprocessing preserves source order, groups identical scenario text, selects one rotating target item per unique scenario, and performs no content filtering. It does not inject a target-model initial answer: that answer is elicited at runtime before pair construction. The exact commands are recorded in the machine-readable manifest/log and in `README.md`.

Known risk: BIG-bench intentionally carries a benchmark canary and is likely represented in contemporary model training corpora. Therefore this task is a pipeline and causal-intervention pilot, not evidence of unseen-task generalization. Main experiments require additional task families and explicit contamination sensitivity analysis.

## Pilot model

| Item | Value |
|---|---|
| Model | `microsoft/Phi-3.5-mini-instruct` |
| Canonical source | <https://huggingface.co/microsoft/Phi-3.5-mini-instruct> |
| Immutable revision | `ccf028fc8e1b3ab750a7c55b22792f57ba69f216` |
| Visible license | MIT |
| License source | <https://huggingface.co/microsoft/Phi-3.5-mini-instruct/blob/ccf028fc8e1b3ab750a7c55b22792f57ba69f216/LICENSE> |
| Access checked | 2026-07-22 |
| Status | Downloaded on CloudLab; file-level manifest imported to `cloudlab_artifacts/cloudlab-manifest.jsonl` |
| Intended role | 50-instance feasibility pilot, not a sole main-experiment model |

The exact download command is in `README.md`. `scripts/prepare_hf_model.py` records every downloaded file, byte size, SHA-256 checksum, storage path, source URL, revision, license, terms URL, and command in `data_provenance/manifest.jsonl`. Model weights remain outside Git and are not redistributed.

The imported snapshot record reports `7,644,702,568` total bytes. The two weight shards are `4,972,489,328` bytes (SHA-256 `c5214cdb995ed3dd716add8d9efbfe016b76bb2f1c4c1e6c1c6a95497d7a8837`) and `2,669,692,552` bytes (SHA-256 `41246eed2b75b66526339c5d32d6f7acdefe0bd24180f97c74303f4656877344`). Every other snapshot file and Hugging Face metadata file is enumerated in the imported manifest.

## Second-family replication model

| Item | Value |
|---|---|
| Model | `Qwen/Qwen2.5-1.5B-Instruct` |
| Canonical source | <https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct> |
| Immutable revision | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| Visible license | Apache-2.0 |
| License source | <https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/989aa7980e4cf806f80c7fef2b1adb7bc71aa306/LICENSE> |
| Selection reason | Independently developed family; permissive license; float16 weights fit the allocated P100 |
| Status | Downloaded and file-hashed on CloudLab; imported manifest at `cloudlab_artifacts/cloudlab-manifest-qwen.jsonl` |

The second-family experiment repeats the identical 50-item intervention, seed, decoding, and parser. It is a model-family replication for the predeclared kill/pivot decision, not an opportunistic search for a positive result.

The imported snapshot record reports `3,098,974,477` total bytes. The weight file `model.safetensors` is `3,087,467,144` bytes with SHA-256 `dd924a11b4c220f385b51ffa522daea7c9f3d850e31b162bb5661df483c6d3ee`; the upstream license file is `11,343` bytes with SHA-256 `832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e`. The manifest enumerates every snapshot and Hugging Face metadata file. Model weights are not redistributed.

## CloudLab pilot hardware allocation

The original Wisconsin `d7525` request failed because the portal reported zero allocatable nodes. No scientific computation occurred in that attempt. The replacement experiment requests one Wisconsin `c240g5` through the version-controlled `cloudlab/lad-c240g5.rspec`. The official hardware manual describes this type as one Tesla P100 12 GB GPU, 20 Intel Skylake CPU cores, and 192 GB RAM. Because P100 does not provide the planned A30 bfloat16 regime, the pilot uses `--dtype float16`; this is a documented infrastructure pivot, not a post-result analysis choice. CloudLab assigned node `c240g5-110121` with hostname `c240g5-110121.wisc.cloudlab.us`. The captured environment records Ubuntu 22.04.2, kernel `5.15.0-177-generic`, NVIDIA driver `535.309.01`, CUDA compatibility `12.2`, `torch==2.5.1+cu121`, and P100 compute capability `(6, 0)`. See `cloudlab_attempts.md`.

## Local reference material

| Material | Role | Source/access | License/terms | Integrity | Redistribution | Experimental evidence? |
|---|---|---|---|---|---|---|
| 15 PDFs in `Reference Paper/` | Topic-search background only | User-provided local files; access date 2026-07-22 | To be verified paper-by-paper before quotation or redistribution | Byte sizes and SHA-256 in `reference_inventory.tsv` | Not redistributed | No |
| Extracted text in `outputs/work/extracted/` | Search aid derived locally from the PDFs | Generated locally; extraction command to be recorded | Inherits source-paper restrictions | Checksums pending | Not for release unless terms permit | No |

## Required record for each future dataset/model

Every added item must record: canonical source URL; access timestamp; visible license/terms and version; original filename; byte size; SHA-256; raw storage path; exact download command; exact preprocessing command; filtering/deduplication decisions; split construction; privacy/consent concerns; redistribution status; derived artifacts; and the claims/tables that consume it.

Hugging Face model records must additionally pin repository revision/commit, tokenizer revision, model license, quantization, dtype, inference library versions, chat template, generation parameters, and local cache policy.

## Planned storage convention

- Immutable downloads: `data/raw/<source>/<version>/`
- Processed data: `data/processed/<study_version>/`
- Machine-readable manifest: `data_provenance/manifest.jsonl`
- Download/preprocessing logs: `results/strong_accept_loop/provenance_logs/`
- Large files: excluded from Git and represented by manifests/checksums; released only when the source terms allow.
