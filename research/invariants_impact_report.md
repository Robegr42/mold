# Research Report: Impact of Prompt Invariants on GenSIE Agents

## Executive Summary
This experiment rigorously tested the impact of "Extraction Invariants" (TypeScript Schema Compression, Null Rule, Dialect Awareness) across four agent architectures on Llama 3.2 3B. The results reveal a significant performance boost for **Grounded (+7.9% F1)** and **Auditor (+8.7% F1)** agents, primarily due to a **75% reduction in hallucinations**. 

However, a critical regression was discovered in the **Two-Pass Agent (-4.9% F1)**, where invariants actually *increased* hallucinations by 233%. Efficiency analysis shows a flat token cost of ~80 tokens per task, which is offset by a **7% reduction in latency**, suggesting invariants improve model "decisiveness".

**Final Recommendation:** **RETAIN** invariants for Grounded, Auditor, and End-Anchored agents. **DISCARD/REWORK** invariants for the Two-Pass agent.

---

## Research Questions

### 1. Comparative Performance Baseline (Without Invariants)
- **Baseline Leaderboard (No Inv):** Two-Pass (0.6052) > End-Anchored (0.5929) > Auditor (0.5120) > Grounded (0.4728).
- **Error Profile:** Hallucinations were the primary precision bottleneck for single-pass agents.

Detailed Benchmarks: [research/invariants-experiment/benchmarks.md](research/invariants-experiment/benchmarks.md)

---

### 2. Performance Delta with Invariants Applied
- **Grounded & Auditor:** Saw the largest gains (+8% and +9% relative F1).
- **End-Anchored:** Modest improvement (+2%).
- **Two-Pass:** Significant regression. The "Null Rule" likely conflicts with the reasoning established in Pass 1.

Detailed Benchmarks: [research/invariants-experiment/benchmarks.md](research/invariants-experiment/benchmarks.md)

---

### 3. Structural & Semantic Impact Analysis
- **Hallucination Suppression:** Highly effective for grounded strategies.
- **Dialect Awareness:** Minimal impact on sim scores; hints in descriptions are likely ignored during high-token generation.
- **TypeScript Compression:** Confirmed as an efficiency and attention anchor for small models.

Mechanism Analysis: [research/invariants-experiment/mechanism_analysis.md](research/invariants-experiment/mechanism_analysis.md)

---

### 4. Efficiency & Cost-Benefit Analysis
- **Cost:** ~80 extra tokens/task.
- **Gains:** Better precision and faster inference.
- **Verdict:** For Grounded/Auditor, the precision gain is well worth the 10-20% token increase. For Two-Pass, it is a net loss.

## Conclusions
1. **Invariants are Architecture-Sensitive:** The same prompt component that saves the Grounded agent destroys the Two-Pass agent's coherence.
2. **Precision over Recall:** Invariants consistently shift the error profile toward "Missing" fields rather than "Hallucinated" fields, which is the preferred behavior for high-precision extraction.
3. **Prompt "Lock-in":** Invariants reduce latency by providing a more rigid instruction set, helping SLMs converge on the JSON structure faster.

## Recommendations
1. **Retain Invariants in `GroundedAgent`, `AuditorAgent`, and `EndAnchoredAgent`.**
2. **Optimize `TwoPassAgent`:** Remove the `InvariantPromptMixin` and instead integrate its components manually into Pass 1 (Analysis) rather than Pass 2 (Extraction).
3. **Standardize `EndAnchoredAgent`:** Officially include it in the `InvariantPromptMixin` inheritance list in `src/gensie/baseline.py`.

**Research Complete.** You can now use the `/draft` command to turn this executive report into a fully fleshed-out article or white paper.
