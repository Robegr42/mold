# GenSIE: Llama 3.2 3B `eval2` Results Analysis

## Executive Summary
This report analyzes the detailed performance metrics of Llama 3.2 3B obtained via the `eval2` function. The data reveals a significant **Efficiency Gap**: while multi-pass strategies like `Two-Pass` and `Auditor` increase recall, they carry a heavy token (~2.6k/task) and latency (~12s) tax that often results in lower absolute F1 than more efficient single-pass methods. The **Grounded Strategy** emerged as the most cost-effective, achieving an F1 of 0.5531 on the Dev set with the highest F1-per-token ratio. Key failure modes include the **Rigid Type Bottleneck** (Enum/Boolean mismatches) and **List Exhaustion Failure**. Recommendations focus on refining the Grounded strategy with semantic Enum mapping and pruning templates to reduce attention drift.

## Research Questions

### 1. Efficiency and Cost Analysis
**How does token usage and execution time correlate with performance (F1)?**
*   **Grounded Supremacy:** The `Grounded` strategy is the most efficient (1.08 F1/1k tokens on Starter). On Dev, it outperforms the expensive `Two-Pass` agent in both F1 and cost.
*   **The Reasoning Tax:** `Two-Pass` uses >2x the tokens of `Grounded` for a -5% F1 drop on Dev, suggesting the model's self-generated analysis may be introducing more noise than clarity.
*   **Detailed Analysis:** [Efficiency & Cost Analysis](eval2_results_analysis/efficiency_cost.md)

### 2. Failure Mode Deep-Dive
**What specific JSON fields and error types are most prevalent?**
*   **The Enum Bottleneck:** Most "Incorrect" errors (sim=0.00) occur on Rigid Types (Enums/Booleans). The model fails to map Spanish synonyms to the strict English Enum values.
*   **Recall Gaps:** "Missing" errors are prevalent in hierarchical arrays, where the model extracts the first few items but fails to exhaustively list all entities.
*   **Detailed Analysis:** [Failure Mode Deep-Dive](eval2_results_analysis/failure_modes.md)

### 3. Pipeline Scalability
**How do the metrics change when moving from `starter` to `dev`?**
*   **End-Anchored Collapse:** F1 drops from 0.60 to 0.47 on Dev as schema complexity grows. Token usage increases by 80% due to larger templates, consuming the model's attention.
*   **Robustness of Grounding:** The `Grounded` pipeline is the only one that *improves* or stays stable in F1 when moving to the more complex Dev set, proving its robustness.

## Conclusions
1.  **Grounded Reasoning > Abstract Analysis:** For SLMs like Llama 3.2 3B, anchoring every extraction to a source quote is more effective than a separate "step-by-step" reasoning pass.
2.  **Structural Attention is Finite:** Verbose templates (End-Anchored) and verbose analysis (Two-Pass) both lead to "drift," where the model loses focus on the context-to-schema mapping.
3.  **Semantic Mapping Gap:** The binary scoring of Rigid Types penalizes the model heavily for minor dialectal or lexical mismatches in Enums.

## Recommendations
1.  **Refine Grounded Prompting:** Update `GroundedAgent` to specifically mandate quotes for Rigid Type fields to improve mapping accuracy.
2.  **Semantic Enum Priming:** For all agents, include a "Synonym Map" in the prompt for Enum values (e.g., `AUTOIMMUNE (inmunitario, autoinmune)`).
3.  **Template Pruning:** In `EndAnchoredAgent`, prune the blank template to only include `required` fields to save tokens and minimize attention drift.
4.  **Final Suggestion:** The research is complete. You can now use the `/draft` command to turn this executive report into a fully fleshed-out article or white paper.
