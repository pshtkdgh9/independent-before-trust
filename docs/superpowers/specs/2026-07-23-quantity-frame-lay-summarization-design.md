# Quantity-Frame-Preserving Lay Summarization Design

## Status and decision boundary

This document specifies a candidate method study. It does not select the topic, support a manuscript claim, or authorize a main experiment. The candidate advances to a small audited pilot only if the closest-work and data audits confirm the narrow gap below. It is retired if the gap collapses into generic numerical factuality, PICO preservation, or benchmark construction.

## Research question

Can a source-grounded quantity frame improve preservation of quantitative meaning during lay summarization by keeping a number bound to its denominator or base population, subgroup, time window, comparator, and unit?

The primary object is the binding between a value and its measurement frame. Readability, generic factuality, and overall summary quality are secondary constraints. The study does not claim that all medical or scientific factuality errors are numerical, that a structured representation guarantees clinical correctness, or that the method improves retrieval-augmented generation.

## Alternatives considered

1. **Generic numerical-factuality prompting.** Rejected because numerical summarization and factuality correction are crowded, and an instruction to “preserve numbers” does not isolate a reusable linguistic mechanism.
2. **PICO-conditioned lay summarization.** Rejected because FactPICO already makes population, intervention, comparator, outcome, and findings central to factuality evaluation. A PICO-only method would have an unacceptable collision risk.
3. **Typed quantity-frame conditioning with counterfactual equivariance.** Recommended for the pilot. It has a narrower scientific question: whether explicit value-to-frame bindings survive simplification and respond correctly when exactly one frame slot changes.

## Quantity-frame contract

Each auditable quantity mention is represented as:

```text
(value, denominator_or_base, subgroup, time_window, comparator, unit, source_span)
```

`value` and `source_span` are required. Other fields may be explicitly `not_stated`; they may not be inferred from world knowledge. A frame is valid only when every populated field is licensed by the source span or its local evidence window. The representation must distinguish a missing slot from a slot whose value is zero, unknown, or not applicable.

## Data path

The first pilot uses two independently sourced public lay-summarization corpora only after exact revisions, files, licenses, checksums, and redistribution boundaries are recorded. The preferred primary corpus is Cochrane simplification because its source/target pairs are short enough for one P100 and frequently contain effect sizes, counts, percentages, and comparison language. The replication corpus is selected between the canonical PLOS/eLife scientific lay-summarization release and CARES after a source audit measures the prevalence and recoverability of complete quantity frames.

No item from the submitted trust/reputation paper, LAD, DCEA, CLEP, ESP, evidence-state triage, or their output packets may enter the sample. Existing repository code may contribute only generic hashing, immutable-run, model-loading, and artifact-validation patterns, with each reused component recorded.

## Candidate construction and audit

Source examples are scanned in deterministic source order for quantity candidates. Automatic extraction retrieves candidates only; it does not create gold frames. A fixed audit packet must record whether the quantity is source-grounded, whether each slot is stated, whether the target summary preserves each stated slot, and whether a minimal one-slot counterfactual can be written without changing the surrounding claim.

Two independent audit lanes inspect an overlapping subset. Agreement is reported separately for frame validity, denominator/base binding, comparator binding, time-window binding, subgroup binding, and counterfactual validity. Model-agent audits remain development evidence and are never called human annotations. A claim-grade study requires qualified human annotation or a deterministic endpoint whose validity has been independently established.

## Methods and baselines

The pilot compares, within each open model family:

1. direct lay summarization;
2. a generic instruction to preserve quantitative details;
3. extracted quantity-frame conditioning;
4. an oracle-frame condition only if independently reviewed frames exist.

The quantity-frame method first emits or receives the typed frame and then generates a lay summary constrained to preserve populated slots. The direct and generic conditions receive the same source text and output budget. No method receives the reference summary at generation time.

The two initial model families are the already pinned Phi-3.5 Mini Instruct and Qwen2.5-1.5B Instruct snapshots. Their prior outputs are not reused. Exact generation parameters, chat templates, library versions, and execution commits are captured anew.

## Counterfactual design

For each valid base item, one counterfactual changes exactly one of denominator/base population, comparator, time window, subgroup, value, or unit while preserving topic, syntax envelope, non-target facts, and output instruction. The expected response is a corresponding change in the generated quantity frame and lay statement, with unrelated content stable.

Counterfactuals are rejected if the edit creates an implausible statement, changes clinical direction through an unrecorded slot, leaks the condition through labels, or makes the target recoverable from formatting. Natural-source performance and controlled counterfactual equivariance are reported separately.

## Metrics

Primary metrics are slot-level exact or normalized match for denominator/base, comparator, time window, subgroup, value, and unit; all-stated-slots exact match; unsupported-number rate; and paired counterfactual equivariance. Denominator and comparator error rates are always reported separately.

Secondary metrics are content coverage, source copying, readability, output length, parse failures, and unsupported non-numeric additions. Automatic lexical metrics are diagnostic, not sufficient headline evidence. Human judgments, if run, must score denominator correctness, comparator correctness, quantitative overstatement or omission, and lay usefulness under blinded condition labels.

## Pilot and kill gate

The pre-GPU source audit must find at least 100 valid natural examples across two corpora, with at least 30 denominator/base cases and 30 comparator cases, and at least 60 valid one-slot counterfactual pairs. If not, retire or rescope before generation.

The GPU pilot uses a fixed 100-example development slice and both model families. Advance only if all of the following hold:

- the structured method reduces the combined denominator/comparator error rate by at least 10 absolute percentage points versus the strongest observed non-oracle baseline in each model family;
- neither denominator error nor comparator error worsens in either family;
- paired counterfactual equivariance improves in both families;
- unsupported-number rate and blinded lay-usefulness are no worse than the strongest baseline;
- all artifact-integrity reports pass under the frozen parser and schema.

If any condition fails, retire the method rather than tuning labels, selecting a favorable family, changing the parser after outputs are seen, or reframing the result as a benchmark contribution.

## Error handling and evidence limits

Malformed structured outputs are failures, not silently repaired. Missing source slots remain `not_stated`; generation is penalized for inventing them. Infrastructure failures may be rerun from the same immutable commit and configuration, while scientific failures remain in the audit trail.

No abstract, introduction, or contribution claim is written from this pilot until the advance gate passes. External paper numbers are contextual only and are never presented as same-regime comparisons. RAG is motivational framing only unless a separate end-to-end retrieval experiment is designed and executed.

## Venue and ethics fit

The candidate is an NLP method and controlled linguistic-faithfulness study about semantic binding during lay rewriting, not a leaderboard or dataset paper. It fits summarization, generation, factuality, and responsible biomedical NLP. The work uses public scholarly or trial documents, avoids private health records, documents redistribution constraints, and requires explicit limitations against clinical-use inference.
