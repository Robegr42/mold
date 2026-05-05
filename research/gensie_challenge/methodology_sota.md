# Methodology & SOTA (2024-2026) for GenSIE Challenge

## 1. GenSIE Challenge Overview (IberLEF 2026)
The **GenSIE (General-purpose Schema-guided Information Extraction)** challenge is a shared task at **IberLEF 2026**. It targets the development of robust systems for zero-shot, structured information extraction from Spanish texts using **Small Language Models (SLMs)** with fewer than 14 billion parameters.

### Core Constraints & Objectives
- **Zero-Shot Schema Alignment:** Models must adapt to previously unseen JSON schemas provided at runtime.
- **Language Focus:** Spanish-language texts across multiple domains (legal, medical, news, etc.).
- **Model Size:** Optimization for SLMs (<14B) to enable high performance on commodity hardware.
- **Hallucination Mitigation:** Explicit "traps" in the data require models to output `null` for information not grounded in the source text.
- **Evaluation:** Uses **Flattened Schema Scoring (Micro-F1)**, combining exact matching for enums/booleans and semantic similarity for free-text.

---

## 2. Target Models & Performance Comparison

### 2.1 Qwen Series (Alibaba) - The Structured Output Leader
Qwen 2.5 (released late 2024) and Qwen 3 (2025) are currently the state-of-the-art for structured data handling in the sub-14B category.
- **Qwen 2.5 7B/14B:** Specifically optimized for "structural data analysis" and instruction following. It offers the best "quality-to-speed ratio" for JSON extraction.
- **Qwen 2.5-Coder 7B:** Highly recommended for schema-guided tasks due to its extensive training on code, which translates to superior logic for nested JSON structures.
- **Strengths:** High reasoning accuracy, excellent Spanish comprehension (IberoBench SOTA for 7B models), and native support for tool-calling patterns.

### 2.2 Llama 3 / 3.1 / 3.2 (Meta) - The Reliability Standard
- **Llama 3.1 8B:** Known for the highest **JSON schema compliance (95.7%)** in its weight class. It is the "safest choice" for strict formatting needs.
- **Llama 3.2 3B/11B:** Notable for specific entity extraction (NER) and multimodal capabilities (Vision).
- **Weakness:** Can be more verbose than Qwen, requiring explicit "output only JSON" instructions to avoid conversational filler.

### 2.3 Salamandra (BSC-LT) - The Iberian Specialist
Developed by the Barcelona Supercomputing Center, Salamandra (2B, 7B, 40B) is the "soberano" model for the Iberian context.
- **Multilingual Excellence:** Outperforms Llama and Qwen when processing texts involving **Catalan, Basque, or Galician** alongside Spanish.
- **Architecture:** 7.7B parameters, GQA attention, 8k context window, trained on 12.8T tokens on the MareNostrum 5 supercomputer.
- **Use Case:** Crucial for GenSIE tasks involving documents from Spanish autonomous regions or specific cultural/legal nuances of Spain.

---

## 3. Best Prompting Strategies for Schema Alignment

### 3.1 "Reason-then-Extract" (Structured-of-Thought)
Recent research (2025) highlights a **"constraint tax"**: forcing a model to follow a strict JSON schema too early degrades its reasoning.
- **Strategy:** Prompt the model to generate a reasoning trace (SoT/CoT) *before* the JSON block.
- **Pattern:** `[Reasoning Step-by-Step] -> [Final JSON Output]`.
- **Implementation:** Use tools like **Outlines** to constrain only the final portion of the output while allowing the reasoning to be free-text.

### 3.2 Schema-First & TypeScript Prompting
Instead of describing the JSON in natural language, provide the raw **JSON Schema** or a **TypeScript interface** at the start of the prompt.
- **Why it works:** SLMs are heavily trained on code (GitHub data), making them more proficient at "populating" a code structure than following prose instructions.

### 3.3 ReAct (Reasoning + Acting)
For GenSIE tasks that require external verification or multi-step logic (e.g., calculating growth from monthly data):
- **Loop:** `Thought -> Action -> Observation -> Final JSON`.
- **2025 SOTA:** Use **MCP (Model Context Protocol)** to allow the model to "see" the schema of its own tools before calling them.

### 3.4 Multi-Agent Refinement (OneKE Style)
For complex, nested extraction, split the task across specialized roles:
1. **Schema Agent:** Analyzes the target schema and identifies required entities.
2. **Extraction Agent:** Performs the raw IE into the JSON format.
3. **Reflection/Review Agent:** Checks the output against the source text for hallucinations and schema compliance.

---

## 4. SOTA Tools & Methodologies (2024-2026)

### 4.1 Constrained Decoding Frameworks
These guarantee 100% valid JSON by modifying the model's token sampling at the logit level.
- **XGrammar (2024):** 100x faster than traditional grammar libraries; uses a persistent parsing stack.
- **SGLang (2024/2025):** Features "Jump-Forward Decoding" to skip generating boilerplate JSON tokens (brackets, keys), significantly reducing latency.
- **Outlines / Guidance:** Industry standards for integrating Finite State Machine (FSM) constraints into inference.

### 4.2 Key Papers & Benchmarks
- **ThinkJSON (2025):** Distills "deep thinking" traces into SLMs for structured tasks.
- **JSONSchemaBench (2025):** Evaluates models against 10,000 real-world schemas.
- **DICE (2025):** A framework where SLMs guide the formatting of larger LLM outputs.
- **OneKE (2024):** Bilingual (EN/ZH) knowledge extraction framework using multi-agent loops.

---

## 5. Spanish-Language Considerations

### 5.1 IberoBench (2024/2025)
A comprehensive benchmark for Spanish, Catalan, Galician, and Basque. 
- **Results:** Qwen 2.5 7B and Llama 3.1 8B are top performers in Spanish reasoning. 
- **The "Spanish Gap":** Models generally perform 10-15% worse on Spanish reasoning compared to English on the same architecture.

### 5.2 GenSIE "Hallucination Traps"
Specific to the challenge, systems must be tuned to resist "internal knowledge bias."
- **Technique:** Include a "self-correction" step where the model maps every extracted value back to a specific quote in the text. If no quote exists, the value must be set to `null`.

### 5.3 Regional Nuances
For documents involving regional administration (Catalonia, Basque Country), **Salamandra** should be used as the primary extractor or as a "Multilingual Verifier" to ensure entity names in regional languages are correctly mapped to the Spanish schema.
