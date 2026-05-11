# GenSIE Champion: Modular Pipeline Roadmap

## Executive Summary
This roadmap defines the architectural path to a "GenSIE Champion" pipeline, an inference-time system designed to maximize accuracy and structural reliability in zero-shot Spanish information extraction. By modularly integrating established Tier 1 extraction engines (`Grounded-Null`, `End-Anchored-Null`, `Two-Pass-NI`) with advanced meta-layers, the system directly addresses the core challenges of the IberLEF 2026 GenSIE task. 

Key pillars of this roadmap include:
1.  **Engine Modularization:** A standardized interface to swap extraction strategies based on model architecture.
2.  **Dynamic Context Injection:** An ARCHITECT module and a local FAISS-based RAG layer to convert zero-shot tasks into high-accuracy few-shot extractions.
3.  **Self-Correcting Verification:** A time-budgeted ReAct loop that aggressively nullifies ungrounded data to protect the Flattened Schema Score.
4.  **Ensemble Robustness:** A 3-run consensus mechanism using majority voting and embedding similarity.
Crucially, this architecture corrects previous feasibility flaws by transitioning to API-native `json_schema` constraints, ensuring full compliance with the competition's "Hosted Inference" requirements.

## Research Questions

### 1. Modular Engine Architecture
*See full details in: [engine_architecture.md](./gensie_modular_roadmap/engine_architecture.md)*

**Overview of Findings:**
To leverage Tier 1 strengths, the system will use a unified `IExtractionEngine` interface that decouples the extraction strategy from the core pipeline logic.

*   **Standardized Interface:** The `Grounded-Null`, `End-Anchored-Null`, and `Two-Pass-NI` strategies are wrapped into a common interface. This allows the "Champion" pipeline to swap the underlying extraction logic modularly based on the model or task complexity.
*   **Model-Specific Selection:** 
    *   **Qwen Engines:** Standardize on `End-Anchored-Null` to prevent instruction dilution in long contexts.
    *   **Llama Engines:** Standardize on `Two-Pass-NI` to exploit the model's superior responsiveness to explicit analytical passes.
*   **Universal Null Rule:** The "Null Rule" (return `null` for missing information) is enforced via the `InvariantPromptMixin` at the engine level and reinforced by a post-extraction validation layer that audits grounding.

### 2. Pre-processing & Retrieval (RAG)
*See full details in: [retrieval_rag.md](./gensie_modular_roadmap/retrieval_rag.md)*

**Overview of Findings:**
The RAG layer transforms the zero-shot task into a "dynamic few-shot" task, significantly boosting SLM performance on novel schemas.

*   **ARCHITECT Module:** Converts complex JSON schemas into structured natural language "extraction dossiers." This reduces the cognitive load on SLMs by replacing raw JSON syntax with clear semantic definitions and explicit negative constraints.
*   **Dynamic Retrieval Mechanism:** Uses a local FAISS index with `MiniLM-L6-v2` embeddings (fully offline compliant). It employs Maximal Marginal Relevance (MMR) to select up to 3-5 diverse examples from the development set that match the target schema's structure.
*   **Optimal Context Balance:** Research identifies 3-5 examples as the optimal point. This fits well within the 32K token budget, leaving ample room for the source context and multiple ReAct loops, while avoiding the "few-shot collapse" observed at higher shot counts.

### 3. The Verification & Accuracy Layer
*See full details in: [verification_layer.md](./gensie_modular_roadmap/verification_layer.md)*

**Overview of Findings:**
The verification layer acts as a "safety gate" that audits the extraction engine's draft, specifically targeting the suppression of hallucinations.

*   **Modular ReAct Auditor:** A pluggable `AuditorAgent` is triggered after the primary extraction. It performs a field-by-field "Thought-Action-Observation" check, verifying that each value exists in the source text.
*   **Time-Budgeted Stop Conditions:** To comply with the 60s timeout, verification follows a "Budgeted Priority" model: it verifies Rigid types (Enums/Bools) first and has a hard cutoff at 50s total execution time. If the timeout is reached, any unverified fields are automatically nullified to prevent penalties.
*   **Aggressive "Nullify" Logic:** Research confirms that for the GenSIE 2026 metric (Flattened Schema Score), a False Negative (returning `null` for a value that exists) is less penalized than a False Positive (hallucinating a value). The verification loop therefore aggressively nullifies any field that cannot be explicitly grounded in the text.

### 4. Ensembling & Compliance Optimization
*See full details in: [ensembling_compliance.md](./gensie_modular_roadmap/ensembling_compliance.md)*

**Overview of Findings:**
The final layer of the roadmap focuses on robustness through redundancy and strict adherence to the competition's technical constraints.

*   **Consensus Aggregation:** To merge results from multiple runs, the pipeline uses "Field-Level Majority Voting" for rigid types (Booleans/Enums) and "Embedding Medoid Selection" for free text. This ensures the final JSON is not only valid but also the most representative across stochastic runs.
*   **Hosted Inference Fix:** The roadmap permanently removes `llguidance` and switches to API-native `json_schema` constraints. This ensures 100% compliance with the "Hosted Inference" rule (Section 6.2) while maintaining the structural validity required by the Flattened Schema Score.
*   **Optimal Ensemble Configuration:** An ensemble size of **N=3** is recommended. This configuration, when combined with asynchronous API calls and the provided 32K token budget, allows for robust "2-vs-1" tie-breaking within the 60s timeout, providing a significant stability boost over single-pass baselines.

## Conclusions
The path to a competitive GenSIE submission lies in shifting from "single-pass generation" to "iterative, ensemble-verified extraction." This research confirms that:
*   **Modularity is essential:** Different SLMs (Qwen vs. Llama) respond best to different prompting invariants (End-Anchored vs. Two-Pass). A modular engine architecture allows for model-specific optimization without rewriting the pipeline.
*   **The Zero-Shot gap is bridgeable:** By using a local FAISS index to inject dynamically retrieved few-shot examples, we can significantly boost the performance of models on unseen schemas.
*   **Precision is the priority:** The Flattened Schema Score heavily penalizes hallucinations. An aggressive ReAct verification layer that favors `null` over "maybe" is mathematically superior for this specific competition metric.
*   **API Compliance is a hard constraint:** Any logic relying on local logit manipulation (`llguidance`) must be replaced with API-native `json_schema` constraints to survive the Docker evaluation environment.

## Recommendations
*   **Build Phase 1 (Core Engines):** Standardize the `IExtractionEngine` interface and implement wrappers for the current Tier 1 strategies.
*   **Build Phase 2 (The ARCHITECT & RAG):** Implement the schema-to-natural-language translator and set up the local FAISS index using `MiniLM-L6-v2`.
*   **Build Phase 3 (The Auditor):** Integrate the pluggable ReAct verification loop. Ensure it has hard time-budgeting logic to trigger "Emergency Nullification" at 50 seconds.
*   **Validation:** Use the 30-example Starter Kit to profile the latency of an N=3 ensemble. If the 60s limit is consistently breached, reduce the ensemble size to N=2 for those specific high-complexity schemas.
*   **Final Submission:** Prepare "Pipeline 1" (Full Champion) and "Pipeline 2" (Single-Pass Engine) to hedge across both the Performance and Efficiency leaderboards.