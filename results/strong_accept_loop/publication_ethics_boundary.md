# Publication Ethics and Non-Overlap Boundary

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

Current reuse register: **none**. The reference PDFs and extracted text are used only to orient topic search; they are not manuscript prose and are not empirical evidence.

## New-work boundary

The selected project studies directional evidence use in supplied-context generation: whether a model's answer follows a controlled change to an answer-bearing source fact, including when equivalent support is redundant. It does not study signed networks, trust/reputation prediction, graph calibration, or the prior submission's evidence package. The DCEA task artifacts, source packs, transformations, prompts, outputs, metrics, tables, figures, and claims will be created anew in this repository.

The retired LAD pilot code and results may remain as an ethical audit trail and as generic examples of model loading, deterministic generation, logging, hashing, and artifact validation. They cannot be relabeled as DCEA evidence, cannot appear as DCEA results, and cannot justify any DCEA claim. Any generic utility actually reused by DCEA must be added to the reuse register with its exact boundary.

## Citation and disclosure

- If the existing submission becomes public or is sufficiently related to require disclosure under ACL policy, it will be cited and its differences explained without deanonymizing the ARR submission improperly.
- All contemporaneous related work will be cited; external reported numbers will be labeled as external and never presented as same-regime head-to-head results.
- AI assistance in research, coding, and writing will be disclosed according to the current ACL policy and institutional requirements. Authors remain responsible for every claim, citation, result, and ethical decision.
- No full unpublished manuscript or private corpus will be sent to an external model provider for review without explicit authorization.

## Audit gate before submission

Before submission, perform a lexical-overlap scan, a contribution/claim comparison, and a dataset/result lineage audit against the existing journal manuscript. Any ambiguous overlap blocks submission until removed or explicitly resolved under ACL policy.
