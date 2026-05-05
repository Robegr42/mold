# Invariant Strategies Analysis: GenSIE Challenge

## Overview
This report identifies the core strategies from our initial research that must be elevated from optional techniques or specific agent architectures to **fundamental system invariants**. By embedding these strategies into the foundational pipeline, we ensure that every agent built for the GenSIE challenge inherently respects the task's strict constraints.

## 1. Fundamental Invariants vs. Optional Strategies
Based on the review of the research and the constraints of the GenSIE challenge, the following strategies must be classified as **fundamental invariants** (required for *all* agents):

*   **Extract-or-Null Policy**: Must be universal. Given the heavy penalties for hallucinations in the challenge, a strict fallback to `null` is a mandatory safety mechanism for all extraction tasks.
*   **TypeScript Schema Compression**: Must be universal. Transforming verbose JSON schemas into concise TypeScript interfaces reduces prompt token size and exploits the strong code-generation capabilities inherent in modern <14B models.
*   **SGLang / XGrammar Constrained Decoding**: Must be universal. Enforcing the exact schema structure at the logits level during decoding is critical. It avoids structural hallucinations and guarantees perfectly parseable outputs.
*   **Context Caching**: Must be universal. Given the offline hardware constraints, caching the system prompts and schema definitions is necessary for computational viability and speed across large evaluation sets.

*(Note: While Dialect-Awareness is highly valuable for Spanish texts, it is best treated as a global baseline prompt enhancement rather than a rigid structural invariant.)*

## 2. Addressing GenSIE Constraints
These invariants directly map to the core metrics and limitations of the challenge:

*   **Flattened Schema Scoring:** SGLang/XGrammar guarantees that the model only generates keys that exist in the expected flattened schema. This eliminates nested hallucinated objects that would otherwise cause parsing failures or misalign with the flattened scoring metric.
*   **Heavy Hallucination Penalties:** The "Extract-or-Null" protocol acts as a hard constraint against over-eager extraction. By setting the default state to `null` and requiring high confidence to extract, the model optimizes for precision over recall, perfectly avoiding severe penalty deductions.
*   **Zero-Shot Extraction:** In a zero-shot setting, models lack examples of the expected output. TypeScript schema compression bridges this gap by presenting the schema in a syntactically dense, logically structured format that code-trained models intuitively understand without needing few-shot examples.
*   **Offline <14B Models:** Models like Llama-3-8B or Qwen-2.5-7B have limited reasoning capacity and context windows. TypeScript compression minimizes the token load. SGLang speeds up inference by cutting off invalid token trees. Context caching ensures that running thousands of instances locally doesn't redundantly process the identical schema and prompt prefixes.

## 3. Demotion of "Agent" Status to Universal Baselines
Several strategies currently framed as distinct agent architectures must be stripped of their "agent" status and baked into the core universal pipeline:

*   **`TypeScriptSchemaAgent` $\rightarrow$ Baseline Input Processor:**
    Schema representation is an input formatting choice, not a behavioral agent strategy. Every single agent in the ecosystem will perform better if the schema is compressed into TypeScript. Therefore, the TypeScript converter should become a mandatory preprocessing step for the pipeline, making the `TypeScriptSchemaAgent` obsolete as a distinct entity.
*   **`DialectAwareAgent` $\rightarrow$ Baseline Prompt Directive:**
    Given that the task involves Spanish texts (with potential regional variations from Spain, Latin America, etc.), dialect awareness shouldn't require a specialized agent routing step. Instead, a "dialect and linguistic variation" directive should be permanently appended to the baseline extraction prompt. This ensures all agents possess baseline robustness to regional terminology without the overhead of maintaining a separate agent architecture.

### Conclusion
By stripping these elements of their "agent" status and making them universal baselines, we create a robust, invariant core. Future agent development can then focus entirely on advanced reasoning loops (like ReAct, Self-Correction, or Multi-Step Verification) rather than solving baseline formatting and constraint issues.
