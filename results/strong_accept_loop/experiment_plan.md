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
- Main: two independently developed open-weight families that fit the recorded hardware regime, exact revisions/licenses pinned.
- Optional: quantized 14B robustness only after the pipeline is stable.
- CloudLab pilot: Wisconsin `c240g5`, one Tesla P100 12 GB, Ubuntu 22.04, after the requested `d7525` was unavailable.
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

## Phi-3.5 pilot outcome

The integrity-validated 50-item logical-deduction pilot produced 100 complete paired revisions with no parse failures. It did not support the anticipated LAD direction: COMMON-minus-INDEPENDENT harmful revision was `-0.04545` with paired bootstrap interval `[-0.13636, 0]`, while beneficial revision was `+0.07143` with interval `[0, 0.17857]`. The result is bounded to one model, one task, and one prompt protocol. Per the predeclared kill rule, the next experiment is a same-protocol replication on a second independently developed open model family; a second non-supporting result triggers a topic pivot rather than selective scaling.

## Qwen2.5 replication and LAD stop decision

At exact execution commit `0db697f`, `Qwen/Qwen2.5-1.5B-Instruct` revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` ran the same 50-item input, seed, decoding, prompt, parser, and COMMON/INDEPENDENT construction. Three private outputs were not parseable under the fixed 64-token protocol, leaving 47 paired items; two COMMON outputs also failed, leaving 45 complete parsed pairs. Across those pairs the model made no harmful or beneficial revision in either condition, so both paired differences were exactly zero. The integrity report remains `fail` because all five parse failures and three missing pairs are intentionally disqualifying for claim-grade promotion.

This second independently developed family does not support source-multiplicity sensitivity. The predeclared LAD kill criterion therefore fires. No larger LAD run, parser expansion, or favorable-model search is planned. The artifacts support only the decision to stop LAD.

## DCEA replacement plan

The replacement topic is Directional Counterfactual Evidence Audit. Each item contains a query, a fixed source pack with stable opaque source identifiers, a single answer-bearing atomic fact, matched distractors, and an expected response. A paired intervention changes only the answer-bearing value in one source; a redundancy cell supplies a second independently worded source carrying the same value. No retrieval occurs in the controlled primary comparison.

The minimal factorial pilot crosses: (1) original versus directional fact replacement; (2) singleton versus redundant support; and (3) ordinary citation prompting versus a contrastive instruction that requires the answer and cited source to follow the supplied evidence. Every cell uses deterministic decoding and counterbalanced order. Primary outcomes are directional answer-following, citation validity, citation-support correctness, exact/normalized answer change, source-removal response change, and teacher-forced log-likelihood differences for the original and counterfactual answers.

Baselines are semantic answer-source support, direct citation correctness, exact source removal with regeneration, leave-one-out log-likelihood attribution, and no-context parametric response. DCEA adds matched value replacement, which provides a signed expected response rather than only asking whether probability decreases. The redundancy interaction is the decisive test: if a model uses either of two equivalent sources, removing one may have little effect, whereas changing their shared value should move the answer.

The first pilot must include the already pinned Phi-3.5 and Qwen2.5 families before scaling. Ablations remove redundancy, the contrastive instruction, source-ID randomization, or counterbalancing. Kill DCEA if replacement response is nearly identical to source removal, if the redundancy interaction is absent across both families, or if intervention artifacts make the answer recoverable from non-evidence cues. LAD runs are excluded from all DCEA effect estimates.

## Claim limits

The study cannot establish human-like cognition, universal resistance to social influence, production security, or RAG reliability. Claims remain bounded to measured regimes. External paper values are contextual only.

## DCEA outcome and stop decision

The DCEA pilot crossed two model families, singleton/redundant support, and ordinary/contrastive instructions for 320 raw generations. All four fixed-parser integrity reports failed because the required citation format was not recovered reliably. Within the interpretable Phi outputs, singleton and redundant pair-flip rates were both 1.0, so the decisive redundancy interaction was absent; contrastive prompting did not improve directional following. Qwen generations were frequently free-form and cannot rescue the claim. DCEA is retired without post-hoc parser changes.

## CLEP replacement plan

The replacement pilot uses matched propositions with four typed fields: speaker, proposition, polarity, and certainty. Each item has independently checked English, Korean, and Spanish realizations. The query and requested English report remain fixed while evidence language changes. Operator classes include negated, possible, probable, and certain claims; unattributed controls test whether speaker errors are separable from proposition errors.

Conditions are: direct answer from source-language evidence; translate-then-answer using an open translation model or the evaluated model under a frozen translation prompt; and typed epistemic-slot generation, which emits a constrained JSON tuple before producing the report. Primary outcomes are exact proposition recovery, polarity preservation, ordinal certainty preservation, speaker-attribution preservation, all-fields exact match, parse failure, and latency/tokens. The decisive estimand is a within-item language-channel difference, not a leaderboard score.

The first pilot uses the already pinned Phi-3.5 and Qwen2.5-1.5B snapshots, deterministic decoding, counterbalanced item and language order, raw-output retention, and an independently reproducible validator. Kill CLEP if two model families show no non-English preservation gap, if errors are explained entirely by proposition mistranslation, or if typed generation does not improve all-fields exact match over translate-then-answer. Scaling requires public parallel or uncertainty-annotated data with license, checksum, preprocessing, and storage records.
