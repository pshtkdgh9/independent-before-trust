# Research State

- Phase: topic selected; deterministic LAD core and mock pipeline implemented
- Primary target: EACL 2027 long paper via ARR
- Selected topic: Lineage-Aware Deliberation (LAD)
- Core question: whether repeated-source evidence creates false corroboration in language-agent belief revision
- Current highest-ROI blocker: download/checksum the pinned pilot model on CloudLab and run the 50-item private-first pilot
- Reproducible code checkpoint: `be28f14` on `origin/codex/lad-private-first-pilot`
- CloudLab allocation state: Wisconsin reports one free `d7525`; experiment submission is intentionally held until the portal confirms `phystype=d7525`
- Compute target: one CloudLab Wisconsin d7525 node, NVIDIA A30 24 GB, Ubuntu 22.04
- Evidence status: no empirical headline claim is currently supported
- Submission status: not ready

## Decision history

1. Initial seed: independent-before-trust/private commitment.
2. Parallel search proposed conflict-aware RAG.
3. A 28-work collision matrix found both areas crowded.
4. Selected LAD because it isolates source dependence rather than generic trust, confidence, grounding, or retrieval conflict.

## Next gate

The Apache-2.0 BIG-bench source is pinned and checksummed, and 50 private-first pilot items are reproducibly constructed. The runner now elicits the target model's actual private answer before constructing matched COMMON/INDEPENDENT revision pairs; this avoids treating an injected answer as model belief. Next, download/checksum the pinned model on CloudLab and run the pilot before adding result-bearing manuscript language.
