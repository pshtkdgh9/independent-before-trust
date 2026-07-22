# Cold Review Protocol

This directory is intentionally initialized before any scored review exists. A review may be added only after a complete anonymous PDF and its immutable evidence package are available. Topic notes, plans, mock outputs, and author summaries are not review inputs.

## Frozen review input

Each review round records:

- manuscript PDF SHA-256 and page count;
- supplement/archive SHA-256, if supplied;
- evidence-map revision and immutable result-artifact identifiers;
- review timestamp and persona;
- whether the reviewer had access to code or supplement;
- prompt/instructions used for the cold review.

Reviewers must not receive earlier reviews, intended scores, rebuttal language, or the terminal acceptance target. Every persona reads the same frozen submission independently.

## Required personas

1. ARR Area Chair / broad NLP significance;
2. empirical NLP / statistical validity;
3. NLP methods / causal identification and baselines;
4. resources and evaluation / artifacts and provenance;
5. ethics and reproducibility / disclosure and release risk.

## Required review fields

- score: `Strong Accept`, `Accept`, `Weak Accept`, `Borderline`, `Weak Reject`, or `Reject`;
- confidence;
- summary;
- strengths;
- weaknesses;
- missing citations;
- unsupported claims;
- reproducibility concerns;
- ethics or data concerns;
- exact blockers to acceptance;
- recommended decision.

## Integrity rules

- No score is created before the frozen PDF exists.
- Review text must cite manuscript pages/sections and evidence artifact paths.
- A reviewer cannot be asked to revise a score upward; a materially changed submission receives a new round.
- Failed gates and negative findings remain in the audit trail.
- The terminal gate requires five independent reviews with no `Reject` or `Weak Reject` and at least two `Strong Accept`; this file itself is not a review and supplies no score.

## Naming

Use `round-<NN>/reviewer-<NN>-<persona>.md`, with a `round_manifest.json` containing the frozen input hashes. The adversarial meta-review is stored separately at `results/strong_accept_loop/meta_review.md` after all five reviews are complete.
