# ESP Counterfactual Equivariance Design

## Goal

Test whether explicit epistemic-frame conditioning makes open-model lay rewrites respond to a controlled change in uncertainty strength while preserving the same underlying proposition. This is a method test, not a benchmark contribution, and it does not replace blinded human evaluation.

## Alternatives considered

1. **Natural-text minimal pairs only.** Highest ecological validity, but grammatical edits and proposition invariance require manual audit.
2. **Synthetic templates only.** Strongest causal isolation and easiest automatic scoring, but too weak for an ACL-family natural-language claim.
3. **Natural primary plus synthetic stress test (selected).** Use audited minimal edits of BioLaySumm scopes for the primary paired test and small hand-authored templates only to diagnose failure modes. This balances causal identification and natural-text relevance within one P100.

An NLI or LLM judge is rejected as the primary endpoint because it would replace the target semantic judgment with another opaque model. Automatic cue matching remains diagnostic.

## Natural minimal-pair contract

Each item contains one source sentence, one minimally edited counterfactual sentence, the unchanged propositional skeleton, original and counterfactual strength bins, attribution, edit span, and provenance link to the existing ESP item. Allowed transitions are adjacent bins only: `possible <-> likely` and `suggestive <-> likely`. Categorical transitions are excluded from the first run because deleting modals often changes tense or grammaticality.

Two isolated development auditors must verify that each pair is grammatical, changes only epistemic force, preserves polarity and all material arguments, and contains no new factual content. Any disagreement removes the pair before generation. These audits are not called human validation.

## Experimental cells

Cross two pinned model families (Phi-3.5 and Qwen2.5-1.5B) with two prompts: generic uncertainty preservation and explicit frame conditioning. Direct prompting is omitted because the feasibility run already shows generic is the stronger non-frame baseline and GPU budget should target the decisive comparison. Each retained pair produces an original and counterfactual rewrite under deterministic decoding.

## Outcomes and decision rule

Primary outcome: paired equivariance, meaning both rewrites express the same proposition and each preserves its assigned strength bin. Secondary outcomes: one-sided directional response, scope retention, unsupported additions, copying, readability, output length, and failures. Exact cue-bin matching is diagnostic only.

Advance ESP only if frame exceeds generic on paired equivariance in both model families under reliable blinded judgments and does not increase unsupported additions or copying. Retire or reframe ESP if the natural-pair audit cannot produce at least 12 valid pairs, if semantic judgment reliability remains inadequate after the frozen v1 rubric, or if either family shows no frame benefit.

## Reproducibility and boundaries

The manifest, validation reports, prompts, raw outputs, configs, environment, hashes, and analysis are versioned. Source text remains subject to the BioLaySumm/eLife provenance boundary. No retired LAD, DCEA, or CLEP result contributes to an ESP estimate. RAG is not claimed because no retriever is used.
