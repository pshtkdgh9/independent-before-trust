# Novelty Matrix

Last updated: 2026-07-22. This matrix contains 28 directly relevant works. “Verified” here means the title, venue/preprint identifier, and abstract-level method were checked at the linked primary record; it does not imply reproduction. Full-text inspection of the closest works remains a submission gate.

## Candidate under audit

**Lineage-Aware Deliberation (LAD):** test whether language-agent groups mistake repeated or derived evidence for independent corroboration, and mitigate this *corroboration illusion* by binding atomic claims to source lineage and discounting dependent support during revision and aggregation.

A cited span can be valid yet be counted repeatedly when multiple agents derive their positions from one underlying source. LAD therefore differs from generic grounding, confidence weighting, identity anonymization, trust scoring, and majority voting: its causal factor is support dependence.

| # | Work | Venue/year | Main contribution | Relation and difference |
|---:|---|---|---|---|
| 1 | [GAVEL](https://aclanthology.org/2026.findings-acl.1789/) | Findings ACL 2026 | Atomic subclaims bound to evidence units with deterministic citation/span scrutiny. | Closest evidence-contract work; verifies provenance and sufficiency, but does not test duplicated-source dependence or corroboration inflation. |
| 2 | [The Ringelmann Effect in Multi-Agent LLM Systems](https://arxiv.org/abs/2606.02646) | arXiv 2026 | Models effective team size; nominal agents can overstate independent evidence. | Closest independence framing; studies scaling/diversity rather than claim-level source lineage and belief revision. |
| 3 | [Not All Flips Are Conformity](https://arxiv.org/abs/2606.00820) | arXiv 2026 | Counterfactual decomposition of self-instability, stance conformity, and reasoning persuasion. | Separates causes of answer change; does not manipulate common-source versus independent evidence. |
| 4 | [Demystifying Multi-Agent Debate](https://aclanthology.org/2026.findings-acl.1694/) | Findings ACL 2026 | Diversity-aware initialization and calibrated-confidence updates. | Weights agents/confidence rather than evidence independence; LAD tests diverse agents sharing one source. |
| 5 | [Free-MAD](https://aclanthology.org/2026.findings-acl.1600/) | Findings ACL 2026 | Removes consensus and final-round majority to reduce conformity/error propagation. | Strong protocol baseline; no correlated-support diagnosis. |
| 6 | [SELENE](https://aclanthology.org/2026.eacl-industry.7/) | EACL Industry 2026 | Selective debate initiation and evidence-weighted self-consistency. | Close evidence-weighting baseline; source-lineage dependence is not its stated mechanism. |
| 7 | [CONSENSAGENT](https://aclanthology.org/2025.findings-acl.1141/) | Findings ACL 2025 | Interaction-driven prompt refinement to mitigate sycophancy. | Targets agreement behavior, not evidential dependence. |
| 8 | [An Empirical Study of Group Conformity](https://aclanthology.org/2025.findings-acl.265/) | Findings ACL 2025 | Measures majority/intelligence-driven stance adoption. | LAD manipulates the source correlation behind apparent agreement. |
| 9 | [Conformity, Confabulation, and Impersonation](https://aclanthology.org/2024.c3nlp-1.2/) | C3NLP 2024 | Studies persona/opinion instability and conformity. | No evidence-lineage representation or intervention. |
| 10 | [When Identity Skews Debate](https://aclanthology.org/2026.acl-long.650/) | ACL 2026 | Identity-weighted Bayesian account and anonymization intervention. | Removes identity bias; LAD controls whether support is independent. |
| 11 | [Belief in Authority](https://aclanthology.org/volumes/2026.findings-acl/) | Findings ACL 2026 | Systematic role-based authority-bias analysis. | Authority is a crossed stress factor, not LAD's mechanism. |
| 12 | [Enhancing Multi-Agent Debate via Confidence Expression](https://aclanthology.org/2025.findings-emnlp.343/) | Findings EMNLP 2025 | Confidence-aware debate (ConfMAD). | Confidence may amplify repeated evidence but does not encode source ancestry. |
| 13 | [CortexDebate](https://aclanthology.org/2025.findings-acl.495/) | Findings ACL 2025 | Sparse agent graph guided by helpfulness/trust scoring. | Agent graph may still repeat one source; LAD models the source graph and uses no reputation score. |
| 14 | [Stay Focused](https://aclanthology.org/2026.findings-eacl.268/) | Findings EACL 2026 | Detects and mitigates problem drift. | Dialogue drift differs from corroboration illusion; useful robustness check. |
| 15 | [Exploring Collaboration Mechanisms for LLM Agents](https://aclanthology.org/2024.acl-long.782/) | ACL 2024 | Varies traits and debate/reflection; observes conformity. | Foundational adjacent work without source dependence. |
| 16 | [Improving Factuality and Reasoning through Multiagent Debate](https://proceedings.mlr.press/v235/du24e.html) | ICML 2024 | Canonical propose/critique/revise debate. | Required ordinary-debate baseline; nominal agents are treated as separate. |
| 17 | [Should We Be Going MAD?](https://proceedings.mlr.press/v235/smit24a.html) | ICML 2024 | Systematic debate-strategy study. | Broad evaluation without claim-source lineage. |
| 18 | [Encouraging Divergent Thinking through Multi-Agent Debate](https://aclanthology.org/2024.emnlp-main.992/) | EMNLP 2024 | Debate intervention for degeneration-of-thought. | Argument diversity is not evidence independence. |
| 19 | [Ask-Before-Detection](https://aclanthology.org/2025.acl-long.80/) | ACL 2025 | Creates an adaptive reference before judging solutions. | Useful independence control; does not model correlated sources across agents. |
| 20 | [Red-Teaming LLM Multi-Agent Systems](https://aclanthology.org/2025.findings-acl.349/) | Findings ACL 2025 | Agent-in-the-middle message manipulation. | LAD makes no general security claim; repeated-source injection is only a bounded stress test. |
| 21 | [Agents Under Siege](https://aclanthology.org/2025.acl-long.476/) | ACL 2025 | Prompt attacks under bandwidth/latency constraints. | Different threat model. |
| 22 | [Belief Revision](https://aclanthology.org/2024.emnlp-main.586/) | EMNLP 2024 | Delta-reasoning setup for revising beliefs under new evidence. | Single-model revision foundation; LAD studies social amplification of dependent evidence. |
| 23 | [Dynamic Epistemic Friction in Dialogue](https://aclanthology.org/2025.conll-1.21/) | CoNLL 2025 | Formalizes resistance to belief integration. | Discourse-theoretic basis; no LLM group intervention. |
| 24 | [Building Common Ground in Dialogue](https://aclanthology.org/2025.luhme-1.2/) | LUHME 2025 | Organizes common-ground dimensions. | LAD operationalizes repeated support masquerading as corroboration. |
| 25 | [Can LLMs Ground when they Don't Know?](https://aclanthology.org/2025.acl-long.728/) | ACL 2025 | Tests grounding under false presuppositions. | Single-interlocutor grounding without multi-source lineage. |
| 26 | [How Memory Management Impacts LLM Agents](https://aclanthology.org/2026.acl-long.27/) | ACL 2026 | Shows experience-following and error propagation. | Memory provenance is adjacent; LAD operates within deliberation and source multiplicity. |
| 27 | [Correlated Information Reduces Accuracy of Pioneering Decision-Makers](https://doi.org/10.1103/PhysRevResearch.5.033020) | PRR 2023 | Normative group-decision analysis with correlated observations. | Direct non-NLP theoretical antecedent; LAD operationalizes linguistic evidence and LLM revision. |
| 28 | [PROV-AGENT](https://arxiv.org/abs/2508.02866) | arXiv 2025 | Agent-workflow provenance model. | Infrastructure provenance, not a causal dependence-aware deliberation study. |

## Crowded territory

- Generic multi-agent debate improvements.
- Confidence-, identity-, authority-, trust-, and consensus-based weighting.
- Conformity measurement based only on answer flips.
- Evidence contracts that only verify cited spans.
- Conflict-aware RAG: CARE, Astute RAG, authority-bias RAG, and evidence-tree search substantially narrow that novelty window.
- Communication sparsification and debate-on-demand.

## Residual gap and bounded novelty

The scan did not identify work whose primary intervention holds semantic claims and nominal agreement fixed while varying whether support comes from a common or independent source, then measures language-model belief revision. GAVEL checks whether evidence is valid; LAD asks whether several valid citations collapse to one lineage and should count once. Ringelmann-effect work identifies independence as a scaling issue but does not supply claim-level lineage operations.

Pending full-text verification of the closest works (#1--#6), the bounded novelty claim is: **a controlled NLP study and lightweight protocol for source-lineage-aware belief revision in language-agent deliberation**. The paper will not claim the first use of provenance, evidence constraints, private answers, graphs, or multi-agent debate.

## Remaining novelty gate

1. Read and annotate full PDFs for #1--#6, #10, #12--#13, #19, and #27.
2. Re-run ARR/OpenReview and arXiv searches within 72 hours of submission.
3. Add contemporaneous work and weaken or pivot if a claim-level dependence intervention appears.
4. Keep external numerical results out of same-regime comparison tables.
