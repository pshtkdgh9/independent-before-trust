# ESP Counterfactual Equivariance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, validate, run, and audit a natural-text counterfactual test of epistemic-strength equivariance for generic versus frame-conditioned lay rewriting.

**Architecture:** A deterministic manifest builder consumes separately authored pair edits and rejects contract violations. The existing Hugging Face backend runs four model-by-prompt cells. A validator reconstructs counts and hashes from raw outputs; blinded review remains separate from the condition key.

**Tech Stack:** Python 3.10, `unittest`, JSONL, PyTorch 2.5.1, Transformers 4.43.0, CloudLab P100.

---

### Task 1: Freeze pair schema and validation

**Files:**
- Create: `src/esp/counterfactual.py`
- Modify: `tests/test_esp.py`

- [ ] Write failing tests for unique IDs, adjacent-bin transitions, identical proposition skeletons, one declared edit span, and rejection of polarity or argument changes.
- [ ] Run `python -m unittest tests.test_esp -v` and confirm the new tests fail because the validator is absent.
- [ ] Implement immutable pair records plus deterministic validation with explicit error messages.
- [ ] Re-run the targeted tests and confirm they pass.

### Task 2: Author and independently audit natural pairs

**Files:**
- Create: `data/annotations/esp_counterfactual_pairs_v0.jsonl`
- Create: `results/strong_accept_loop/esp_counterfactual/pair_audit_a.jsonl`
- Create: `results/strong_accept_loop/esp_counterfactual/pair_audit_b.jsonl`
- Create: `results/strong_accept_loop/esp_counterfactual/pair_agreement.json`

- [ ] Author candidate minimal pairs from the 38 valid natural scopes without reading model outputs.
- [ ] Have two isolated development auditors label grammaticality, proposition invariance, polarity, argument preservation, and edit validity.
- [ ] Retain only exact-agreement valid pairs and require at least 12; otherwise fire the kill gate.
- [ ] Record exclusions and reiterate that model-agent audits are not human evidence.

### Task 3: Implement deterministic paired generation

**Files:**
- Create: `scripts/run_esp_counterfactual.py`
- Create: `scripts/cloudlab_run_esp_counterfactual.sh`
- Modify: `tests/test_esp.py`

- [ ] Write failing tests that require two variants per pair, condition-blind raw rows, frozen seed/decoding, and complete configs.
- [ ] Implement prompts using existing `render_rewrite_prompt` and `HuggingFaceBackend` without changing the feasibility-run artifacts.
- [ ] Confirm tests pass and `git diff --check` is clean.
- [ ] Commit and push the runner before CloudLab execution so the execution commit is immutable.

### Task 4: Run and validate four CloudLab cells

**Files:**
- Create: `results/strong_accept_loop/cloudlab_artifacts/esp-counterfactual-v0/`
- Create: `scripts/validate_esp_counterfactual.py`

- [ ] Run Phi generic, Phi frame, Qwen generic, and Qwen frame sequentially on the existing CloudLab node.
- [ ] Preserve every raw output; never terminate a valid long cell for convenience.
- [ ] Recompute row counts, pair completeness, diagnostic cue bins, config fields, and hashes independently.
- [ ] Pull artifacts to the commit-named audit directory.

### Task 5: Blind semantic review and decision

**Files:**
- Create: `results/strong_accept_loop/esp_counterfactual/blind_packet.jsonl`
- Create: `results/strong_accept_loop/esp_counterfactual/blind_key.jsonl`
- Create: `results/strong_accept_loop/esp_counterfactual/development_summary.json`
- Modify: `results/strong_accept_loop/status.md`
- Modify: `results/strong_accept_loop/evidence_map.md`
- Modify: `results/strong_accept_loop/experiment_plan.md`
- Modify: `results/strong_accept_loop/data_provenance.md`

- [ ] Build a packet that hides model, prompt condition, and variant identity while retaining the two target strength labels required for paired semantic judgment.
- [ ] Apply the frozen v1 rubric independently; treat model-agent labels as development calibration only.
- [ ] Compute paired equivariance by family and condition, agreement, additions, copying, readability, and failures.
- [ ] Apply the predeclared advance/retire rule without hiding negative results or strengthening claims beyond evidence.
- [ ] Run the full test suite, `git diff --check`, commit with Lore trailers, and push.
