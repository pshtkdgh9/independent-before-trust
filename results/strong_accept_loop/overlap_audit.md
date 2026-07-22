# Overlap Audit

## Audit scope

This is a conservative comparison between the proposed ACL-family contribution and the existing journal submission using the boundary information currently available. Uncertainty is treated as risk, not proof of independence.

## Existing-work artifact and signature excluded from this project

The author-local manuscript inspected for the direct audit is **CaliTrust: Distribution-Free Uncertainty Quantification for Dynamic Trust Prediction in Signed Networks** (`calitrust_main.tex`, 37,567 bytes, SHA-256 `c415c1e997bd46f05448ccd5eec2df184876c7d6066eed576c8d0fbd43678d0f`, last modified 2026-06-24). Its contribution is temporal graph conformal prediction for calibrated signed trust-link prediction: adaptive conformal inference, polarity-stratified calibration, a graph-aware nonconformity score, signed-network datasets, coverage/set-size metrics, and fraud-decision utility. The execution brief also identifies prior work involving CHTrust, CAT comparisons, Guardian, TrustGuard, TEAMS, LEAKLESS, and signed-trust/reputation graphs. Those labels, algorithms, graph constructions, results, claims, prose, and evaluation package are excluded.

## New-work signature

Lineage-Aware Deliberation studies how claims supported by common versus independent evidence influence language-model belief revision. Its objects are atomic claims, source identifiers, derivation relations, revision operations, and effective corroboration counts. Its principal manipulation is source dependence while semantic content and nominal agent count are controlled.

| Dimension | CaliTrust / existing-work signature | LAD boundary | Risk | Required control |
|---|---|---|---|---|
| Research question | Calibration of dynamic signed trust-link predictions | Causal effect of common-source versus independent-source linguistic corroboration on belief revision | Low | Frame as evidential dependence and dialogue belief revision, not trust. |
| Contribution | Temporal graph conformal prediction components and guarantees | Matched lineage intervention, effective-support diagnostic, and bounded revision rule | Low | No conformal component, guarantee, or renamed extension. |
| Task framing | Signed-edge prediction and downstream fraud decisions | Private answer, peer-message exposure, and post-exposure answer revision | Low | Different target, intervention, and unit of analysis. |
| Representation | Signed trust/reputation graph | Minimal claim-to-source lineage DAG | Medium | No agent trust scores, signatures, reputation, or inherited graph algorithm. |
| Method | ACI, polarity-stratified calibration, graph-aware nonconformity | Collapse/discount dependent support in a paired language intervention | Low--medium | Implement anew; run code and semantic overlap audits. |
| Dataset/evaluation package | Signed-network temporal splits; calibration, coverage, set size, fraud utility | Newly acquired public language tasks; harmful/beneficial revision, effective support, parser/resource diagnostics | Low | New checksums, preprocessing, splits, prompts, logs, and metrics. |
| Claim set | Calibration validity, class balance, efficiency, and fraud utility | Bounded effects of evidence ancestry in tested model/task regimes | Low | Map every claim to new artifacts; no external values as head-to-head evidence. |
| Writing | Existing title, abstract, narrative, equations, tables, figures, and related-work synthesis | Independently drafted ACL manuscript | Low | Final normalized n-gram and manual semantic audit. |
| Experimental evidence | Existing signed-network runs and reported numbers | New model generations, paired manifests, environment logs, analyses, and failure records | Low | No prior output or evidence-package reuse. |

## Direct audit result (topic-selection stage)

- **Research question:** CaliTrust asks whether predictions over signed trust edges are calibrated under temporal shift. LAD asks whether semantically matched peer messages with common versus independent source ancestry cause different belief revision. The prediction target, intervention, and unit of analysis differ.
- **Method:** CaliTrust wraps signed-graph predictors with conformal calibration. LAD changes neither model weights nor probability calibration; it manipulates source lineage in natural-language deliberation and measures revision. No ACI, Mondrian calibration, graph-aware nonconformity score, signed edge, trust score, or reputation propagation is used.
- **Data/evidence:** CaliTrust's signed-network splits, reported tables, numerical findings, and fraud-utility analysis are prohibited. LAD uses newly downloaded public language tasks, newly generated paired prompts/logs, and a new claim-to-artifact map.
- **Lexical scan:** after stripping LaTeX commands and punctuation and lowercasing, the 4,442-token CaliTrust source shared **zero contiguous 8-token sequences** with each of the 13 current LAD research documents under `results/strong_accept_loop/*.md`. This is a screening result, not a substitute for a final-manuscript audit.
- **Lineage:** the word *graph* is not itself a contribution transfer. LAD's optional claim-to-source DAG records verifiable derivation only; it cannot contain signed edges, learned trust/reputation values, or CaliTrust algorithms.

## Verdict

**Topic-stage clearance: pass; submission-stage clearance: pending.** The located existing manuscript was directly inspected and the selected LAD question, method, data, metrics, and planned claims are substantively distinct. LAD must not import trust weights, signed edges, reputation propagation, conformal-calibration components, prior code, prior prose, or prior results. Lineage is permitted only to represent verifiable source ancestry. Re-run the lexical scan and this contribution/data/result audit against the complete ACL manuscript and supplement immediately before submission; any newly discovered concurrent manuscript must also be added.
