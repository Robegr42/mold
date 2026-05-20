# 🧱 M.O.L.D. (Micro-model Object Language Decoder)

**Official University of Havana Submission for the GenSIE 2026 Challenge (IberLEF)**

> *High-Fidelity Zero-Shot Information Extraction from Spanish Text using Open-Weight Small Language Models.*

## 🔬 Scientific Abstract

**M.O.L.D.** is a specialized research framework engineered to optimize structured information extraction from unstructured Spanish text using Small Language Models (SLMs < 14B). Developed as a primary response to the [GenSIE 2026 Challenge](./docs/gensie.pdf), the system addresses the critical bottleneck of **Zero-Shot Schema Adherence**—where the target extraction format is only provided at inference time. 

By rejecting monolithic prompting in favor of a **Bifurcated Inference Architecture**, M.O.L.D. enforces deterministic prompt invariants that strictly prioritize evidence-based grounding over parametric hallucination, directly satisfying the challenge's mandate for **"Extract-or-Null"** logic.

---

## 🏗 Architectural Innovations

The framework implements four technical pillars to reduce the model's structural entropy and improve zero-shot reliability:

1.  **TypeScript Schema Compression (TSC):** Condenses complex JSON Schemas into minimal TypeScript interfaces, exploiting the coding-centric pre-training of modern SLMs to reduce token overhead by ~40%.
2.  **Bifurcated Inference Chain:** A two-pass strategy that decouples **Semantic Decomposition** (unstructured Spanish analysis) from **Structural Serialization** (deterministic JSON mapping).
3.  **Deterministic Invariant Pruning:** Hard-coded prompt constraints enforcing the GenSIE "Null-Rule" for missing data and IberLEF-compliant dialect awareness.
4.  **Greedy Bipartite Evaluation:** A native implementation of **Flattened Schema Scoring (FSS)** using greedy bipartite matching to ensure list-order invariance.

---

## 🤖 The GenSIE Agent Ecosystem

M.O.L.D. features three distinct agent architectures, each providing a unique trade-off between inference cost and extraction fidelity:

### 1. **M.I.R.A.** (Minimalist Invariant Reasoning Agent)
*   **Strategy:** `mira` (Zero-Shot Bifurcated Reasoning)
*   **Mechanism:** Decouples Spanish linguistic reasoning from structural mapping to maximize precision in high-latency zero-shot environments.

### 2. **V.I.G.I.L.** (Validated In-context Gated Intelligence Layer)
*   **Strategy:** `vigil` (Latent Semantic Routing)
*   **Mechanism:** Employs a $\tau = 0.55$ similarity gate to dynamically select semantic anchors, preventing "Context Poisoning" from low-similarity RAG examples.

### 3. **A.R.C.A.N.E.** (Audited Reasoning via Cached Anchors & Neural Examples)
*   **Strategy:** `arcane` (Recursive Synthetic Grounding)
*   **Mechanism:** Autonomously bootstraps grounding signals through a dual-layer audit (Structural + Semantic $\ge 0.70$) for adaptation to out-of-distribution (OOD) schemas.

---

## 💻 Operational Reproduction

M.O.L.D. utilizes [uv](https://github.com/astral-sh/uv) for deterministic dependency management (Python 3.13+).

```bash
# Bootstrapping environment
git clone https://github.com/Robegr42/mold.git && cd mold && uv sync

# Service Deployment (FastAPI)
uv run gensie serve --port 8000

# Challenge-Specific Evaluation (Per-field Error Profiling)
uv run gensie eval2 --data data/starter --pipeline vigil --model qwen/qwen3-1.7b

# Official Ranking (Gap Closed Analysis)
uv run gensie rank --baseline-pipeline baseline
```

---

## 📄 Attribution & Challenge Context

*   **Lead Institution:** University of Havana - MOLD Team.
*   **Target Task:** [GenSIE @ IberLEF 2026](./docs/gensie.pdf) - General-purpose Schema-guided Information Extraction.
*   **Metric:** Flattened Schema Scoring (Micro-F1).
*   **License:** MIT.

---
*For in-depth experimental results and ablation reports, see the [research/](./research/) directory.*
