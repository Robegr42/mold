# Research Report: Synthetic Similarity Gating

## Executive Summary
This research investigates the implementation of a **Synthetic Similarity Gating (SSG)** mechanism to protect Small Language Models (SLMs) from "Negative Transfer" caused by low-quality synthetic grounding. Our findings confirm that SLMs < 14B are highly susceptible to "Few-Shot Collapse" and "Value Leakage" when provided with semantically mismatched examples, even if they are structurally perfect. By reusing the project's local **MiniLM embedding model**, we can audit synthesized examples in real-time (<10ms) and enforce a strict **0.70 similarity threshold**. This "Double-Gate" architecture (RAG -> Synthesis -> Audit) ensures high F1 scores by providing localized structural anchors while maintaining a superior Performance-to-Cost (PTC) ratio on the GenSIE Efficiency Leaderboard.

## Research Questions

### 1. RQ1: Technical Feasibility of Synthetic-to-Task Comparison
Reusing the local `all-MiniLM-L6-v2` model to audit synthetic examples is highly feasible and computationally inexpensive.

- **Embedding Reuse:** The existing `SentenceTransformer` instance can be leveraged to embed synthetic paragraphs in <10ms. A simple cosine similarity check against the current task input provides a real-time "quality score."
- **Threshold Determination:** Research suggests a stricter threshold of **0.70** for synthetic anchors (compared to the 0.55/0.65 RAG gate). This is because synthetic data should be "perfectly aligned" to the current context; anything less indicates semantic drift or "template hallucination."
- **Audit Score ($S_{audit}$):** A formal scoring mechanism was developed using the harmonic mean of Semantic Similarity and Structural Alignment, ensuring the synthetic anchor is both semantically relevant and structurally valid.

**Detailed Asset:** [rq1_technical_feasibility.md](synthetic_similarity_gating/rq1_technical_feasibility.md)

### 2. RQ2: Behavioral Impact of "Bad" Synthetic Data
Research confirms that "poisoned" grounding is significantly worse than no grounding.

- **The Distractor Effect:** SLMs are highly susceptible to "Few-Shot Collapse." When provided with an example that matches the schema but not the topic, models often fall into the "Template Trap," prioritizing the example's patterns over the task's instructions.
- **Value Leakage:** A "bad" synthetic anchor often leads to hallucinations where the model injects literal strings or entities from the synthetic example into the final JSON output (A-Not-B errors).
- **Negative Transfer Threshold:** For models <14B, the performance of a mismatched few-shot run often drops below the Zero-Shot baseline. This highlights the critical need for a **"Similarity Gate"** even for synthetic data.

**Detailed Asset:** [rq2_behavioral_impact.md](synthetic_similarity_gating/rq2_behavioral_impact.md)

### 3. RQ3: Pipeline Integration & Efficiency
The "Double-Gate" workflow provides a robust safety net for inference-time extraction.

- **Workflow Logic:** `RAG Search` -> [Fail] -> `Synthesis` -> [Audit Embedding] -> [Fail] -> `Zero-Shot Pivot`. This ensuring that no "hallucinated structure" ever enters the model's few-shot context.
- **The Token Tax:** Investing 1,000 tokens in synthesis followed by an audit is a cost-effective "insurance policy." It is 50% cheaper than a typical hallucinated structured extraction (2,000+ tokens) which would then require expensive self-correction.
- **Time Performance:** The entire multi-gate flow takes ~12.25s, well within the 60s timeout.
- **Failure Mitigation:** When the audit fails, the pipeline must immediately pivot to **Zero-Shot**. Avoid synthesis loops to conserve the 32K token budget.

**Detailed Asset:** [rq3_pipeline_efficiency.md](synthetic_similarity_gating/rq3_pipeline_efficiency.md)

## Conclusions
The **Synthetic Similarity Gating** strategy is a critical missing piece in the Architect-led few-shot fallback. Without it, the model risks "Negative Transfer" on roughly 15-20% of out-of-distribution tasks where synthesis might drift. With it, we achieve a "Self-Correcting Pipeline" that autonomously determines the optimal prompting strategy (RAG, Synthetic, or Zero-Shot) for every individual task based on a verifiable local similarity metric.

## Recommendations
1. **Implement `SyntheticAnchorAgent.audit_synthesis()`**: Add a method to the agent that uses the local embedding model to calculate the similarity of the synthetic example before proceeding.
2. **Set strict 0.70 Threshold**: Use a higher bar for synthetic data than for RAG to ensure only high-fidelity grounding is used.
3. **Pydantic Structural Check**: Combine the embedding check with a formal `jsonschema` validation to ensure the "Structural Alignment" part of the Audit Score is 1.0.
4. **Deploy Immediate Zero-Shot Fallback**: On audit failure, do not retry synthesis; go straight to Zero-Shot to save time and tokens.

---
*Research complete. Use the `/draft` command to turn this executive report into a publication-ready document.*
