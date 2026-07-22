# Table Generation Contract

No empirical table exists yet. LaTeX tables are generated from recorded machine-readable results; values are not copied by hand.

## Planned tables

| ID | Purpose | Required input | Required fields |
|---|---|---|---|
| T1 | Dataset/model/protocol inventory | provenance manifest and run configs | dataset revision, model revision, license, split, seed, decoding, eligible and failed counts |
| T2 | Primary paired intervention | `paired_effects.json` | harmful revision, beneficial revision, paired difference, 95% interval, denominator |
| T3 | Fair method comparison | `method_comparison.json` | no-peer, peer exposure, majority, confidence, evidence validation, exact/semantic deduplication, LAD |
| T4 | Ablations and robustness | registered ablation/robustness summaries | component removed, estimate, interval, model, task, seed regime |
| T5 | Error analysis | registered examples and counts | category, count, rate, representative artifact identifier |

External paper numbers may appear only in a separately labeled contextual related-work table and never in T2--T4. Each generated table requires an input/script/output checksum sidecar and a validation that manuscript prose matches every cited cell.
