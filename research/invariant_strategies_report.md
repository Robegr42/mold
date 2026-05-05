# GenSIE 2026: Invariant Strategies Research Report

## Executive Summary
This report establishes the foundational, invariant strategies for the **GenSIE 2026 Challenge** that must be universally applied across all extraction agents. Through iterative research, we determined that **Extract-or-Null logic**, **Dialect-Awareness**, and **TypeScript Schema Compression** are not distinct agent architectures, but rather fundamental requirements for maximizing the Performance-to-Cost ratio and surviving GenSIE's strict hallucination penalties. These invariants can be strictly implemented using generic OpenAI-compatible API features via prompt engineering, ensuring true offline portability. We recommend isolating these invariants using Python Mixins and utility functions, allowing them to be uniformly injected into any specialized agent architecture without disrupting their core reasoning logic.

## Research Questions

### 1. Identify Invariant Strategies
- **Fundamental Invariants:** "Extract-or-Null" logic, TypeScript Schema Compression, Constrained Decoding (SGLang/XGrammar via `response_format`), and Dialect-Aware System Prompts must be universal baselines applied to every agent.
- **Metric Alignment:** "Extract-or-Null" directly mitigates GenSIE's heavy hallucination penalties. SGLang ensures output strictly matches the "Flattened Schema Scoring" keys. TypeScript compression maximizes the Performance-to-Cost ratio by minimizing prompt tokens.
- **Architecture Demotion:** `TypeScriptSchemaAgent` and `DialectAwareAgent` are not distinct agent architectures. Their core concepts (schema transformation and dialect system prompting) should be stripped of agent status and integrated as universal preprocessing steps and base prompt mixins for all other agents.
- **Detailed Asset:** [identify_invariants.md](invariant_strategies/identify_invariants.md)

### 2. Review API Constraints
- **Generic Implementation:** Invariant strategies can be implemented purely via prompt engineering. TypeScript compression, Extract-or-Null instructions, and Dialect awareness are injected directly into the standard `messages` array payload, supported by any OpenAI-compatible endpoint.
- **Offline Structured Outputs:** While modern servers like vLLM and SGLang support `response_format={"type": "json_schema"}`, compiling complex schemas into FSMs can cause latency spikes. A robust offline implementation should gracefully fallback to `{"type": "json_object"}` with strong system prompts if strict schema enforcement fails or isn't natively supported.
- **Zero Internet/Framework Dependency:** To ensure an air-gapped run, no orchestration libraries (LangChain, LlamaIndex) should be used. The control flow, prompt chaining, schema transformation, and retry loops must rely entirely on native Python primitives and the minimal `openai` client.
- **Detailed Asset:** [api_constraints.md](invariant_strategies/api_constraints.md)

### 3. Isolate Invariants for Modular Application
- **Design Patterns:** Invariants should be isolated using Utility Functions for data transformations (e.g., `compress_schema_to_ts()`) and Python Mixins for behavior injection (e.g., `InvariantPromptMixin`).
- **Implementation:** The `InvariantPromptMixin` exposes methods like `get_invariant_system_instructions()` that return concatenated strings covering Extract-or-Null and Dialect-Awareness rules.
- **Uniform Application:** Agents inherit from both `GenSIEAgent` and `InvariantPromptMixin`. They call `self.get_invariant_system_instructions()` to augment their unique system prompts before calling the OpenAI API. This allows strategies like Two-Pass Reasoning or Source-Grounding to exist alongside the universal invariant rules without logic collision.
- **Detailed Asset:** [isolate_invariants.md](invariant_strategies/isolate_invariants.md)

## Conclusions
- **Universal Baselines Over Specialized Agents:** Dialect awareness and TypeScript schema parsing should not be siloed into specific agent classes. They are universal prerequisites for dealing with GenSIE's Spanish texts and <14B token limits.
- **API Portability:** Achieving these invariants does not require complex frameworks. Standard Python string manipulation and the basic `openai` client are sufficient to implement TypeScript conversion and Prompt Mixins, ensuring compatibility with offline environments like vLLM or SGLang.
- **Modular Architecture:** The most effective way to combine these universal truths with distinct reasoning strategies (like Two-Pass or Source-Grounded) is through multiple inheritance (Mixins) and utility modules.

## Recommendations
1. **Refactor Baseline Agents:** Demote the `TypeScriptSchemaAgent` and `DialectAwareAgent` concepts from standalone architectures.
2. **Implement Invariant Mixin:** Create a Python class (e.g., `GenSIEInvariantMixin`) that houses the standard "Extract-or-Null" and Spanish dialect handling prompts. Have all agents inherit from this.
3. **Implement Utility Module:** Create a `utils/schema.py` module containing the `compress_schema_to_ts()` logic to universally shrink payload sizes before sending requests.
4. **Standardize Fallbacks:** Ensure all agents implement a try-except block that falls back to `{"type": "json_object"}` if the strict `json_schema` response format fails due to local server limitations.
5. **Next Step:** You can now use the `/draft` command to convert this research report into an actionable refactoring plan or directly update the `src/gensie/baseline.py` codebase to implement these modular invariants across the remaining agent architectures.
