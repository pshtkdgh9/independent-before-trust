# Evidence-State Triage Router Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and evaluate a paired causal router that chooses `proceed`, `retrieve`, or `abstain` before a fixed downstream answerer under sufficient, insufficient, and conflicting evidence states.

**Architecture:** A provenance-first item builder creates paired evidence-state records from public licensed sources and rejects unauditable items. A deterministic router runner evaluates two open model families against fixed action-capable and final-output baselines, then a validator computes macro-F1, selective risk, directional paired flips, coverage, sufficient/proceed answer exactness, and false-answer rate from raw outputs. CloudLab execution is allowed only from an immutable commit after local TDD checks pass.

**Tech Stack:** Python 3.10, `unittest`, JSONL, PyTorch, Transformers, CloudLab GPU node, repository-local artifact validators.

---

## File structure

- Create: `src/evidence_state/__init__.py` for public package exports.
- Create: `src/evidence_state/schema.py` for immutable records, labels, and validation errors.
- Create: `src/evidence_state/provenance.py` for source license/provenance validation.
- Create: `src/evidence_state/builder.py` for deterministic paired-item construction.
- Create: `src/evidence_state/router.py` for prompt rendering, route parsing, and downstream answer control.
- Create: `src/evidence_state/metrics.py` for macro-F1, selective risk, paired flips, and false-answer rate.
- Create: `tests/test_evidence_state_schema.py`.
- Create: `tests/test_evidence_state_provenance.py`.
- Create: `tests/test_evidence_state_builder.py`.
- Create: `tests/test_evidence_state_router.py`.
- Create: `tests/test_evidence_state_metrics.py`.
- Create: `scripts/build_evidence_state_items.py`.
- Create: `scripts/run_evidence_state_router.py`.
- Create: `scripts/validate_evidence_state_artifacts.py`.
- Create: `scripts/cloudlab_run_evidence_state_router.sh`.
- Create: `data/evidence_state/source_manifest.jsonl`.
- Create: `data/annotations/evidence_state_pairs_v0.jsonl`.
- Create: `results/strong_accept_loop/evidence_state_triage/`.

### Task 1: Define evidence-state schema

**Files:**
- Create: `src/evidence_state/__init__.py`
- Create: `src/evidence_state/schema.py`
- Create: `tests/test_evidence_state_schema.py`

- [ ] Write failing tests for allowed evidence states: `sufficient`, `insufficient`, and `conflict`.
- [ ] Write failing tests for allowed router actions: `proceed`, `retrieve`, and `abstain`.
- [ ] Write failing tests for the gold action mapping: `sufficient` -> `proceed`, `insufficient` -> `retrieve`, and `conflict` -> `abstain`.
- [ ] Write failing tests that require each pair to preserve the same question and change only the evidence state.
- [ ] Run `python -m unittest tests.test_evidence_state_schema -v` and confirm the new tests fail because the package is absent.
- [ ] Implement frozen dataclasses or typed records with deterministic validation errors.
- [ ] Re-run `python -m unittest tests.test_evidence_state_schema -v` and confirm all schema tests pass.
- [ ] Commit the schema and tests with Lore trailers.

### Task 2: Enforce public licensed-data provenance

**Files:**
- Create: `src/evidence_state/provenance.py`
- Create: `tests/test_evidence_state_provenance.py`
- Create: `data/evidence_state/source_manifest.jsonl`

- [ ] Write failing tests requiring `source_name`, `source_url`, `license_or_terms_url`, `retrieved_utc`, `raw_record_hash`, `transform_script`, `derived_item_hash`, and `redistributable_text`.
- [ ] Write failing tests rejecting rows copied from old manuscript artifacts, retired experiment outputs, unpublished review packets, or unlabeled JSONL files.
- [ ] Run `python -m unittest tests.test_evidence_state_provenance -v` and confirm provenance validation is absent.
- [ ] Implement provenance validation that rejects missing license data and records a specific exclusion reason.
- [ ] Populate `data/evidence_state/source_manifest.jsonl` only with public licensed or citeable sources selected for this method test.
- [ ] Re-run `python -m unittest tests.test_evidence_state_provenance -v` and confirm all provenance tests pass.
- [ ] Commit the provenance validator, manifest, and tests.

### Task 3: Build paired causal items

**Files:**
- Create: `src/evidence_state/builder.py`
- Create: `tests/test_evidence_state_builder.py`
- Create: `scripts/build_evidence_state_items.py`
- Create: `data/annotations/evidence_state_pairs_v0.jsonl`

- [ ] Write failing tests for insufficiency pairs that remove or restore one necessary premise while preserving the question and expecting a `proceed` -> `retrieve` flip.
- [ ] Write failing tests for conflict pairs that retain the supporting sentence, insert or remove one incompatible evidence sentence, preserve all non-target context, and expect a `proceed` -> `abstain` flip.
- [ ] Write failing tests for sufficient controls with a stable answer target and no artificial uncertainty cues.
- [ ] Run `python -m unittest tests.test_evidence_state_builder -v` and confirm the builder is absent.
- [ ] Implement deterministic pair construction with stable IDs, item hashes, source links, and expected directional flips.
- [ ] Run `python scripts/build_evidence_state_items.py --manifest data/evidence_state/source_manifest.jsonl --output data/annotations/evidence_state_pairs_v0.jsonl`.
- [ ] Re-run `python -m unittest tests.test_evidence_state_builder -v` and confirm item-contract tests pass.
- [ ] Commit the builder, generated paired items, and tests.

### Task 4: Implement router and downstream answer control

**Files:**
- Create: `src/evidence_state/router.py`
- Create: `tests/test_evidence_state_router.py`
- Create: `scripts/run_evidence_state_router.py`

- [ ] Write failing tests that route output must parse to exactly one of `proceed`, `retrieve`, or `abstain`.
- [ ] Write failing tests that the downstream answerer is called only after `proceed` or after a completed retrieval path, and is never called directly for `abstain`.
- [ ] Write failing tests that retrieval-needed cases record a `retrieve` action before any downstream final answer is produced or scored.
- [ ] Run `python -m unittest tests.test_evidence_state_router -v` and confirm the router is absent.
- [ ] Implement prompt rendering, route parsing, deterministic decoding config capture, and downstream answer gating.
- [ ] Add two open model-family configurations, initially `phi` and `qwen`, with exact checkpoints pinned in config output at runtime.
- [ ] Re-run `python -m unittest tests.test_evidence_state_router -v` and confirm router tests pass.
- [ ] Commit the router, runner, and tests.

### Task 5: Implement baselines and metrics

**Files:**
- Create: `src/evidence_state/metrics.py`
- Create: `tests/test_evidence_state_metrics.py`
- Modify: `scripts/run_evidence_state_router.py`
- Create: `scripts/validate_evidence_state_artifacts.py`

- [ ] Write failing tests for direct answerer, always-answer, conflict-cue abstain, answerability-only, prompt-only triage, action-capable router, and final-output baselines.
- [ ] Write failing tests for macro-F1 over all action labels.
- [ ] Write failing tests for coverage as the rate of `proceed` actions.
- [ ] Write failing tests for final-answer exactness on sufficient/proceed cases.
- [ ] Write failing tests for selective risk computed separately for insufficiency and conflict.
- [ ] Write failing tests for directional paired flips and false-answer rate.
- [ ] Run `python -m unittest tests.test_evidence_state_metrics -v` and confirm metric implementation is absent.
- [ ] Implement metrics from raw rows only, with no model-judge-only primary endpoint.
- [ ] Implement strongest-baseline selection from observed baseline results, separating action-capable baselines for action metrics from final-output baselines for answer safety metrics.
- [ ] Re-run `python -m unittest tests.test_evidence_state_metrics -v` and confirm all metric tests pass.
- [ ] Commit baselines, metrics, validator, and tests.

### Task 6: Run local validation

**Files:**
- Modify only files created or modified by Tasks 1-5.

- [ ] Run `python -m unittest tests.test_evidence_state_schema tests.test_evidence_state_provenance tests.test_evidence_state_builder tests.test_evidence_state_router tests.test_evidence_state_metrics -v`.
- [ ] Run `python scripts/validate_evidence_state_artifacts.py --items data/annotations/evidence_state_pairs_v0.jsonl --dry-run`.
- [ ] Run `git diff --check`.
- [ ] Confirm `git status --short` contains no unrelated staged files and no modified old manuscript artifacts.
- [ ] Commit local validation fixes, if any, with Lore trailers.

### Task 7: Execute CloudLab run

**Files:**
- Create: `scripts/cloudlab_run_evidence_state_router.sh`
- Create: `results/strong_accept_loop/evidence_state_triage/cloudlab_artifacts/<execution-commit>/`

- [ ] Commit and push the exact execution state before starting CloudLab.
- [ ] Run the CloudLab script for both open model families and all baselines.
- [ ] Capture `RUN_COMPLETE`, run timestamps, execution commit, environment, configs, raw generations, route rows, baseline rows, and validation JSON.
- [ ] Do not stop long valid GPU jobs for convenience.
- [ ] Pull artifacts into `results/strong_accept_loop/evidence_state_triage/cloudlab_artifacts/<execution-commit>/`.
- [ ] Run the artifact validator against pulled CloudLab outputs.
- [ ] Commit CloudLab artifacts and validation reports.

### Task 8: Apply the strict kill gate

**Files:**
- Create: `results/strong_accept_loop/evidence_state_triage/decision_summary.json`
- Create: `results/strong_accept_loop/evidence_state_triage/decision_summary.md`

- [ ] Select the strongest action-capable baseline from observed macro-F1 results.
- [ ] Select the strongest final-output baseline from observed selective-risk and false-answer results.
- [ ] Confirm the router beats the strongest action-capable baseline on macro-F1.
- [ ] Confirm the router beats the strongest final-output baseline on selective risk for insufficiency.
- [ ] Confirm the router beats the strongest final-output baseline on selective risk for conflict.
- [ ] Confirm `proceed` -> `retrieve` directional paired flips are greater than 50%.
- [ ] Confirm `proceed` -> `abstain` directional paired flips are greater than 50%.
- [ ] Confirm false-answer rate is no worse than the strongest final-output baseline.
- [ ] Retire the method if any gate fails; do not convert a failed method test into a benchmark claim.
- [ ] Run `git diff --check` and the evidence-state unit tests before the final commit.
- [ ] Commit the decision summary with Lore trailers.
