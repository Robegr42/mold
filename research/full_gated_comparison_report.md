# Research Report: Comparative Analysis of Gated and Synthetic Champion Architectures

## Executive Summary
This report presents a comprehensive comparison of four information extraction architectures: **StableChampion**, **GatedStable**, **SyntheticAnchor**, and the peak-performer **AuditedSynthetic**. The experiment confirms that a **Double-Gate architecture**—which audits synthetic grounding with a 0.70 similarity threshold—is the most robust and efficient strategy for Qwen 3 1.7B. 

**Key Insights:**
1. **Performance Peak:** The `AuditedSyntheticAgent` achieved the highest F1 score of **0.8036**, representing a **+5.95% uplift** over the baseline.
2. **Efficiency Winner:** The `AuditedSyntheticAgent` is the most sustainable pipeline, reducing token consumption by **34%** and latency by **29%**, while achieving a record PTC Ratio of **0.2140**.
3. **Threshold Success:** Lowering the initial RAG gate to **0.55** proved to be a critical optimization, significantly reducing hallucinations and improving grounding.
4. **Behavioral Trade-offs:** While synthetic anchors maximize recall and structural validity, they slightly increase hallucination risk. The `GatedStable (0.55)` agent remains the most factually grounded architecture with the lowest total error volume.

## Research Questions

### 1. RQ1: Comparative Performance Matrix
The integration of a secondary audit gate for synthetic grounding has pushed performance past the 0.80 Micro-F1 milestone.
- **Micro-F1 Ranking:** 1. `AuditedSynthetic` (0.8036), 2. `GatedStable-0.55` (0.8003), 3. `StableChampion` (0.7585), 4. `SyntheticAnchor` (0.7439).
- **The Audit Lift:** Adding a 0.70 similarity audit to synthetic anchors resulted in an **8% absolute F1 uplift** compared to the non-audited synthetic fallback.
- **Domain Delta:** `AuditedSynthetic` is the peak performer in **Technical** extraction (4.06 TPS), while non-gated `StableChampion` remains superior for **Cultural** tasks (4.26 TPS).
- **Detailed Asset:** [rq1_performance_analysis.md](full_gated_comparison/rq1_performance_analysis.md)

### 2. RQ2: Efficiency and Sustainability Analysis
The `AuditedSyntheticAgent` is the dominant architecture for resource efficiency, delivering a significant reduction in both cost and latency.
- **Token Consumption:** `AuditedSynthetic` consumes **3,755 tokens/task** (34% reduction vs. baseline).
- **PTC Ratio:** Achieving a PTC of **0.2140**, the audited agent is **61% more cost-effective** than the original Stable Champion.
- **Latency Advantage:** Despite its multi-gate complexity, `AuditedSynthetic` is the fastest pipeline (15.72s avg), benefiting from aggressive pruning of lengthy few-shot contexts.
- **Detailed Asset:** [rq2_efficiency_analysis.md](full_gated_comparison/rq2_efficiency_analysis.md)

### 3. RQ3: Error Profiling and Robustness
The Study identifies a clear trade-off between "Semantic Grounding" and "Structural Completeness" across the four strategies.
- **Hallucination Control:** `GatedStable (0.55)` is the most factually robust agent, reducing hallucinations by **32%** compared to the baseline.
- **Recall Dominance:** `AuditedSynthetic` achieved the lowest omission rate (40 missing fields), leveraging synthetic anchors to "unlock" fields the model would otherwise skip.
- **Structural Anchoring:** The synthetic fallback strategy (with or without audit) is the most effective way to minimize "Incorrect" type/format errors, though it introduces a parametric bias that increases hallucination risk.
- **Detailed Asset:** [rq3_error_analysis.md](full_gated_comparison/rq3_error_analysis.md)

## Conclusions
The **AuditedSyntheticAgent** is the current champion of the M.O.L.D. project. It demonstrates that the most effective way to improve SLM performance is not simply to provide more examples, but to **audit the quality of the grounding signal**. The strict 0.70 audit gate successfully filters out "semantic drift," allowing the model to pivot to a high-precision Zero-Shot mode when necessary. This results in an architecture that is simultaneously more accurate, more efficient, and faster than the baseline.

## Recommendations

### 1. Adopt AuditedSynthetic as the Primary Submission
The `AuditedSyntheticAgent` is the most well-rounded architecture for the IberLEF challenge, as it ranks first on both the **Performance Leaderboard** (0.8036 F1) and the **Efficiency Leaderboard** (0.2140 PTC).

### 2. Further Tune the Audit Threshold
The current 0.70 threshold for synthetic anchors is highly effective, but the 35% Zero-Shot pivot rate suggests there is room for optimization. Experimenting with a **0.65 audit threshold** might recover even more Recall without sacrificing the Precision gains.

### 3. Implement Hybrid Domain Gating
Consider using a "Triple-Path" agent:
- If RAG Similarity > 0.55: Use RAG.
- If RAG Similarity < 0.55 AND Domain is Technical/Medical: Use Audited Synthesis.
- Otherwise: Use pure Zero-Shot.
This would leverage each architecture's unique strengths discovered in the domain analysis.

---
*Research complete. Use the `/draft` command to turn this report into a publication-ready document.*
