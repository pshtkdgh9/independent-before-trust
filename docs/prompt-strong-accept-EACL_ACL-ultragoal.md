# Strong-Accept EACL/ACL Ultragoal Prompt

## Mission

Run an autonomous strong-submission research loop for an EACL/ACL main-conference paper through ACL Rolling Review. The target is an ARR-ready, EACL/ACL-fit, strong-accept-level NLP/Computational Linguistics paper.

Do not mark the task complete until all terminal gates pass.

Primary target: EACL next available main conference through ARR.
Backup target: ACL next available main conference through ARR.
If the official target-year CFP is not yet available, use the latest ARR CFP and Dates page as the controlling process, and record uncertainty.

## Mandatory first step: venue and policy check

Before changing the paper, verify the latest official information from:

* ACL Rolling Review CFP
* ACL Rolling Review Authors Guidelines
* ACL Rolling Review Dates and Venues
* ARR Responsible NLP Research Checklist
* The current EACL CFP, if available
* The current ACL CFP, if available

Create or update:

* `results/strong_accept_loop/venue_check.md`

Record:

* target venue and year
* ARR cycle deadline
* commitment deadline
* long/short paper page limits
* anonymization requirements
* limitations requirement
* ethics / Responsible NLP checklist requirement
* AI writing/coding assistance disclosure requirement
* multiple-submission and overlap policy
* supplementary material policy
* any venue-specific theme tracks

If venue information is missing or outdated, do not guess. Mark the venue gate as blocked and proceed only with venue-invariant ARR preparation.

## Topic policy

The topic is not fixed. Existing drafts, code, prior experiments, and previous ideas are seeds only.

The final paper must be a genuine NLP/Computational Linguistics contribution, not merely a general graph ML, recommender-system, or benchmark-engineering paper with NLP wording added later.

Acceptable directions include, but are not limited to:

* trustworthy / reliable NLP evaluation
* LLM factuality, citation, attribution, or retrieval evaluation
* retrieval-augmented generation evaluation
* multilingual or low-resource NLP
* computational social science with language data
* information retrieval and text mining
* resources and evaluation
* model analysis and interpretability
* human-centered NLP or human-AI interaction
* ethics, bias, and fairness
* LLM agents, tool use, or grounded reasoning
* efficient methods for NLP

Reject topics that are:

* benchmark-only without a clear scientific question
* mostly engineering without a reusable NLP insight
* incremental model variants without a strong failure-mode analysis
* duplicate-submission risks with existing or already-submitted work
* dependent on private data that cannot be ethically described or evaluated
* impossible to support with available experiments

## Non-overlap and self-plagiarism guard

Do not reuse submitted or published paper text, claim structure, tables, figures, or evidence packages in a way that creates duplicate-submission or self-plagiarism risk.

Existing work such as CHTrust, CAT comparisons, Guardian, TrustGuard, TEAMS-style robustness, LEAKLESS-style temporal evaluation, or signed-trust graph papers may be used only as background or inspiration if the new paper has a clearly different:

* research question
* contribution
* task framing
* dataset/evaluation package
* claim set
* writing
* experimental evidence

Create or update:

* `results/strong_accept_loop/overlap_audit.md`

The audit must explicitly compare the new paper against related in-house or prior drafts and state why it is not a duplicate submission.

## Required artifacts

Maintain the following files during the loop:

* `STATE.md`
* `results/strong_accept_loop/status.md`
* `results/strong_accept_loop/venue_check.md`
* `results/strong_accept_loop/topic_decision.md`
* `results/strong_accept_loop/novelty_matrix.md`
* `results/strong_accept_loop/overlap_audit.md`
* `results/strong_accept_loop/evidence_map.md`
* `results/strong_accept_loop/data_provenance.md`
* `results/strong_accept_loop/ethics_checklist_draft.md`
* `results/strong_accept_loop/reproducibility_checklist.md`
* `results/strong_accept_loop/cold_reviews/`
* `results/strong_accept_loop/meta_review.md`

The paper should live in:

* `paper/main.tex`
* `paper/references.bib`
* `paper/figures/`
* `paper/tables/`

Scripts and logs should live in:

* `scripts/`
* `results/`

## Paper requirements

The final paper must satisfy the following:

1. Clear NLP/CL problem statement.
2. Explicit ARR/EACL/ACL venue fit.
3. Strong related work grounded in recent ACL Anthology, TACL, CL, EMNLP, NAACL, EACL, ACL, Findings, and relevant ML/IR venues.
4. Novel contribution stated in 2-3 precise claims.
5. Method or evaluation protocol described with enough detail to reproduce.
6. Experiments that directly test the headline claims.
7. Strong baselines and fair comparison protocols.
8. Ablation studies for each proposed component.
9. Robustness or stress tests.
10. Error analysis with concrete examples.
11. Limitations section.
12. Ethical considerations section when relevant.
13. Responsible NLP checklist draft.
14. Data provenance and license/terms documentation.
15. No hallucinated references.
16. No unsupported SOTA claim.
17. No hidden prompt-injection or machine-reader manipulation text.
18. Anonymous supplementary material if supplementary material is used.

## Evidence standard

Every headline claim must map to evidence.

Update `results/strong_accept_loop/evidence_map.md` with:

* claim
* paper section
* table/figure
* script
* command
* result file
* interpretation
* known weakness

A claim cannot remain in the abstract, introduction, conclusion, or contribution list unless it appears in the evidence map.

## Data provenance standard

For every dataset, model, API, annotation source, or benchmark, update `data_provenance.md` with:

* name
* source
* download/access date
* license or terms
* preprocessing steps
* filtering decisions
* privacy or consent concerns
* whether redistribution is allowed
* whether the paper can release derived artifacts
* known risks

If license or terms are unclear, mark the risk explicitly and avoid making release claims.

## Reproducibility standard

Create or update:

* `README.md`
* `scripts/run_all.sh`
* `requirements.txt` or environment file
* fixed random seeds where possible
* hardware/software description
* exact commands for main results
* exact commands for ablations
* exact commands for figures/tables

The paper must not depend on undocumented manual steps.

## Literature and novelty matrix

Create `novelty_matrix.md` with at least 25 relevant papers, prioritizing recent ACL Anthology, TACL, CL, EMNLP, NAACL, EACL, ACL, Findings, and related IR/ML venues.

For each paper, record:

* citation key
* venue/year
* task
* method
* dataset
* evaluation
* limitation
* relation to this paper
* why this paper is different

The related work section must be written from this matrix, not from memory.

## Iteration loop

Repeat the following loop until all terminal gates pass:

1. Read current `STATE.md`, `status.md`, `evidence_map.md`, `venue_check.md`, and latest cold reviews.
2. Identify the single highest-ROI failing gate.
3. Make the smallest useful change that addresses it.
4. Run the required build, checks, or experiments.
5. Record evidence paths, not raw logs.
6. Update `STATE.md`, `status.md`, `evidence_map.md`, `data_provenance.md`, and other relevant files.
7. Re-run cold review only after meaningful changes.
8. Do not mark complete unless all terminal gates pass.

## Cold review protocol

Run at least 5 independent cold-review personas:

1. ARR Area Chair persona
2. Empirical NLP reviewer persona
3. NLP methods reviewer persona
4. Resources/evaluation reviewer persona
5. Ethics/reproducibility reviewer persona

Each review must include:

* score
* confidence
* summary
* strengths
* weaknesses
* missing citations
* unsupported claims
* reproducibility concerns
* ethics or data concerns
* exact blockers to acceptance
* recommended decision

Use ARR-style decisions:

* Strong Accept
* Accept
* Weak Accept
* Borderline
* Weak Reject
* Reject

After the 5 reviews, run an adversarial meta-review that decides whether the paper is submit-ready.

## Terminal gates

Do not mark complete until all gates pass:

1. Official venue/ARR process has been checked and recorded.
2. Topic is clearly EACL/ACL-fit and not duplicate work.
3. Paper builds successfully with official ACL style.
4. Paper respects page, anonymity, limitations, ethics, and supplementary-material requirements.
5. Every headline claim maps to evidence.
6. All data provenance, licenses, terms, and preprocessing decisions are recorded.
7. Related work is current, accurate, and sufficient.
8. All references are real and citation keys compile.
9. Main experiments, ablations, robustness tests, and error analysis are present.
10. Responsible NLP checklist draft is complete.
11. AI assistance disclosure is prepared if applicable.
12. Five cold reviews contain no Reject or Weak Reject.
13. At least two of the five cold reviews are Strong Accept.
14. Adversarial meta-review says submit-ready.
15. Final cleanup/review gate passes.

## Final cleanup gate

Before completion, check:

* abstract matches actual contributions
* introduction does not overclaim
* contribution bullets are evidence-backed
* method notation is consistent
* tables and figures are referenced in order
* results text matches table values
* limitations do not introduce new results
* ethics section is specific, not generic
* bibliography compiles
* all anonymous-review risks are removed
* appendix does not hide essential claims
* PDF has no formatting errors
* no TODO, placeholder, broken citation, or missing figure remains

## Final response format

When reporting progress, use at most 8 lines:

STATUS:
DONE:
FAILED_GATE:
CHECKS:
EVIDENCE:
NEXT:
FILES:
NOTES:
