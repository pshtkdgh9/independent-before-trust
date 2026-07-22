# Quantity-Frame-Preserving Lay Summarization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an auditable two-corpus pilot that tests whether typed quantity-frame conditioning preserves value-to-denominator, comparator, subgroup, time-window, and unit bindings during lay summarization.

**Architecture:** A provenance-first acquisition layer pins raw public corpora; a deterministic candidate extractor retrieves quantity-bearing source/target pairs; a frozen schema and audit packet distinguish source-grounded frames from automatic candidates; a model runner compares direct, generic, extracted-frame, and oracle-frame conditions; and a validator applies a predeclared two-family kill gate. Natural-source fidelity and one-slot counterfactual equivariance remain separate evidence tracks.

**Tech Stack:** Python 3.10, standard-library dataclasses and JSONL, `pytest`, Hugging Face Hub HTTP artifacts, PyTorch 2.5, Transformers 4.43, CloudLab P100, Phi-3.5 Mini Instruct, Qwen2.5-1.5B Instruct.

---

## File structure

- Create `src/quantity_frame/schema.py` for immutable quantity frames, candidate records, and validation errors.
- Create `src/quantity_frame/provenance.py` for pinned-source manifests and license/redistribution checks.
- Create `src/quantity_frame/extract.py` for deterministic quantity-candidate retrieval only.
- Create `src/quantity_frame/counterfactual.py` for one-slot edits and invariant checks.
- Create `src/quantity_frame/prompts.py` for the four frozen generation conditions.
- Create `src/quantity_frame/metrics.py` for slot fidelity, unsupported-number rate, and paired equivariance.
- Create `src/quantity_frame/decision.py` for the predeclared source and GPU gates.
- Create matching focused tests under `tests/`.
- Create acquisition, construction, execution, validation, and CloudLab entry scripts under `scripts/`.
- Store machine-readable source records in `data_provenance/quantity_frame_manifest.jsonl` and generated audit artifacts under `results/strong_accept_loop/quantity_frame/`.

### Task 1: Pin and acquire the two public corpora

**Files:**
- Create: `src/quantity_frame/provenance.py`
- Create: `tests/test_quantity_frame_provenance.py`
- Create: `scripts/acquire_quantity_frame_sources.py`
- Create: `data_provenance/quantity_frame_manifest.jsonl`
- Modify: `results/strong_accept_loop/data_provenance.md`

- [ ] Write a failing test requiring `name`, `canonical_url`, `revision`, `license`, `license_url`, `accessed_utc`, `raw_path`, `bytes`, `sha256`, `download_command`, `redistribution`, and `intended_role`.

```python
def test_source_record_requires_reproducibility_fields():
    with pytest.raises(ProvenanceError, match="missing: revision"):
        SourceRecord.from_dict({"name": "cochrane"})
```

- [ ] Run `python -m pytest tests/test_quantity_frame_provenance.py -q` and verify failure because `src.quantity_frame` is absent.
- [ ] Implement a frozen `SourceRecord` and canonical SHA-256 validation.

```python
@dataclass(frozen=True)
class SourceRecord:
    name: str
    canonical_url: str
    revision: str
    license: str
    license_url: str
    accessed_utc: str
    raw_path: str
    bytes: int
    sha256: str
    download_command: str
    redistribution: str
    intended_role: str
```

- [ ] Resolve immutable Hugging Face commit SHAs for `GEM/cochrane-simplification` and `tomasg25/scientific_lay_summarisation`; record exact JSON artifact URLs rather than relying on remote loader execution.
- [ ] Download only the smallest development/validation files needed for prevalence estimation, writing to `data/raw/quantity_frame/<source>/<revision>/`; record exact byte counts and SHA-256 values.
- [ ] Run `python scripts/acquire_quantity_frame_sources.py --manifest data_provenance/quantity_frame_manifest.jsonl --verify-only` and require `verified_sources=2` with zero hash failures.
- [ ] Run the focused test and `git diff --check`.
- [ ] Commit only provenance code, tests, manifest records, and documentation with a Lore commit.

### Task 2: Define the quantity-frame schema

**Files:**
- Create: `src/quantity_frame/__init__.py`
- Create: `src/quantity_frame/schema.py`
- Create: `tests/test_quantity_frame_schema.py`

- [ ] Write failing tests for required `value` and `source_span`, explicit `not_stated` slots, normalized units, and rejection of inferred fields.

```python
def test_frame_preserves_missingness():
    frame = QuantityFrame(
        value="12", denominator_or_base="100 participants",
        subgroup=NOT_STATED, time_window="12 weeks",
        comparator="placebo", unit="percent", source_span="12 of 100 participants",
    )
    assert frame.subgroup is NOT_STATED
```

- [ ] Write failing tests requiring stable item IDs, source-record hashes, split names, and source/target text hashes without embedding retired-topic identifiers.
- [ ] Run `python -m pytest tests/test_quantity_frame_schema.py -q` and verify the tests fail.
- [ ] Implement frozen enums/dataclasses for `QuantityFrame`, `CandidateItem`, `SlotName`, and `NOT_STATED` serialization.
- [ ] Run the schema tests and require all pass.
- [ ] Commit schema and tests with a Lore commit.

### Task 3: Retrieve candidates without treating extraction as gold

**Files:**
- Create: `src/quantity_frame/extract.py`
- Create: `tests/test_quantity_frame_extract.py`
- Create: `scripts/build_quantity_frame_candidates.py`
- Create: `results/strong_accept_loop/quantity_frame/candidate_build.json`

- [ ] Write failing tests for percentages, fractions, counts, units, date/time windows, comparison cues, duplicate suppression, and deterministic source-order limits.

```python
@pytest.mark.parametrize("text", ["12 of 100 participants", "18% after 6 months", "3.2 mg versus 1.4 mg"])
def test_candidate_retrieval_finds_quantities(text):
    assert retrieve_candidates(text)
```

- [ ] Write a failing test proving the extractor emits `candidate_only=True` and never assigns an audit verdict.
- [ ] Run `python -m pytest tests/test_quantity_frame_extract.py -q` and verify failure.
- [ ] Implement conservative regex/token-window retrieval with deterministic ordering and explicit exclusion reasons.
- [ ] Build up to 300 candidates per corpus from development splits without inspecting model outcomes.
- [ ] Record rows read, candidates found, duplicates skipped, exclusions by reason, output bytes, SHA-256, command, and source revisions in `candidate_build.json`.
- [ ] Run focused tests, the builder twice, and compare output hashes for determinism.
- [ ] Commit extractor, tests, script, and build metadata; keep redistributability-restricted raw text out of Git.

### Task 4: Build a blinded source audit and enforce the pre-GPU gate

**Files:**
- Create: `src/quantity_frame/decision.py`
- Create: `tests/test_quantity_frame_source_gate.py`
- Create: `scripts/build_quantity_frame_audit.py`
- Create: `scripts/summarize_quantity_frame_audit.py`
- Create: `results/strong_accept_loop/quantity_frame/audit_packet.jsonl`
- Create: `results/strong_accept_loop/quantity_frame/source_gate.json`

- [ ] Write failing tests for opaque item IDs, hidden corpus/condition keys, document-disjoint overlap, and audit fields for frame validity plus every slot.
- [ ] Write failing tests for the exact source gate: at least 100 valid items across two corpora, at least 30 denominator/base cases, at least 30 comparator cases, and at least 60 valid one-slot counterfactual candidates.

```python
def test_source_gate_rejects_thin_comparator_support():
    result = evaluate_source_gate(valid=120, corpora=2, denominator=40, comparator=29, counterfactual=80)
    assert result.advance is False
    assert "comparator<30" in result.failures
```

- [ ] Run the focused tests and verify failure before implementation.
- [ ] Implement blinded packet construction and a deterministic summary that labels model-agent reviews as `model_agent_development_only` and `human_evidence=false`.
- [ ] Produce two independent development audits with an overlapping subset; report agreement by field and preserve raw disagreements.
- [ ] Run the summary and write `source_gate.json`; if it fails, document retirement and stop this topic before GPU.
- [ ] Commit the packet builder, summary, tests, and gate artifact without claiming human evidence.

### Task 5: Construct and validate one-slot counterfactuals

**Files:**
- Create: `src/quantity_frame/counterfactual.py`
- Create: `tests/test_quantity_frame_counterfactual.py`
- Create: `scripts/build_quantity_frame_counterfactuals.py`

- [ ] Write failing tests that exactly one slot changes and that topic, non-target facts, instruction, and opaque identifiers remain invariant.

```python
def test_denominator_edit_changes_one_slot_only():
    pair = build_pair(BASE_FRAME, slot="denominator_or_base", replacement="200 participants")
    assert pair.changed_slots == ("denominator_or_base",)
    assert pair.original.value == pair.counterfactual.value
```

- [ ] Write failing tests rejecting arithmetic inconsistency, clinical-direction changes through unrecorded slots, label leakage, and implausible edits.
- [ ] Run the focused tests and verify failure.
- [ ] Implement construction and validation without automatic semantic approval; generated pairs remain candidates until audited.
- [ ] Build only pairs admitted by the source audit, preserve original and counterfactual hashes, and rerun the audit summary.
- [ ] Commit counterfactual code, tests, and non-sensitive metadata.

### Task 6: Freeze generation conditions and metrics

**Files:**
- Create: `src/quantity_frame/prompts.py`
- Create: `src/quantity_frame/metrics.py`
- Create: `tests/test_quantity_frame_prompts.py`
- Create: `tests/test_quantity_frame_metrics.py`
- Create: `scripts/run_quantity_frame_pilot.py`
- Create: `scripts/validate_quantity_frame_artifacts.py`

- [ ] Write failing snapshot tests for direct, generic-preservation, extracted-frame, and oracle-frame prompts with equal source and output budgets.
- [ ] Write failing tests for slot accuracy, all-stated-slots exact match, denominator error, comparator error, unsupported-number rate, parse failure, and paired equivariance.

```python
def test_unsupported_number_rate_counts_unlicensed_values():
    assert unsupported_number_rate([{"source": {"12"}, "output": {"12", "99"}}]) == 1.0
```

- [ ] Run both focused test files and verify failure.
- [ ] Implement frozen prompts and metrics from raw outputs only; malformed structures count as failures.
- [ ] Implement dry-run fixtures for both model families without invoking a model.
- [ ] Run `python scripts/validate_quantity_frame_artifacts.py --dry-run` and require `status=pass`.
- [ ] Run all quantity-frame tests and commit prompts, runner, validator, and metrics.

### Task 7: Execute the two-family CloudLab pilot

**Files:**
- Create: `scripts/cloudlab_run_quantity_frame_pilot.sh`
- Create: `results/strong_accept_loop/quantity_frame/cloudlab_artifacts/<execution-commit>/`
- Modify: `README.md`
- Modify: `results/strong_accept_loop/reproducibility_checklist.md`

- [ ] Commit and push the exact execution state before model generation.
- [ ] In a clean CloudLab worktree, run the frozen 100-item slice for Phi and Qwen across all authorized non-oracle conditions; run oracle only when reviewed frames exist.
- [ ] Capture execution commit, model revisions, environment, configs, seeds, prompts, generations, parsed rows, metrics, timestamps, and `RUN_COMPLETE` markers.
- [ ] Allow long valid jobs to finish; rerun only documented infrastructure failures from the same commit/configuration.
- [ ] Pull artifacts into the execution-commit directory and run the validator locally.
- [ ] Require every planned cell to pass integrity; scientific metric failures remain valid negative results.
- [ ] Commit validated raw-output artifacts and reproducibility documentation.

### Task 8: Apply the immutable kill gate and update research state

**Files:**
- Create: `results/strong_accept_loop/quantity_frame/decision_summary.json`
- Create: `results/strong_accept_loop/quantity_frame/decision_summary.md`
- Modify: `results/strong_accept_loop/topic_search.md`
- Modify: `results/strong_accept_loop/topic_decision.md`
- Modify: `results/strong_accept_loop/status.md`
- Modify: `results/strong_accept_loop/evidence_map.md`
- Modify: `results/strong_accept_loop/experiment_plan.md`
- Modify: `results/strong_accept_loop/publication_ethics_boundary.md`

- [ ] Write a failing decision test for the exact gate: at least 10-point absolute combined denominator/comparator error reduction versus the strongest non-oracle baseline in each family; no component worsening; improved equivariance in both families; no worse unsupported-number rate or blinded lay usefulness; all integrity reports pass.
- [ ] Implement the decision calculation with no post-output threshold or parser changes.
- [ ] Generate machine-readable and prose summaries directly from validated metrics.
- [ ] If any gate fails, mark the candidate retired, keep all negative artifacts, and reopen topic search without favorable-family scaling.
- [ ] If every gate passes, mark only the pilot advance decision; keep headline manuscript claims unearned until claim-grade human and main-study evidence exist.
- [ ] Run `python -B -m pytest -q`, `git diff --check`, artifact validation, and a scan for conflict markers, placeholders, unsupported `human` labels, and RAG claims.
- [ ] Commit the decision and state updates with a Lore commit, then push the branch for audit.
