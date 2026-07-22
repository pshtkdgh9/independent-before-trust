# Topic Search

Date: 2026-07-22. Candidate selection excludes benchmark-only work and requires a reusable NLP insight, public/open evidence path, A30 24 GB feasibility, EACL/ACL fit, and separation from the already-submitted journal manuscript.

Scores use 1--5 for venue fit (F), plausible novelty (N), experimental feasibility (E), analysis depth (A), and non-overlap (O). They are planning judgments, not acceptance predictions.

| Rank | Candidate | F | N | E | A | O | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | **Lineage-Aware Deliberation:** distinguish repeated evidence from independent corroboration and discount dependent support during belief revision. | 5 | 5 | 5 | 5 | 4 | 24 | Selected, subject to full-text gate. |
| 2 | **Evidence-First Deliberation:** private structured commitment before peer exposure plus evidence-linked revision. | 5 | 3 | 5 | 5 | 5 | 23 | Demoted after close 2026 conformity/debate work. |
| 3 | **Contradiction-Budgeted Common Ground:** preserve unresolved propositions rather than forcing consensus. | 5 | 4 | 4 | 5 | 5 | 23 | First fallback; extraction validity risk. |
| 4 | **Pragmatic Clarification before Revision:** ask targeted clarification rather than accept ambiguous or presupposition-loaded peer claims. | 5 | 4 | 4 | 4 | 5 | 22 | Human/judge validation burden. |
| 5 | **Cross-Lingual Deliberation Consistency:** analyze language-conditioned peer influence and evidence preservation. | 5 | 4 | 3 | 5 | 5 | 22 | Translation is a major confound. |
| 6 | **Conflict-Aware RAG Evidence Graphs:** route answer/verify/abstain decisions under retrieved conflicts. | 4 | 2 | 4 | 4 | 5 | 19 | Rejected: CARE/Astute RAG and related work crowd the space. |
| 7 | **Provenance-Gated Agent Memory:** outcome-, source-, and expiry-aware memory lifecycle. | 4 | 3 | 4 | 5 | 5 | 21 | Rejected: close ACL 2026 memory work. |
| 8 | **Selective Communication under Uncertainty:** communicate only high-information claims. | 4 | 3 | 5 | 4 | 5 | 21 | Rejected: sparse/selective debate is crowded. |

## 1. Lineage-Aware Deliberation (selected)

**Gap.** Current systems can verify that each citation is real yet still count several linguistic restatements derived from one source as multiple votes. This creates apparent corroboration without independent evidence.

**Method hypothesis.** Bind atomic claims to source IDs and derivation parents; compute effective independent support; collapse or discount dependent support during typed belief revision. The method assigns no trust/reputation to agents.

**Evidence package.** Paired common-source and independent-source conditions hold semantic claims, correctness, confidence, order, and agent count fixed. Baselines: no interaction, ordinary debate, majority vote, confidence weighting, evidence-contract validation, exact/semantic deduplication. Outcomes: harmful and beneficial revision, calibration, apparent/effective support, evidence-grounded revision, cost, and lineage/parser errors.

## 2. Evidence-First Deliberation

Separates private belief, peer exposure, and justified revision. It remains a useful control but is not sufficiently distinctive as the headline after 2026 work on conformity decomposition, confidence/diversity, identity, consensus-free debate, and evidence contracts.

## 3. Contradiction-Budgeted Common Ground

Maintains a ledger of supported, opposed, and unresolved propositions so consensus cannot silently erase conflict. Strong theme fit, but extraction quality complicates causal interpretation.

## 4. Pragmatic Clarification before Revision

Models whether an agent should clarify an underspecified or presupposition-loaded claim before revising. Scientifically attractive, but appropriateness labels likely require human evaluation.

## 5. Cross-Lingual Deliberation Consistency

Studies whether evidence and confidence survive translation-mediated peer exchange. Valuable but translation quality and cultural knowledge would confound the main mechanism.

## 6. Conflict-Aware RAG Evidence Graphs

The parallel search proposed a graph that routes answer/verify/abstain decisions under retrieval conflicts. It was rejected after identifying CARE, Astute RAG, authority-bias RAG, evidence-tree search, and conflict-robust RAG work. It would also require an actual retriever and end-to-end RAG evaluation; motivational framing alone would be insufficient.

## Search conclusion

The first search favored private commitment, while an unsupervised parallel edit favored conflict-aware RAG. The 28-work collision analysis rejected both as headline contributions and selected source-lineage dependence. This change is recorded rather than hidden. The decision remains falsifiable under the kill/pivot criteria in `topic_decision.md`.

## Post-LAD empirical-pivot search

After two independent model families failed the LAD decision gate, the CBCG fallback was also rejected as too crowded: current work already covers common-ground tracking, clarification, abstention, budgeted debate stopping, confidence-aware updating, consensus-free debate, and explicit conflict resolution.

Five new non-benchmark method/mechanism candidates were compared with the same five-point feasibility (F), novelty (N), evidence tractability (E), ACL/EACL fit (A), and non-overlap (O) criteria.

| Rank | Candidate | F | N | E | A | O | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | **Directional Counterfactual Evidence Audit:** replace an answer-bearing fact in a cited source and test whether the generated claim changes in the intervention's direction. | 5 | 4 | 5 | 5 | 5 | 24 | Selected provisionally; direct pilot and full closest-work audit required. |
| 2 | **Claim-Preserving Provenance Repair:** minimally repair unsupported spans in an existing answer while preserving supported content and meaning. | 5 | 1 | 5 | 5 | 5 | 21 | Rejected: RARR (ACL 2023) already retrieves attribution and minimally edits unsupported LM output. |
| 3 | **Conflict-Preserving Synthesis:** retain attributed disagreement structure instead of flattening contradictory sources. | 4 | 2 | 4 | 5 | 5 | 20 | Rejected: MoDS (NAACL 2025) already targets balanced synthesis of opposing perspectives. |
| 4 | **Clarify-or-Abstain Evidence Triage:** choose answer, clarify, abstain, or acquire evidence under insufficiency/conflict. | 4 | 3 | 4 | 5 | 5 | 21 | Rejected as close to refusal/abstention and routing work. |
| 5 | **Memory-vs-Retrieval Conflict Routing:** select memory, retrieval, or reconciliation under context-memory conflict. | 4 | 3 | 4 | 4 | 5 | 20 | Rejected as crowded retrieval routing. |
| 6 | **Argument-Role Coverage Repair:** restore missing argumentative roles in long-document synthesis. | 3 | 1 | 3 | 5 | 5 | 17 | Rejected: Arg-LLaDA (ACL 2026) already performs sufficiency-guided iterative repair of unsupported, redundant, and incomplete spans. |

The selected problem is causal identification, not citation scoring or benchmark construction. Existing citation metrics test whether a source can support a claim; ContextCite and AttriBoT estimate source necessity mainly through removal and likelihood change. The proposed audit asks a different, directional question: when an answer-bearing source fact is minimally changed while identifiers, query, distractors, order, and surface envelope are controlled, does the model's claim and citation change in the predicted direction? This design is intended to expose two unresolved cases: causally inert but semantically supportive citations, and redundant support for which single-source removal understates evidence use. The novelty claim remains provisional until a direct pilot and full-text closest-work review pass.
