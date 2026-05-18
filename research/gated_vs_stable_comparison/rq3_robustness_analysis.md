# RQ3: Qualitative Robustness and Error Analysis

## Executive Summary
This report investigates the behavioral impact of the 0.65 RAG Similarity Gate. The gate triggered in 10% of the tasks, successfully transitioning the agent to a Zero-Shot Pivot mode. However, in these specific cases, the Stable agent (with noisy RAG) generally maintained better accuracy than the Gated agent (zero-shot), suggesting that for this model size, "noisy context" is often better than "no context."

## Gating Behavior Analysis

The gate triggered in 4 tasks out of 40 (10%). Below is a comparison of performance on those specific "OOD-adjacent" tasks:

| Task ID | Gate Triggered? | Stable TPS | Gated TPS | Delta | Result |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `legal_legislation_001` | **YES** | **4.97** | 4.55 | -8.5% | Stable Won |
| `legal_legislation_005` | **YES** | **3.26** | 3.23 | -1.0% | Stable Won |
| `technical_software_004` | **YES** | **8.08** | 7.08 | -12.4% | Stable Won |
| `legal_legislation_004` | **YES** | 3.43 | **3.52** | +2.6% | **Gated Won** |

## Error Profile Comparison

### 1. Hallucinations vs. Omissions
- **Stable Agent:** Showed a higher tendency to hallucinate keys or formats from the (potentially irrelevant) few-shot examples. This confirmed the "Negative Transfer" hypothesis, though the impact on the final FSS score was mitigated by the model's overall reasoning ability.
- **Gated Agent:** Showed fewer schema-drift hallucinations but increased **omission errors** (Missing keys). Without few-shot examples to "prime" the model on what might be hidden in the text, it defaulted to a more conservative `null` strategy.

### 2. Effectiveness of the "Generalization Directive"
The "Generalization Directive" successfully steered the Gated agent to extract information zero-shot without crashing. However, the drop in TPS suggests that the `qwen/qwen3-1.7b` model struggles to follow complex schemas zero-shot as effectively as it does when prompted with even slightly irrelevant examples.

## Conclusion
The **0.65 Similarity Gate** is technically robust and triggers as expected. However, for the Qwen 3 1.7B model, the "safety threshold" of 0.65 might be too conservative. The model appears to benefit from the structural grounding of few-shot examples even when semantic similarity is low. 

**Recommendation:** Consider lowering the gate threshold to **0.55** or implementing an "Architect-only few-shot" (synthetic examples) when retrieval fails, rather than a pure zero-shot pivot.
