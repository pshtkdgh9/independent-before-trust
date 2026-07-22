# Evidence-State Triage Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, validate, run, and gate a paired evidence-state triage policy that chooses `clarify`, `retrieve`, or `abstain` while leaving answer generation downstream.

**Architecture:** A schema layer represents query, evidence pack, evidence state, and required action. A deterministic intervention builder constructs licensed paired variants for insufficiency and conflict. Baselines and the state-aware router emit only triage actions; an integrity validator reconstructs invariants and metrics from raw artifacts before any decision gate is applied.

**Tech Stack:** Python 3.10, `unittest`, JSONL, deterministic hashing, existing Hugging Face backend, CloudLab GPU runner.

---

## Verification Note

Commands that target future files in this plan are implementation-time commands and cannot be fully verified before those files exist. The repository-level command `python -m unittest discover -s tests -v` is the current executable verification command.

## File Structure

- Create: `src/evidence_state/__init__.py` - package exports for schema, interventions, baselines, and metrics.
- Create: `src/evidence_state/schema.py` - immutable records and validation for evidence states and actions.
- Create: `src/evidence_state/interventions.py` - paired intervention construction and invariant checks.
- Create: `src/evidence_state/baselines.py` - prompt rendering and parser logic for direct, clarify, retrieve, abstain, and state-aware router outputs.
- Create: `src/evidence_state/metrics.py` - macro-F1, selective risk, directional flip, and false-answer leakage metrics.
- Create: `scripts/build_evidence_state_pilot.py` - licensed-source pilot builder.
- Create: `scripts/run_evidence_state_triage.py` - deterministic local or CloudLab generation runner.
- Create: `scripts/validate_evidence_state_artifacts.py` - integrity validator that reconstructs all counts and hashes from raw artifacts.
- Create: `tests/test_evidence_state_schema.py` - schema and action validation tests.
- Create: `tests/test_evidence_state_interventions.py` - paired intervention invariant tests.
- Create: `tests/test_evidence_state_baselines.py` - prompt and parser tests.
- Create: `tests/test_evidence_state_metrics.py` - metric and kill-gate tests.
- Create: `data/processed/evidence-state-pilot-v0/items.jsonl` - generated only after license and checksum records exist.
- Create: `results/strong_accept_loop/evidence_state_triage/` - raw outputs, configs, validation reports, and analysis summaries.

### Task 1: Schema and Action Contract

**Files:**
- Create: `src/evidence_state/__init__.py`
- Create: `src/evidence_state/schema.py`
- Create: `tests/test_evidence_state_schema.py`

- [ ] Write failing tests for allowed states `sufficient`, `insufficient`, and `conflict`; allowed actions `clarify`, `retrieve`, and `abstain`; unique item IDs; non-empty query text; non-empty evidence packs; and rejection of answer text in the primary prediction field.
- [ ] Run `python -m unittest tests.test_evidence_state_schema -v` and confirm the tests fail because the package does not exist.
- [ ] Implement frozen dataclasses or equivalent immutable records for source records, evidence snippets, item variants, and router decisions.
- [ ] Re-run `python -m unittest tests.test_evidence_state_schema -v` and confirm the tests pass.
- [ ] Commit only the schema and tests with a Lore message.

### Task 2: Licensed-Source Pilot Construction

**Files:**
- Create: `scripts/build_evidence_state_pilot.py`
- Create after verification: `data/processed/evidence-state-pilot-v0/items.jsonl`
- Modify only if needed: `results/strong_accept_loop/data_provenance.md`
- Test: `tests/test_evidence_state_schema.py`

- [ ] Select one public source corpus only after recording license, source URL, revision if available, bytes, checksum, preprocessing command, and storage path.
- [ ] Write failing tests that reject pilot rows without provenance IDs, license IDs, source checksums, or allowed redistribution flags.
- [ ] Run `python -m unittest tests.test_evidence_state_schema -v` and confirm the new provenance tests fail.
- [ ] Implement a deterministic builder that emits only schema-valid JSONL rows and records excluded rows with reasons.
- [ ] Run the builder on a small fixed sample and inspect row counts without making any empirical claim.
- [ ] Re-run schema tests and `python -m unittest discover -s tests -v`.
- [ ] Commit the builder, tests, and provenance records.

### Task 3: Paired Intervention Validator

**Files:**
- Create: `src/evidence_state/interventions.py`
- Create: `tests/test_evidence_state_interventions.py`

- [ ] Write failing tests for `sufficient -> insufficient`, `sufficient -> conflict`, and `insufficient -> conflict` pairs.
- [ ] Add tests that reject changed query wording, changed answer target, changed source-ID envelope, missing edit rationale, and non-minimal edits without an explicit exclusion reason.
- [ ] Run `python -m unittest tests.test_evidence_state_interventions -v` and confirm failure before implementation.
- [ ] Implement pair construction and validation with deterministic hashes for each base item and variant.
- [ ] Re-run intervention tests and the full test suite.
- [ ] Commit the validator and tests.

### Task 4: Prompt and Router Baselines

**Files:**
- Create: `src/evidence_state/baselines.py`
- Create: `tests/test_evidence_state_baselines.py`

- [ ] Write failing tests that every baseline returns exactly one action label and no downstream answer text in the primary field.
- [ ] Add parser tests for case variants, whitespace, malformed JSON, multiple labels, and attempts to answer instead of triage.
- [ ] Run `python -m unittest tests.test_evidence_state_baselines -v` and confirm failure before implementation.
- [ ] Implement prompt renderers for direct answer-or-abstain, selective QA confidence, ambiguity-aware clarification, adaptive retrieval, conflict-aware RAG, oracle-state diagnostic, and the proposed state-aware router.
- [ ] Implement a strict parser that stores malformed outputs instead of repairing them silently.
- [ ] Re-run baseline tests and the full test suite.
- [ ] Commit the baseline layer.

### Task 5: CloudLab Runner

**Files:**
- Create: `scripts/run_evidence_state_triage.py`
- Create on execution: `results/strong_accept_loop/evidence_state_triage/<run_id>/config.json`
- Create on execution: `results/strong_accept_loop/evidence_state_triage/<run_id>/generations.jsonl`
- Create on execution: `results/strong_accept_loop/evidence_state_triage/<run_id>/run-started-utc.txt`
- Create on execution: `results/strong_accept_loop/evidence_state_triage/<run_id>/run-completed-utc.txt`
- Test: `tests/test_evidence_state_baselines.py`

- [ ] Write failing tests for config completeness, deterministic decoding fields, model revision fields, condition-blind output rows, and raw-response retention.
- [ ] Run the runner tests and confirm failure before implementation.
- [ ] Implement the runner using the existing Hugging Face backend pattern without modifying retired LAD, DCEA, CLEP, or ESP artifacts.
- [ ] Run a one-item smoke test locally or on CloudLab and preserve raw output even if parsing fails.
- [ ] Commit the runner before any full CloudLab execution.

### Task 6: Integrity Validator

**Files:**
- Create: `scripts/validate_evidence_state_artifacts.py`
- Create on execution: `results/strong_accept_loop/evidence_state_triage/<run_id>/integrity-report.json`
- Test: `tests/test_evidence_state_metrics.py`

- [ ] Write failing tests that tampering with config, item hashes, prompt hashes, row counts, action labels, or model IDs causes validation failure.
- [ ] Run `python -m unittest tests.test_evidence_state_metrics -v` and confirm failure before implementation.
- [ ] Implement a validator that reconstructs all metrics from raw `generations.jsonl` plus frozen input items.
- [ ] Ensure parse failures are counted by state, action, model family, and baseline rather than dropped.
- [ ] Re-run validator tests and the full test suite.
- [ ] Commit the integrity validator.

### Task 7: Analysis and Kill Gate

**Files:**
- Create: `src/evidence_state/metrics.py`
- Create on execution: `results/strong_accept_loop/evidence_state_triage/<run_id>/metrics.json`
- Create on execution: `results/strong_accept_loop/evidence_state_triage/<run_id>/gate-decision.json`
- Test: `tests/test_evidence_state_metrics.py`

- [ ] Write failing tests for macro-F1, selective risk by insufficiency and conflict, directional action flips, false-answer rate, two-family aggregation, and exact kill-gate logic.
- [ ] Run metric tests and confirm failure before implementation.
- [ ] Implement metrics and the gate: advance only when macro-F1 beats the strongest baseline, selective risk beats the strongest baseline separately for insufficiency and conflict, predicted directional flips exceed 50%, two open model families pass, and false-answer rate is no worse.
- [ ] Add tests that each individual failed condition produces `advance=false`.
- [ ] Re-run metric tests and the full test suite.
- [ ] Commit the analysis layer.

### Task 8: Documentation and Audit Updates

**Files:**
- Modify: `results/strong_accept_loop/status.md`
- Modify: `results/strong_accept_loop/topic_search.md`
- Modify: `results/strong_accept_loop/topic_decision.md`
- Modify: `results/strong_accept_loop/research_scan.md`
- Modify: `results/strong_accept_loop/experiment_plan.md`
- Modify: `results/strong_accept_loop/evidence_map.md`
- Modify: `results/strong_accept_loop/publication_ethics_boundary.md`

- [ ] Update status only after artifacts exist; do not describe hypotheses as findings.
- [ ] Record verified licenses, checksums, source URLs, model revisions, and commands only after they are actually verified.
- [ ] Map every claim to a required artifact and leave it `HYPOTHESIS` until the gate passes.
- [ ] Run `git diff --check`.
- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Commit documentation updates with Lore trailers.

## Self-Review

- Spec coverage: the plan covers schema, licensed-source pilot construction, paired intervention validation, prompt/router baselines, CloudLab execution, integrity validation, analysis/gating, and documentation.
- Placeholder scan: no task uses `TBD`, `TODO`, or an unspecified "add tests" instruction.
- Type consistency: state labels and action labels match the design spec: `sufficient`, `insufficient`, `conflict`, `clarify`, `retrieve`, and `abstain`.
