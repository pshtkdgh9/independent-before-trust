# Topic Decision

Date: 2026-07-22

## Selected direction after the first novelty gate

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
- **Contradiction-Budgeted Common Ground:** retained as fallback, but proposition extraction introduces an additional unvalidated component.
- **Provenance-Gated Agent Memory:** ACL 2026 already establishes experience-following and error propagation, making simple filtering incremental.
- **Selective Communication:** feasible but crowded by sparse debate and debate-on-demand; token savings alone are engineering-led.
- **Cross-Lingual Deliberation:** important extension, but translation competence would confound the primary causal factor.
- **Benchmark construction:** explicitly excluded.

## Kill/pivot criteria

Pivot to Contradiction-Budgeted Common Ground if:

1. a contemporaneous paper already tests claim-level common-source versus independent-source evidence in LLM deliberation;
2. two open-model families show no source-multiplicity sensitivity after content controls;
3. source lineage cannot be constructed deterministically and would require an unvalidated proprietary judge; or
4. LAD gives neither benefit nor diagnostic insight beyond citation validation or simple exact deduplication.

## Ethics boundary

LAD uses no trust/reputation score, signed edge, or prior graph algorithm. All code, datasets, transformations, prompts, results, prose, and figures will be new. Negative results trigger weaker claims or pivot, never suppression.
