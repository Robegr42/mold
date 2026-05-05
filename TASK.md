# 📋 Project Tasks (M.O.L.D.)

This file tracks the progress of the M.O.L.D. project.

## 🛠 Active Tasks
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
- [/] **Refactor Agent Architecture (Phase 2.3: AuditorAgent)**
    - Status: 🚧 In Progress
    - Plan: [plans/final_refactoring_plan.md](plans/final_refactoring_plan.md)
- [ ] **Initial Planning**
    - Status: ⏳ Pending
    - Plan: [plans/initial_strategy.md](plans/initial_strategy.md)
- [x] **Implement Reasoning-Guided Extraction (Thinking-First)**
    - Status: ✅ Done
    - Plan: [plans/thinking-first-strategy.md](plans/thinking-first-strategy.md)

## 🐛 Bug Fixes
- [x] **Fix `json_object` response format compatibility in `EndAnchoredAgent`**
    - Status: ✅ Done
    - Issue: Some models/servers do not support `json_object` and require `json_schema` or `text`.
