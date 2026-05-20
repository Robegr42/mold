# 🤖 GenSIE Agent Roster

This document provides a technical specification of the core agent architectures available in the GenSIE ecosystem. Each agent is designed with a specific trade-off between **Inference Speed**, **Schema Precision**, and **Autonomous Robustness**.

---

## 🔬 Agent Profiles

### 1. **M.I.R.A.** (Minimalist Invariant Reasoning Agent)
*The Surgical Scalpel*

- **Technical Strategy:** `two-pass-null`
- **Architectural Mechanism:** **Bifurcated Inference Strategy**. Decouples cross-lingual reasoning (Spanish analysis) from structural mapping (JSON extraction) to minimize token-level hallucination.
- **Primary Objective:** Maximizing JSON extraction precision via internal linguistic alignment.
- **Core Constraint:** **Deterministic Invariant Pruning**. Enforces a strict "Null-Rule" to eliminate false positives in zero-shot contexts.

### 2. **V.I.G.I.L.** (Validated In-context Gated Intelligence Layer)
*The Shield*

- **Technical Strategy:** `gated-stable-champion`
- **Architectural Mechanism:** **Latent Semantic Routing (LSR)**. Implements a threshold-gated retrieval layer ($\tau = 0.55$) to dynamically augment prompts with high-similarity semantic anchors.
- **Primary Objective:** Optimizing Context Signal-to-Noise Ratio (SNR) for high-fidelity grounding.
- **Core Constraint:** **Similarity-Gated Context Pruning**. Prevents context poisoning by filtering out irrelevant or noisy few-shot examples.

### 3. **A.R.C.A.N.E.** (Audited Reasoning via Cached Anchors & Neural Examples)
*The Forge*

- **Technical Strategy:** `audited-synthetic`
- **Architectural Mechanism:** **Recursive Synthetic Grounding**. Utilizes autonomous few-shot synthesis to bootstrap internal anchors in low-resource or novel domains.
- **Primary Objective:** Performance stabilization and autonomous domain adaptation.
- **Core Constraint:** **Structural-Semantic Validation Loops**. Every synthetic anchor undergoes a dual-layer audit (schema compliance and embedding consistency) before being used in final inference.

---

## 📊 Identity Mapping & Performance

| Branded Identity | Technical Strategy | Primary Scientific Mechanism | Focus |
| :--- | :--- | :--- | :--- |
| **M.I.R.A.** | `two-pass-null` | Decoupled Invariant Pruning | Precision & Speed |
| **V.I.G.I.L.** | `gated-stable-champion` | Latent Semantic Routing | Grounding & SNR |
| **A.R.C.A.N.E.** | `audited-synthetic` | Recursive Synthetic Grounding | Robustness & Autonomy |

---

## 🛠 Architectural Traceability

For implementation details, refer to the following entry points in `src/gensie/baseline.py`:

- **M.I.R.A. Logic:** `TwoPassAgent` class with `use_null=True`.
- **V.I.G.I.L. Logic:** `GatedStableChampionAgent` utilizing `GatedRAGModule`.
- **A.R.C.A.N.E. Logic:** `AuditedSyntheticAgent` with `ArchitectModule` synthesis loops.
