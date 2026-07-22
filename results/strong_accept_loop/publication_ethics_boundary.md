# Publication Ethics and Non-Overlap Boundary

## ESP boundary after topic pivots and retirement

ESP was a new manuscript direction and is now retired as a headline candidate. It must not reuse prose, claims, figures, result tables, or evidence packages from the submitted journal paper, LAD, DCEA, or CLEP. LAD, DCEA, CLEP, and ESP are retained for transparency. Their code may contribute only generic experiment plumbing for future searches and cannot be presented as a scientific contribution to a later topic. Their data and negative outcomes cannot be pooled into a new result.

## Existing submission

The existing manuscript associated with prior trust/reputation work has already been submitted to another journal. The author-local artifact inspected in this audit is *CaliTrust: Distribution-Free Uncertainty Quantification for Dynamic Trust Prediction in Signed Networks* (source SHA-256 `c415c1e997bd46f05448ccd5eec2df184876c7d6066eed576c8d0fbd43678d0f`). It is outside the contribution set of the EACL/ACL project and is treated as confidential concurrent work, not as reviewer-visible prior art. Venue, submission identifier, and submission date remain author-controlled metadata to add to the final disclosure record if policy requires them.

## Prohibited reuse

- No sentence, paragraph, title, abstract, related-work synthesis, figure, or table is copied or lightly paraphrased from the existing submission.
- No headline claim, theorem, empirical result, evidence map, or evaluation package from that submission is presented as a contribution here.
- The EACL/ACL manuscript does not claim an extension of the existing paper and does not use a renamed version of its core signed-trust/reputation-graph method.
- Existing private reviewer comments or unpublished results are not used as anonymous supporting evidence.

## Permitted background/tool reuse

Code may be reused only if it is a generic, independently testable utility (for example deterministic seeding, model loading, logging, or metric serialization), its license and authorship permit reuse, and its behavior is documented. Data may be reused only when independently public/licensed, newly downloaded or checksummed for this project, and not itself the distinctive evidence package of the submitted manuscript.

Any reused component must be listed here and in `data_provenance.md` or the reproducibility checklist with: source path/repository, original purpose, license, exact files/functions used, reason for reuse, modifications, and why it does not transfer the prior paper's contribution or evidence.

Current reuse register:

- `src/lad/hf_backend.py` is reused solely as generic local Hugging Face model loading and deterministic generation plumbing in `scripts/run_esp_pilot.py`. It was written in this repository, carries no prior-paper scientific method, and transfers no prior results or data.
- `src/lad/provenance.py` and `scripts/download_public_file.py` are reused solely for download checksums and provenance serialization. Their dataset-specific privacy and redistribution text was removed; ESP supplies its own source-specific declarations.
- The pinned Phi and Qwen snapshots are public third-party models reused as compute inputs under their recorded MIT and Apache-2.0 licenses. No prior LAD/DCEA/CLEP output is reused.

The reference PDFs and extracted text are used only to orient topic search; they are not manuscript prose and are not empirical evidence.

## Retired ESP boundary

The retired ESP project studied epistemic strength and semantic scope in scientific lay rewriting. It did not study signed networks, trust/reputation prediction, graph calibration, lineage-aware deliberation, causal source attribution, or multilingual channel effects. ESP source selection, annotations, prompts, outputs, metrics, tables, figures, and claims were created anew in this repository from the separately pinned public BioLaySumm source.

Retired-branch code and results remain as an ethical audit trail. They cannot be relabeled as ESP evidence, cannot appear as ESP findings, and cannot justify any ESP claim. Only the generic utilities named in the reuse register cross the boundary.

The ESP counterfactual review records Phi as passing, Qwen as failing, and the combined gate as `advance=false`; it also records `evidence_class=model_agent_development_only` and `human_evidence=false`. Future work must not cite this as human evaluation or as support for an ESP headline claim.

## Citation and disclosure

- If the existing submission becomes public or is sufficiently related to require disclosure under ACL policy, it will be cited and its differences explained without deanonymizing the ARR submission improperly.
- All contemporaneous related work will be cited; external reported numbers will be labeled as external and never presented as same-regime head-to-head results.
- AI assistance in research, coding, and writing will be disclosed according to the current ACL policy and institutional requirements. Authors remain responsible for every claim, citation, result, and ethical decision.
- No full unpublished manuscript or private corpus will be sent to an external model provider for review without explicit authorization.

## Audit gate before submission

Before submission, perform a lexical-overlap scan, a contribution/claim comparison, and a dataset/result lineage audit against the existing journal manuscript. Any ambiguous overlap blocks submission until removed or explicitly resolved under ACL policy.
