# Data Provenance Register

## Quantity-frame source acquisition

This records source acquisition only for the provisional Quantity-Frame-Preserving Lay Summarization candidate paper. No preprocessing, prevalence estimate, benchmark result, model run, or experimental claim is made from these records. Machine-readable manifest: `data_provenance/quantity_frame_manifest.jsonl`.

| Item | Value |
|---|---|
| Name | GEM/cochrane-simplification validation |
| Canonical repository | <https://huggingface.co/datasets/GEM/cochrane-simplification> |
| Exact artifact URL | <https://huggingface.co/datasets/GEM/cochrane-simplification/resolve/75a92ae445171fa1b7641a229bfe3c77c0d8723d/validation.json> |
| Immutable revision | `75a92ae445171fa1b7641a229bfe3c77c0d8723d` |
| License / terms | CC BY 4.0; <https://creativecommons.org/licenses/by/4.0/> |
| Access date | 2026-07-23 |
| Raw storage path | `data/raw/quantity_frame/cochrane-simplification/75a92ae445171fa1b7641a229bfe3c77c0d8723d/validation.json` |
| Bytes / SHA-256 | `1,538,508` / `18c883a77ff20f718b71c05251146d9648022f277cd4dc345b43820cd6ba2d5f` |
| Download command | `python scripts/acquire_quantity_frame_sources.py --manifest data_provenance/quantity_frame_manifest.jsonl` |
| Preprocessing status | None |
| Privacy / consent | Public biomedical review summaries; no private clinical notes or patient records are expected |
| Redistribution | Metadata, scripts, and hashes may be tracked; raw corpus files remain Git-ignored and should be fetched from the pinned public source with CC BY 4.0 attribution |
| Known risks | Validation-only acquisition is not a representative corpus analysis; no claim should cite it until a separate preprocessing and sampling plan is executed |

| Item | Value |
|---|---|
| Name | tomasg25/scientific_lay_summarisation eLife validation |
| Canonical repository | <https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation> |
| Exact artifact URL | <https://drive.usercontent.google.com/download?id=1WKW8BAqluOlXrpy1B9mV3j3CtAK3JdnE&export=download&authuser=1&confirm=t&uuid=1332bc11-7cbf-4c4d-8561-85621060f397&at=APZUnTVLLKAGVSBpQlYKojrJ57xb%3A1716450570186> |
| Immutable source locator | <https://huggingface.co/datasets/tomasg25/scientific_lay_summarisation/resolve/9e109befb07bfb993843991d09b8aa6ee40b9267/scientific_lay_summarisation.py> |
| Immutable revision | `9e109befb07bfb993843991d09b8aa6ee40b9267` |
| License / terms | Dataset card reports CC BY 4.0; <https://creativecommons.org/licenses/by/4.0/> |
| Access date | 2026-07-23 |
| Raw storage path | `data/raw/quantity_frame/scientific_lay_summarisation/9e109befb07bfb993843991d09b8aa6ee40b9267/elife_val.json` |
| Bytes / SHA-256 | `16,023,867` / `24fe7b98f04d2e6e5a80dda26ba241d5742de0f02c9e13a33121cabd98e9aeed` |
| Download command | `python scripts/acquire_quantity_frame_sources.py --manifest data_provenance/quantity_frame_manifest.jsonl` |
| Preprocessing status | None |
| Privacy / consent | Public scholarly articles and expert-written lay summaries; no private clinical notes or patient records are expected |
| Redistribution | Metadata, scripts, hashes, and acquisition command may be tracked; raw corpus files remain Git-ignored and should be fetched from the public source with CC BY 4.0 attribution |
| Known risks | The immutable HF repository exposes a loader that points to a Google Drive bulk archive rather than a split-level URL. This task downloaded that archive only to extract `val.json`; the raw archive itself remains Git-ignored and is not a claimed analysis artifact |

## FEVER evidence-state source acquisition

| Item | Value |
|---|---|
| Name | FEVER wiki pages archive |
| Source URL | <https://fever.ai/download/fever/wiki-pages.zip> |
| Dataset card / revision | <https://huggingface.co/datasets/EleutherAI/fever/tree/85ebc1eaacc6b6bf0d54719c942b7aad097a1abd> |
| CloudLab archive path | `/users/SangSong/evidence-state-data/raw/fever/wiki-pages.zip` |
| Downloaded | 2026-07-23 |
| Archive bytes / SHA-256 | `1,713,485,474` / `4b06d95da6adf7fe02d2796176c670dacccb21348da89cba4c50676ab99665f2` |
| Download command | `curl -L --fail --retry 5 -C - https://fever.ai/download/fever/wiki-pages.zip -o /users/SangSong/evidence-state-data/raw/fever/wiki-pages.zip` |
| Extraction command | `unzip -q .../wiki-pages.zip -d .../wiki-pages` |
| Extracted path | `/users/SangSong/evidence-state-data/raw/fever/wiki-pages` |
| Extracted size | Approximately `7.2G`; this is not an exact byte count |
| Extracted file count | 221 files |
| File checksum manifest / file count path | `/users/SangSong/evidence-state-data/raw/fever/wiki-pages.files.sha256` |
| Extracted aggregate checksum | Not recorded; no extracted aggregate checksum is asserted |
| License/terms | FEVER Hugging Face pinned revision `85ebc1eaacc6b6bf0d54719c942b7aad097a1abd` tags `cc-by-sa-3.0` and `gpl-3.0`; underlying Wikipedia text is CC BY-SA 3.0 |
| Redistribution boundary | Attribution and share-alike obligations apply. Derived Wikipedia text must not be redistributed unless the CC BY-SA 3.0 boundary is satisfied |
| Experimental claim status | Source acquisition only; no benchmark claim is made |

### FEVER candidate source pack

| Item | Value |
|---|---|
| Name | FEVER candidate source pack |
| Status | Candidate material only; not a benchmark result, evidence result, or headline result, and not yet paired with gold data |
| Generated on | CloudLab |
| Source Git commit | `d3750f87a9b1628b5a529dc4b369d9a816e09a58` |
| Exact command | `python scripts/extract_fever_source_pack.py --claims data/raw/fever/paper_dev.jsonl --wiki-dir /users/SangSong/evidence-state-data/raw/fever/wiki-pages/wiki-pages --output /users/SangSong/evidence-state-data/fever_candidate_source_pack.jsonl --limit 120 --seed 0` |
| Source rows read | 9,999 |
| Duplicate claims skipped | 256 |
| Candidate references retained | 4,186 |
| Candidate rows available | 4,151 |
| Rows written | 120 |
| Local path | `data/evidence_state/fever_candidate_source_pack.jsonl` |
| Bytes / SHA-256 | `101,910` / `967c9996bf3a871d96d4a6d66376461404dfbb890d8fb4ff68eec5d81f7290e8` |
| Redistribution boundary | Exact source text retains the CC BY-SA attribution/share-alike boundary |

## ESP retired corpus and artifact provenance

| Item | Value |
|---|---|
| Name | BioLaySumm 2025 eLife validation and blind-test Parquet splits |
| Canonical repository | <https://huggingface.co/datasets/BioLaySumm/BioLaySumm2025-eLife> |
| Immutable revision | `144e9c785e3a309da804eb6786feb38e6596f390` |
| Upstream corpus paper | Goldsack et al., EMNLP 2022, <https://aclanthology.org/2022.emnlp-main.724/> |
| License/terms | Underlying eLife articles and summaries are CC BY 4.0 according to the corpus paper; the Hugging Face dataset card does not expose a separate license field, so that packaging ambiguity is retained rather than silently normalized |
| Access date | 2026-07-22 |
| Validation raw path | `data/raw/biolaysumm-elife/144e9c78/validation-00000-of-00001.parquet` |
| Validation bytes / SHA-256 | `6,921,124` / `6a64c7cd2b93fd74601f93cd620bd063c7acd5a7e5daf12c4a4eda22d20390f4` |
| Blind-test raw path | `data/raw/biolaysumm-elife/144e9c78/test-00000-of-00001.parquet` |
| Blind-test bytes / SHA-256 | `3,274,608` / `00b9fe32d05d013d21d4796986ef030b72f8f9302827a97c94303a130c7ee0e3` |
| Raw storage policy | Git-ignored; recoverable from immutable URLs and commands recorded in `data_provenance/manifest.jsonl` |
| Preprocessing command | `python scripts/build_esp_pilot.py --input data/raw/biolaysumm-elife/144e9c78/validation-00000-of-00001.parquet --output data/processed/esp-pilot-v0/items.jsonl --limit 40 --source-revision 144e9c785e3a309da804eb6786feb38e6596f390` |
| Processed result | 40 fixed-lexicon frames from 31 validation documents; `188,002` bytes; SHA-256 `8d77925b026492a3a81b411beaf7281a9cda65dbe01752b12dd5eea52cc06da9` |
| Selection | Source order; abstract section only; first occurrences of a frozen conservative cue lexicon; no outcome-dependent filtering |
| Privacy/consent | Public scholarly articles and editor/author lay summaries; no private clinical notes or patient records |
| Redistribution | Do not redistribute the HF Parquet packaging until its card-level terms are clarified; release scripts, hashes, IDs, and derived annotations where attribution and source terms permit |
| Known risks | Cue matching is candidate retrieval, not gold scope annotation; the validation split is used only for method development; the blind-test summaries are empty and cannot be used for reference-based claims |

The two downloads were checksum-verified against their Git-LFS object hashes. The blind test was inspected only to establish its schema and absence of reference summaries; it was not used to tune or score the method. Human-reviewed scope labels and a document-disjoint evaluation split were never completed before ESP retirement, and no ESP finding is promoted.

### ESP CloudLab feasibility artifacts

The six deterministic cells ran on 2026-07-22 from Git commit `beca9cc32f9082985535d24fdcbb2cea1199267e` with `torch==2.5.1+cu121`, `transformers==4.43.0`, NVIDIA driver `535.309.01`, and one Tesla P100 12 GB. Each directory contains `config.json`, `generations.jsonl`, and `metrics.json`; all have 38 outputs and no empty recorded generation. The Git-tracked audit location is `results/strong_accept_loop/cloudlab_artifacts/esp-pilot-beca9cc/`.

| Run | Total bytes | generations SHA-256 |
|---|---:|---|
| `esp-phi-direct` | 60,017 | `91aa0ade20a72ffb1e2411cf9b673df73a409246adc53e86da10fb3069de662f` |
| `esp-phi-generic` | 63,051 | `fb893f32293c081c9661c59e72a9036b30ad25456e0ca9e0e219b9c828f9756e` |
| `esp-phi-frame` | 68,139 | `dcfe8fb46bf14f5ce34f1e0593cecab12db4ec10bc6de2a5fab9e91419541221` |
| `esp-qwen-direct` | 62,114 | `689708f820aa045ec8db7d906941c87beaf87ba48e71d9e5cab0cf0b029f76c9` |
| `esp-qwen-generic` | 62,891 | `e8d96cd95f2a3134c6583f9fe131974f6308fb343b2fd0ec5c609f0045111036` |
| `esp-qwen-frame` | 68,846 | `6aab8aeb762f18f61bdaaf438706c9292ff97dee05686e72fb0c8330a580f402` |

The blind packet, hidden condition key, two model-agent audits, and deterministic summary are stored in `esp_output_reviews/`. They are derived evaluation artifacts and may be released with the code subject to the upstream text redistribution boundary above. They are explicitly not human annotations.

### ESP counterfactual review artifact

The natural-text counterfactual gate is recorded at `results/strong_accept_loop/esp_counterfactual/review_summary_v1.json`. It contains 112 model-agent review rows across Phi and Qwen generic/frame comparisons. It records `evidence_class=model_agent_development_only` and `human_evidence=false`; no human annotation or adjudication artifact exists for this gate.

The review summary records Phi as advancing and Qwen as not advancing; the combined gate is `advance=false`. This artifact is provenance for the decision to retire ESP and reopen topic search. It is not provenance for a supported ESP claim.

## CLEP provisional data boundary

No external CLEP dataset has been acquired yet. The first controlled pilot will use newly authored minimal propositions and independently checked English/Korean/Spanish parallel realizations. These are method-development fixtures, not a released benchmark and not sufficient for a headline generalization claim. Before any public corpus is downloaded, this file must record source URL, revision/version, visible license or terms, acquisition time, compressed and extracted sizes, SHA-256 checksums, exact preprocessing command, output location, and redistribution boundary.

The LAD BIG-bench data and all DCEA synthetic templates are excluded from CLEP effect estimates. Generic immutable-run, hashing, and validation utilities may be reused as tooling only.

The retired LAD pilot source and both pinned model snapshots are recorded below. The new DCEA falsification pilot uses newly authored synthetic controlled facts and reuses only the already recorded model snapshots; no result has yet been promoted to evidence. The local reference inventory remains checksummed in `reference_inventory.tsv`.

## DCEA controlled pilot material

| Item | Value |
|---|---|
| Name | DCEA hand-authored controlled facts v0 |
| Source | `src/dcea/fixtures.py` at the execution Git commit |
| External download | None |
| License/terms | Original project material; release intended with repository license, which must be finalized before public release |
| Records | 20 templates, each expanded deterministically into original/counterfactual by singleton/redundant cells |
| Construction | Fictional entities and values authored for this experiment; no real-world factual claim is intended |
| Filtering | None after authorship; tests require unique item IDs, distinct intervention values, and unique source IDs |
| Privacy/consent | No persons, user data, or private data |
| Redistribution | Intended; repository-level license is still a release gate |
| Derived artifacts | Per-run `templates.jsonl`, `generations.jsonl`, `metrics.json`, and `config.json` |
| Known risk | Synthetic phrasing may overestimate control and underrepresent natural-document variation; it is a falsification pilot, not main generalization evidence |

The exact transformation is implemented in `src/dcea/core.py`; `scripts/run_dcea_pilot.py` serializes the expanded templates and raw model outputs. The study does not call these materials a benchmark. If the controlled mechanism survives, a separate natural-text replication will require its own source URL, immutable revision, license, checksum, preprocessing record, and contamination analysis.

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
