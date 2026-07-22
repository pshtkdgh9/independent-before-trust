# Adversarial Meta-Review Protocol

**Status:** NOT RUN. No submit-readiness verdict exists because the frozen anonymous manuscript, evidence package, and five independent cold reviews do not yet exist.

## Preconditions

The meta-review may run only when one review-round manifest records the SHA-256 and page count of the anonymous PDF, the supplement/archive SHA-256 when supplied, the evidence-map revision, and exactly five independently produced reviews conforming to `cold_reviews/README.md`. All reviews must evaluate the same frozen inputs without access to other reviewers' reports or the target score distribution.

## Adversarial questions

The meta-reviewer must try to falsify submission readiness by checking:

1. whether the central research question is an NLP/CL mechanism question rather than a benchmark leaderboard exercise;
2. whether each abstract and introduction claim is no stronger than a mapped immutable result artifact;
3. whether the COMMON-versus-INDEPENDENT contrast holds message content, correctness, confidence, order, and nominal peer count fixed;
4. whether alternative explanations survive the baselines, ablations, robustness tests, uncertainty estimates, and error analysis;
5. whether external paper numbers are presented only as contextual prior results and never as same-regime head-to-head evidence;
6. whether RAG, human-behavior, deployment, or general multi-agent claims exceed the actual end-to-end evidence;
7. whether negative or null findings are visible and reflected in weakened claims;
8. whether data, model, code, prompts, seeds, hardware, licenses, preprocessing, and artifact hashes are sufficient for reproduction;
9. whether the new manuscript is independently written and evidentially distinct from the existing journal submission; and
10. whether anonymity, page limits, limitations, ethics, and supplementary-material rules are satisfied.

## Decision rule

`SUBMIT-READY` is permitted only if all five reviews contain neither `Reject` nor `Weak Reject`, at least two are `Strong Accept`, every reviewer blocker is either resolved in the frozen revision or explicitly shown to be non-blocking with evidence, every headline claim maps to an artifact, provenance is complete, the official-style PDF builds without errors, and the final cleanup gate passes. Any unmet condition yields `NOT SUBMIT-READY` and identifies exactly one highest-ROI blocker for the next iteration.

## Required output when run

- frozen round and input hashes;
- reviewer-score table and confidence values;
- cross-review agreements and disagreements;
- unsupported-claim and missing-evidence audit;
- publication-ethics and venue-compliance audit;
- highest-ROI blocker, if any;
- verdict: `SUBMIT-READY` or `NOT SUBMIT-READY`;
- artifact paths supporting the verdict.

This protocol is not itself evidence of acceptance quality and must never be counted as a cold review.
