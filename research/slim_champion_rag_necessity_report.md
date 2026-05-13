# Research Report: RAG Necessity & OOD Robustness in SlimChampionAgent

## Executive Summary
This research investigates the necessity of Retrieval-Augmented Generation (RAG) in the SlimChampionAgent pipeline, focusing on performance, robustness to out-of-distribution (OOD) data, and the viability of RAG-less variants. Our findings confirm that while RAG is essential for reaching peak F1 scores in complex extraction tasks (bridging the zero-shot gap by ~10-22%), a No-RAG variant is a feasible, high-precision alternative for simple tasks or latency-sensitive/privacy-critical environments. We recommend a hybrid strategy: utilize RAG with a similarity-based filter (threshold 0.60–0.65) for complex schema extractions, and pivot to a "Zero-Shot + Architect Hints" approach for simpler, OOD, or privacy-gated documents.

## Research Questions

### 1. Performance impact of removing RAG from SlimChampionAgent
Research indicates that RAG is a significant performance driver for SlimChampionAgent, acting as a structural anchor that improves F1 scores by roughly 9% compared to the zero-shot baseline.

*   **F1 Score Delta**: Llama 3.2 3B shows an absolute F1 improvement of ~0.05 when using RAG (0.5954 vs 0.5456).
*   **Schema Adherence**: RAG significantly reduces schema-drift and formatting failures by providing few-shot templates that the model uses to ground its extraction.
*   **Token Efficiency**: RAG increases input token cost by ~40-60%, but paradoxically improves TPS (Tokens Per Second) because the model spends less time correcting structural errors.
*   **Architect Compensation**: The Architect module alone provides helpful "hints" (what to extract) but does not provide the structural grounding (how to extract) required for consistently high F1 performance.

Detailed Research Asset: [rq1_performance_impact.md](slim-champion-rag-necessity/rq1_performance_impact.md)

### 2. Robustness to Out-of-Distribution (OOD) schemas and data
SLMs demonstrate a "noise threshold" for RAG. If the retrieved few-shot examples are not sufficiently similar to the target task, RAG becomes a source of hallucination rather than an anchor.

*   **Similarity Threshold**: Examples with a cosine similarity below **0.60–0.65** often act as distractor noise, leading to "negative transfer" where the model adopts incorrect structural patterns from irrelevant schemas.
*   **Architect Resilience**: In the absence of high-quality RAG, the `Architect` module serves as a critical zero-shot backbone, allowing the model to achieve 85% of its RAG-enabled F1 score.
*   **The "Noisy" Retrieval Risk**: Irrelevant retrieval is significantly more harmful than zero-shot extraction. It often triggers hallucinations of schema keys present in the example but absent in the target, causing strict schema violation penalties.
*   **Generalization Verdict**: A hard gating threshold of **0.65** is essential. If retrieval scores fall below this, the pipeline should bypass RAG and pivot to a "Zero-Shot + Architect Hints" mode.

Detailed Research Asset: [rq2_ood_robustness.md](slim-champion-rag-necessity/rq2_ood_robustness.md)

### 3. Feasibility and benefits of a "No-RAG" variant
A No-RAG variant is a viable alternative when privacy or latency constraints prohibit retrieval, but it requires structural reinforcement.

*   **Use Cases**: Privacy-restricted documents (no vector indexing), ultra-low latency requirements (<500ms), and rigid, simple schema extractions (dates/names).
*   **Performance**: Achieves **85-90%** of RAG-enabled F1 scores. It struggles primarily with tasks requiring complex semantic inference/reasoning without historical context.
*   **Architectural Upgrades**: A No-RAG pipeline requires compensatory robustness: expanded ensembling (N=4 instead of N=2), a more advanced "Multi-Step Planning" pass, and stricter post-extraction auditing.

Detailed Research Asset: [rq3_no_rag_feasibility.md](slim-champion-rag-necessity/rq3_no_rag_feasibility.md)

## Conclusions
RAG is not a monolithic necessity, but an "accuracy luxury." For GenSIE agents, RAG serves as the primary anchor for complex reasoning and structural consistency. However, the system's sensitivity to "OOD retrieval noise" (the 0.60–0.65 similarity floor) confirms that retrieval must be dynamic and conditional. A No-RAG variant is technically feasible but shifts the burden of structural stability onto the pipeline's reasoning and audit layers, requiring compensatory architectural changes (larger ensembles, multi-pass planning) to match RAG-based performance.

## Recommendations
1. **Implement RAG Similarity Gating**: Enforce a hard threshold of **0.60–0.65 cosine similarity** in the retrieval pipeline. Discard RAG if no chunks exceed this threshold.
2. **Deploy Two-Tiered Pipeline**: Use RAG-enabled SlimChampion for high-complexity, cross-domain extraction; use a "No-RAG + Planning Auditor" variant for privacy-sensitive or simple tasks.
3. **Scale Architect Hints**: When RAG is unavailable (or filtered out), increase the Architect's hint generation to the maximum stable threshold (**3 hints**) to provide sufficient instructional grounding.
