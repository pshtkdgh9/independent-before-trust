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
