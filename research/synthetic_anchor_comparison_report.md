# Research Report: Synthetic Anchor vs. Gated vs. Stable Champion

## Executive Summary
This report synthesizes the results of a three-way comparative experiment between the **StableChampionAgent**, **GatedStableChampionAgent**, and the newly implemented **SyntheticAnchorAgent** using the Qwen 3 1.7B model. 

**Key Findings:**
1. **Stable is Champion:** The non-gated `StableChampionAgent` remains the overall performance leader (0.7585 F1), primarily due to superior grounding in the Cultural domain.
2. **Synthesis Recovers Precision:** The `SyntheticAnchorAgent` successfully recovered Precision (+1.1% vs gated baseline) and achieved the lowest count of "Incorrect" extraction errors (95), proving its value as a structural stabilizer.
3. **The Grounding Paradox:** Real RAG examples, even when semantically distant (low similarity), provide a better grounding signal for the 1.7B model than synthetic examples, which showed the highest hallucination count (202).
4. **Efficiency vs. Performance:** `StableChampion` provides the best Performance-to-Cost (PTC) ratio (0.1324). The `SyntheticAnchorAgent` is the most resource-intensive due to a ~2.3% token overhead from the synthesis pass.

## Research Questions

### 1. RQ1: Quantitative Extraction Performance
The `StableChampionAgent` maintains the overall performance lead, while the `SyntheticAnchorAgent` demonstrates improved precision over the gated baseline.
- **F1 Score Ranking:** 1. `StableChampion` (0.7585), 2. `SyntheticAnchor` (0.7439), 3. `GatedStable` (0.7408).
- **Precision vs. Recall:** The `SyntheticAnchorAgent` recovered significant precision (+1.1%) compared to the `GatedStableChampionAgent`, nearly matching the non-gated stable agent.
- **Domain Delta:** `SyntheticAnchorAgent` is the top performer in **Technical** and **Medical** domains, while `StableChampion` dominates in **Cultural** tasks.
- **Detailed Asset:** [rq1_performance_analysis.md](synthetic_anchor_comparison/rq1_performance_analysis.md)

### 2. RQ2: Efficiency and Cost-to-Performance Analysis
The `StableChampionAgent` remains the most cost-effective solution, while the `SyntheticAnchorAgent` incurs a "Synthesis Tax."
- **Token Consumption:** `GatedStable` is the most efficient (5,607 tokens/task), while `SyntheticAnchor` is the most expensive (5,739 tokens/task).
- **PTC Ratio:** `StableChampion` leads with 0.1324, followed by `GatedStable` (0.1321) and `SyntheticAnchor` (0.1296).
- **Synthesis Overhead:** The dynamic synthesis pass adds ~2.3% token overhead and ~1.7% latency compared to the gated baseline.
- **Detailed Asset:** [rq2_efficiency_analysis.md](synthetic_anchor_comparison/rq2_efficiency_analysis.md)

### 3. RQ3: Comparative Robustness and Error Analysis
The architectures differ primarily in their "error flavor," with the non-gated agent showing superior grounding.
- **Hallucination Mitigation:** `StableChampion` is the most grounded (182 hallucinations), while `SyntheticAnchor` has the most (202), suggesting "noisy" RAG is better than synthetic for grounding this model.
- **Incorrect Extraction:** `SyntheticAnchor` achieved the fewest "Incorrect" errors (95), confirming the effectiveness of the synthetic structural anchor.
- **Error Distribution:** Total error volume is nearly identical across all agents (~350), indicating the gated tasks are fundamentally challenging.
- **Detailed Asset:** [rq3_error_analysis.md](synthetic_anchor_comparison/rq3_error_analysis.md)

## Conclusions
The **SyntheticAnchorAgent** successfully addresses the precision drop seen in gated architectures, making it a powerful tool for complex, domain-specific tasks (Technical/Medical). However, for the Qwen 3 1.7B model on the current starter distribution, the **StableChampionAgent** (Inclusive RAG) is the optimal generalist choice. The research highlights a "Grounding Paradox" where even semantically distant real examples outperform localized synthetic ones in preventing hallucinations. The 0.55 similarity gate effectively identifies "Hard Tasks," but the current fallback strategies primarily shift the error profile rather than reducing the overall error volume.

## Recommendations

### 1. Domain-Aware Gating
Implement a **Domain-Aware Gate**. Use the `SyntheticAnchor` strategy for Technical and Medical tasks (where it wins) and maintain the `StableChampion` strategy for Cultural and Legal tasks. This hybrid approach would likely push the overall F1 score toward **0.78+**.

### 2. Grounded Synthesis
Enhance the `ArchitectModule` synthesis prompt to include a "Grounding Directive." Force the model to generate synthetic JSON values that are directly traceable to specific phrases in the synthetic text. This could solve the grounding gap and reduce the hallucination count for the `SyntheticAnchorAgent`.

### 3. Synthetic Similarity Gating (SSG)
Implement **Synthetic Similarity Gating**. Before using a synthesized anchor, verify its similarity to the task using the local embedding model (Gate 2). If similarity is < 0.70, reject the anchor and pivot to Zero-Shot. This "Double-Gate" strategy would prevent "distractor synthesis" from poisoning the worker context.

---
*Research complete. Use the `/draft` command to turn this report into a publication-ready document.*
