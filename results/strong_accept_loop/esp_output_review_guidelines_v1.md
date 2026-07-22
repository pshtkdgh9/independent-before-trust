# ESP Output Review Guidelines v1

## Status and use

These guidelines evaluate whether a lay rewrite preserves one pre-annotated epistemic proposition. They were frozen after diagnosing disagreement in the v0 development audits. A new audit must not consult model identity, prompt condition, automatic cue scores, or prior reviewer labels. Model-agent audits are calibration evidence only; only genuinely independent human judgments may be reported as human evaluation or inter-annotator agreement.

## Unit of judgment

For each row, define the target proposition **T** from `gold_scope`, `gold_strength`, and `gold_attribution`. Split the output into atomic propositions. All semantic labels refer to T, not to any other finding in the source.

Annotate in this order: `scope_preserved`, `strength_preserved`, `unsupported_addition`, then `acceptable_lay_rewrite`.

## Scope preservation

- `yes`: the output expresses a lay paraphrase of T with all truth-conditional arguments that materially identify it: entity, relation, polarity, population or condition, comparator, and attribution where relevant. The epistemic operator must attach to T.
- `no`: T is omitted; replaced by another result; reverses polarity; changes a material argument, population, condition, or comparator; or places a hedge on a different proposition.
- `unclear`: use only when corruption or unresolved coreference makes both entailment and contradiction genuinely undecidable. Omission is `no`, not `unclear`.

## Strength preservation

Use the ordered bins `categorical > likely/probable > suggestive/evidence-consistent > possible/may/might/could`.

- `yes`: T is present and the output remains in the same bin. Cue-free wording counts only when it is explicitly nonassertive and semantically equivalent.
- `no`: T moves upward or downward to another bin, becomes categorical, changes direction, or is omitted.
- `unclear`: T is present but its modal force remains linguistically ambiguous after careful reading.

Invariant: `scope_preserved=no` forces `strength_preserved=no`.

## Unsupported addition

- `yes`: the output asserts a material proposition not entailed by the source, including a new cause, mechanism, population, intervention recommendation or effect, direction, or generalization.
- `no`: every asserted proposition is entailed by the source. Benign definitions, acronym expansions, and strictly entailed compression are allowed.
- `unclear`: use only when the full supplied source does not resolve whether the addition is entailed.

## Acceptable lay rewrite

- `yes` only if scope and strength are both `yes`, unsupported addition is `no`, there is no material contradiction, and the sentence is self-contained and understandable to an educated non-specialist.
- `no` if any semantic prerequisite fails, T is omitted, or the output is a fragment or unintelligible.
- `unclear` only for borderline readability after all semantic prerequisites pass.

Invariants: `acceptable_lay_rewrite=yes` requires `scope_preserved=yes`, `strength_preserved=yes`, and `unsupported_addition=no`. Fluency alone is never sufficient.

## Reliability and decision gate

Before full human annotation, two independent annotators must complete a 10--15 item calibration set spanning target omission, wrong-scope hedges, upward and downward strength shifts, unsupported mechanisms or recommendations, and faithful paraphrases. Disagreements are discussed only during calibration. The full packet is then labeled independently and blinded.

Report raw agreement and a chance-corrected coefficient for each semantic field. Freeze the coefficient and threshold before viewing condition labels. If scope or strength reliability misses the predeclared threshold after one guideline revision and adjudication round, ESP is retired or reframed without that claim. Development model-agent agreement can reveal ambiguity but cannot pass this gate.
