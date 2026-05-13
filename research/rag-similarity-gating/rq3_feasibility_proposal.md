# Research Asset: RQ3 - Feasibility and Agent Proposal

## 1. Architectural Modification
The gate can be integrated with minimal code changes. 
- **Proposed Logic**: Modify `SlimChampionAgent.run()` to perform a conditional branch *after* the `RAGModule` search but *before* constructing the prompts for Pass 1 and Pass 2.
- **Minimal Changes**: The `Architect` and `Pass1`/`Pass2` extraction logic remains untouched. The agent state (hint counts, system instructions) remains constant across the RAG vs. Zero-Shot modes.

## 2. Maintaining Performance
- **Positive Gain**: The gate preserves the RAG-enabled gains for high-similarity tasks while preventing the ~20% performance collapse observed with "noisy" (low-similarity) retrieval. 
- **Consistency**: The `Architect` module's fixed hints act as the fallback stabilizer, ensuring that Zero-Shot extractions maintain the same schema-following rigor as RAG extractions.

## 3. Edge Cases & Risks
- **Rare-Structure Discard**: Extremely rare or unique schema structures might occasionally be discarded if the vector index is sparse.
- **Mitigation**: The `Architect` module's "Generalization Directive" (injected into system prompts) explicitly forces the model to treat the task as a general extraction, preventing reliance on potentially missing few-shot examples for rare edge cases.
