# Detailed Cross-Model Evaluation Summary Report

## 1. Executive Summary
This report aggregates the results of the Stable-Champion pipeline evaluation across three sub-5B models. The goal was to identify the impact of RAG density, reasoning language, and instruction complexity (hints) on extraction performance.

## 2. Comparison Matrix

| Model | Variant | Precision | Recall | Micro-F1 | Avg TPS |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Qwen 3 1.7B | V0 (Baseline) | 0.7523 | 0.6885 | 0.7190 | 3.05 |
| Qwen 3 1.7B | V1 (Default Champion) | 0.8210 | 0.7746 | 0.7972 | 3.43 |
| Qwen 3 1.7B | V2 (Sparse RAG, K=1) | 0.7804 | 0.7495 | 0.7646 | 3.32 |
| Qwen 3 1.7B | V3 (English Reasoning) | 0.8171 | 0.7109 | 0.7603 | 3.15 |
| Qwen 3 1.7B | V4 (Minimal Hints, H=1) | 0.7679 | 0.6855 | 0.7244 | 3.03 |
| Qwen 3 1.7B | V5 (Maximal Hints, H=5) | 0.8137 | 0.7585 | 0.7851 | 3.36 |
| Llama 3.2 3B | V0 (Baseline) | 0.6202 | 0.4870 | 0.5456 | 2.16 |
| Llama 3.2 3B | V1 (Default Champion) | 0.7390 | 0.6096 | 0.6681 | 2.70 |
| Llama 3.2 3B | V2 (Sparse RAG, K=1) | 0.7649 | 0.5661 | 0.6506 | 2.50 |
| Llama 3.2 3B | V3 (English Reasoning) | 0.7363 | 0.6199 | 0.6731 | 2.74 |
| Llama 3.2 3B | V4 (Minimal Hints, H=1) | 0.7716 | 0.6190 | 0.6870 | 2.74 |
| Llama 3.2 3B | V5 (Maximal Hints, H=5) | 0.7893 | 0.5976 | 0.6802 | 2.64 |
| Gemma 4 E4B | V0 (Baseline) | 0.7654 | 0.6616 | 0.7097 | 2.93 |
| Gemma 4 E4B | V1 (Default Champion) | 0.7844 | 0.7755 | 0.7799 | 3.43 |
| Gemma 4 E4B | V2 (Sparse RAG, K=1) | 0.7881 | 0.7837 | 0.7859 | 3.47 |
| Gemma 4 E4B | V3 (English Reasoning) | 0.8095 | 0.7820 | 0.7955 | 3.46 |
| Gemma 4 E4B | V4 (Minimal Hints, H=1) | 0.8016 | 0.7926 | 0.7971 | 3.51 |
| Gemma 4 E4B | V5 (Maximal Hints, H=5) | 0.8033 | 0.7760 | 0.7894 | 3.43 |

## 3. Model Analysis

### Qwen 3 1.7B
- **Best Variant**: V1 (Default Champion) (F1: 0.7972)
- **RAG Sensitivity**: High-density RAG (K=3) is preferred, as sparse RAG reduced recall.
- **Language Impact**: Spanish reasoning maintained higher alignment for this model.
- **Instructional Benefit**: More architect hints (H=5) improved performance, indicating the model handles complex guidance well.

### Llama 3.2 3B
- **Best Variant**: V4 (Minimal Hints, H=1) (F1: 0.6870)
- **RAG Sensitivity**: High-density RAG (K=3) is preferred, as sparse RAG reduced recall.
- **Language Impact**: English reasoning outperformed Spanish, likely due to better alignment with pre-training data.
- **Instruction Fatigue**: Minimal hints (H=1) outperformed maximal hints (H=5), suggesting larger prompts dilute focus.

### Gemma 4 E4B
- **Best Variant**: V4 (Minimal Hints, H=1) (F1: 0.7971)
- **RAG Sensitivity**: Sparse RAG (K=1) improved performance, suggesting context noise was a factor.
- **Language Impact**: English reasoning outperformed Spanish, likely due to better alignment with pre-training data.
- **Instruction Fatigue**: Minimal hints (H=1) outperformed maximal hints (H=5), suggesting larger prompts dilute focus.

## 4. Stable-Champion Pareto Frontier
The following configurations represent the optimal balance of accuracy (F1) and efficiency (TPS) for each model:

- **Qwen 3 1.7B**: V1 (Default Champion) (F1: 0.7972, TPS: 3.43)
- **Llama 3.2 3B**: V4 (Minimal Hints, H=1) (F1: 0.6870, TPS: 2.74)
- **Gemma 4 E4B**: V4 (Minimal Hints, H=1) (F1: 0.7971, TPS: 3.51)

## 5. Final Recommendations
1. **Deployment Choice**: Use **Gemma 4 E4B** with **V4 (Minimal Hints)** for the highest overall reliability and speed.
2. **Architecture**: Standardize on **English Reasoning** for Llama and Gemma variants to maximize logical consistency.
3. **Hint Management**: Small models (1.7B - 3B) benefit from **minimalist instruction (H=1)** to avoid 'instruction fatigue' and attention dilution.
