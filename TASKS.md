# 📋 Project Tasks (M.O.L.D.)

This file tracks the progress of the M.O.L.D. project.

## 🛠 Active Tasks
- [x] **Initial Planning**
    - Status: ✅ Done
    - Strategy: [README.md](README.md)
- [x] **Implement Two-Pass Champion Pipeline (Modular RAG + ReAct)**
    - Status: ✅ Done
    - Plan: [plans/gensie_agent_architecture_plan.md](plans/gensie_agent_architecture_plan.md)
- [x] **Design & Implement Slim Champion Pipeline (Optimized for SLMs)**
    - Status: ✅ Done
    - Plan: [plans/slim_champion_pipeline.md](plans/slim_champion_pipeline.md)
    - Analysis: [research/champion_pipeline_analysis.md](research/champion_pipeline_analysis.md)
- [x] **Optimize Prompt Invariants across Agents**
    - Status: ✅ Done
    - Plan: [research/invariants_impact_report.md](research/invariants_impact_report.md)
- [x] **Implement End-Anchored Template & Delimiter Separation**
    - Status: ✅ Done
    - Plan: [plans/end-anchored-strategy.md](plans/end-anchored-strategy.md)
- [x] **Refactor Agent Architecture (Phase 1-3)**
    - Status: ✅ Done
    - Plan: [plans/final_refactoring_plan.md](plans/final_refactoring_plan.md)
- [x] **Implement Gated Stable-Champion Agent (V.I.G.I.L.)**
    - Status: ✅ Done
    - Implementation: [src/gensie/baseline.py](src/gensie/baseline.py)
- [x] **Implement Synthetic Anchor Agent (Architect Few-Shot)**
    - Status: ✅ Done
    - Implementation: [src/gensie/baseline.py](src/gensie/baseline.py)
- [x] **Implement Audited Synthetic Agent (A.R.C.A.N.E.)**
    - Status: ✅ Done
    - Plan: [plans/implement-audited-synthetic-agent.md](plans/implement-audited-synthetic-agent.md)
- [x] **Create Gated vs. Stable Experiment Script**
    - Status: ✅ Done
    - Plan: [plans/run-gated-experiment-script.md](plans/run-gated-experiment-script.md)
- [x] **Cross-Model Stable-Champion Evaluation (Llama, Qwen, Gemma)**
    - Status: ✅ Evaluation Complete
    - Plan: [plans/cross-model-stable-champion-experiment.md](plans/cross-model-stable-champion-experiment.md)
    - Research: [research/cross-model-stable-champion_report.md](research/cross-model-stable-champion_report.md)
- [x] **Generate Detailed Cross-Model Evaluation Summary Report**
    - Status: ✅ Done
    - Report: [research/cross-model-stable-champion_matrix_report.md](research/cross-model-stable-champion_matrix_report.md)
- [x] **Generate Final Experimental Synthesis & Generalization Report**
    - Status: ✅ Done
    - Report: [research/final_experimental_synthesis_report.md](research/final_experimental_synthesis_report.md)
- [x] **Generate Pipelines In Dev Analysis Report**
    - Status: ✅ Done
    - Goal: Create a profound analysis of M.I.R.A., V.I.G.I.L., and A.R.C.A.N.E.
    - Report: [research/pipelines_in_dev_analysis_report.md](research/pipelines_in_dev_analysis_report.md)
    - Plan: [plans/pipelines-in-dev-analysis.md](plans/pipelines-in-dev-analysis.md)
- [x] **Create Mermaid Diagrams for Agent Architectures**
    - Status: ✅ Done
    - Doc: [research/slim_champion_architecture.md](research/slim_champion_architecture.md)

## 🐛 Bug Fixes
- [x] **Fix `json_object` response format compatibility in `EndAnchoredAgent`**
    - Status: ✅ Done
    - Issue: Some models/servers do not support `json_object` and require `json_schema` or `text`.
