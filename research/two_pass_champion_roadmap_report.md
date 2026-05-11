# Two-Pass Champion: The Robust GenSIE Roadmap

## Executive Summary
This roadmap establishes the "Two-Pass Champion" pipeline, a robust, model-agnostic architecture for the IberLEF 2026 GenSIE task. By leveraging the proven cross-model stability of the `Two-Pass-NI` engine, this design integrates modular layers for dynamic retrieval, schema-aware reasoning, and iterative verification. The resulting system is engineered to maximize the Flattened Schema Score while adhering to strict wall-clock (60s) and token (32K) limits. Key architectural shifts include an adaptive N=2 ensembling strategy and a transition to API-native structured outputs, ensuring 100% compliance with the GenSIE "Hosted Inference" environment. This roadmap provides the most reliable path to a high-performance, competition-ready submission that remains effective regardless of the underlying Small Language Model (SLM) provided by the organizers.

## Research Questions

### 1. Engine Integration (Two-Pass-NI Base)
*See full details in: [engine_integration.md](./two_pass_champion_roadmap/engine_integration.md)*

**Overview of Findings:**
Refactoring `Two-Pass-NI` into a modular `IExtractionEngine` provides the stable foundation needed for a high-accuracy pipeline.

*   **Modular Refactoring:** The Two-Pass logic is encapsulated in a new engine that accepts structured reasoning hints from the `ARCHITECT`. This allows the pipeline to provide the model with "What to look for" (analytical pass) and "How to format" (extraction pass) separately.
*   **Unified Null Rule:** The "Null Rule" is elevated from a local instruction to a global pipeline invariant. By using the `InvariantPromptMixin`, we ensure that the requirement to return `null` for missing information is consistently enforced in both passes.
*   **Performance Baseline:** A single modular Two-Pass execution takes ~4.2 seconds and roughly 2.5K tokens. While more expensive than single-pass engines, its model-agnostic stability justifies its role as the primary engine for the "Champion" pipeline.

### 2. Contextual Augmentation (RAG & Refinement)
*See full details in: [contextual_augmentation.md](./two_pass_champion_roadmap/contextual_augmentation.md)*

**Overview of Findings:**
The augmentation layer is split to support the two distinct phases of the extraction engine.

*   **Split Retrieval Strategy:** The RAG module uses **Semantic Retrieval** (MiniLM) for the Analytical Pass to fetch examples demonstrating complex reasoning. For the Extraction Pass, it uses **Structural Retrieval** to provide examples of perfect JSON syntax for similar schemas.
*   **Token Budgeting:** Given the multi-pass overhead, the roadmap limits the system to **3-4 high-quality examples**. This leaves roughly 9K tokens for retrieval within the 32K limit, ensuring the model isn't overwhelmed by context during the second (extraction) pass.
*   **ARCHITECT-Generated Hints:** The ARCHITECT module does not just refine the schema; it generates "Reasoning Hints" that act as a playbook for the Analytical Pass, guiding the model on how to interpret ambiguous fields before they are formatted into JSON.

### 3. Post-Extraction Audit (ReAct Verification)
*See full details in: [verification_audit.md](./two_pass_champion_roadmap/verification_audit.md)*

**Overview of Findings:**
The verification stage is added as a final "sanity check" to suppress any hallucinations that survived the two-pass process.

*   **Pluggable Verifier:** The `AuditorAgent` is triggered only for the specific fields identified in the second pass. It uses a ReAct loop to perform "grounding checks" (finding the exact sentence in the source text that supports a value).
*   **Restricted ReAct Budget:** To stay within 60s, the verifier is limited to **3-5 cycles**. The system uses "Batch Verification" (checking multiple fields in one prompt) to maximize the audit coverage within this limited turn budget.
*   **Emergency Nullification (Hard Stop):** The roadmap implements a hard stop at **55 seconds**. If the audit is not complete, any fields that are still "pending verification" are automatically set to `null` to protect the F1 score from False Positive penalties.

### 4. Ensembling & Hosted Compliance
*See full details in: [ensembling_compliance.md](./two_pass_champion_roadmap/ensembling_compliance.md)*

**Overview of Findings:**
The final design focuses on ensuring the pipeline is mathematically and technically compliant with the competition environment.

*   **Adaptive Ensembling (N=2 + Tie-breaker):** Research indicates that an N=3 Two-Pass ensemble (6 calls) is too risky for a 60s timeout. The roadmap recommends an **N=2 strategy with a third pass triggered only if the first two results diverge significantly**. This balances accuracy with "survival" probability.
*   **JSON Schema Refactoring:** The engine is permanently switched to use API-native **Structured Outputs**. By enforcing `json_schema` constraints at the API level (using `strict: true` or `response_schema`), we eliminate the need for local logic masking and guarantee 100% compliance with Section 6.2.
*   **Medoid Aggregation:** Instead of field-level voting (which can create logically inconsistent JSON), the pipeline uses **Medoid Selection**. It embeds the entire JSON output and selects the candidate that has the highest similarity to all others, ensuring structural and logical consistency.

## Conclusions
The research confirms that a "Champion" pipeline built on a Two-Pass-NI foundation offers the highest probability of stable, high-accuracy performance across unknown models.
*   **Stability is the competitive edge:** Unlike strategies that depend on model-specific quirks, the Two-Pass-NI base ensures consistent 2nd-place ranking across architectures, which is superior when the target model is unknown (Section 6.4).
*   **Efficiency requires strict limits:** The multi-pass nature of this architecture pushes the 60s/32K limits. Integration of RAG and ReAct must be "surgical"—limiting retrieval to 3-4 examples and verification to 3-5 cycles.
*   **Precision-over-Recall is the winner:** For GenSIE, protecting the precision of the output via "Emergency Nullification" at 55 seconds is a mathematically superior strategy for maximizing F1 scores in the presence of hallucination traps.
*   **Agnosticism requires API Native features:** To be truly model-agnostic and compliant, the system must abandon local grammar masking and fully embrace the hosted API's `json_schema` constraints.

## Recommendations
*   **Immediate implementation:** Refactor the existing `TwoPassAgent` in `baseline.py` to a modular `TwoPassEngine` that supports `json_schema` payloads.
*   **RAG Calibration:** Set up the local FAISS index with `MiniLM-L6-v2` and cap the dynamic retrieval at 4 examples to protect the 32K token budget.
*   **The Auditor Loop:** Implement the ReAct verifier as a "lazy" component that only audits the top-3 most complex/ambiguous fields identified in the analytical pass.
*   **Validation:** Use the `run_evals.sh` script to test the N=2 adaptive ensemble on both Qwen 1.7B and Llama 3B. If the 60s limit is breached on Llama 3B, set the default ensemble size to N=1 (single pass + verification) for that model class.
*   **Survival Check:** Ensure the "Emergency Nullification" logic is unit-tested to trigger at exactly 55 seconds, returning a safe, partially-nullified JSON.