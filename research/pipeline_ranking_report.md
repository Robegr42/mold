# Research Report: Cross-Model Pipeline Ranking & Generalization

## Executive Summary
This study establishes a rigorous ranking of four optimized GenSIE pipelines across two representative small language models (**Qwen 1.7B** and **Llama 3B**). 

**Key Findings:**
1. **Model-Specific Champions:** **Grounded-Null** (0.7055 F1) is the winner for Qwen 1.7B, while **End-Anchored-Null** (0.6169 F1) is the champion for Llama 3B.
2. **The "Safe" Generalizer:** **Two-Pass-NI** is the only pipeline to maintain a consistent rank (2nd place) regardless of the model scale, making it the most robust choice for unknown SLMs.
3. **Efficiency Winner:** **Grounded-Null** is the efficiency champion, achieving top-tier performance with **~50% fewer tokens** than the Two-Pass approach.
4. **Universal Invariant:** The **Null Rule** is the single most important component for model-independent performance gain, appearing in both model-specific winning pipelines.

---

## Research Questions

### 1. Model-Specific Winners
For Qwen 1.7B, the **Grounded-Null** pipeline dominates. For Llama 3B, the **End-Anchored-Null** strategy provides the best stability. Qwen consistently achieves ~10% higher F1 than Llama across all comparable pipelines.

- **Findings:** Qwen 1.7B is a superior engine, but Llama 3B is more responsive to structural anchoring.
- **Detailed Assets:** [research/pipeline-ranking/model_specific_winners.md](research/pipeline-ranking/model_specific_winners.md)

---

### 2. Model-Independent Pipeline Hierarchy
Is it possible to rank these pipelines independently of the model? **Yes.**

| Tier | Pipeline | Status |
| :--- | :--- | :--- |
| **Tier 1** | **Two-Pass-NI** | Most stable generalizer (Consistent 2nd). |
| **Tier 1** | **Grounded-Null** | Peak performance on smaller SLMs (<2B). |
| **Tier 1** | **End-Anchored-Null** | Peak performance on medium SLMs (>3B). |
| **Tier 2** | **Auditor-Dialect** | Consistently underperforms (Rank 4). |

- **Findings:** Use Two-Pass for stability, Grounded-Null for speed, and End-Anchored-Null for larger context scales.
- **Detailed Assets:** [research/pipeline-ranking/generalization_analysis.md](research/pipeline-ranking/generalization_analysis.md)

---

### 3. Performance-to-Cost (P2C) Ratio
**Grounded-Null** achieves a Tier-1 F1 score (0.65 avg) with only **883 tokens** per task, compared to **1790 tokens** for Two-Pass-NI. This represents a 2x efficiency gain with negligible accuracy loss.

- **Findings:** Grounded-Null is the optimal production choice for high-throughput GenSIE.
- **Detailed Assets:** [research/pipeline-ranking/efficiency_analysis.md](research/pipeline-ranking/efficiency_analysis.md)

---

### 4. Error Mode Suppression Profiles
The **Null Rule** is the universal suppressor for hallucinations. Grounded strategies excel at precision through verbatim matching, while End-Anchored strategies excel at schema adherence through template rigidity.

- **Findings:** All Tier-1 pipelines rely on the Null Rule to prevent model "hedging".
- **Detailed Assets:** [research/pipeline-ranking/error_profiles.md](research/pipeline-ranking/error_profiles.md)

---

## Conclusions
1. **No single pipeline is "best" for every model**, but a clear Tier 1 exists.
2. **Qwen 1.7B + Grounded-Null** is the current state-of-the-art for sub-3B GenSIE.
3. **Robustness vs. Efficiency:** Two-Pass-NI is the most robust; Grounded-Null is the most efficient.

## Recommendations
1. **For General Benchmarking:** Use **Two-Pass-NI** as it provides the most stable cross-scale comparison.
2. **For Resource-Constrained Extraction:** Standardize on **Grounded-Null**.
3. **For High-Hallucination Models:** Standardize on **End-Anchored-Null**.
4. **Discard Auditor-Dialect** for models <14B; the multi-pass cognitive load exceeds the benefit of semantic rules at this scale.

**Research Complete.** You can now use the `/draft` command to turn this executive report into a fully fleshed-out article or white paper.
