# GenSIE 2026: General-purpose Schema-guided Information Extraction Research Report

## Executive Summary
This report outlines a state-of-the-art strategy for the **GenSIE 2026 Challenge** (General-purpose Schema-guided Information Extraction) using Small Language Models (SLMs) in a zero-shot, offline environment. To maximize the **Performance-to-Cost Ratio**, we recommend a **hybrid agentic pipeline** that leverages **Qwen 2.5 (14B)** or **Llama 3.1 (8B)** with **structured decoding (XGrammar/SGLang)**. The strategy focuses on decoupling reasoning from extraction ("Reason-then-Extract"), utilizing token-efficient schema representations (TypeScript/YAML), and implementing aggressive hallucination mitigation via "Source Grounding." By prioritizing "Focused CoT" and context caching on A100 GPUs, this approach balances high F1 scores with extreme token efficiency.

## Research Questions

### 1. Methodology & SOTA (2024-2026)
- **Model Performance:** Qwen 2.5 (7B/14B) leads in overall Spanish IE reasoning, while Llama 3.1 8B excels in strict JSON compliance. Salamandra 7B is best for Ibero-cultural nuances.
- **Key Strategies:** "Reason-then-Extract" (separating CoT from JSON output) and Multi-Agent Refinement (Analysis -> Extraction -> Reflection) are critical for accuracy.
- **Zero-Shot Alignment:** Leveraging raw JSON Schemas or TypeScript interfaces in prompts is more effective than natural language descriptions.
- **Detailed Asset:** [methodology_sota.md](gensie_challenge/methodology_sota.md)

### 2. Structured Decoding & Schema Representation
- **Leading Engines:** XGrammar and SGLang are SOTA for A100 environments, offering "Jump-Forward decoding" that can actually increase throughput compared to unconstrained generation.
- **Inference Reliability:** Modern engines (SGLang, Guidance) eliminate the "sampling tax" and guarantee 100% validity, removing the need for costly retry loops.
- **Efficient Formats:** TypeScript interfaces and Pydantic models are ~60-70% more token-efficient for prompts than raw JSON Schema. YAML is a viable alternative for output payloads to save ~15%.
- **Detailed Asset:** [structured_decoding.md](gensie_challenge/structured_decoding.md)

### 3. Efficiency & Token Optimization
- **Focused CoT (F-CoT):** Limiting reasoning to ambiguous or complex fields rather than full-document CoT can save 60-70% of output tokens with minimal accuracy loss.
- **Context Caching:** Essential for the A100 environment to reduce repetitive input costs by up to 90% for long-form documents or multi-stage pipelines.
- **Output Compression:** Using YAML or shorthand keys can reduce structural overhead by 20-40% compared to standard JSON.
- **Detailed Asset:** [efficiency_optimization.md](gensie_challenge/efficiency_optimization.md)

### 4. Metric Alignment & Reliability
- **Metric Tuning:** The GenSIE metric uses `paraphrase-multilingual-MiniLM-L12-v2` for semantic similarity (threshold 0.8) in free-text fields. Rigid fields require exact matches.
- **Hallucination Mitigation:** "Source Grounding" (quoting source text before extraction) and using "Skeptical Auditor" personas are the most effective zero-shot strategies for SLMs.
- **Spanish Nuances:** Dialectal variations (*móvil* vs *celular*) and morphosyntactic agreement are critical. Using multilingual embeddings for similarity helps bridge lexical gaps.
- **Logic:** Implementing "Extract-or-Null" logic with explicit reasoning steps prevents forced completions and hallucination penalties.
- **Detailed Asset:** [metric_reliability.md](gensie_challenge/metric_reliability.md)

## Conclusions
- **Model Selection:** Qwen 2.5 14B is the current "sweet spot" for Spanish-language reasoning and zero-shot schema alignment within the <14B constraint.
- **Reliability:** Grammar-constrained decoding is mandatory, not optional, for zero-shot IE. It eliminates formatting errors and improves throughput via structural jump-forwarding.
- **Efficiency:** Token consumption is the primary bottleneck. Moving from JSON to YAML for outputs and JSON Schema to TypeScript for prompts can reduce overhead by 30-70%.
- **Metric Alignment:** Success depends on strict "Extract-or-Null" logic to avoid hallucination penalties and aligning free-text extraction with the `MiniLM-L12` semantic similarity threshold.

## Recommendations
1. **Pipeline Architecture:** Implement a three-stage pipeline: **Schema Analysis -> Source-Grounded Extraction -> Structural Refinement**.
2. **Decoding Engine:** Use **SGLang** with **XGrammar** for the inference backend to leverage jump-forward decoding and bitmask-based structural constraints.
3. **Prompting Strategy:** Replace verbose JSON Schemas with compact **TypeScript interfaces**. Use **Focused CoT** (F-CoT) only for complex or nested fields to preserve the token budget.
4. **Validation:** Incorporate a "Skeptical Auditor" reasoning step to verify each extracted value against the source text before final JSON generation.
5. **Next Step:** Use the `/draft` command to convert this research report into a technical architecture document or competition submission draft.
