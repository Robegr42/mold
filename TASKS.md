# 📋 Project Tasks (M.O.L.D.)

This file tracks the progress of the M.O.L.D. project.

## 🛠 Active Tasks
- [x] **Implement Two-Pass Champion Pipeline (Modular RAG + ReAct)**
    - Status: ✅ Done
    - Plan: [plans/implement-two-pass-champion.md](plans/implement-two-pass-champion.md)
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
- [x] **Refactor Agent Architecture (Phase 1: Foundational Invariants)**
    - Status: ✅ Done
    - Plan: [plans/final_refactoring_plan.md](plans/final_refactoring_plan.md)
- [x] **Refactor Agent Architecture (Phase 2.1: TwoPassAgent)**
    - Status: ✅ Done
    - Plan: [plans/final_refactoring_plan.md](plans/final_refactoring_plan.md)
- [x] **Refactor Agent Architecture (Phase 2.2: GroundedAgent)**
    - Status: ✅ Done
    - Plan: [plans/final_refactoring_plan.md](plans/final_refactoring_plan.md)
- [x] **Refactor Agent Architecture (Phase 2.3 & 3: AuditorAgent & Integration)**
    - Status: ✅ Done
    - Plan: [plans/final_refactoring_plan.md](plans/final_refactoring_plan.md)
- [x] **Cross-Model Stable-Champion Evaluation (Llama, Qwen, Gemma)**
    - Status: ✅ Evaluation Complete
    - Plan: [plans/cross-model-stable-champion-experiment.md](plans/cross-model-stable-champion-experiment.md)
    - Research: [research/cross-model-stable-champion_report.md](research/cross-model-stable-champion_report.md)
- [x] **Generate Detailed Cross-Model Evaluation Summary Report**
    - Status: ✅ Done
    - Goal: Create a formatted markdown report aggregating results from all evaluation runs across Qwen, Llama, and Gemma.
    - Report: [research/cross-model-stable-champion_matrix_report.md](research/cross-model-stable-champion_matrix_report.md)
- [/] **Generate Final Experimental Synthesis & Generalization Report**
    - Status: 🚧 In Progress
    - Goal: Produce a profound report of the cross-model experiment, selecting the best 3 strategies for generalizing, and identifying the best 3 strategies without RAG.
- [ ] **Initial Planning**
    - Status: ⏳ Pending
    - Plan: [plans/initial_strategy.md](plans/initial_strategy.md)

## 🐛 Bug Fixes
- [x] **Fix `json_object` response format compatibility in `EndAnchoredAgent`**
    - Status: ✅ Done
    - Issue: Some models/servers do not support `json_object` and require `json_schema` or `text`.
