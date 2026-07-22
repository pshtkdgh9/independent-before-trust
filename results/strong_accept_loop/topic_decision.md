# Topic Decision

Date: 2026-07-23

## Current direction after the quantity-frame negative gate

No headline topic is currently selected. Topic search is reopened after LAD, DCEA, CLEP, ESP, evidence-state triage, and Denominator-/Quantity-Frame-Preserving Lay Summarization all failed their recorded gates. The next topic must not be chosen in this file until a new candidate passes a documented search, novelty boundary, provenance path, and falsifiable pilot plan.

## Retired quantity-frame audit target before GPU

Denominator-/Quantity-Frame-Preserving Lay Summarization was an audit target only, not a selected direction. It is **RETIRED before GPU** after the negative source gate at commit `2d4b079`.

The decision artifacts are `quantity_frame/candidate_build.json`, `quantity_frame/model_audit_packet.jsonl`, and `quantity_frame/source_gate.json`. They record 332 candidate items from two corpora, 664 completed model-agent development audit rows, `human_evidence=false`, no integrity failures, and overall `advance=false`.

The source gate fails because the pre-GPU source inventory does not meet the minimum evidence thresholds: `valid=253`, `denominator=0<30`, `comparator=0<30`, and `counterfactual=184`. Comparator labels do not rescue the gate: 39 candidates proposed a stated comparator and 33 had both reviewers mark the comparator slot `yes`, but zero also had both reviewers validate the entire frame; denominator proposed stated is 0.

This is a negative source-gate result only. It supports no manuscript claim, no GPU run, no human-evidence statement, and no favorable subset search. Task5-7 were not executed because the gate failed.

## Retired evidence-state triage before GPU

Evidence-state triage is retired before GPU experiments. It does not support a headline claim.

The audit record is `evidence_state_triage/candidate_audit_summary.json`. Both model-agent lanes contain 24 rows, balanced 12 SUPPORTS and 12 REFUTES. Their 13-row intersection agrees on labels 13/13, sufficiency usability 13/13, ambiguity 13/13, self-contained evidence 13/13, but only conflict usability 7/13 and natural incompatible sentence existence 6/13.

The evidence class is `model_agent_development_only`; `human=false` and `human_evidence=false`. The candidate is retired because of a novelty/action aggregation collision and invalid conflict construction. The design, schema, builder, provenance code, and candidate pack remain negative auditable artifacts only.

## Retired ESP direction after the third empirical pivot

**Say Less, Mean the Same: Epistemic-Scope-Preserving Lay Summarization**

Research question: *Can an explicit representation of uncertainty strength and semantic scope prevent lay summaries from turning qualified scientific findings into categorical claims without forfeiting accessibility?*

This is a generation-method and linguistic-analysis paper, not a new benchmark. The provisional method extracts auditable uncertainty frames `(cue, strength, scoped proposition, attribution)` from a scientific source, exposes those frames to an open generator, and validates whether the lay realization preserves both strength and scope. Public PLOS/eLife or another clearly licensed source--lay corpus will be used only after exact version, license, checksum, and preprocessing provenance are recorded.

Its claims start unearned:

- ESP-C1: standard open-model lay summarization measurably changes source uncertainty strength or scope on naturally occurring scientific claims;
- ESP-C2: frame-conditioned generation reduces those changes relative to matched direct and generic self-refinement baselines;
- ESP-C3: the reduction is not purchased by source copying or a material loss of readability and content coverage.

Selection is retired. The natural-text counterfactual review in `esp_counterfactual/review_summary_v1.json` records Phi as passing (`advance=true`) and Qwen as failing (`advance=false`); the combined gate is `advance=false`. The evidence class is `model_agent_development_only` and `human_evidence=false`. Scaling ESP would therefore amount to continuing after a negative two-family gate using non-human development evidence. The June 2026 diagnostic-uncertainty benchmark remains a close evaluation collision, not omitted; it no longer matters for topic selection because ESP itself failed the advance rule.

## Retired CLEP direction

**Lost in Translation, Overstated in Generation: Cross-Lingual Epistemic Preservation**

Research question: *When propositional content is held fixed, does changing the language channel alter whether an open language model preserves negation, uncertainty, and source attribution, and can an explicit epistemic-slot representation reduce those meaning-changing errors?*

This is a multilingual generation and model-analysis paper, not a benchmark release. The controlled unit is a proposition with an epistemic operator and an attributed speaker. Parallel realizations preserve the proposition while changing only the evidence language. The primary comparison measures whether the generated English report preserves the operator and attribution. A lightweight method first extracts a typed tuple (speaker, proposition, polarity, certainty) and then realizes the answer, making the intervention and error analysis auditable.

Its claims start unearned:

- CLEP-C1: language-channel changes cause measurable operator-preservation errors even when proposition content is matched;
- CLEP-C2: errors differ by operator class rather than being explained only by general answer accuracy or translation fluency;
- CLEP-C3: typed epistemic-slot generation reduces meaning-changing errors without materially degrading proposition recovery.

Closest-work boundary: Muller et al. (EMNLP 2023) study attribution in cross-lingual QA; Krause et al. (MMNLG 2023) study multilingual uncertainty expression; XRAG studies cross-lingual retrieval and response-language failures; Mehrparvar and Pezzelle (MRL 2024) study ambiguity preservation in translation; and 2025--2026 work studies multilingual calibration and hallucination detection. CLEP does not claim to introduce cross-lingual attribution, calibration, or uncertainty evaluation. Its provisional contribution is a matched causal decomposition of operator preservation plus an auditable typed-generation intervention. A full-text collision audit and direct two-family pilot remain mandatory.

**Decision after protocol v2:** retire CLEP. All six v2 artifacts pass integrity, but the predicted non-English preservation deficit is not consistent across languages, models, or methods. Typed generation improves aggregate exact match for Qwen (0.333 direct to 0.500 typed) but does not outperform translate-then-classify for Phi (both 0.750). Scaling would search for favorable languages or models after the decisive pilot. The next topic must begin from a licensed public-data task and a method contribution, not another small synthetic behavior effect.

## Retired second direction

**Beyond Leave-One-Out: Directional Counterfactual Audits of Evidence Use (DCEA)** is retired. All four fixed-protocol CloudLab cells failed the artifact integrity gate because the predeclared parser did not recover the required citation structure. Among the interpretable Phi generations, singleton and redundant pair-flip rates were both 1.0 and the contrastive instruction did not improve directional following. Qwen outputs were frequently free-form and likewise did not establish the predicted redundancy interaction. A later literature check also found *Source Attribution in Retrieval-Augmented Generation* (2025), which explicitly applies Shapley attribution to redundancy, complementarity, and synergy. The 320 raw generations remain diagnostic artifacts; none supports a manuscript claim.

## Retired direction after the first novelty gate

**Lineage-Aware Deliberation: When Repeated Evidence Masquerades as Independent Corroboration in Language-Agent Collaboration**

Research question: *When language agents collaborate, do multiple claims derived from the same source create a corroboration illusion, and can source-lineage-aware revision prevent harmful amplification without suppressing genuinely independent correction?*

This is not a benchmark paper. The contributions are a controlled causal study of source dependence, a lightweight lineage-aware revision rule, and analysis of the gap between nominal consensus and effective independent support. Public datasets are instruments rather than the contribution.

## Why this direction

1. **Crisp scientific distinction:** nominally distinct agents are not independent witnesses when their evidence shares ancestry.
2. **EACL fit:** the problem connects discourse, common ground, evidentiality, belief revision, LLM agents, and the EACL 2027 theme *The Human in Language*.
3. **Controlled test:** common versus independent source lineage can vary while claim meaning, correctness, fluency, confidence, order, and nominal agent count remain fixed.
4. **Feasibility:** inference-only experiments with open 3B--8B models fit one A30 24 GB; lineage is deterministic where source IDs are known.
5. **Novelty boundary:** the 28-work matrix shows extensive work on confidence, identity, conformity, valid evidence, and effective team size, but no verified claim-level study of duplicated-source corroboration.

## Planned claims—not yet earned

- C1: Source dependence changes harmful and beneficial revision rates when nominal agreement is fixed.
- C2: Lineage-aware aggregation reduces duplicated-evidence amplification relative to majority, confidence-, and evidence-weighted baselines in tested regimes.
- C3: Effective independent support explains failure cases hidden by final accuracy, nominal agent count, and citation validity alone.

These remain hypotheses until the evidence map points to completed artifacts.

## Rejected alternatives

- **Evidence-First Deliberation:** demoted after contemporaneous papers were found on counterfactual conformity decomposition, calibrated-confidence debate, identity anonymization, evidence contracts, and consensus-free debate. Independent first-round answers remain a control.
- **Conflict-aware evidence graphs for RAG:** rejected as the main topic because CARE, Astute RAG, authority-bias RAG, evidence-tree search, and related conflict routing make novelty tight. No RAG claim will be made without a real retriever and end-to-end evidence.
- **Contradiction-Budgeted Common Ground:** rejected after the LAD pivot because 2024--2026 work already covers its common-ground, clarification, abstention, stopping-budget, confidence-update, and conflict-resolution components.
- **Claim-Preserving Provenance Repair:** rejected because RARR (ACL 2023) already finds attribution for existing LM output and minimally edits unsupported content while preserving the original.
- **Conflict-Preserving Synthesis:** rejected because MoDS (NAACL 2025) already targets coverage and balance across opposing perspectives.
- **Argument-Role Coverage Repair:** rejected because Arg-LLaDA (ACL 2026) already performs sufficiency-aware iterative repair of unsupported, redundant, and incomplete spans.
- **Provenance-Gated Agent Memory:** ACL 2026 already establishes experience-following and error propagation, making simple filtering incremental.
- **Selective Communication:** feasible but crowded by sparse debate and debate-on-demand; token savings alone are engineering-led.
- **Cross-Lingual Deliberation:** rejected as a multi-agent topic. The new provisional direction instead makes language-channel effects the manipulated variable and measures operator preservation directly.
- **Benchmark construction:** explicitly excluded.

## LAD and DCEA kill/pivot decisions

Pivot to Contradiction-Budgeted Common Ground if:

1. a contemporaneous paper already tests claim-level common-source versus independent-source evidence in LLM deliberation;
2. two open-model families show no source-multiplicity sensitivity after content controls;
3. source lineage cannot be constructed deterministically and would require an unvalidated proprietary judge; or
4. LAD gives neither benefit nor diagnostic insight beyond citation validation or simple exact deduplication.

Criterion 2 fired on 2026-07-22. The integrity-validated Phi-3.5 run did not show the anticipated direction. The exact-protocol Qwen2.5-1.5B replication produced 45 complete parsed pairs and zero answer revisions in either condition; five outputs failed the fixed parser and are retained. The second artifact is diagnostic rather than claim-grade because its validator correctly rejects those failures, but scaling LAD would amount to searching for a responsive model after two independently developed families failed to support the mechanism. LAD is therefore retired as the submission topic. Its negative artifacts remain part of the audit trail and cannot support DCEA claims.

## Ethics boundary

DCEA will use no trust/reputation score, signed edge, or prior graph algorithm. LAD code and negative artifacts remain background tooling/audit evidence only; they will not be relabeled as DCEA evidence. All DCEA data transformations, prompts, results, claims, prose, and figures must be newly generated. Negative results trigger weaker claims or another documented pivot, never suppression.

CLEP must use newly authored prompts, paired items, analysis, prose, figures, and result artifacts. LAD and DCEA code may be reused only for generic hashing, immutable-run layout, and validator patterns, with that boundary recorded. Their data and outcomes cannot be relabeled as CLEP evidence. Kill CLEP if the full-text audit finds a direct matched operator-preservation study, if paired language effects are absent in two independent open-model families, or if the typed representation provides no improvement beyond a translate-then-answer baseline.

ESP used newly authored prompts, model-agent development audits, counterfactual review artifacts, and separately pinned BioLaySumm source material. LAD, DCEA, and CLEP data and outcomes cannot be relabeled as ESP evidence. ESP is now retired because the counterfactual gate did not advance across two model families, and no ESP artifact is human evidence.
