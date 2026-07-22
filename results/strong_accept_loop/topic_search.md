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
