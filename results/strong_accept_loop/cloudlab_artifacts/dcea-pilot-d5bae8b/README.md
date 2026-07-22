# DCEA falsification pilot

- Execution commit: `d5bae8bd802970603b3723c077919a8693cf2b60`
- Hardware: CloudLab Wisconsin `c240g5-110121`, Tesla P100 12 GB
- Models: pinned Phi-3.5-mini-instruct and Qwen2.5-1.5B-Instruct snapshots already recorded in `data_provenance.md`
- Design: 20 synthetic templates expanded to 80 cells per run; ordinary and contrastive prompts for both model families
- Completion: all four directories contain `RUN_COMPLETE`, 80 raw generations, config, templates, and stored metrics
- Integrity: every run is diagnostic-only because the fixed two-line parser rejected at least one answer or citation. The independent validator records `status: fail` without deleting or repairing raw outputs.

The observed Phi runs do not support the predeclared mechanism: singleton and redundant pair-flip rates are both `1.0`, and contrastive prompting does not improve counterfactual following. Qwen frequently used unrequested sentence or parenthetical formats, so its exact-format outcome metrics are not claim-grade. The artifacts may justify a stop/pivot decision only; they cannot support DCEA-C1--C3.
