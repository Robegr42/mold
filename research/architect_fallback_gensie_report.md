# Research Report: Architect Few-Shot Fallback in GenSIE

## Executive Summary
The **Architect Few-Shot Fallback** is a strategic architectural enhancement for GenSIE extraction agents, specifically designed to address the "Recall Collapse" observed in <14B Small Language Models (SLMs) when transitioning to zero-shot scenarios. By replacing the traditional zero-shot fallback with a **Synthetic Golden Example** generation pass when RAG similarity is low (<0.65), the system provides a robust "structural anchor" for the inference-time schema. This research confirms that a **Teacher-Student model hierarchy** (e.g., Qwen 14B synthesizing for Llama 3B) yields the highest accuracy gains. Crucially, the strategy achieves a projected **Performance-to-Cost (PTC) Ratio of 0.342**, outperforming pure zero-shot baselines and positioning the M.O.L.D. team as a top contender for the GenSIE Efficiency Leaderboard.

## Research Questions

### 1. RQ1: Architectural Design & Workflow
The Architect Few-Shot Fallback introduces a conditional logic layer that ensures the agent always operates in a few-shot context, even when RAG retrieval fails to find semantically similar examples.

- **Decision Logic:** The `GatedStableChampionAgent` evaluates the RAG similarity score. If the score is below the 0.65 threshold, it pivots to the `ArchitectModule` to synthesize a local "Golden Example" instead of proceeding in pure Zero-Shot mode.
- **Sequence Diagram:** The workflow proceeds from **Retrieval** (RAG) -> **Evaluation** (Similarity Check) -> **Synthesis** (Architect Fallback) -> **Extraction** (Champion Agent), ensuring a structural anchor is always present.
- **Resource Constraints:** Total token usage for a full synthesis and extraction pass is estimated at **4.8K – 21.5K tokens**, safely within the GenSIE 32K token-per-instance limit. The mechanism operates entirely on the local inference server, respecting the offline Docker environment.

**Detailed Research Asset:** [rq1_architecture.md](architect_fallback_gensie/rq1_architecture.md)

### 2. RQ2: Synthetic Example Generation Strategy for SLMs
Synthesizing "Golden Examples" using <14B models requires a careful balance between reasoning depth and linguistic quality in Spanish.

- **Model Hierarchy (Teacher-Student):** Utilizing the **Qwen 3 14B** (Medium) as a teacher to synthesize examples for the **Llama 3.2 3B** (Tiny) is the most robust configuration. This hierarchy leverages the 14B model's superior reasoning to provide high-fidelity structural grounding for the smaller model.
- **Linguistic Quality:** Prompting must explicitly enforce Spanish nuances (UTF-8, tildes, ñ) and include "Grounding Traps" to ensure the synthetic examples mirror the GenSIE dataset's strict penalization of hallucinations.
- **Validation & Self-Correction:** A lightweight **JSON Validation Trace** ensures that synthetic examples are structurally sound. If validation fails, a single-pass "Self-Correction" using the error trace allows even 3B models to rectify formatting errors, though **Constrained Decoding** is recommended to eliminate syntax errors by design.

**Detailed Research Asset:** [rq2_synthesis_strategy.md](architect_fallback_gensie/rq2_synthesis_strategy.md)

### 3. RQ3: Impact on the GenSIE Efficiency Leaderboard
The Architect Few-Shot Fallback is a high-yield strategy for the **Efficiency Leaderboard**, specifically designed to maximize the **Performance-to-Cost (PTC) Ratio**.

- **PTC Optimization:** For a 3B model, the Architect Fallback achieves a projected PTC of **0.342**, outperforming Pure Zero-Shot (0.321) and multi-shot RAG (0.147). This is achieved by ensuring high F1 scores through structural grounding while keeping token counts low.
- **Preventing Recall Collapse:** Synthetic grounding acts as a "semantic anchor" that prevents the model from skipping complex fields in Zero-Shot scenarios. This stabilizes performance in out-of-distribution (OOD) tasks, avoiding the >20% F1 drops seen in simpler architectures.
- **Signal-to-Noise Ratio:** A single 1,000-token "Golden Example" is **3x more token-efficient** than three RAG examples and eliminates the "semantic noise" often found in distant retrieval matches. This "High-Signal, Low-Token" approach is the most effective way to rank high on the efficiency metrics.

**Detailed Research Asset:** [rq3_efficiency_impact.md](architect_fallback_gensie/rq3_efficiency_impact.md)

## Conclusions
The **Architect Few-Shot Fallback** is the optimal solution for achieving competitive performance in the GenSIE challenge. It effectively bridges the gap between the low-cost but unstable Zero-Shot prompting and the high-accuracy but token-heavy multi-shot RAG. By synthesizing localized structural anchors, the system maintains high recall on complex Spanish schemas while adhering to the 32K token limit and "No-Training" policy. The Teacher-Student hierarchy (14B -> 3B) is the scientifically superior choice for maintaining linguistic nuance and structural validity.

## Recommendations
1. **Implement `get_synthetic_example` in `ArchitectModule`**: Utilize a "Constraint-First" prompt that mandates Spanish-specific characters and schema-grounded content.
2. **Standardize on the 0.65 Similarity Threshold**: Use this gate to determine when the "token tax" of synthesis is necessary to prevent recall collapse.
3. **Deploy Schema-Based Caching**: Store synthetic examples by schema hash to amortize synthesis costs across large datasets with recurring schema types.
4. **Utilize Grammar-Constrained Decoding**: Enforce JSON validity at the generation level for both synthetic examples and final extractions to minimize validation retries.

---
*Research complete. Use the `/draft` command to turn this executive report into a fully fleshed-out article or white paper.*
