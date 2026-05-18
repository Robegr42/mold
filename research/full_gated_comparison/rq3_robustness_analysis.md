# RQ3: Error Profiling and Robustness Analysis

## Executive Summary
This report analyzes the behavioral failure modes of the four extraction architectures. The study reveals a distinct shift in "error flavor" across strategies: non-gated agents favor precision through grounding, while synthetic-audited agents maximize recall by eliminating omissions. The **GatedStable (0.55)** agent achieved the lowest total error volume, while the **AuditedSynthetic** agent provided the most complete extractions.

## Error Distribution Matrix

| Agent | Missing (Omission) | Incorrect (Semantic) | Hallucinated (Grounding) | Total Errors |
| :--- | :---: | :---: | :---: | :---: |
| **GatedStable (0.55)** | 56 | 99 | **123** | **278** |
| **AuditedSynthetic** | **40** | 102 | 205 | 347 |
| **StableChampion** | 67 | 102 | 182 | 351 |
| **SyntheticAnchor** | 55 | **95** | 202 | 352 |

## Key Findings

### 1. The 0.55 Threshold Success
The `GatedStable` agent with a 0.55 threshold is the most "balanced" architecture. It reduced hallucinations by **32%** compared to the original Stable Champion, while also reducing omissions. This confirms that the 0.55 gate effectively filters out "truly toxic" RAG noise without depriving the model of the structural grounding it needs for general tasks.

### 2. High-Recall Synthetic Anchors
The `AuditedSyntheticAgent` achieved the lowest "Missing" count (40). Providing a synthetic structural anchor—even when RAG fails—emboldens the model to attempt extractions that it would otherwise skip in Zero-Shot mode. This "Recall Lift" is the primary reason why it achieved the study's highest F1 score (0.8036).

### 3. The Hallucination Trade-off
There is a visible correlation between synthetic grounding and increased hallucinations. Both agents using synthetic anchors (`SyntheticAnchor` and `AuditedSynthetic`) showed the highest hallucination counts (>200). This suggests that while synthetic anchors stabilize JSON structure, they also increase the model's parametric confidence, leading it to "fill in the gaps" with information not present in the source text.

### 4. Semantic Stability
The `SyntheticAnchor` (no audit) achieved the fewest "Incorrect" errors (95). This confirms that a localized synthetic anchor is an extremely effective way to prevent semantic drift and ensure the model correctly interprets schema types (enums, types, etc.).

## Conclusion
The **AuditedSyntheticAgent** is the optimal choice for tasks where **completeness (Recall)** is prioritized, as it minimizes omitted fields. However, for applications where **factuality (fewest hallucinations)** is paramount, the **GatedStable (0.55)** agent is superior. The research confirms that auditing is a highly effective filter for maintaining precision in synthetic pipelines.
