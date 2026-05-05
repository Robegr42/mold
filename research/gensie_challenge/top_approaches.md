# GenSIE 2026: Top 5 Strategic Approaches for Information Extraction

This report synthesizes research findings and baseline analysis to propose five optimal strategies for the GenSIE 2026 challenge. These approaches are designed for **Small Language Models (<14B)**, **zero-shot** performance, and **maximum token efficiency** in an offline environment.

---

## 1. The "Reason-then-Extract" Hybrid Agent
**Backbone:** Qwen 2.5 (14B) + SGLang/XGrammar
**Concept:** Decouple reasoning from structural formatting to avoid the "constraint tax."
- **Implementation:** Use a two-step internal pipeline. Step 1 (unconstrained) generates a brief analysis of the text. Step 2 (constrained) takes the analysis and original text to produce the final JSON.
- **Why it works:** SLMs often lose reasoning depth when forced into rigid schemas mid-stream. Separating the "thinking" from the "formatting" preserves both accuracy and structural integrity.
- **Baseline Adaptation:** Improves upon `ThinkingAgent` by using XGrammar for the `<answer>` block to guarantee validity without regex fallbacks.

## 2. Source-Grounded "Skeptical Auditor"
**Backbone:** Llama 3.1 (8B)
**Concept:** Minimize hallucinations by requiring evidence before extraction.
- **Implementation:** Modify the schema to include a transient `_source_quote` field for every entity. The agent must find and quote the exact Spanish text before populating the corresponding field.
- **Why it works:** Forcing the model to ground its extraction in local context reduces "hallucination by completion" and aligns with the strict Micro-F1 metric.
- **Baseline Adaptation:** Extends `BasicAgent` by injecting "Grounding Instructions" into the system prompt and refining the schema.

## 3. Focused CoT (F-CoT) with Context Caching
**Backbone:** Qwen 2.5 (7B/14B)
**Concept:** Maximize Performance-to-Cost ratio by being selective with reasoning tokens.
- **Implementation:** The agent identifies only "high-ambiguity" fields (e.g., nested lists, complex legal relationships) for step-by-step reasoning, while extracting "rigid" fields (dates, numbers) directly. Use A100 context caching to store the document during these multiple passes.
- **Why it works:** Full-document CoT is token-expensive. F-CoT provides the accuracy boost of reasoning where needed while maintaining a high Efficiency score.
- **Baseline Adaptation:** A more surgical version of `ThinkingAgent` that uses conditional prompting.

## 4. TypeScript-Guided Multi-Agent Refinement
**Backbone:** Salamandra 7B (for Spanish context) / Qwen 2.5
**Concept:** Use code-centric representations to leverage the pre-training of modern SLMs.
- **Implementation:** Replace the verbose JSON Schema in the prompt with a minified **TypeScript Interface**. Use a "Refiner" agent that takes a draft extraction and performs a "Diff" against the source text to check for missing fields.
- **Why it works:** SLMs are often "better at code than prose." TypeScript is ~60% more token-efficient than JSON Schema and provides clearer hierarchical context.
- **Baseline Adaptation:** Refines the prompt formatting in `BasicAgent` and adds a secondary validation loop.

## 5. Dialect-Aware "Extract-or-Null" Strategy
**Backbone:** Salamandra 7B
**Concept:** Optimize for Spanish nuances and the "Null" penalty.
- **Implementation:** Use a system prompt that explicitly accounts for Iberian and Latin American variations (e.g., *móvil* vs *celular*). Implement a strict "Negative Few-Shot" example set where the model is shown how to output `null` when information is absent.
- **Why it works:** Prevents the model from "guessing" to fill a field, which is heavily penalized in the GenSIE metric. Salamandra’s specific Ibero-linguistic training provides an edge here.
- **Baseline Adaptation:** Specializes the `system_content` of `BasicAgent` for Spanish-specific nuances.

---

## Technical Constraints & Alignment
- **Offline Integrity:** All proposed engines (SGLang, XGrammar) and models (Qwen, Llama, Salamandra) run locally on the provided A100.
- **No Training:** All improvements are achieved via **Prompt Engineering**, **Agentic Orchestration**, and **Decoding Constraints**.
- **Metric Focus:** These strategies prioritize the **Micro-F1** (accuracy) and **Performance-to-Cost Ratio** (token efficiency) by minimizing retries and unnecessary reasoning steps.
