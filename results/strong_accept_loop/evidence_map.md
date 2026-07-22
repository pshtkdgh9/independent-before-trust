# Evidence Map

Only `SUPPORTED` claims may be stated as findings.

| ID | Headline claim | Status | Required comparison | Required artifacts | Current evidence | Known weakness |
|---|---|---|---|---|---|---|
| C1 | Source dependence changes harmful and beneficial revision when nominal agreement is fixed. | HYPOTHESIS | Paired COMMON vs INDEPENDENT with content/correctness/confidence/order/agent count controlled | pair manifest, generations, metrics, bootstrap CI | Validated Phi-3.5 one-task pilot: harmful difference `-0.04545` CI `[-0.13636, 0]`; beneficial `+0.07143` CI `[0, 0.17857]`; anticipated direction not supported | One model/task; intervals touch zero; point estimates weakly favor COMMON. |
| C2 | LAD reduces duplicated-evidence amplification relative to majority, confidence-, and evidence-weighted baselines. | HYPOTHESIS | LAD vs debate, vote, confidence, evidence contract, exact/semantic deduplication | configs, outputs, effect sizes, ablations | None | Exact deduplication may match LAD. |
| C3 | Effective independent support exposes failures hidden by nominal consensus and citation validity. | HYPOTHESIS | Stratified analysis with citation validity fixed | diagnostic figure, statistical model, examples | None | Association is not causal without the paired intervention. |

## Artifact contracts

- `data_provenance/manifest.jsonl`: immutable source/model/data records.
- `data/processed/<version>/items.jsonl`: source-derived questions without injected target answers.
- `results/runs/<run_id>/baseline_generations.jsonl`: actual private answers elicited before peer exposure.
- `results/runs/<run_id>/pairs.jsonl`: runtime paired interventions built around the fixed private answer.
- `results/runs/<run_id>/config.json`: model/prompt/seed configuration.
- `results/runs/<run_id>/generations.jsonl`: raw responses and parser outcomes.
- `results/runs/<run_id>/metrics.json`: deterministic metrics.
- `results/strong_accept_loop/statistics/`: paired intervals and model outputs.
- `paper/tables/` and `paper/figures/`: generated only from recorded results.

## Current tooling evidence (not finding evidence)

- `src/lad/pilot.py`: elicits actual private answers, constructs and validates complete pairs, counterbalances execution order, renders condition-label-blind prompts, retains raw responses and parse errors, and computes deterministic condition summaries.
- `src/lad/provenance.py`: records per-file bytes and SHA-256 for pinned model snapshots.
- `scripts/prepare_hf_model.py` and `scripts/run_cloudlab_pilot.py`: executable download/provenance and inference paths.
- `src/lad/validation.py` and `scripts/validate_pilot_artifacts.py`: independently reviewed integrity path that reconstructs parsing, correctness, prompt hashes, support, condition summaries, and paired effects from raw artifacts.
- `tests/`: 34 passing tests as of 2026-07-22, including private-first elicitation, paired invariants, condition-label leakage, bounded parsing, tamper rejection, output schemas, and provenance checksums.

These artifacts establish implementation readiness only. They do not change C1--C3 from `HYPOTHESIS` to `SUPPORTED`.

## Interpretation rules

1. Prompt examples, mock outputs, and external paper numbers are not empirical evidence.
2. Failed parsing is reported by condition and included in sensitivity analysis.
3. Supplied evidence context is not called RAG unless retrieval is actually run end to end.
4. Negative or mixed results change claim status and manuscript framing.
5. Generalization is bounded to tested models, tasks, prompts, and transformations.
