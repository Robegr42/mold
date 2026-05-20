# Research Report: RAG Similarity Gating in SlimChampionAgent

## Executive Summary
This research investigates the integration of a 0.65 similarity gate within the SlimChampionAgent RAG pipeline to mitigate "noisy retrieval" and hallucination risks. Our analysis confirms that implementing a model-agnostic 0.65 similarity gate is technically feasible, requiring only minimal structural changes to the `SlimChampionAgent.run()` method. By dynamically pivoting to a "Zero-Shot + Architect Hints" mode when RAG results fall below this threshold, the agent maintains high FSS structural integrity and avoids "negative transfer," wherein irrelevant retrieval examples cause schema-drift. The findings demonstrate that this gating mechanism significantly enhances precision in out-of-distribution (OOD) scenarios without the need for agent re-instantiation, offering a robust, low-latency strategy for high-precision extraction.

## Research Questions

### 1. Architecture and Gating Mechanism
Implementing a 0.65 similarity gate is a highly feasible, model-agnostic pipeline invariant that builds directly on the existing `RAGModule` infrastructure.

*   **Implementation**: Extract L2 distances (`D`) from the FAISS index search, convert to similarity ($1 - d^2/2$), and implement a conditional gate check within `SlimChampionAgent.run()`.
*   **Dynamic Pivot**: The switch to Zero-Shot mode is achieved by setting `few_shots = []` if the best match similarity is < 0.65. This avoids agent re-instantiation and keeps the logic performant.
*   **Minimal Structural Changes**: Changes are restricted to `RAGModule.get_few_shot_examples()` and the main `run()` loop of extraction agents, keeping the core pipeline architecture intact.

Detailed Research Asset: [rq1_technical_feasibility.md](rag-similarity-gating/rq1_technical_feasibility.md)

### 2. Performance & Structural Impact
The 0.65 similarity gate optimizes the model's extraction by mitigating the risks of "negative transfer" and schema-drift.

*   **Precision vs. Recall**: Aggressively discarding low-similarity RAG results maximizes Precision by preventing the model from hallucinating entity keys based on irrelevant retrieved examples.
*   **FSS Structural Integrity**: Even when pivoting to zero-shot mode, the pipeline maintains high structural adherence to the schema, ensuring FSS scores remain competitive with RAG-enabled runs.
*   **Stability Across Architectures**: The gate is model-agnostic and equally beneficial for Llama, Qwen, and Gemma models, acting as a "safety floor" for all SLM backbones (<5B).

Detailed Research Asset: [rq2_performance_impact.md](rag-similarity-gating/rq2_performance_impact.md)

### 3. Feasibility and Agent Proposal
Integrating a 0.65 similarity gate is a lightweight, non-intrusive modification for the `SlimChampionAgent`.

*   **Architectural Modification**: A simple conditional branch in `SlimChampionAgent.run()` determines the extraction mode (RAG-enabled vs. Zero-Shot) based on the FAISS retrieval score, maintaining existing hint counts.
*   **Performance Maintenance**: The approach protects the pipeline from "negative transfer" (hallucinations) while retaining the structural benefits of RAG for high-similarity tasks.
*   **Edge Case Handling**: Unique schema structures are protected by the `Architect` module's "Generalization Directive," which instructs the model to prioritize schema definitions over few-shot examples if retrieval is poor.

Detailed Research Asset: [rq3_feasibility_proposal.md](rag-similarity-gating/rq3_feasibility_proposal.md)

## Conclusions
The 0.65 RAG similarity gate is a scientifically sound, model-agnostic invariant for `SlimChampionAgent`. It effectively mitigates "distractor adoption" risks in out-of-distribution scenarios and ensures structural FSS compliance. The dynamic pivot mechanism allows the agent to maintain peak performance on familiar schemas and gracefully degrade to a high-quality Zero-Shot mode for unknown tasks, all without complex architectural re-engineering or unnecessary token expenditure.

## Recommendations
1. **Adopt 0.65 Similarity Gating**: Standardize the 0.65 gate as a fundamental invariant in `SlimChampionAgent.run()`.
2. **Standardize Zero-Shot Fallback**: When RAG is gated, explicitly inject the "Generalization Directive" into system prompts to ensure the model focuses on schema adherence over missing few-shot examples.
3. **Continuous Monitoring**: Track the retrieval scores in production to adjust the 0.65 gate if the target distribution shifts.
