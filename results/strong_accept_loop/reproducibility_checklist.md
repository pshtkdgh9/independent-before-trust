# Reproducibility Checklist

## Already present

- [x] Durable research state and decision history
- [x] Topic-search and 28-work novelty records
- [x] Publication-ethics and overlap boundaries
- [x] Local reference file sizes and SHA-256 hashes
- [x] Deterministic lineage core tests
- [x] Deterministic revision-metric tests
- [x] CloudLab bootstrap and test scripts
- [x] Machine-readable pilot config, raw-generation, metric, and provenance schemas
- [x] Parser failures retained and reported by condition
- [x] Pinned-snapshot download and file-level checksum tooling
- [x] Paired item-resampling analysis with a fixed bootstrap seed and replicate count
- [x] Version-controlled CloudLab RSpec with an explicit physical GPU node type and image

## Required before pilot

- [x] Dataset source, version, license/terms, checksum, download/preprocessing commands
- [x] Pilot model source, immutable revision, license, chat-template path, dtype/quantization arguments
- [ ] `nvidia-smi`, OS, Python, CUDA, PyTorch, Transformers, and driver record
- [x] Machine-readable run config and output schemas
- [x] Versioned pilot prompt and deterministic primary revision metrics
- [x] Pilot sample construction log and invariant validation

## Required before submission

- [ ] Exact main, ablation, robustness, and figure/table commands
- [ ] Random seeds and deterministic-control notes
- [ ] Runtime, token, GPU-memory, and compute totals
- [ ] All raw generations retained or release restrictions documented
- [ ] Parser failures and excluded records enumerated
- [x] Statistical analysis code is integrated into the pilot metrics artifact; empirical-value regeneration remains pending the run
- [ ] Tables/figures regenerate from immutable result artifacts
- [ ] Anonymous supplement contains no identity-leaking paths or URLs
- [ ] Clean-room run from a fresh environment succeeds
