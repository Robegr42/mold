# 🧱 M.O.L.D. (Micro-model Object Language Decoder)

**Technical Specification: High-Fidelity Schema-Guided Information Extraction for Small Language Models**

## 🔬 Scientific Abstract

**M.O.L.D.** (GenSIE) is a research framework engineered to optimize the inferential performance of Small Language Models (SLMs < 14B) in zero-shot and low-resource information extraction tasks. Addressing the cognitive bottleneck inherent in simultaneous linguistic reasoning and structural serialization, M.O.L.D. employs a **Multi-Pass Bifurcated Architecture**. By enforcing deterministic prompt invariants and dynamic latent routing, the framework achieves state-of-the-art precision in Spanish-language extraction without requiring parameter-efficient fine-tuning (PEFT).

---

## 🏗 Architectural Core: Prompt Invariants

The framework's stability is anchored in four foundational prompting invariants that reduce the model's structural entropy:

1.  **TypeScript Schema Compression (TSC):** Replaces verbose JSON Schema definitions with condensed TypeScript interfaces, reducing token overhead by up to 40% and aligning with the programming-heavy pre-training of modern SLMs.
2.  **Bifurcated Inference Strategy:** Decouples the **Semantic Analysis Pass** (unstructured reasoning in Spanish) from the **Structural Extraction Pass** (deterministic JSON mapping).
3.  **Deterministic Invariant Pruning:** Hard-coded constraints including "Extract-or-Null" gating (penalizing inference over evidence) and "Dialect-Aware Semantic Mapping".
4.  **Greedy Bipartite Metric Alignment:** Uses an internal evaluation engine that measures similarity via bipartite matching for lists and hybrid semantic/lexical vectors for free text.

---

## 🤖 Agent Roster: Technical Strategies

### 1. **M.I.R.A.** (Minimalist Invariant Reasoning Agent)
*   **Mechanism:** **Bifurcated Zero-Shot Reasoning.**
*   **Strategy:** Decouples semantic decomposition from structural serialization. It prioritizes **Inference Speed** and **Precision** by utilizing a reasoning pass in Spanish to map entities before the extraction pass enforces a strict `null` fallback for missing data.
*   **Ideal Use:** High-latency requirements where zero-shot generalization is sufficient.

### 2. **V.I.G.I.L.** (Validated In-context Gated Intelligence Layer)
*   **Mechanism:** **Latent Semantic Routing (LSR).**
*   **Strategy:** Implements a similarity-gated RAG layer with a strict threshold ($\tau = 0.55$). It dynamically selects semantic anchors only when positive transfer is statistically likely, preventing the "Context Poisoning" often observed in SLMs when exposed to low-similarity few-shot examples.
*   **Ideal Use:** Datasets with high internal semantic variance.

### 3. **A.R.C.A.N.E.** (Audited Reasoning via Cached Anchors & Neural Examples)
*   **Mechanism:** **Recursive Synthetic Grounding Loop.**
*   **Strategy:** For Out-of-Distribution (OOD) schemas, the system autonomously bootstraps grounding signals by synthesizing localized few-shot examples. Each synthetic anchor undergoes a **Dual-Layer Audit** (Structural JSON Schema validation + Semantic Embedding Similarity $\ge 0.70$) before integration into the context window.
*   **Ideal Use:** Novel or extremely niche extraction domains where RAG data is non-existent.

---

## 📊 Formal Evaluation Framework

The framework provides native tools to compute **Flattened Schema Scoring (FSS)**:

*   **Metric:** Micro-F1 calculated over dot-notation flattened paths.
*   **Bipartite Matching:** Employs the Hungarian Algorithm (greedy) to resolve list-order invariance.
*   **Semantic Delta:** Cosine similarity via `fastembed` (BGE-small) weighted with Jaccard lexical overlap.
*   **Gap Closure:** Measures the percentage of the F1 gap bridged between a baseline and a perfect score ($1.0$).

---

## 💻 Implementation & Reproduction

### Environment Bootstrapping
Requires Python 3.13+ and the `uv` package manager for deterministic dependency resolution.

```bash
git clone https://github.com/Robegr42/mold.git && cd mold
uv sync
```

### Operational Commands
*   **Service Deployment:** `uv run gensie serve` (FastAPI + Uvicorn).
*   **Recursive Evaluation:** `uv run gensie eval2` (Per-field error profiling + token usage).
*   **Statistical Ranking:** `uv run gensie rank` (Comparative F1 gap-closed analysis).

---

## 📄 Research & Attribution

*   **Lead Institution:** University of Havana - MOLD Team.
*   **Competition:** IberLEF 2026 - GenSIE Challenge.
*   **License:** MIT.

---
*For in-depth experimental results, including ablation studies on the impact of TSC and LSR, see the [research/](./research/) directory.*
