# GenSIE: Technical Specification of Agent Architectures

## Executive Summary
This report presents a formalized technical specification of the GenSIE (General-purpose Schema-guided Information Extraction) agent ecosystem. We define the transition from generic pipeline labels to high-density scientific identities: **M.I.R.A.**, **V.I.G.I.L.**, and **A.R.C.A.N.E.** 

Key findings include:
- **Architectural Rigor:** Each agent is built on verifiable mechanics including **Bifurcated Inference**, **Latent Semantic Routing**, and **Recursive Synthetic Grounding**, ensuring precise information extraction across varying data regimes.
- **Expert-Oriented Communication:** Standardized technical abstracts facilitate immediate understanding for expert users and scientific reviewers by focusing on the underlying *Mechanism-Objective-Constraint* triad.
- **Traceability:** A comprehensive mapping table bridges high-level branded identities with low-level implementation strategies in `src/gensie/baseline.py`.

This framework establishes a peer-review-standard baseline for communicating the technical utility of the GenSIE suite in both corporate environments and academic literature.

## Research Questions

### 1. Formal Architectural Definition & Terminology

**Overview**
The GenSIE agent ecosystem is grounded in advanced prompting strategies and inference optimization. Each agent is formalized through the following architectural principles:

- **M.I.R.A. (Minimalist Invariant Reasoning Agent):** Operates on a **Bifurcated Inference Strategy**. It utilizes **Decoupled Inference Pipelines** to separate reasoning (Spanish Analysis) from structural mapping (JSON Extraction). Performance is stabilized via **Deterministic Invariant Pruning**, specifically through a "Null-Rule" that optimizes Precision-at-K by pruning false positives in zero-shot contexts.
- **V.I.G.I.L. (Validated In-context Gated Intelligence Layer):** Implements **Latent Semantic Routing (LSR)** through a threshold-gated ($\tau = 0.55$) retrieval layer. This mechanism maximizes the **Contextual Signal-to-Noise Ratio (SNR)** by ensuring only high-similarity semantic anchors are used for **Dynamic Prompt Augmentation**, preventing context poisoning from irrelevant few-shot examples.
- **A.R.C.A.N.E. (Audited Reasoning via Cached Anchors & Neural Examples):** Employs **Recursive Synthetic Grounding** to maintain performance in low-resource/new domains. It utilizes **Autonomous Few-Shot Synthesis** to bootstrap internal anchors, which are then passed through **Structural-Semantic Audit Gates** (validating schema compliance and embedding similarity) to ensure cognitive scaffolding reliability.

**Detailed Research Asset:**
[formal_terminology.md](gensie_technical_branding/formal_terminology.md)

### 2. Design of Concise Technical Abstracts

**Overview**
To satisfy both scientific reviewers and GitHub maintainers, agent descriptions have been standardized into a high-density "Mechanism-Objective-Constraint" format. This ensures that expert users can identify the underlying logic and operational boundaries of each agent instantaneously.

**Standardized Technical Abstracts:**
- **M.I.R.A.:** Decoupled two-pass Spanish-mediated reasoning. Maximizes JSON extraction precision via internal linguistic alignment. Core constraint: Strict Null-Rule invariant enforcement.
- **V.I.G.I.L.:** Gated Retrieval-Augmented Generation ($\tau = 0.55$). Optimizes Context SNR for high-fidelity grounding. Core constraint: Similarity-gated context pruning.
- **A.R.C.A.N.E.:** Audited synthetic grounding loop. Stabilizes performance in low-resource/new domains. Core constraint: Recursive structural-semantic validation checks.

**Identity Mapping Table:**

| Branded Identity | Technical Strategy Label | Primary Scientific Mechanism |
| :--- | :--- | :--- |
| **M.I.R.A.** | `two-pass-null` | Decoupled Invariant Pruning |
| **V.I.G.I.L.** | `gated-stable-champion` | Latent Semantic Routing |
| **A.R.C.A.N.E.** | `audited-synthetic` | Recursive Synthetic Grounding |

**Detailed Research Asset:**
[technical_abstracts.md](gensie_technical_branding/technical_abstracts.md)

## Conclusions
The refinement of the GenSIE agent ecosystem into **M.I.R.A.**, **V.I.G.I.L.**, and **A.R.C.A.N.E.** provides a robust framework for communicating high-stakes information extraction capabilities. By formalizing these identities using peer-reviewed concepts such as *Decoupled Inference*, *Latent Semantic Routing*, and *Recursive Grounding*, the project achieves a high level of scientific transparency. The standardized abstract format ensures that both corporate stakeholders and expert users can quickly assess the architectural trade-offs between precision, reliability, and autonomous robustness.

## Recommendations
- **Official Documentation Update:** Replace existing pipeline descriptions in `README.md` and `AGENTS.md` with the new standardized technical abstracts.
- **Codebase Annotation:** Explicitly label the core logic blocks in `src/gensie/baseline.py` with their branded identities (e.g., `# [M.I.R.A.] Decoupled reasoning pass`) to improve developer ergonomics.
- **Publication Strategy:** Use this technical report as a foundational draft for a scientific white paper on "Optimizing Inference Stability in Small Language Models via Invariant Pruning and Audited Synthesis."
- **Performance Integration:** Link the Identity Mapping Table to the live performance metrics in the `results/` directory for dynamic traceability.
