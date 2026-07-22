# Experiment Plan: Lineage-Aware Deliberation

## Research questions

- RQ1: With nominal agreement fixed, does common-source support cause different belief revision than independently sourced support?
- RQ2: Does lineage-aware aggregation outperform majority, confidence weighting, valid-evidence weighting, and simple deduplication?
- RQ3: Which factors—claim correctness, evidence validity, confidence, authority cue, paraphrase diversity, and order—interact with source dependence?
- RQ4: What accuracy, calibration, communication-cost, and parser-failure trade-offs hold across open model families?

## Paired intervention

Each instance contains a target agent's private answer and peer messages. A pair shares the same question, peer claims, correctness labels, confidence values, message order, and surface-length envelope. Only lineage differs:

- **COMMON:** peer messages ultimately derive from one evidence source.
- **INDEPENDENT:** peer messages are supported by distinct sources that independently entail the claim.

Source identifiers shown to the model use condition-neutral random labels. Surface forms are counterbalanced so condition cannot be inferred from naming or message length alone.

The private answer is elicited from the evaluated model in a separate no-peer prompt. It is never assigned by preprocessing. After that answer is frozen, an incorrect peer claim is used for initially correct items and the gold claim is used for initially incorrect items. This creates eligible harmful- and beneficial-revision strata without pretending that an injected answer is the model's belief.

## Protocols and baselines

1. Target agent without peer exposure.
2. Ordinary free-form peer exposure.
3. Majority vote.
4. Confidence-weighted aggregation.
5. Evidence-contract validation of claim/span support.
6. Exact source-ID deduplication.
7. Semantic claim deduplication without lineage.
8. LAD: atomic claim/source bindings, derivation-parent closure, effective independent-support count, and lineage-aware typed revision.

Ablations remove parent closure, counterbalanced source hiding, typed revision, confidence calibration, or dependence discounting.

## Tasks and data policy

Use at least three public, license-compatible structures: factual verification with attributable evidence; multi-hop reasoning with document provenance; and distributed-information reasoning. Dataset choice follows license and contamination checks. Dataset performance is not the contribution. If no retriever is run, supplied evidence contexts are never called RAG.

## Outcomes

- verified accuracy;
- harmful and beneficial revision;
- unjustified revision and justified non-revision;
- Brier score and expected calibration error;
- nominal support, effective support, and corroboration gap;
- evidence-grounded revision rate;
- tokens, wall time, messages, peak GPU memory;
- parser/lineage failures by condition.

## Models and hardware

- Pilot: `microsoft/Phi-3.5-mini-instruct`, pinned revision, MIT license, deterministic decoding.
- Main: two independently developed open-weight 7B–8B Hugging Face families, exact revisions/licenses pinned.
- Optional: quantized 14B robustness only after the pipeline is stable.
- CloudLab: Wisconsin d7525, one NVIDIA A30 24 GB, Ubuntu 22.04.
- Deterministic decoding for the primary comparison; seeded stochastic decoding only for planned robustness.

## Statistical plan

Primary estimands are paired differences in harmful and beneficial revision between COMMON and INDEPENDENT. Report paired bootstrap confidence intervals and effect sizes. Mixed-effects logistic regression is secondary, with task/model grouping and pre-specified interactions. Correct secondary comparison families and report all conditions and failures.

## Stages and stop rules

1. Unit tests with hand-authored lineage DAGs and mock responses.
2. Deterministic, explicitly non-empirical mock end-to-end pilot.
3. 50–100 instance open-model CloudLab pilot.
4. Kill/pivot decision from `topic_decision.md`.
5. Main paired runs, ablations, robustness, and stratified error analysis.

Long runs stop only for documented infrastructure failure, invalid configuration, a recorded resource bound, or a pre-registered futility/safety condition. Partial outputs remain logged.

## Claim limits

The study cannot establish human-like cognition, universal resistance to social influence, production security, or RAG reliability. Claims remain bounded to measured regimes. External paper values are contextual only.
