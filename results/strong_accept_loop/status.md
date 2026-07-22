# Strong-Accept Loop Status

Date: 2026-07-23

- Phase: LAD, DCEA, CLEP, and ESP retired; topic search reopened
- Primary target: EACL 2027 long paper via ARR 2026 August cycle
- Backup: a later ARR cycle and compatible ACL-family venue if evidence is not ready
- Selected direction: none; do not select the next topic until a new evidence-first search passes its gates
- Terminal gate: not satisfied

## Completed

- Official EACL 2027 and current ARR policy check.
- Eight non-benchmark topic candidates compared.
- Initial Evidence-First Deliberation and parallel conflict-aware RAG choices explicitly reconsidered.
- Twenty-eight-work novelty matrix and direct topic-stage overlap audit against the located CaliTrust manuscript.
- Publication-ethics boundary, initial provenance register, evidence map, and LAD experiment plan.
- Independent Git repository boundary and target remote established.
- Deterministic lineage roots, effective-support metrics, paired intervention generator, and mock-pilot serialization tests.
- Pinned Hugging Face snapshot downloader, file-level provenance hashing, condition-blind pilot prompt, raw-output retention, and CloudLab inference CLI.
- Pinned Apache-2.0 BIG-bench logical-deduction source, raw checksum, preprocessing record, and 50 private-first pilot items.
- Adaptive protocol that elicits the model's private answer before constructing its matched lineage intervention.
- Anonymous evidence-bounded manuscript scaffold and review contracts pushed in `d824fb2`.
- Paired COMMON-minus-INDEPENDENT bootstrap analysis, candidate-bounded answer normalization, and tamper-resistant artifact validation exercised by 34 passing unit tests and an independent scoped code review.
- Dedicated `c240g5` CloudLab RSpec/profile created after the unavailable `d7525` allocation failed transparently.
- Direct comparison separates the prior and new research questions, contributions, task framings, datasets/evaluation packages, claim sets, writing, and experimental evidence; the current 13 LAD research documents share zero normalized contiguous 8-token sequences with the prior source.

## In progress

- Full-text verification of closest competing methods.
- CloudLab experiment `cbnu-ai-lab/lad-phi35-p100` remains ready on Wisconsin node `c240g5-110121` with verified P100/CUDA access.
- First compatibility-fixed 50-item run completed at exact execution commit `0462b68`; its strict parser failure is preserved as diagnostic evidence.
- Bounded-parser rerun completed at exact execution commit `e53721e`: 50 baseline and 100 paired generations, zero parse failures, and validator status `pass`.
- Fixed-protocol Qwen2.5-1.5B replication completed at exact execution commit `0db697f`: 50 baseline outputs, 47 paired items, 94 revision generations, and 45 complete parsed pairs.
- The Qwen artifact validator reproduces all stored metrics and hashes; it correctly reports three unpaired baseline failures and five total parse failures rather than promoting the run.
- The predeclared LAD two-family kill criterion fired: Qwen made zero revisions in either condition across all 45 complete pairs, while the validated Phi result was negative/mixed. LAD is retired rather than selectively scaled.
- DCEA's four CloudLab cells completed at execution commit `d5bae8b`: 320 raw generations are preserved with configs, manifests, timestamps, hashes, and validator reports.
- DCEA was retired without parser repair or favorable reruns: every fixed-parser integrity report is `fail`, the interpretable Phi pair-flip rates did not distinguish singleton from redundant support, and the contrastive condition did not improve Phi directional following.
- CLEP protocol v1 completed 72 CloudLab generations at `bbf75d1` across two models and three methods. All six integrity reports are `fail`; the exact proposition field was underspecified and output-format compliance was incomplete. The raw artifacts are retained as diagnostic only and will not be rescored.
- CLEP closed-label protocol v2 completed 144 new generations at `fa3102a`; all six integrity reports pass. Language effects were not directionally consistent across English, Korean, and Spanish, and typed generation improved Qwen but not Phi relative to translate-then-classify.
- A third-pivot search compared six public-data method candidates. Question-guided simplification repair and ToTTo input repair were rejected after direct 2024--2025 collisions; epistemic-scope-preserving lay summarization is provisional pending full-text and data gates.
- Pinned BioLaySumm eLife revision `144e9c785e3a309da804eb6786feb38e6596f390`; checksum-verified validation and blind-test splits were acquired, and a deterministic 40-frame/31-document development manifest was built from abstract sections.
- Two isolated agent annotation lanes applied the frozen v0 guidelines to all 40 candidates. They agreed on all four controlled labels and rejected the same two non-epistemic capability uses; this is development-label consistency, not human inter-annotator evidence.
- Six deterministic ESP cells completed on CloudLab at commit `beca9cc`: Phi-3.5 and Qwen2.5-1.5B crossed with direct, generic-preservation, and explicit-frame prompts, with 38/38 non-empty generations per cell.
- Automatic cue preservation increased from generic to frame for both families (Phi `0.3684` to `0.5789`; Qwen `0.2368` to `0.3947`), but this metric remains diagnostic only.
- Two condition-blind model-agent audits covered all 228 outputs. Strict two-reviewer strength/scope consensus favored frame over generic in both families, but exact agreement was only `0.640` for strength, `0.443` for scope, and `0.268` for overall acceptability. These audits are development evidence, not human judgments.
- A failure analysis froze the v1 semantic rubric: omitted targets are `scope=no`, wrong-scope hedges do not preserve strength, and acceptability is conjunctive over semantic fidelity and readability. Two new blinded model-agent audits improved raw agreement to `0.895` strength, `0.689` scope, `0.811` unsupported additions, and `0.899` acceptability. One attempted lane was discarded before writing after accidental exposure to old labels; a completed lane consulted only another file's field names, not labels, and this protocol deviation is retained. None of these audits is human evidence.
- ESP's natural-text counterfactual negative gate is complete in `esp_counterfactual/review_summary_v1.json`: Phi passes (`advance=true`), Qwen fails (`advance=false`), and the overall gate is `advance=false`. The evidence class is `model_agent_development_only` and `human_evidence=false`, so ESP is retired as the headline candidate rather than selectively scaled.

## Blocking evidence

- ESP cannot be promoted: the counterfactual gate did not pass across two families, Qwen failed the gate, the overall gate is `advance=false`, and the review summary explicitly records model-agent development evidence only with `human_evidence=false`.
- DCEA cannot be promoted: its required citation format failed in all four cells, its predicted redundancy separation was absent in the interpretable Phi outputs, and a 2025 Shapley source-attribution paper directly covers redundancy/complementarity/synergy.
- CPR was rejected after the initial post-LAD shortlist because RARR (ACL 2023) already performs attribution-assisted minimal repair of unsupported LM output.
- Generic causal context attribution is also prior work: ContextCite (NeurIPS 2024) and AttriBoT (ICLR 2025) require the new topic to focus narrowly on directional replacement interventions and redundancy, not source removal alone.
- The first full run had a `0.48` strict-format baseline parse-failure rate and only 26 paired items; it remains diagnostic evidence, not a headline result.
- The validated rerun's harmful difference was `-0.04545` (CI `[-0.13636, 0]`) and beneficial difference was `+0.07143` (CI `[0, 0.17857]`), both COMMON-minus-INDEPENDENT and both contrary to the anticipated direction.
- The first pilot dataset is recorded, but additional main-experiment task families remain unselected.
- The first `d7525` allocation failed because zero nodes were available; the failure is recorded in `cloudlab_attempts.md`.
- The first real invocation exposed and preserved a `transformers==5.14.1` incompatibility; official model-card versions were pinned and a one-item paired smoke test passed before the full rerun.
- No main experiments, ablations, robustness tests, or error analysis.
- The ESP cue extractor supplies candidates only. Same-family agent frame labels and model-agent output audits cannot satisfy an independent-human annotation gate; the completed counterfactual review is also model-agent development evidence only.
- No manuscript/PDF, supplement, cold-review pass, or meta-review pass.
- Topic-stage overlap clearance does not replace the mandatory final manuscript/supplement lexical, semantic, and evidence-lineage audit.

## Highest-ROI next step

Reopen topic search from the existing audit constraints. Preserve LAD, DCEA, CLEP, and ESP as retired topics with their negative evidence; do not select a replacement until a new candidate has a licensed evidence path, a direct novelty boundary, and a predeclared two-family gate.
