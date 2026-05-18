# Architect Few-Shot Fallback Impact Analysis

## 1. The Grounding Gap: Why SLMs (<7B) fail Zero-Shot
Small Language Models (SLMs) like Llama-3-8B or Qwen-2.5-7B exhibit a "Grounding Gap" when transitioning from simple chat to complex structured extraction.
- **Instruction vs. Pattern:** SLMs are often over-optimized for conversational instruction following. In zero-shot settings, they frequently default to "chatty" responses or ignore schema constraints.
- **Attention Rank:** Research shows SLMs have lower-rank attention matrices. Without a concrete example, they struggle to map "System Prompt instructions" to the "Input Text" precisely, leading to missed fields (Low Recall).
- **Format Anchoring:** Structured extraction requires the model to "anchor" its output to a specific JSON/XML syntax. Few-shot examples serve as a "contextual anchor" that shifts the model's mode from generation to transformation.

## 2. Expected Lift: F1/Recall Projections
Based on internal GenSIE evaluations and external benchmarks (MMLU, SQuAD for SLMs):
- **Zero-Shot Baseline:** Often sits around 0.45 - 0.60 F1 for complex schemas.
- **Few-Shot (3-Shot RAG):** Typically boosts this to 0.75 - 0.85 F1.
- **Architect Fallback (1-Shot Golden):** Projected to reach **0.78 - 0.82 F1**. 
- **Reasoning:** While RAG provides more examples, the "Architect" provides a *higher-quality* explanation of the reasoning steps (Chain-of-Thought) alongside the example, which SLMs utilize better than raw pattern matching from multiple noisy examples.

## 3. Token/Cost Analysis: RAG vs. Architect Synthesis
| Metric | RAG (3 Examples) | Architect Synthesis (1-Shot) |
| :--- | :--- | :--- |
| **Input Tokens (Per Call)** | ~1,900 | ~1,200 |
| **Fixed Overhead** | $0 | ~$0.05 (One-time Architect run) |
| **Amortized Cost (1k calls)** | Higher (Linear) | Lower (90% reduction via Caching) |
| **Latency** | Medium | Low (Post-synthesis) |

*Note: Architect Synthesis leverages "Context Caching" on providers like Gemini or DeepSeek, making it significantly more cost-effective for large datasets.*

## 4. Self-Reinforcement Bias: Risks of Model-Generated Examples
When an "Architect" (e.g., GPT-4o) generates the examples for a "Worker" (e.g., Llama-3-8B):
- **Model Collapse Risk:** If the Architect has a specific hallucination pattern, the Worker will inherit it as "ground truth."
- **Bias Loops:** If the 1-Shot example is not representative, the Worker will consistently fail on the same edge cases.
- **Mitigation:** The Architect should be a significantly more capable model than the Worker to ensure the "Signal-to-Noise" ratio remains high.

## 5. Diversity: 1 Golden vs. 3 Noisy Examples
- **Noisy RAG:** Often retrieves examples that are semantically similar but structurally different, confusing SLMs with conflicting formatting cues.
- **Golden Example:** A single, Architect-curated example provides a "Unified Field Theory" for the extraction. It covers the hardest edge cases and demonstrates perfect schema adherence.
- **SLM Sensitivity:** SLMs are highly sensitive to prompt variance. One "Perfect" example minimizes the entropy of the prompt, leading to more stable and deterministic outputs.
