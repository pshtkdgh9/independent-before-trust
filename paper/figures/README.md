# Figure Generation Contract

No empirical figure exists yet. Figures are generated only after the referenced result artifacts are immutable and their checksums are recorded.

## Planned figures

| ID | Purpose | Required input | Generation rule |
|---|---|---|---|
| F1 | Paired harmful and beneficial revision differences for COMMON vs INDEPENDENT | `results/strong_accept_loop/statistics/paired_effects.json` | Plot paired effect estimates with bootstrap 95% intervals; show eligible instance counts and parser failures. |
| F2 | Nominal support, effective support, and corroboration gap | `results/strong_accept_loop/statistics/support_diagnostics.parquet` | Aggregate only pre-specified strata; keep model/task facets visible. |
| F3 | Baseline and LAD comparison | `results/strong_accept_loop/statistics/method_comparison.json` | Use rerun values from the shared protocol only; never import numerical values from prior papers. |
| F4 | Error taxonomy | `results/strong_accept_loop/error_analysis/error_counts.json` | Show all registered categories, including zero counts and lineage/parser failures. |

Every generation script must write a sidecar JSON containing input paths and SHA-256 values, script revision, command, library versions, output dimensions, and output SHA-256. Captions must state the model/task regime and uncertainty unit. Negative and null effects remain visible.
