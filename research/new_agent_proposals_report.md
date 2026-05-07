# GenSIE: Proposal for 5 Next-Generation Agents

## Executive Summary
The GenSIE challenge poses unique difficulties for Small Language Models (SLMs < 14B), primarily involving binary scoring for rigid types, exhaustive list extraction, and maintaining focus on complex hierarchical schemas. This report proposes **5 new agent architectures** that address these bottlenecks through structural prompt engineering and algorithmic flow. These designs synthesize findings from our Llama 3.2 3B analysis and SOTA research into a cohesive roadmap for high-performance, cost-effective extraction. Key innovations include **Quote-First Sequencing**, **Recursive Schema Pruning**, and **Incremental "Next Item" Loops**, all optimized for the Spanish linguistic context and the project's zero-shot constraints.

## Research Questions (Agent Designs)

### 1. The Lexicon-Grounded Agent
**How can we solve the Rigid Type Bottleneck and Hallucinations in a single pass?**
*   **Quote-First Sequencing**: Forces the model to generate a `verbatim_quote` before the `value` in the JSON sequence, leveraging self-attention to ground the extraction.
*   **Dialectal Hint Injection**: Embeds Spanish synonyms directly into schema descriptions (e.g., mapping "inmunitario" to `AUTOIMMUNE`) to solve binary rigid type failures.
*   **Detailed Design**: [Lexicon-Grounded Agent](new_agent_proposals/lexicon_grounded.md)

### 2. The Pruned-Hierarchical Planner
**How can we eliminate Attention Drift on complex schemas?**
*   **Recursive Schema Pruning (RSP)**: A pre-pass logic that strips the schema of optional fields with no context evidence, reducing prompt noise by up to 50%.
*   **Skeleton-of-Thought (SoT)**: Forces the model to generate an evidence map (Key -> Quote) before synthesis, preventing "extraction laziness."
*   **Detailed Design**: [Pruned-Hierarchical Planner](new_agent_proposals/pruned_planner.md)

### 3. The Sequential List Processor
**How can we solve the List Exhaustion failure for large arrays?**
*   **Incremental "Next Item" Loop**: A multi-turn logic that extracts exactly one item at a time, preventing the truncation common in small models.
*   **Termination Sentinels**: Uses high-contrast markers like `[DONE]` to signal loop completion reliably.
*   **Detailed Design**: [Sequential List Processor](new_agent_proposals/list_processor.md)

### 4. The Joint-Verification Auditor
**How can we maximize precision with minimal token overhead?**
*   **Single-Turn Chain-of-Verification (CoVe)**: Embeds a `draft -> verify -> final` logic within a single structured JSON response.
*   **Adversarial Gating**: Mandatory `is_evidence_present` boolean checks before every block to enforce the GenSIE "Null Rule."
*   **Detailed Design**: [Joint-Verification Auditor](new_agent_proposals/joint_auditor.md)

### 5. The Compressed-YAML Specialist
**How can we maximize the factual attention window using token-dense formats?**
*   **Key Aliasing**: Maps verbose Spanish keys to 1-3 letter English aliases (e.g., `pathology_name` -> `pn`) to maximize the model's factual attention window.
*   **YAML for Density**: Achieves 20-30% token savings over JSON, better aligning with the training data of code-specialized SLMs.
*   **Detailed Design**: [Compressed-YAML Specialist](new_agent_proposals/yaml_specialist.md)

## Conclusions
1.  **Structural Integrity > Reasoning Capacity**: For models < 14B, the sequence of fields (Quote-First) and the density of the format (YAML/Aliasing) are more critical than high-level reasoning instructions.
2.  **Mapping must be Early-Binding**: Solving the Rigid Type bottleneck requires providing semantic hints *during* generation (Lexicon-Grounded) rather than through post-processing.
3.  **State-Awareness is Essential for Recall**: Solving List Exhaustion requires the agent controller to manage extraction state across turns (Sequential List Processor).

## Recommendations
1.  **Implementation Priority**: Start with the **Lexicon-Grounded Agent** for immediate precision gains on Enums and Booleans.
2.  **Infrastructure Task**: Develop the **Recursive Schema Pruning (RSP)** utility as a shared service for all agent types to combat attention drift on Dev schemas.
3.  **Refactoring**: Update the `GenSIEAgent` base class to support multi-turn internal loops required by the Sequential List Processor.
4.  **Final Suggestion**: The research is complete. You can now use the `/draft` command to turn this executive report into a fully fleshed-out article or white paper.
