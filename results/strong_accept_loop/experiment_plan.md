# Experiment Plan: Retired Audit Trail

## Current planning state after quantity-frame source gate

No headline experiment is currently selected. Denominator-/Quantity-Frame-Preserving Lay Summarization was an audit target only and is **RETIRED before GPU** after the source gate failed at commit `2d4b079`.

The gate artifacts are `quantity_frame/candidate_build.json`, `quantity_frame/model_audit_packet.jsonl`, and `quantity_frame/source_gate.json`. They record 332 items across two public corpora, 664 completed model-agent development audit rows, `human_evidence=false`, zero integrity failures, and `advance=false`. The decisive counts are `valid=253`, `denominator=0<30`, `comparator=0<30`, and `counterfactual=184`.

Comparator interpretation: 39 candidates proposed a stated comparator and 33 had both reviewers mark the comparator slot `yes`, but zero also had both reviewers validate the entire frame. Denominator proposed stated is 0. The claim is frozen as a negative source-gate result only: no manuscript claim, no GPU, no human evidence, no favorable subset search, and no Task5-7 execution.

Next step: reopen topic search under the existing audit constraints and do not name a new selected candidate here.

## Retired Evidence-State Triage Policy Plan

## Current research questions

- RQ1: Can a model or router distinguish missing evidence, user-intent ambiguity, and conflicting evidence before attempting a downstream answer?
- RQ2: Does a state-aware triage method choose `clarify`, `retrieve`, or `abstain` more reliably than direct prompting, selective QA gates, adaptive retrieval routers, and conflict-aware RAG prompts?
- RQ3: Do paired evidence-state interventions cause predicted directional action flips while query wording, answer target, topic, source envelope, and distractor count remain controlled?
- RQ4: Can the policy reduce selective risk for both insufficiency and conflict without increasing false-answer rate?

## Current paired intervention

Each item contains a query, an answer target used only for validation, and a controlled evidence pack. The primary output is one action label: `clarify`, `retrieve`, or `abstain`. The primary task does not generate the final answer.

Paired variants manipulate evidence state:

- `sufficient -> insufficient`: remove or mask only the minimal required evidence slot.
- `sufficient -> conflict`: introduce a contradictory answer-bearing statement while preserving the surface envelope.
- `insufficient -> conflict`: preserve query and topic while changing the blocking state from missing evidence to contradictory evidence.

The validator must reject pairs that change the query, alter the answer target, leak the condition through source names, change unrelated distractors, or lack a minimal-edit rationale.

## Current protocols and baselines

1. Direct answer-or-abstain prompt.
2. Selective QA confidence or self-consistency gate.
3. Ambiguity-aware clarification prompt.
4. Adaptive retrieval or knowledge-boundary router.
5. Conflict-aware RAG or evidence-reconciliation prompt.
6. Oracle state label diagnostic, reported only as an upper-bound diagnostic.
7. EST: explicit evidence-state policy that maps query/evidence state to `clarify`, `retrieve`, or `abstain`.

## Current tasks and data policy

Use only public, license-compatible source material after recording source URL, license/terms, revision if available, bytes, checksum, preprocessing command, and storage path. Do not state any source URL, checksum, license, item count, or model result until it is verified and recorded.

The pilot construction is implementation-gated by `docs/superpowers/plans/2026-07-23-evidence-state-triage-plan.md`: schema, licensed-source pilot construction, paired intervention validator, prompt/router baselines, CloudLab runner, integrity validator, analysis/gate, and docs.

## Current outcomes

- action macro-F1 over `clarify`, `retrieve`, and `abstain`;
- selective risk for insufficiency;
- selective risk for conflict;
- predicted directional action-flip rate across paired interventions;
- false-answer rate, where any downstream answer attempt in a non-answer state is counted against the method;
- parse/format failure by state, model family, and baseline;
- cost, wall time, and token counts.

## Current models and hardware

The pilot must use two independently developed open model families. Exact model IDs, revisions, licenses, and checksums are not selected yet and must not be invented. CloudLab use follows the existing repository pattern only after the runner, config capture, raw-output retention, and integrity validator pass tests.

## Current kill gate

Advance only if all conditions pass:

1. The state-aware method beats the strongest baseline on macro-F1.
2. The state-aware method beats the strongest baseline on selective risk separately for insufficiency.
3. The state-aware method beats the strongest baseline on selective risk separately for conflict.
4. More than 50% of paired interventions produce the predicted directional action flip.
5. The result holds across two independently developed open model families.
6. The state-aware method has no worse false-answer rate than the strongest baseline.

If any condition fails, retire the topic. Do not repair labels, alter the gate, change model families, or narrow the item subset after outcome inspection.

## Claim limits

The study cannot claim a new benchmark, universal abstention safety, general RAG reliability, human-like uncertainty reasoning, or downstream answer correctness. It can claim only behavior observed under the licensed paired evidence-state protocol after integrity validation.

## Retired Lineage-Aware Deliberation Plan

## Current planning state

LAD, DCEA, CLEP, ESP, and evidence-state triage are retired. No headline experiment is currently selected.

Evidence-state triage stopped before GPU. The model-agent audit summary records two balanced 24-row lanes and a 13-row intersection, but conflict construction failed the audit: overlap agreement is only 7/13 for conflict usability and 6/13 for natural incompatible sentence existence. The candidate is retired for novelty/action aggregation collision and invalid conflict construction. Its design, schema, builder, provenance path, and candidate pack remain negative auditable artifacts only.

Denominator-/Quantity-Frame-Preserving Lay Summarization was later audited and retired before GPU after its source gate failed; Task5-7 were not executed.

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

Protocol v1 ran but is invalid for claims. Its free-form `proposition` field did not operationalize lemma-equivalent outputs, and every model/method cell contained at least one fixed-format parse failure. The 72 generations remain under `cloudlab_artifacts/clep-pilot-bbf75d1` and will never be rescored with relaxed rules. Protocol v2 must replace free text with closed-set speaker, action, polarity, and certainty labels; freeze those labels and the parser before generating new outputs; and store results in a distinct artifact directory.

Protocol v2 then generated 144 new outputs under the closed labels. All six integrity reports pass. Exact accuracy by English/Korean/Spanish was: Phi direct 0.625/0.500/0.750, Phi translate 0.750/0.625/0.875, Phi typed 0.875/0.625/0.750; Qwen direct 0.250/0.250/0.500, Qwen translate 0.250/0.375/0.375, and Qwen typed 0.625/0.500/0.375. The language direction is inconsistent and typed generation is not a cross-family winner. The predeclared kill condition therefore fires; no larger CLEP run is planned.

## ESP feasibility plan

ESP begins with 40 naturally occurring uncertainty-cue candidates extracted in fixed source order from abstracts in the pinned BioLaySumm eLife validation split. The lexicon is candidate retrieval only. Before scoring, two annotators must independently label cue validity, semantic scope, strength class, attribution, and whether a faithful lay rewrite should retain the qualification; disagreements are adjudicated and agreement is reported. No regex match is treated as gold.

The first generation pilot compares the already pinned Phi-3.5 and Qwen2.5 families under deterministic decoding:

1. direct lay rewriting of the source abstract;
2. a generic instruction to preserve uncertainty;
3. an explicit uncertainty-frame condition containing cue, strength, scoped proposition, and attribution;
4. an oracle-frame condition using human-reviewed frames, separated from automatic extraction.

Primary outcomes are frame-strength preservation and scope attachment on retained propositions. Secondary outcomes are readability, source copying, content coverage, unsupported additions, output length, and parse/validation failures. Automatic cue overlap is diagnostic only; headline evidence requires blinded human judgments of meaning and scope. A counterfactual robustness cell changes only the source uncertainty strength and tests whether the output changes in the same direction while unrelated content remains stable.

Kill ESP if full-text review finds the same frame-conditioned lay-generation method; if scope annotation agreement is inadequate after guideline revision; if both model families show no improvement over the generic preservation instruction; or if gains arise from copying the source or degrading readability/coverage. The clinical 2026 benchmark's numerical values are context only and will never be presented as same-regime comparison.

## ESP feasibility outcome before final gate

At exact execution commit `beca9cc32f9082985535d24fdcbb2cea1199267e`, the direct, generic-preservation, and explicit-frame conditions each produced 38 outputs from Phi-3.5 and Qwen2.5-1.5B. Automatic cue preservation increased under frame conditioning in both families, and a condition-blind two-agent development audit also produced higher strict-consensus strength and scope counts for frame than generic. However, agreement between the two model-agent reviewers was only `0.640` for strength, `0.443` for scope, and `0.268` for overall acceptability. Several frame outputs introduced unsupported content, including a treatment recommendation absent from the source.

At this stage, the no-benefit kill condition had not fired, but neither had the evidence gate passed. The run was a feasibility signal only. Before any scaling, the study still needed a clearer semantic rubric, controlled counterfactual changes in uncertainty strength, copying/readability/coverage checks, and reliable blinded human judgments. No result from the development audit may be described as human evaluation.

## ESP counterfactual outcome and stop decision

The natural-text counterfactual review is complete in `esp_counterfactual/review_summary_v1.json`. Phi passes its family gate: paired equivariance increases from generic `0.0` to frame `0.5714285714285714`, frame acceptable rate is not lower (`0.6071428571428571` versus `0.35714285714285715`), and unsupported additions are not higher (`0.07142857142857142` versus `0.07142857142857142`). Qwen fails: paired equivariance decreases from generic `0.07142857142857142` to frame `0.0`, frame acceptable rate is lower (`0.25` versus `0.32142857142857145`), and unsupported additions are higher (`0.14285714285714285` versus `0.10714285714285714`).

The combined rule requires the frame condition to be strictly better on paired equivariance in both model families, no worse on unsupported additions, and no lower on acceptable rate. The combined gate is `advance=false`. The artifact records `evidence_class=model_agent_development_only`, `human_evidence=false`, and `row_count=112`.

ESP is therefore retired as the headline candidate. No larger ESP run, rubric tuning, pair selection change, or favorable-family scaling is planned. The artifacts support only the decision to stop ESP and reopen topic search.
