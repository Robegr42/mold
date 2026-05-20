# 🧱 M.O.L.D. (Micro-model Object Language Decoder)

**Official University of Havana Submission for the GenSIE 2026 Challenge (IberLEF)**

> *High-Fidelity Zero-Shot Information Extraction from Spanish Text using Open-Weight Small Language Models.*

## 🔬 Scientific Abstract

**M.O.L.D.** is a research-grade framework engineered by the **University of Havana MOLD Team** as a primary response to the [GenSIE 2026 Challenge](./docs/gensie.pdf). The system is architected to optimize structured JSON extraction from general-domain Spanish texts using Small Language Models (SLMs < 14B) in resource-constrained, CPU-only environments.

Addressing the cognitive bottleneck of simultaneous linguistic reasoning and structural serialization, M.O.L.D. implements a **Bifurcated Inference Architecture**. By enforcing deterministic prompt invariants and utilizing **Zero-PyTorch** local embeddings via **FastEmbed**, the framework achieves robust zero-shot schema adherence while strictly maintaining the GenSIE **"Extract-or-Null"** grounding mandate to eliminate parametric hallucinations.

---

## 🏗 Architectural Innovations

The framework anchors its reliability in four technical pillars designed for high-stakes IE tasks:

1.  **TypeScript Schema Compression (TSC):** We map complex JSON Schemas to condensed TypeScript interfaces, exploiting the coding-centric pre-training of modern SLMs to reduce token entropy and improve structural alignment.
2.  **Bifurcated Inference Chain:** A two-pass strategy that decouples **Semantic Decomposition** (unstructured Spanish analysis) from **Structural Serialization** (deterministic JSON mapping).
3.  **Deterministic Invariant Pruning:** Hard-coded prompt constraints enforcing the GenSIE "Null-Rule" for missing data and IberLEF-compliant dialect awareness.
4.  **Minimal Hardware Footprint:** Optimized for the GenSIE CPU-only mandate by eliminating heavy deep-learning frameworks (Zero-PyTorch) in favor of **ONNX-based** local embeddings.

---

## 🤖 The GenSIE Agent Ecosystem

M.O.L.D. implements three distinct pipelines, each providing a unique trade-off between inference cost and extraction fidelity:

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

### Local Execution
```bash
# Bootstrapping environment
git clone https://github.com/Robegr42/mold.git && cd mold && uv sync

# Service Deployment (FastAPI)
uv run gensie serve --port 8000

# Challenge-Specific Evaluation (Per-field Error Profiling)
uv run gensie eval --data data/starter --pipeline vigil --model qwen/qwen3-1.7b
```

### Containerization (Docker)
M.O.L.D. is fully containerized to ensure reproducibility in internet-isolated environments.

#### 1. Build the Submission Image
```bash
docker build -t gensie-agent .
```

#### 2. Run the Agent Server
The container automatically starts the FastAPI server on port 8000. Inject the official inference backend details via environment variables.

```bash
docker run -p 8000:8000 \
  -e OPENAI_BASE_URL="http://official-inference-server:8000/v1" \
  -e OPENAI_API_KEY="official-api-key" \
  gensie-agent
```

#### 3. Development with Docker Compose
For rapid local iteration with hot-reloading:
```bash
docker compose up
```

---

## 📄 Attribution & Challenge Context

*   **Lead Institution:** University of Havana - MOLD Team.
*   **Target Task:** [GenSIE @ IberLEF 2026](./docs/gensie.pdf).
*   **Metric:** Flattened Schema Scoring (Micro-F1) with Greedy Bipartite Matching.
*   **License:** MIT.

---
*For in-depth experimental results and ablation reports, see the [research/](./research/) directory.*
