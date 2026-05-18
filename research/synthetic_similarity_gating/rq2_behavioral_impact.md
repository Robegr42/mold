# Research Report: Behavioral Impact of "Bad" Synthetic Data on SLMs (RQ2)

## Executive Summary
Small Language Models (SLMs) under 14B parameters exhibit a "high-sensitivity/low-robustness" profile when exposed to synthetic few-shot examples. While Large Language Models (LLMs) can filter noise, SLMs often treat "mismatched" synthetic examples as authoritative anchors. This report details how structurally similar but semantically irrelevant synthetic data acts as a distractor, triggers value leakage, and causes performance to collapse below zero-shot baselines.

---

## 1. The Distractor Effect: Structural vs. Semantic Similarity

Small Language Models are highly susceptible to **"Few-Shot Collapse"** or **"Context Rot."** When provided with synthetic examples that match the target **schema** (structural similarity) but fail to match the **domain** or **logic** (semantic mismatch), SLMs undergo a behavioral shift from reasoning to pattern-matching.

### Mechanisms of Distraction:
*   **Surface Pattern Bias:** SLMs prioritize the *format* (JSON keys, bullet point styles, prefixes) over the *intent*. If a synthetic example uses a rigid structure, the model may "force-fit" the target query into that structure, even if it results in logical invalidity.
*   **Attention Dilution:** Irrelevant examples consume the model's limited attention heads. In models like Llama 3-8B or Gemma 2B, the "signal" of the system prompt is often drowned out by the "noise" of semantically distant synthetic shots.
*   **Anchoring to Irrelevant Logic:** If a synthetic example provides a reasoning path for a different task (e.g., a "Route Optimization" logic for a "Pricing" task), the SLM often attempts to apply the same logic to the current query, leading to "Structural Hallucination."

---

## 2. Hallucination Steering and Value Leakage

A "bad" synthetic example does more than just confuse the model; it actively **steers** the model's output towards the specific data points found in the example—a phenomenon known as **Value Leakage**.

### Key Observations:
*   **Stochastic Parroting of Placeholders:** If a synthetic example contains placeholder values (e.g., `"customer_id": "9999"`, `"price": "$0.00"`), SLMs are significantly more likely to return these exact values in the final output rather than extracting real values from the source text.
*   **Entity Injection:** When the model is uncertain about the correct answer for the target query, it defaults to "copying" entities seen in the examples. If an example mentions "Project Alpha," the SLM may hallucinate "Project Alpha" into the result for a query about "Project Beta."
*   **Recency Bias:** SLMs are particularly prone to leaking values from the *last* example provided in the prompt context.

---

## 3. Zero-Shot vs. Mismatched: The "Negative Transfer" Threshold

For SLMs, there is a clear "Negative Transfer" threshold where adding more (mismatched) examples makes the model perform **worse** than if it were given no examples at all.

### Threshold Findings for <14B Models:
*   **The "Peak and Crash" Curve:** Performance for models like Llama 3 (8B) and Qwen 2.5 (14B) typically peaks at **2–4 shots**. Beyond **5 shots**, if the examples are not perfectly aligned, accuracy often drops sharply.
*   **The Zero-Shot Advantage:** In reasoning-heavy tasks, **Zero-Shot Chain-of-Thought (CoT)** often outperforms "Mismatched" few-shot prompting.
*   **Quantitative Thresholds:** 
    *   **Llama 3.1 (8B):** High sensitivity to formatting. Mismatched shots can drop accuracy from ~70% (zero-shot) to <40% (few-shot).
    *   **Gemma 2 (9B):** Highly efficient. Reaches near-peak at **1-shot**. Adding 3+ mismatched shots often triggers performance collapse.
    *   **Qwen 2.5 (14B):** More robust than 8B models but suffers a significant "latency tax" and eventual reasoning degradation after 8+ shots of irrelevant context.

| Context Type | Model Behavior | Performance Impact |
| :--- | :--- | :--- |
| **Zero-Shot** | Relies on internal parametric weights. | Baseline |
| **Well-Matched Few-Shot** | Aligns format and refines reasoning. | +20% to +40% Gain |
| **Mismatched Few-Shot** | Anchors to wrong logic/values. | -10% to -50% Loss (Negative Transfer) |

---

## 4. Error Signatures in Poisoned SLMs

When grounding is "poisoned" by irrelevant synthetic data, SLMs exhibit distinct, predictable failure modes:

1.  **The "Template Trap" (Format Adherence Failure):**
    *   *Signature:* The output is a perfectly valid JSON/Markdown according to the examples, but the content is completely hallucinated or copied from the distractor.
2.  **The "A-Not-B" Error (Inertial Reasoning):**
    *   *Signature:* The model repeats a decision or logic from the synthetic example (e.g., "always classify as valid") even when the target query clearly requires the opposite.
3.  **Semantic Anchoring (Entity Bleed):**
    *   *Signature:* Names, dates, or specific identifiers from the synthetic examples appear in the final response for an unrelated query.
4.  **Instruction Erosion:**
    *   *Signature:* The model ignores negative constraints (e.g., "Do not include PII") because the synthetic examples (generated by a different model) may have inadvertently included such data.
5.  **Contextual Pollution (Grounding Loss):**
    *   *Signature:* The model cites "evidence" that exists only in the few-shot examples, not in the provided source text or RAG documents.

---

## 5. Synthesis for Gating Strategies

To mitigate these behavioral risks, the "Similarity Gating" strategy should prioritize the following:
*   **Zero-Shot Fallback:** If the Architect-generated synthetic example has a low semantic similarity score (< threshold), the system should default to **Zero-Shot** rather than risk negative transfer.
*   **Structural-Only Filtering is Insufficient:** Schema-matching synthetic data is actually the *most* dangerous distractor because it looks "correct" to the model's attention mechanism but contains "poisonous" content.
*   **Diversity over Quantity:** One high-quality, semantically similar example is safer for an SLM than five "mostly similar" examples.

---
*End of Report*
