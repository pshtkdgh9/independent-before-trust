# Evidence Map

Only `SUPPORTED` claims may be stated as findings.

| ID | Headline claim | Status | Required comparison | Required artifacts | Current evidence | Known weakness |
|---|---|---|---|---|---|---|
| DCEA-C1 | Semantic citation support does not imply directional causal use of the cited evidence in tested generation regimes. | HYPOTHESIS | Matched original-versus-fact-replacement source pairs with citation-support and directional-response labels | task manifest, raw generations, citation labels, paired effects and CIs | None | The intervention must preserve fluency and avoid changing unrelated cues. |
| DCEA-C2 | Directional replacement detects evidence use that single-source removal misses under redundant support. | HYPOTHESIS | Singleton and redundant-support cells evaluated with replacement, removal, and likelihood-based LOO attribution | configs, token likelihoods, outputs, interaction table | None | Redundancy construction may be too synthetic unless replicated on natural paraphrases. |
| DCEA-C3 | An explicit contrastive evidence-use instruction improves directional grounding without reducing answer validity. | HYPOTHESIS | Ordinary citation prompting versus contrastive source-difference prompting under identical models and decoding | paired outputs, validity checks, ablation table, error analysis | None | Prompt-only gains may be brittle and cannot support a universal method claim. |

## Retired LAD evidence (audit only)

The validated Phi-3.5 run and diagnostic Qwen2.5 run directly tested the LAD hypothesis and did not justify continuing it. Phi harmful COMMON-minus-INDEPENDENT was `-0.04545` (CI `[-0.13636, 0]`) and beneficial was `+0.07143` (CI `[0, 0.17857]`). Qwen had 45 complete parsed pairs, zero harmful revisions, zero beneficial revisions, and five fixed-parser failures. These artifacts justify the documented topic pivot; they are not evidence for DCEA-C1--C3.

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
- `tests/`: 35 passing tests as of 2026-07-22, including private-first elicitation, paired invariants, condition-label leakage, bounded parsing, runner/validator normalization parity, tamper rejection, output schemas, and provenance checksums.

These LAD artifacts establish historical implementation readiness only. They do not change DCEA-C1--C3 from `HYPOTHESIS` to `SUPPORTED`.

## Interpretation rules

1. Prompt examples, mock outputs, and external paper numbers are not empirical evidence.
2. Failed parsing is reported by condition and included in sensitivity analysis.
3. Supplied evidence context is not called RAG unless retrieval is actually run end to end.
4. Negative or mixed results change claim status and manuscript framing.
5. Generalization is bounded to tested models, tasks, prompts, and transformations.
