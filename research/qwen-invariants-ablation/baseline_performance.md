# RQ1: Performance Baseline Analysis (No Invariants)

## 1. Quantitative Metrics (Qwen3-1.7b)
The following metrics represent the performance of the agents on `data/starter/` using the `qwen/qwen3-1.7b` model without any prompt invariants (Standard JSON Schema, no explicit null rule, no dialect rule).

| Agent | Precision | Recall | Micro-F1 |
| :--- | :--- | :--- | :--- |
| **Grounded-NI** | 0.5701 | 0.5056 | 0.5359 |
| **Auditor-NI** | 0.5856 | 0.5029 | 0.5411 |
| **End-Anchored-NI** | 0.6414 | 0.5979 | 0.6189 |
| **Two-Pass-NI** | 0.7412 | 0.6574 | 0.6968 |

## 2. Error Profile Analysis
- **Schema Adherence:** Qwen3-1.7b shows remarkably high baseline schema adherence for its size. Very few "Call Failed" errors were recorded in the NI configuration.
- **Two-Pass Dominance:** The Two-Pass agent (NI) is the strongest baseline (0.6968 F1), leveraging Qwen's strong Spanish reasoning capabilities in Pass 1 to structure the extraction in Pass 2.
- **Entity Labeling:** The primary error mode across all agents is incorrect categorization of entity labels (e.g., `Incorrect: entities.0.label (sim=0.00)`). The model often correctly identifies the text but uses a different label name than the one specified in the schema.
- **Hallucinations:** Grounded-NI and Auditor-NI show a significant number of "Hallucinated" fields in nested arrays (e.g., `technical_entities`, `medical_entities`), suggesting that without the "Null Rule", the model attempts to fill slots even when evidence is weak.
- **Recall Bottleneck:** Recall is consistently lower than precision, primarily due to the model missing optional fields or complex nested structures.

## 3. Comparison with Llama-3.2-3b
Surprisingly, the smaller Qwen model (1.7B) outperforms the larger Llama model (3B) in the baseline configuration across all comparable agents.

| Agent | Llama-3.2-3b (F1) | Qwen3-1.7b (F1) | Delta |
| :--- | :--- | :--- | :--- |
| Grounded-NI | 0.4728 | 0.5359 | **+13.3%** |
| Auditor-NI | 0.5120 | 0.5411 | **+5.7%** |
| End-Anchored-NI | 0.5929 | 0.6189 | **+4.4%** |

**Conclusion:** Qwen3-1.7b has a higher "raw" extraction capability out of the box than Llama-3.2-3b for the GenSIE task. This establishes a higher ceiling for the invariant experiments.
