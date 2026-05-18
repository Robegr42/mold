# RQ2: Efficiency and Sustainability Analysis

## Executive Summary
This report analyzes the computational efficiency of the gated and synthetic architectures. The **AuditedSyntheticAgent** is the clear winner in efficiency, achieving the highest Performance-to-Cost (PTC) Ratio (**0.2140**) and reducing average token consumption by **34%** compared to the Stable Champion baseline.

## Efficiency Comparison Matrix

| Agent | Avg Tokens / Task | Avg Latency / Task | PTC Ratio (F1/kTok) | Efficiency Rank |
| :--- | :---: | :---: | :---: | :---: |
| **AuditedSyntheticAgent** | **3,755** | **15.72s** | **0.2140** | 1 |
| **GatedStable (0.55 Gate)** | 5,629 | 21.35s | 0.1422 | 2 |
| **StableChampion (No Gate)**| 5,728 | 22.06s | 0.1324 | 3 |
| **SyntheticAnchor (No Audit)** | 5,739 | 22.92s | 0.1296 | 4 |

## Key Findings

### 1. The Power of Pruning
The `AuditedSyntheticAgent` achieved a massive reduction in token overhead. By enforcing a strict **0.70 similarity audit** for synthetic examples, it rejected low-quality anchors in **35% of tasks**, pivoting immediately to Zero-Shot extraction. This "fail-fast" strategy saved approximately 2,000 tokens per task while maintaining peak accuracy.

### 2. Latency Optimization
Despite adding a synthesis pass and an audit embedding step, the `AuditedSyntheticAgent` was the fastest architecture (15.72s avg). This is because the time saved by skipping the long few-shot contexts in the extraction pass (for 35% of tasks) far outweighed the <100ms overhead of the embedding and synthesis calls.

### 3. Performance-to-Cost (PTC) Superiority
The `AuditedSyntheticAgent` is the most sustainable option for the GenSIE competition. It provides the highest "accuracy per dollar," outperforming the baseline by **+61% in PTC**. This demonstrates that auditing is not just a safety feature, but a primary driver of resource efficiency.

### 4. GatedStable Efficiency
The `GatedStable` agent with a 0.55 threshold provided a small token saving (~2%) compared to the baseline. This confirms that at the 0.55 level, very few tasks are actually being gated out, whereas the 0.70 synthetic audit is significantly more aggressive and effective.

## Conclusion
The **AuditedSyntheticAgent** represents the production-ready peak of the M.O.L.D. pipeline. It simultaneously maximizes extraction quality and minimizes resource consumption by autonomously choosing between RAG, Synthetic Grounding, and Zero-Shot modes based on a verifiable quality audit.
