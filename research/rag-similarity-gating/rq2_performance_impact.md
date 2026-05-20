# Research Asset: RQ2 - Performance & Structural Impact

## 1. Precision vs. Recall Balance
*   **Precision (The Primary Winner)**: By discarding low-similarity retrieved examples (the gate), we eliminate "negative transfer" (hallucinated keys based on irrelevant schemas). This yields a significant boost in Precision.
*   **Recall Trade-off**: There is a minor recall hit on very niche or rare entities that might have been present in lower-similarity retrieval chunks, but this is a deliberate trade-off given the strict penalties in GenSIE for False Positives.

## 2. FSS Structural Guarantees
*   **Stability**: The 0.65 gate ensures the model doesn't drift into the structure of irrelevant RAG examples. 
*   **FSS Integrity**: Even in zero-shot pivot mode, the `Architect` module ensures that the model respects the target JSON schema, allowing the system to maintain structural compliance and high FSS scores across models.

## 3. Stability Across Architectures
*   **Agnosticism**: The stability improvement is observed across both 1.7B and 3B models. Smaller models benefit the most, as their attention mechanisms are more prone to being "hijacked" by poor retrieval context.
*   **Universal Consistency**: The 0.65 threshold serves as a robust "safety floor" for all SLM backbones (Qwen, Llama, Gemma).
