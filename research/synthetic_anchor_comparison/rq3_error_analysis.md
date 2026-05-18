# RQ3: Comparative Robustness and Error Analysis

## Executive Summary
This report analyzes the behavioral failure modes of the `StableChampionAgent`, `GatedStableChampionAgent`, and `SyntheticAnchorAgent`. Contrary to initial hypotheses, the non-gated `StableChampionAgent` remains the most grounded architecture, exhibiting the fewest total hallucinations (182). The `SyntheticAnchorAgent` succeeds in reducing "Incorrect" extraction errors (-7% vs gated baseline) by providing a strict structural anchor.

## Error Type Distribution

| Agent | Missing (Omission) | Incorrect (Semantic) | Hallucinated (Grounding) | Total Errors |
| :--- | :---: | :---: | :---: | :---: |
| **StableChampionAgent** | 67 | 102 | **182** | 351 |
| **GatedStableChampionAgent** | **48** | 102 | 200 | **350** |
| **SyntheticAnchorAgent** | 55 | **95** | 202 | 352 |

## Behavioral Observations

### 1. The Grounding Paradox
The non-gated **StableChampionAgent** achieved the best grounding (fewest hallucinations). This suggests that even "noisy" RAG examples (those with similarity between 0.0 and 0.55) provide a stabilization effect for the Qwen 3 1.7B model. Removing these examples (Gated) or replacing them with a synthesized one (Synthetic) actually increased the model's tendency to hallucinate entities not present in the source text.

### 2. Structural Stability via Synthesis
The **SyntheticAnchorAgent** achieved the lowest count of "Incorrect" extractions (95). This confirms the research hypothesis that a "Golden Example" synthesized by the ArchitectModule acts as a superior structural anchor compared to Zero-Shot or distant RAG. It helps the model stay within the schema's type constraints and value ranges more effectively.

### 3. Recall Dynamics
The **GatedStableChampionAgent** (Zero-Shot Fallback) showed the fewest "Missing" errors. This indicates that when the model is not "distracted" by RAG examples, it is more likely to attempt to extract every field defined in the schema. However, the high hallucination count (200) for this agent confirms that these extractions are often not grounded in the source text.

### 4. Gating effectiveness
The fact that total errors remain nearly identical across all three architectures (~350) suggests that the current 0.55 gate is triggering on tasks that are fundamentally difficult for the 1.7B model. While the strategy (RAG vs Synthetic vs Zero-Shot) changes the *flavor* of the error (Omission vs Hallucination), it doesn't significantly change the total error volume.

## Conclusion
The **SyntheticAnchorAgent** provides a valuable "High-Fidelity" extraction mode that reduces semantic errors. However, for maximum grounding in the current distribution, the **StableChampionAgent**'s "Inclusive RAG" strategy is superior. The synthetic anchor is a powerful tool for preventing schema drift, but it requires further tuning of the "Generalization Directive" to match the grounding signal of real RAG examples.
