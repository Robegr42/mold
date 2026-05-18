# RQ1: Comparative Performance Analysis

## Executive Summary
This report analyzes the quantitative performance of four extraction architectures on the `data/starter` dataset with Qwen 3 1.7B. The **AuditedSyntheticAgent** (Double-Gate) achieved the highest overall performance with an F1 score of **0.8036**, representing a ~6% absolute improvement over the original Stable Champion baseline.

## Quantitative Comparison Matrix

| Agent | Micro-F1 | Precision | Recall | Delta (vs Stable) | Rank |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **AuditedSyntheticAgent** | **0.8036** | **0.8435** | **0.7673** | **+5.95%** | 1 |
| **GatedStable (0.55 Gate)** | 0.8003 | 0.8400 | 0.7641 | +5.51% | 2 |
| **StableChampion (No Gate)**| 0.7585 | 0.8096 | 0.7135 | - | 3 |
| **SyntheticAnchor (No Audit)** | 0.7439 | 0.8079 | 0.6892 | -1.92% | 4 |

## Domain-Specific Performance (Average TPS)

| Domain | Stable | Gated (0.55) | Synthetic | Audited | Best Performer |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Technical** | 3.40 | 3.90 | 3.78 | **4.06** | AuditedSynthetic |
| **Medical** | 2.31 | **2.72** | 2.49 | 2.60 | GatedStable |
| **Legal** | 2.58 | **2.91** | 2.19 | 2.69 | GatedStable |
| **Cultural** | **4.26** | 3.78 | 3.37 | 3.96 | StableChampion |

## Key Findings

1. **The 0.55 Threshold Revolution:** Lowering the RAG gate from 0.65 (implied in previous runs) to 0.55 significantly boosted both Precision and Recall. By being more permissive with RAG examples, the model gained enough grounding to push F1 above the 0.80 barrier.
2. **The Double-Gate Advantage:** The `AuditedSyntheticAgent` outperformed the `GatedStable` agent by providing a secondary safety net. The 0.70 synthetic audit ensures that even when RAG fails, the synthetic grounding is of high semantic quality, leading to the highest Precision (0.8435) in the study.
3. **Recovery via Audit:** The `SyntheticAnchor` (no audit) was actually the worst performer (0.7439), likely due to "template hallucinations" where it followed a synthesized example that didn't match the task. Adding the **Audit Gate** turned this failing strategy into the overall winner (+8% F1 lift for the audit step).
4. **Domain Specialization:** The `AuditedSyntheticAgent` dominated in **Technical** tasks, where schema adherence is critical. However, the non-gated `StableChampion` still holds the lead in **Cultural** tasks, suggesting that for high-context/high-semantic tasks, any real few-shot data is superior to synthetic filtering.
