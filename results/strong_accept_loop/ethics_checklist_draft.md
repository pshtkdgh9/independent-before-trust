# Responsible NLP Research Checklist Draft

Policy source: https://aclrollingreview.org/static/responsibleNLPresearch.pdf. This is a working response map, not the final OpenReview form. Section/line references remain pending until the manuscript exists.

## Mandatory all-submission items

- **Limitations described:** planned; mandatory manuscript section. Must cover open-model/task scope, synthetic lineage transformations, parser error, source-label leakage, contamination, compute limits, and non-human equivalence.
- **Potential risks discussed:** planned; repeated-source manipulation could inform persuasion or misinformation systems. Release only bounded synthetic transformations and defensive analysis; no targeting of real people or live platforms.
- **Artifacts used/created:** yes. New code, processed paired interventions, prompts, generations, and aggregate results will be documented and released when source terms allow.
- **Licenses/terms:** the current pilot dataset is pinned BIG-bench under Apache-2.0; the selected, not-yet-downloaded Phi-3.5 Mini model reports an MIT license. Exact URLs and revisions are in `data_provenance.md`. Any added item without verified usable terms is excluded.
- **Personal or sensitive data:** the current pilot uses synthetic object-order reasoning and contains no expected personal data. Added task families must be screened and documented before use.

## Data and artifacts

- Record URLs, access times, versions, licenses, bytes, SHA-256, paths, commands, transformations, filtering, splits, and redistribution status.
- Preserve raw sources immutably; transformations are deterministic and versioned.
- Do not redistribute upstream text if terms prohibit it; release IDs/scripts/checksums instead.
- Document any offensive, political, medical, or identifying content and the exposure protocol. Default task selection avoids sensitive domains.
- Report whether dataset labels were human-produced and the original annotation process; this project does not silently relabel human data with an LLM judge.

## Computational experiments

- Report model repository/revision/license, tokenizer/chat template, quantization/dtype, decoding, seeds, hardware, software, runtime, token counts, peak memory, and total compute estimate.
- Report hyperparameter selection and all planned conditions, including failed/negative runs.
- Use paired confidence intervals/effect sizes; do not present external numbers as head-to-head results.
- Archive exact configs, raw generations, parsing failures, and metric code.

## Human participants and annotation

- No new human-subject study is currently planned.
- No crowd annotation is currently planned.
- If either becomes necessary, pause execution and document institutional review/consent, recruitment, compensation, demographics, instructions, quality control, privacy, and data withdrawal before collection.

## AI assistance

- Codex assists with research planning, code, analysis, and drafting under author supervision.
- Authors must verify all citations, methods, results, prose, and ethical decisions.
- The final disclosure will follow the current ACL disclosure policy and institutional requirements.
- Unpublished manuscripts/private data are not sent to external model providers without explicit authorization.

## Current checklist verdict

`INCOMPLETE`: policy has been reviewed and requirements routed to artifacts; the pilot dataset and model candidate are selected with visible licenses. Model-file checksums, actual compute totals, manuscript line references, and the final disclosure do not yet exist.
