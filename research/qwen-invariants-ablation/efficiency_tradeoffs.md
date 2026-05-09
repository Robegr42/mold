# RQ5: Efficiency & Cost-Benefit Analysis

## 1. Token Usage Overhead
The prompt invariants introduce a fixed token overhead to every request. For Qwen3-1.7b, which has a small context window and limited compute, this overhead is critical.

| Config | Avg. Tokens/Task (Grounded) | Delta vs. NI |
| :--- | :--- | :--- |
| **NI (Baseline)** | 390 | - |
| **Full Invariants** | 461 | **+71 tokens (+18%)** |

## 2. Latency and Throughput (TPS)
TPS (Tokens Per Second) remained remarkably stable across all configurations.

- **Baseline TPS:** ~0.57 TPS (Note: this is low due to local endpoint limitations or GenSIE overhead, but consistent).
- **Invariants TPS:** ~0.57 TPS.
- **Latency Verdict:** The latency increase is strictly linear with the number of tokens. Applying all invariants increases total response time by approximately **15-20%** per task.

## 3. Cost-Benefit Verdict
- **For End-Anchored Agent:** The +20% token cost for a **+8.9% F1 boost** (Null Rule) is a highly efficient trade-off.
- **For Auditor Agent:** The +20% token cost for a **+16.4% F1 boost** (Dialect Rule) is the most cost-effective optimization found.
- **For Grounded Agent:** Any token overhead is a net loss as performance degrades.

## 4. Resource Recommendation
For Qwen3-1.7b, **do not use the full invariant suite**. The attention cost and token overhead do not justify the performance drop compared to selective, high-impact rules.
