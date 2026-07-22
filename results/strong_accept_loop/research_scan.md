# Research Scan

## Current synthesis

Recent work establishes that language-agent groups can conform, amplify errors, and become less reliable as interaction structure changes. Closely adjacent 2026 work also studies debate failure, conformity measurement, confidence, identity, consensus, and graph-based collaboration. Those results make a broad "multi-agent debate is unreliable" paper insufficiently novel.

LAD instead isolates a narrower causal variable: whether nominally distinct supporting messages descend from one source or from independent sources. Its paired intervention holds message content, correctness, confidence, ordering, and nominal peer count fixed while changing only source lineage. The target outcome is belief revision, especially harmful revision from an initially correct answer. This is a mechanism study, not a new benchmark and not a generic trust-scoring method.

The novelty claim remains conservative. The 28-work matrix is an abstract/metadata-level collision screen; the closest papers still require full-text protocol comparison before manuscript novelty language is finalized.

## Coverage of the brief's optional direction examples

The execution brief says acceptable directions “include, but are not limited to” the examples below. They are search prompts, not requirements to adopt or independently develop every area. The actual topic-search gate is the comparison of at least five viable non-benchmark candidates; `topic_search.md` compares eight.

| Direction example | Search disposition |
|---|---|
| Trustworthy or reliable NLP evaluation | Adopted at mechanism level: LAD causally tests a reliability failure in language-agent revision. |
| Factuality, citation, attribution, or retrieval evaluation | Covered through evidence-grounding controls and the rejected conflict-aware RAG candidate. |
| Retrieval-augmented generation | Explicitly rejected as crowded; no RAG claim is allowed without a real retriever and end-to-end evaluation. |
| Multilingual or low-resource NLP | Cross-lingual deliberation was compared and rejected because translation would confound source dependence. |
| Computational social science with language data | Not retained as a separate candidate: the present controlled synthetic mechanism study offers a cleaner causal test and avoids claims about human collective behavior. |
| Information retrieval and text mining | Covered only through the rejected conflict-aware RAG candidate; it is not the selected contribution. |
| Resources and evaluation | Public tasks are experimental instruments, not a resource or benchmark contribution. |
| Model analysis and interpretability | Covered through the diagnostic effective-support claim, not as a standalone interpretability method. |
| Human-centered NLP or human–AI interaction | Pragmatic clarification was compared; LAD also connects evidentiality, common ground, and the EACL theme without claiming human equivalence. |
| Ethics, bias, and fairness | Not retained as a standalone topic; the project instead applies a concrete publication-ethics and defensive-release boundary. |
| LLM agents, tool use, or grounded reasoning | Adopted: the selected intervention studies language-agent collaboration and evidence-conditioned revision. |
| Efficient methods for NLP | Selective communication was compared and rejected because efficiency alone would make the contribution engineering-led. |

This coverage record prevents the generated Ultragoal stories from being misread as twelve simultaneous topic commitments.

## Verified anchors

1. GAVEL (Findings of ACL 2026): evaluates and improves multi-agent debate. https://aclanthology.org/2026.findings-acl.225/
2. Demystifying Multi-Agent Debate (Findings of ACL 2026): analyzes when debate helps or harms. https://aclanthology.org/2026.findings-acl.230/
3. The Ringelmann Effect in LLM Multi-Agent Systems (2026 preprint): reports degradation as group size grows. https://arxiv.org/abs/2606.02646
4. Not All Flips Are Conformity (2026 preprint): distinguishes response changes from conformity. https://arxiv.org/abs/2606.00820
5. He et al. (Findings of ACL 2025): communication interception and manipulation can compromise multi-agent systems. https://aclanthology.org/2025.findings-acl.349/
6. Shahroz et al. (ACL 2025): communication constraints create multi-agent attack surfaces. https://aclanthology.org/2025.acl-long.476/
7. Baltaji et al. (C3NLP 2024): multi-agent collaboration exhibits conformity and opinion instability. https://aclanthology.org/2024.c3nlp-1.2/
8. Obiso et al. (CoNLL 2025): epistemic friction models resistance to belief integration. https://aclanthology.org/2025.conll-1.21/
9. Anikina et al. (LUHME 2025): common ground is multidimensional and under-modeled in LM interaction. https://aclanthology.org/2025.luhme-1.2/
10. Wilie et al. (EMNLP 2024): language models struggle with belief revision under new evidence. https://aclanthology.org/2024.emnlp-main.586/

## Remaining scan gate

- Read the full protocols of the closest lineage-, conformity-, and debate-analysis papers, not only abstracts.
- Confirm whether any work already holds message semantics fixed while manipulating common versus independent provenance.
- Verify bibliographic metadata from primary sources before adding citations to the manuscript.
- Treat contemporaneous 2026 preprints as related work, never as same-regime numerical baselines unless reproduced under the LAD protocol.

## Post-LAD closest-work gate

The initial CBCG fallback was rejected after direct primary-source review. Common-ground tracking, clarification, abstention, budgeted debate stopping, confidence-aware updates, consensus-free debate, and explicit conflict resolution are already active 2024--2026 lines; combining them would not provide a sufficiently crisp new contribution.

The first post-LAD replacement, Claim-Preserving Provenance Repair, was rejected after this scan found a direct collision with RARR (ACL 2023): RARR finds attribution for an existing LM output and post-edits unsupported content while preserving the original as much as possible. Generic conflict-preserving synthesis also collides with MoDS (NAACL 2025), and argument-role repair collides with Arg-LLaDA (ACL 2026). These candidates remain in the audit trail but are not selected.

The provisional DCEA direction is bounded against these primary works:

1. Wei et al. (ACL 2026), GenProve: generation-time fluent answers with sentence-level Quotation/Compression/Inference provenance triples and joint training. https://aclanthology.org/2026.acl-long.228/
2. Xu et al. (Findings ACL 2026), GAVEL: inference-time evidence contracts, atomic subclaims, deterministic citation/span validation, and provenance-grounded fact-checking. https://aclanthology.org/2026.findings-acl.1789/
3. Localizing Factual Inconsistencies in Attributable Text Generation (TACL 2026): fine-grained localization rather than the complete minimal-repair objective. https://aclanthology.org/2026.tacl-1.6/
4. Attribution, Citation, and Quotation (ACL 2026): taxonomy and survey of evidence-based generation. https://aclanthology.org/2026.acl-long.1430/
5. CLUE (ACL 2026): source-of-uncertainty explanations in automated fact-checking, adjacent to but distinct from answer repair. https://aclanthology.org/2026.acl-long.2110/
6. ContextCite (NeurIPS 2024): introduces context attribution and estimates which context sources led to a generated statement through masked subsets and response likelihood. https://proceedings.neurips.cc/paper_files/paper/2024/hash/adbea136219b64db96a9941e4249a857-Abstract-Conference.html
7. AttriBoT (ICLR 2025): efficiently approximates leave-one-out context attribution and explicitly distinguishes causal source contribution from merely supportive citations. https://proceedings.iclr.cc/paper_files/paper/2025/hash/2aab664e0d1656e8b56c74f868e1ea69-Abstract-Conference.html
8. Connecting Attributions and QA Model Behavior on Realistic Counterfactuals (EMNLP 2021): evaluates attribution methods against realistic RC counterfactuals. https://aclanthology.org/2021.emnlp-main.447/
9. DisentQA (ACL 2023): uses factual, counterfactual, empty, and random contexts to separate contextual from parametric answers. https://aclanthology.org/2023.acl-long.559/
10. Evaluating Evidence Attribution in Generated Fact Checking Explanations (NAACL 2025): uses citation masking and recovery to evaluate whether explanation context permits recovering cited evidence. https://aclanthology.org/2025.naacl-long.282/

The remaining provisional gap is narrower than causal attribution in general. Removal and likelihood-drop methods estimate source necessity for a fixed response; semantic citation checks estimate support. DCEA instead intervenes on the answer-bearing value and scores whether the generated answer changes in the intervention's signed direction. Its redundancy cell tests the specific case in which removing either of two equivalent sources yields little change even though their shared content directs the answer. This boundary is a hypothesis, not yet a novelty finding; the pilot and further full-text scan can still kill it.

No novelty claim is yet verified. The immediate falsification test is whether directional replacement supplies information beyond semantic support and removal-based attribution specifically in the redundant-support cell. If it does not, DCEA is retired rather than reframed after observing results.

## Third-pivot collision findings

The public-data method search rejected two initially attractive directions after direct collisions. *Automated Feedback Loops to Protect Text Simplification with Generative AI from Information Loss* (Nandiraju et al., 2025, arXiv:2505.16172) already detects missing health-text elements and regenerates simplified text by inserting them, so InfoLossQA-guided minimal repair cannot be claimed broadly as a new repair task. *Improving Factual Accuracy of Neural Table-to-Text Output by Addressing Input Problems in ToTTo* (Sundararajan et al., NAACL 2024, https://aclanthology.org/2024.naacl-long.408/) already repairs malformed ToTTo inputs and measures downstream factual-error reduction.

The remaining provisional gap is epistemic **scope** preservation in natural scientific lay summarization. Relevant boundaries include: hedge use in simplification (W11-2314), BioScope-style hedge cue/scope identification, PLOS/eLife lay-summary corpora (Goldsack et al., EMNLP 2022), InfoLossQA (ACL 2024), reading-comprehension meaning preservation (TACL 2024), lossless LLM simplification (2025), and *Possible or Definite?* (arXiv:2606.18471), which evaluates diagnostic uncertainty preservation in clinical revision. The proposed contribution cannot be merely another uncertainty benchmark or cue counter. It must provide a reproducible frame-conditioned generation method and show strength-and-scope preservation under matched open-model experiments while retaining readability and coverage.

## DCEA retirement and next novelty gate

DCEA failed its direct falsification test. The fixed parser rejected all four model/prompt artifacts. The interpretable Phi outputs did not separate singleton and redundant pair flips, and contrastive prompting did not improve directional following. A further primary-source search found *Source Attribution in Retrieval-Augmented Generation* (2025), which explicitly frames Shapley source attribution around redundancy, complementarity, and synergy: https://arxiv.org/abs/2507.04480. DCEA is therefore retired rather than repaired after outcome inspection.

The provisional CLEP direction is bounded against:

1. Muller et al. (EMNLP 2023), cross-lingual QA attribution: https://aclanthology.org/2023.emnlp-main.10/
2. Krause et al. (MMNLG 2023), multilingual expression and calibration of uncertainty: https://aclanthology.org/2023.mmnlg-1.1/
3. Mehrparvar and Pezzelle (MRL 2024), ambiguity preservation through translation: https://aclanthology.org/2024.mrl-1.26/
4. Fadeeva et al. (Findings ACL 2024), claim-conditioned uncertainty for hallucination detection across four languages: https://aclanthology.org/2024.findings-acl.558/
5. XRAG (2025), cross-lingual retrieval-augmented generation: https://arxiv.org/abs/2505.10089
6. PsiloQA (Findings EMNLP 2025), multilingual span-level hallucination detection: https://aclanthology.org/2025.findings-emnlp.626/
7. Huang et al. (EACL 2026), multilingual calibration effects of instruction tuning: https://aclanthology.org/2026.eacl-short.1/

The remaining proposed gap is not general multilingual QA, calibration, or translation quality. It is the controlled preservation of linguistically realized epistemic operators and attributed speakers when the same evidence is consumed through different language channels, together with a typed intermediate representation whose fields can be validated without an opaque judge. This remains provisional until full-text review and a two-family pilot.
