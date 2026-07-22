# Topic Decision

Date: 2026-07-22

## Current selected direction after the empirical pivot

**Contradiction-Budgeted Common Ground: Deferring Premature Commitment in Language-Agent Deliberation**

Research question: *When language agents receive mutually inconsistent but individually plausible claims, can an explicit budget over unresolved contradictions improve when they commit, defer, or request more evidence?*

This is a mechanism paper, not a benchmark paper. The controlled intervention holds messages and evidence fixed while changing the common-ground update policy. The proposed policy exposes unresolved proposition pairs, spends a bounded verification budget, and permits a calibrated `DEFER` action instead of forcing consensus. Public tasks are experimental instruments only.

The direction is selected provisionally pending a fresh closest-work scan and a direct pilot. Its claims start unearned:

- CBCG-C1: contradiction-budgeted updating reduces harmful premature commitments relative to immediate consensus and confidence-only deferral in tested regimes;
- CBCG-C2: the benefit persists when contradiction count, evidence order, confidence, and surface form are controlled;
- CBCG-C3: explicit unresolved-conflict state predicts failures that final confidence and nominal agreement do not expose.

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
- **Contradiction-Budgeted Common Ground:** retained as fallback, but proposition extraction introduces an additional unvalidated component.
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

Criterion 2 fired on 2026-07-22. The integrity-validated Phi-3.5 run did not show the anticipated direction. The exact-protocol Qwen2.5-1.5B replication produced 45 complete parsed pairs and zero answer revisions in either condition; five outputs failed the fixed parser and are retained. The second artifact is diagnostic rather than claim-grade because its validator correctly rejects those failures, but scaling LAD would amount to searching for a responsive model after two independently developed families failed to support the mechanism. LAD is therefore retired as the submission topic. Its negative artifacts remain part of the audit trail and cannot support CBCG claims.

## Ethics boundary

CBCG will use no trust/reputation score, signed edge, or prior graph algorithm. LAD code and negative artifacts remain background tooling/audit evidence only; they will not be relabeled as CBCG evidence. All CBCG prompts, transformations, results, claims, prose, and figures must be newly generated. Negative results trigger weaker claims or another documented pivot, never suppression.
