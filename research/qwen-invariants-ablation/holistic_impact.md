# RQ3: Holistic Impact Analysis (All Invariants)

## 1. Holistic vs. Baseline vs. Best Invariant
This table compares the performance of applying ALL invariants simultaneously against the No-Invariant (NI) baseline and the best performing individual component discovered in the ablation study.

| Agent | NI Baseline | Best Individual | Full Invariants | Delta (Full vs NI) |
| :--- | :--- | :--- | :--- | :--- |
| Grounded | 0.5359 | 0.5359 (NI/Dia) | 0.5183 | **-3.3%** |
| Auditor | 0.5411 | 0.6298 (Dia) | 0.5596 | +3.4% |
| End-Anchored | 0.6189 | 0.6737 (Null) | 0.6545 | +5.8% |
| Two-Pass | 0.6968 | 0.6968 (NI) | 0.6219 | **-10.7%** |

## 2. The "Prompt Overload" Phenomenon
A critical discovery in this experiment is that **Full Invariants are significantly worse than Best Individual Invariants** for Qwen3-1.7b.

- **Two-Pass Failure:** The most capable agent (Two-Pass) is also the most fragile to holistic invariants, dropping **10.7%** in F1.
- **Auditor Drop:** Applying all invariants (+3.4% over baseline) is far less effective than applying ONLY the Dialect Rule (+16.4% over baseline).
- **Grounded Regression:** Applying all invariants turned a strong baseline into a regression (-3.3%).
- **Explanation:** For a model as small as 1.7B, the additional tokens and instructions in the "Full" configuration likely dilute the model's attention. The model is forced to process complex TS schemas AND strict logic rules AND semantic dialect hints, which exceeds its effective reasoning context for a single prompt.

## 3. Comparative Verdict (Qwen vs. Llama)
- **Llama 3.2 3B:** Showed consistent improvement with full invariants across Grounded, Auditor, and End-Anchored.
- **Qwen 3 1.7B:** Shows a "peak and drop" behavior. It benefits immensely from individual logical constraints but is overwhelmed by the full invariant suite.

**Conclusion:** For SLMs < 2B parameters, a "Minimalist Invariant" strategy (applying only the single most impactful rule) is superior to the holistic approach used for larger models.
