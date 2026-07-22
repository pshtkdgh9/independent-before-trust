# Evidence-State Triage Policy Design

## Goal

Design a falsifiable NLP method study for evidence-state triage: given a user query and a controlled evidence pack, decide whether the system should `clarify`, `retrieve`, or `abstain`. The downstream answer remains out of scope for the primary claim.

The core novelty is the paired causal evidence-state intervention. The project is not a benchmark-construction paper, not a generic abstention paper, and not another RAG routing benchmark. A task dataset may be built only as an instrument for testing the intervention.

## Evidence-State Contract

Each item contains a user query, a frozen answer target used only for validation, and an evidence pack whose state is one of:

- `insufficient`: available evidence lacks a necessary fact or disambiguating slot.
- `conflict`: available evidence contains mutually incompatible claims that cannot both support one answer.
- `sufficient`: available evidence is internally consistent and contains enough support for a downstream answer.

The triage action space is:

- `clarify`: ask for missing intent, entity, time, scope, or user preference when the evidence need is query-side ambiguity.
- `retrieve`: acquire additional evidence when the query is clear but the current evidence pack is incomplete.
- `abstain`: refuse to answer when the evidence pack is contradictory, unsafe to resolve from available data, or otherwise non-recoverable without unsupported judgment.

No primary metric rewards answer generation. Answer correctness is downstream and used only to audit false-answer leakage when a baseline or method violates the triage contract.

## Paired Intervention Design

Each retained base item must produce matched evidence-state variants while holding query wording, answer target, topic, surface envelope, source identifiers, and distractor count as stable as possible.

Required pairs:

- `sufficient -> insufficient`: remove or mask only the minimal evidence slot needed to justify the answer.
- `sufficient -> conflict`: replace or add one incompatible evidence statement while preserving the answerable surface frame.
- `insufficient -> conflict`: keep the same query and topic while changing whether the blocking state is missing evidence or contradictory evidence.

The decisive behavioral signal is a directional action flip. A state-aware method should move from `retrieve` or answer-attempt behavior under insufficiency to `abstain` under conflict, and from premature `abstain` to `clarify` when the missing information is user-intent ambiguity.

## Closest-Work Boundary

Search evidence as of 2026-07-23 supports only a search-limited inference that the exact combination has not been located: paired causal evidence-state interventions over insufficiency and conflict, with an action policy that separates `clarify`, `retrieve`, and `abstain`, while keeping answer generation downstream.

Primary adjacent works to treat as closest boundaries:

- Atanasova et al., TACL 2022, fact checking with insufficient evidence.
- Cole et al., EMNLP 2023, selectively answering ambiguous questions.
- Liu et al., ACL 2025, *Do not Abstain! Identify and Solve the Uncertainty*.
- Nguyen et al., Findings IJCNLP-AACL 2025, *When in Doubt, Ask First*.
- Zhang et al., Findings EMNLP 2025, KBM for adaptive retrieval.
- Abstain-R1, 2026, calibrated abstention and post-refusal clarification.
- CARE-family conflict-aware RAG work.

The study cannot claim first work on insufficient evidence, ambiguity, knowledge-boundary retrieval, abstention, clarification, conflict-aware RAG, or refusal training. Its bounded claim is the causal policy distinction across evidence states under paired interventions.

## Data and Licensing Boundary

The pilot must start from public, license-compatible source material with recorded source URL, license/terms, revision if available, bytes, checksum, preprocessing command, and storage path before any generation run. No URL, checksum, license, or source count may be stated until verified and recorded.

Allowed source families include open QA, fact-checking, or document-grounded QA corpora only after their licenses permit derived intervention items and retained evidence snippets. If a license blocks redistribution, the pilot must store only permitted identifiers and derived metadata.

## Baselines

The method must beat the strongest baseline in each evidence state, not only a weak direct-answer prompt.

Required baseline families:

- direct answer-or-abstain prompt;
- selective QA confidence or self-consistency gate;
- ambiguity-aware clarification prompt;
- adaptive retrieval or knowledge-boundary router;
- conflict-aware RAG or evidence-reconciliation prompt;
- oracle-style state label prompt as a diagnostic upper bound, not a deployable method.

## Decision Rule

Advance only if all gates pass:

1. The state-aware method beats the strongest baseline on macro-F1 for triage actions.
2. The state-aware method beats the strongest baseline on selective risk separately for insufficiency and conflict.
3. More than 50% of paired interventions produce the predicted directional action flip.
4. The result holds in two independently developed open model families.
5. The method has no worse false-answer rate than the strongest baseline.

Retire the topic if any gate fails. Do not repair labels, rerank models, or narrow the item subset after seeing outcomes.

## Non-Reuse Boundary

LAD, DCEA, CLEP, and ESP remain retired audit trails. Their prose, claims, evidence, figures, and result tables cannot be reused. Generic infrastructure may be reused only when independently documented and not presented as a scientific contribution. The manuscript is out of scope for this topic-stage work.
