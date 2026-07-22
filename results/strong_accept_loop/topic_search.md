# Topic Search

Date: 2026-07-22. Candidate selection excludes benchmark-only work and requires a reusable NLP insight, public/open evidence path, A30 24 GB feasibility, EACL/ACL fit, and separation from the already-submitted journal manuscript.

## Search reopened after quantity-frame source gate

Denominator-/Quantity-Frame-Preserving Lay Summarization was an audit target only, not a selected topic. It is **RETIRED before GPU** after the source gate at commit `2d4b079` and artifacts `quantity_frame/candidate_build.json`, `quantity_frame/model_audit_packet.jsonl`, and `quantity_frame/source_gate.json`.

The source gate covered 332 candidate items from two public corpora and 664 completed model-agent development audit rows. It records `human_evidence=false`, `advance=false`, `valid=253`, `denominator=0<30`, `comparator=0<30`, `counterfactual=184`, and zero integrity failures. Agreement was high for slot labels, including denominator/base `0.9759` and comparator `0.9307`, but this is development-audit agreement only.

Comparator interpretation is negative: 39 candidates proposed a stated comparator and 33 had both reviewers mark the comparator slot `yes`, but zero also had both reviewers validate the entire frame; no candidate proposed a stated denominator/base. The result supports only a negative source-gate decision. It is not a manuscript claim, not human evidence, and not a reason to run GPU experiments.

Current selected direction: none. Reopen topic search under the existing constraints; do not name a replacement candidate until a new search, novelty boundary, provenance path, and falsifiable pilot plan pass.

## Evidence-state triage provisional candidate

The next provisional candidate is **Evidence-State Triage Policy**: a method study that decides whether the system should `clarify`, `retrieve`, or `abstain` under controlled evidence states. The downstream answer remains out of scope for the primary claim.

The core novelty is paired causal evidence-state intervention, not benchmark creation. Each base item must support matched variants where the evidence state changes while query wording, answer target, source envelope, distractor count, and topic remain controlled. The decisive behavior is a predicted directional action flip: insufficiency should trigger evidence acquisition or clarification, conflict should trigger abstention, and user-intent ambiguity should trigger clarification rather than an answer attempt.

Closest-work boundary as of the 2026-07-23 search: TACL 2022 insufficient-evidence fact checking; EMNLP 2023 selective ambiguous QA; ACL 2025 *Do not Abstain! Identify and Solve the Uncertainty*; Findings IJCNLP-AACL 2025 *When in Doubt, Ask First*; Findings EMNLP 2025 KBM; Abstain-R1; and CARE-family conflict-aware RAG. These works make generic abstention, ambiguity handling, adaptive retrieval, knowledge-boundary routing, post-refusal clarification, and conflict-aware RAG too crowded as standalone claims. The absence of the exact combination is only a search-limited inference: paired causal evidence-state interventions over insufficiency and conflict with a three-action `clarify`/`retrieve`/`abstain` policy and answer generation held downstream.

Provisional score under the existing 1--5 dimensions: F=5, N=3, E=4, A=5, O=5, total=22. The novelty score is intentionally conservative because the closest-work boundary is dense. Advance requires the exact kill gate in `experiment_plan.md`; otherwise retire without favorable-model search or post-hoc label repair.

## Search reopened after ESP negative gate

ESP is retired as the headline candidate, not erased from the audit trail. The natural-text counterfactual review in `esp_counterfactual/review_summary_v1.json` records Phi as passing the advance gate and Qwen as failing it; the combined gate is `advance=false`. The same file records `evidence_class=model_agent_development_only` and `human_evidence=false`, so the result cannot be promoted by calling it human evaluation or by scaling only the favorable family.

The replacement search uses the same constraints as the earlier pivots: licensed/public evidence path, method contribution rather than benchmark construction, explicit closest-work boundary, and a falsifiable two-family gate before any headline claim. Evidence-state triage is provisional only; no result or manuscript claim is selected.

Evidence-state triage was also audited and retired before GPU. The two model-agent audit lanes each contain 24 balanced rows, but overlap agreement on conflict usability is only 7/13 and natural incompatible sentence existence is only 6/13. The candidate is retired because the framing collides with novelty/action aggregation and the conflict construction is invalid. Its artifacts remain negative audit records only.

Retired audit target: **Denominator-/Quantity-Frame-Preserving Lay Summarization**. Its source gate failed before GPU; Task5-7 were not executed.

## Third-pivot public-data method search

CLEP was retired under its predeclared two-family gate. The next search therefore requires an existing licensed corpus, a method contribution, and a primary outcome that is not a tiny synthetic behavior effect. Scores below use the same five 1--5 dimensions as the earlier searches.

| Rank | Candidate | F | N | E | A | O | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | **Epistemic-Scope-Preserving Lay Summarization:** extract source uncertainty frames and require generated lay summaries to preserve cue strength and scope. | 5 | 4 | 4 | 5 | 5 | 23 | Retired after the counterfactual two-family gate: Phi passed, Qwen failed, overall `advance=false`; evidence remained model-agent development only with `human_evidence=false`. |
| 2 | **Question-Guided Minimal Simplification Repair:** insert only content diagnosed as missing by InfoLossQA. | 5 | 2 | 5 | 5 | 5 | 22 | Rejected as headline: Nandiraju et al. (2025) already detect missing health-text elements and regenerate text by inserting them. |
| 3 | **Input-Normalized Table-to-Text Generation:** repair malformed ToTTo inputs before generation. | 4 | 1 | 4 | 4 | 5 | 18 | Rejected: Sundararajan et al. (NAACL 2024) directly fix ToTTo input problems and report large factual-error reductions. |
| 4 | **Discourse-Relation-Preserving Simplification:** preserve causal, concessive, and contrast relations through typed discourse planning. | 5 | 3 | 3 | 5 | 5 | 21 | Fallback; discourse annotation and reliable automatic evaluation are expensive. |
| 5 | **Denominator-/Quantity-Frame-Preserving Lay Summarization:** bind quantities to populations, time windows, and comparators before generation. | 5 | 3 | 4 | 5 | 5 | 22 | Retired before GPU after the source gate failed at commit `2d4b079`: `denominator=0<30`, `comparator=0<30`, `advance=false`, `human_evidence=false`. |
| 6 | **Targeted Concept Explanation with Context Contracts:** explain only reader-flagged concepts while preserving local claims. | 5 | 2 | 4 | 4 | 5 | 20 | Rejected: WikiDomains and targeted concept simplification already establish this task directly. |

The former provisional winner studied a linguistic failure rather than proposing another benchmark: lay rewriting can delete or strengthen hedges, modal auxiliaries, attribution, and their semantic scope. The proposed method represented each source uncertainty frame as `(cue, strength, scoped proposition, attribution)` and conditioned generation on preserving that frame while simplifying its realization. Primary comparisons would have needed to measure both accessibility and frame preservation; generic semantic similarity was insufficient.

The novelty claim was deliberately narrow. Prior work studies hedge identification, asks humans to use hedges during simplification, evaluates general meaning preservation, or produces minimally lossy summaries. A June 2026 clinical uncertainty benchmark also evaluates preservation. None of these observations alone established a new method contribution. ESP is no longer provisional because its own negative gate fired; this retirement does not select the next candidate.

## Second-pivot addendum

The initial ranking is retained as an audit record rather than rewritten after results. LAD was retired after two model families failed its predeclared mechanism gate. DCEA was then implemented and retired after its fixed-parser artifacts failed integrity, its interpretable outputs lacked the decisive redundancy separation, and a later closest-work search found explicit Shapley treatment of source redundancy and synergy.

The current provisional candidate is **Cross-Lingual Epistemic Preservation (CLEP)**: a matched study of whether models preserve speaker attribution, propositional polarity, and certainty when evidence language changes, plus a typed intermediate representation as a lightweight mitigation. It is not a benchmark proposal; the contribution must be a causal language-channel analysis and an auditable generation method. Provisional score: F=5, N=4, E=4, A=5, O=5, total=23. It remains behind a full-text collision gate and a two-family pilot.

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
| 1 | **Directional Counterfactual Evidence Audit:** replace an answer-bearing fact in a cited source and test whether the generated claim changes in the intervention's direction. | 5 | 4 | 5 | 5 | 5 | 24 | Historically selected provisionally; later retired after its own fixed-parser and redundancy gates failed. |
| 2 | **Claim-Preserving Provenance Repair:** minimally repair unsupported spans in an existing answer while preserving supported content and meaning. | 5 | 1 | 5 | 5 | 5 | 21 | Rejected: RARR (ACL 2023) already retrieves attribution and minimally edits unsupported LM output. |
| 3 | **Conflict-Preserving Synthesis:** retain attributed disagreement structure instead of flattening contradictory sources. | 4 | 2 | 4 | 5 | 5 | 20 | Rejected: MoDS (NAACL 2025) already targets balanced synthesis of opposing perspectives. |
| 4 | **Clarify-or-Abstain Evidence Triage:** choose answer, clarify, abstain, or acquire evidence under insufficiency/conflict. | 4 | 3 | 4 | 5 | 5 | 21 | Rejected as close to refusal/abstention and routing work. |
| 5 | **Memory-vs-Retrieval Conflict Routing:** select memory, retrieval, or reconciliation under context-memory conflict. | 4 | 3 | 4 | 4 | 5 | 20 | Rejected as crowded retrieval routing. |
| 6 | **Argument-Role Coverage Repair:** restore missing argumentative roles in long-document synthesis. | 3 | 1 | 3 | 5 | 5 | 17 | Rejected: Arg-LLaDA (ACL 2026) already performs sufficiency-guided iterative repair of unsupported, redundant, and incomplete spans. |

The selected problem is causal identification, not citation scoring or benchmark construction. Existing citation metrics test whether a source can support a claim; ContextCite and AttriBoT estimate source necessity mainly through removal and likelihood change. The proposed audit asks a different, directional question: when an answer-bearing source fact is minimally changed while identifiers, query, distractors, order, and surface envelope are controlled, does the model's claim and citation change in the predicted direction? This design is intended to expose two unresolved cases: causally inert but semantically supportive citations, and redundant support for which single-source removal understates evidence use. The novelty claim remains provisional until a direct pilot and full-text closest-work review pass.
