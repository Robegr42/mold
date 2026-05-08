# Research Asset: Invariants Experiment Benchmarks (Starter Set)

## 1. Quantitative Delta (No Invariants vs. With Invariants)

| Agent | No Invariants (F1) | With Invariants (F1) | Absolute Delta | Relative Gain |
| :--- | :--- | :--- | :--- | :--- |
| **Auditor** | 0.5120 | **0.5564** | +0.0444 | **+8.7%** |
| **End-Anchored** | 0.5929 | **0.6061** | +0.0132 | **+2.2%** |
| **Grounded** | 0.4728 | **0.5102** | +0.0374 | **+7.9%** |
| **Two-Pass** | **0.6052** | 0.5754 | -0.0298 | **-4.9%** |

## 2. Efficiency Impact Analysis

| Agent | Avg Tokens (No Inv) | Avg Tokens (With Inv) | Token Delta | % Increase |
| :--- | :--- | :--- | :--- | :--- |
| Grounded | 402.53 | 479.78 | +77.25 | 19.2% |
| Auditor | 902.58 | 985.95 | +83.37 | 9.2% |
| End-Anchored | 877.23 | 968.90 | +91.67 | 10.4% |
| Two-Pass | 1318.90 | 1392.10 | +73.20 | 5.5% |

### Analysis
- **Token Burden:** Invariants add a flat overhead of ~80 tokens per task. For the `Grounded` agent, this is a significant 19% increase, but for multi-pass agents like `Two-Pass`, it is negligible.
- **Latency Paradox:** Despite the extra tokens, average latency was consistently ~1.3s *lower* across all agents when invariants were present. This suggests the invariants (especially TS compression and strict rules) help the model "lock-in" to the structured output faster, reducing "thinking" time or tokens wasted on verbose filler.
