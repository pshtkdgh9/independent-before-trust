# Evidence-State Triage Candidate Audit Summary

Date: 2026-07-23

Status: retired before GPU.

Evidence class: `model_agent_development_only`.

Human evidence: `false`.

## Decision

Evidence-State Triage is retired as a candidate before GPU experiments. It does not support a headline claim.

The stop reasons are:

- novelty/action aggregation collision;
- invalid conflict construction.

The design, schema, builder, provenance path, and candidate pack are preserved as negative auditable artifacts. They must not be promoted into findings or used to justify a larger run.

## Audit Counts

| File | Rows | SUPPORTS | REFUTES |
|---|---:|---:|---:|
| `candidate_audit_a.jsonl` | 24 | 12 | 12 |
| `candidate_audit_b.jsonl` | 24 | 12 | 12 |

Intersection: 13 candidate IDs.

| Overlap field | Agreement |
|---|---:|
| Label | 13/13 |
| Sufficiency usability | 13/13 |
| Conflict usability | 7/13 |
| Ambiguity | 13/13 |
| Self-contained evidence | 13/13 |
| Natural incompatible sentence exists | 6/13 |

## Interpretation

The balanced rows show that both audit lanes could find self-contained sufficiency examples, but the overlap does not validate the conflict construction. The conflict-usability and natural-incompatible-sentence disagreements show that the candidate would rely on constructed conflict states rather than a clean natural conflict source.

The audit therefore records a negative development result only. It is not human annotation, not a validated task, and not a manuscript evidence package.

## Preserved Negative Artifacts

- `src/evidence_state/schema.py`
- `src/evidence_state/builder.py`
- `src/evidence_state/provenance.py`
- `data/evidence_state/fever_candidate_source_pack.jsonl`
- `data/evidence_state/source_manifest.jsonl`
- `scripts/build_evidence_state_items.py`
- `results/strong_accept_loop/evidence_state_triage/candidate_audit_a.jsonl`
- `results/strong_accept_loop/evidence_state_triage/candidate_audit_b.jsonl`

## Next Audit Target

Next audit target only, not selected: Denominator-Aware Numerical Lay Summarization.
