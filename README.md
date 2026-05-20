# 🧱 M.O.L.D. (Micro-model Object Language Decoder)

**GenSIE: General-purpose Schema-guided Information Extraction**

> Dynamic JSON extraction on the fly. Your schema changes, M.O.L.D. adapts.

## 📖 Overview

**M.O.L.D.** is a high-performance framework designed to solve the challenges of structured information extraction from unstructured Spanish text using Small Language Models (SLMs). Developed for the **GenSIE 2026** challenge (IberLEF), it provides a robust agent ecosystem that balances inference speed, schema precision, and autonomous grounding.

M.O.L.D. rejects monolithic prompting in favor of specialized multi-pass architectures, utilizing technical invariants like TypeScript schema compression and deterministic "Extract-or-Null" gating to eliminate hallucinations in zero-shot contexts.

## 🤖 The GenSIE Agent Roster

M.O.L.D. features three core agent architectures, each optimized for different operational constraints:

1.  **M.I.R.A.** (*Minimalist Invariant Reasoning Agent*):
    *   **Strategy:** `mira` (Two-Pass Null-Rule)
    *   **Focus:** Precision & Speed. Decouples Spanish linguistic reasoning from JSON structural mapping to minimize cognitive load on sub-14B models.
2.  **V.I.G.I.L.** (*Validated In-context Gated Intelligence Layer*):
    *   **Strategy:** `vigil` (Gated LSR)
    *   **Focus:** Grounding & SNR. Employs **Latent Semantic Routing (LSR)** with a $\tau = 0.55$ similarity gate to filter out noisy few-shot examples and maintain high signal-to-noise ratios.
3.  **A.R.C.A.N.E.** (*Audited Reasoning via Cached Anchors & Neural Examples*):
    *   **Strategy:** `arcane` (Recursive Double-Gate)
    *   **Focus:** Robustness & Autonomy. Bootstraps its own grounding signal through a **Recursive Synthetic Grounding** loop, using a dual-layer audit (structural + semantic) to validate anchors in novel domains.

For detailed technical specifications, see [AGENTS.md](./AGENTS.md).

## ✨ Key Technical Features

*   **Two-Pass Inference:** Separates "Analysis" (thinking in Spanish) from "Extraction" (formatting in JSON) to preserve the model's raw inferential heat.
*   **TypeScript Schema Compression:** Compresses complex JSON Schemas into concise TypeScript interfaces to minimize token consumption and improve structural alignment.
*   **Double-Gate Gating:** Implements RAG-similarity gates and synthesis-audit gates to protect the model from "Negative Transfer" and hallucinations.
*   **Deterministic Invariant Pruning:** Hard-coded prompt invariants (Dialect Awareness, Null-Rule) that force the model to prioritize factuality over inference.
*   **Sophisticated Evaluation:** Native implementation of **Flattened Schema Scoring** with greedy bipartite matching for lists and hybrid semantic/lexical similarity for text.

## 🚀 Installation

M.O.L.D. requires Python 3.13+ and utilizes [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management.

```bash
# Clone the repository
git clone https://github.com/Robegr42/mold.git
cd mold

# Sync environment
uv sync
```

## 💻 Usage

### 1. Start the Agent Server
M.O.L.D. exposes its agents via a FastAPI server, ready for evaluation or production integration.

```bash
uv run gensie serve --port 8000
```

### 2. Run Evaluations
Use the `gensie eval2` command to run a detailed evaluation against a dataset. This tracks token usage, wall-time, and provides a per-field error breakdown.

```bash
uv run gensie eval2 --data data/starter --pipeline vigil --model qwen/qwen3-1.7b
```

### 3. View the Leaderboard
Aggregate results from multiple runs into a ranked leaderboard.

```bash
uv run gensie leaderboard
```

### 4. Official Ranking
Compute the "Gap Closed" metric relative to the official baseline.

```bash
uv run gensie rank --baseline-pipeline baseline
```

## 🧩 Project Structure

*   `src/gensie/`: Core engine implementation.
    *   `baseline.py`: Agent implementations (**MIRAAgent**, **VIGILAgent**, **ARCANEAgent**).
    *   `eval.py`: Flattened Schema Scoring logic.
    *   `cli.py`: Typer-powered developer tools.
*   `data/`: Standardized datasets (`starter`, `dev`).
*   `results/`: JSON evaluation reports and leaderboards.
*   `research/`: Documentation of experimental findings and architectural pivots.
*   `tests/`: Unit and integration tests for all core agents.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---
*Created by the **MOLD Team** - University of Havana*
