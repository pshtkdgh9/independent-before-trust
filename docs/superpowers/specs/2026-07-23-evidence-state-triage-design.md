# Evidence-State Triage Router Design

## Goal

Test whether a paired causal evidence-state router can choose `clarify`, `retrieve`, or `abstain` before a downstream answerer, and whether that router reduces unsafe answers under insufficiency and conflict without suppressing answerable cases. This is a method test, not a benchmark contribution.

The object of study is the routing intervention: the same user question is paired with minimally changed evidence states that make one route correct and another route incorrect. The answer generator is downstream and fixed within each model family so the estimate targets the router, not a new answer-generation benchmark.

## Core contract

Each item contains one question, a stable answerability target, and paired evidence states. The evidence-state label is one of:

- `sufficient`: evidence directly supports a bounded answer.
- `insufficient`: evidence is relevant but missing a necessary premise or value.
- `conflict`: evidence contains incompatible claims that cannot both be true under the question scope.

The router emits exactly one action: `clarify`, `retrieve`, or `abstain`. The downstream answerer runs only when the route permits an answer. A false answer is any non-abstained final response that asserts a target fact contradicted by the item key, unsupported by the supplied evidence, or resolved without the required clarification or retrieval.

## Paired causal design

Pairs isolate evidence-state changes while preserving the user question and topic. For insufficiency pairs, the edit withholds or restores the one fact needed to answer. For conflict pairs, the edit inserts or removes a conflicting evidence sentence while preserving all other context. Sufficient controls preserve the same answer target without introducing uncertainty cues.

The primary causal signal is directional paired flipping: when the evidence state changes, the router should change action in the expected direction. A result must show more than 50% directional paired flips for the targeted insufficiency and conflict transitions; otherwise the method is treated as non-responsive.

## Closest-work distinctions

This is not a hallucination benchmark because the endpoint is a pre-answer routing decision under controlled evidence states, not only the truthfulness of generated answers. It is not a selective QA benchmark because selective risk is measured separately for insufficiency and conflict and tied to paired route flips. It is not a retrieval benchmark because `retrieve` is an action choice, not an evaluation of retriever recall. It is not an uncertainty-calibration benchmark because confidence is not the primary output and no probability calibration claim is made.

The closest empirical neighbors are answerability-aware QA, abstention/selective prediction, clarification-question generation, conflict-aware QA, and retrieval-augmented QA safety. The distinction is the paired causal manipulation of evidence state with a router that can choose among clarification, retrieval, and abstention before a fixed downstream answerer.

## Data and provenance

Use only public, licensed, redistributable or clearly citeable sources whose terms permit research use and derived annotation. Every source row must record source name, source URL or accession, license or terms URL, retrieval date, raw-record hash, transformation script, derived-item hash, and whether the text can be redistributed in repository artifacts.

No old manuscript dataset, retired experiment artifact, unpublished review packet, or previously rejected JSONL may be reused as item content. Prior artifacts may inform file naming and reproducibility conventions only. Any item without auditable public provenance is excluded before model execution.

## Models and execution

Run two open model families with deterministic decoding. The default families are Phi and Qwen because the repository already has CloudLab-oriented open-model execution patterns for them, but the implementation plan may pin exact current checkpoints during execution readiness review.

Run on CloudLab with immutable execution commits, captured environment, raw outputs, configs, validation reports, and hashes. Long GPU jobs are allowed only after local unit tests and dry-run validation pass.

## Baselines

The strongest baseline is selected from:

1. Direct answerer with no router.
2. Always answer when evidence is non-empty.
3. Always abstain on explicit conflict cues.
4. Generic answerability classifier routing to answer or abstain only.
5. Prompt-only triage without paired evidence-state conditioning.

The router advances only against the strongest observed baseline, not against a convenient weak baseline.

## Metrics

Primary routing metrics are macro-F1 over `clarify`, `retrieve`, and `abstain`, plus class-specific macro-F1 slices for insufficiency and conflict. Primary safety metrics are selective risk for insufficiency and conflict, computed separately so a gain on one state cannot hide failure on the other.

Secondary metrics are directional paired flips, false-answer rate, coverage, final-answer exactness for sufficient cases, route/action invalidity, unsupported additions, and answer latency or token budget if captured by the runner.

## Kill gate

Advance only if the paired router beats the strongest baseline on macro-F1 and on selective risk separately for insufficiency and conflict, shows more than 50% directional paired flips, and has no worse false-answer rate than the strongest baseline. If any condition fails, retire this method direction rather than reframing a negative result as a benchmark contribution.

## Boundaries

Human or model-agent labels used during development are not claimed as final human evidence. Model judges may be used for diagnostics but not as the sole primary endpoint unless the design is explicitly revised and re-approved. The final writeup must state that this is a causal method probe over evidence-state routing and must not claim a general benchmark, dataset contribution, or broad hallucination-safety solution.
