# Topic Decision

Date: 2026-07-22

## Current selected direction after the empirical pivot

**Beyond Leave-One-Out: Directional Counterfactual Audits of Evidence Use**

Research question: *Does a cited and semantically supportive source causally direct a model's answer, and can matched value-replacement interventions identify evidence use that source-removal attribution misses under redundancy?*

This is a causal model-analysis paper, not a benchmark paper and not an end-to-end RAG claim. Retrieval is outside the first controlled regime. A paired intervention replaces only an answer-bearing value in a supplied source while holding query, source identifiers, distractors, order, and surface envelope fixed. Unlike semantic support metrics, it asks whether the answer moves in the predicted direction; unlike single-source removal, it can remain identifiable when equivalent evidence is redundant.

Its claims start unearned:

- DCEA-C1: semantic citation support does not imply directional causal evidence use in the tested regimes;
- DCEA-C2: matched value replacement detects evidence use that single-source removal misses under redundant support;
- DCEA-C3: a contrastive evidence-use instruction improves directional grounding without reducing answer validity.

Closest-work boundary: ContextCite (NeurIPS 2024) introduces context attribution with learned subset masking; AttriBoT (ICLR 2025) efficiently approximates leave-one-out likelihood attribution; Ye et al. (EMNLP 2021) evaluate explanation methods on counterfactual reading-comprehension examples; DisentQA (ACL 2023) separates parametric and contextual answers; and evidence-attribution work evaluates citation recovery. DCEA does not claim to invent causal context attribution. Its provisional contribution is a signed, answer-level value-replacement estimand and a redundancy test showing where support and removal-based necessity can fail to identify directional use. A direct two-family pilot and full-text audit remain mandatory.

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
- **Cross-Lingual Deliberation:** important extension, but translation competence would confound the primary causal factor.
- **Benchmark construction:** explicitly excluded.

## LAD kill/pivot criteria and decision

Pivot to Contradiction-Budgeted Common Ground if:

1. a contemporaneous paper already tests claim-level common-source versus independent-source evidence in LLM deliberation;
2. two open-model families show no source-multiplicity sensitivity after content controls;
3. source lineage cannot be constructed deterministically and would require an unvalidated proprietary judge; or
4. LAD gives neither benefit nor diagnostic insight beyond citation validation or simple exact deduplication.

Criterion 2 fired on 2026-07-22. The integrity-validated Phi-3.5 run did not show the anticipated direction. The exact-protocol Qwen2.5-1.5B replication produced 45 complete parsed pairs and zero answer revisions in either condition; five outputs failed the fixed parser and are retained. The second artifact is diagnostic rather than claim-grade because its validator correctly rejects those failures, but scaling LAD would amount to searching for a responsive model after two independently developed families failed to support the mechanism. LAD is therefore retired as the submission topic. Its negative artifacts remain part of the audit trail and cannot support DCEA claims.

## Ethics boundary

DCEA will use no trust/reputation score, signed edge, or prior graph algorithm. LAD code and negative artifacts remain background tooling/audit evidence only; they will not be relabeled as DCEA evidence. All DCEA data transformations, prompts, results, claims, prose, and figures must be newly generated. Negative results trigger weaker claims or another documented pivot, never suppression.
