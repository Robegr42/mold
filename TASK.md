# 📋 Project Tasks (M.O.L.D.)

This file tracks the progress of the M.O.L.D. project.

## 🛠 Active Tasks
- [ ] **Initial Planning**
    - Status: ⏳ Pending
    - Plan: [plans/initial_strategy.md](plans/initial_strategy.md)
- [x] **Implement Reasoning-Guided Extraction (Thinking-First)**
    - Status: ✅ Done
    - Plan: [plans/thinking-first-strategy.md](plans/thinking-first-strategy.md)
- [/] **Implement Grammar-Constrained Decoding (FST-FSA/PDA)**
    - Status: 🚧 In Progress (@dguerrerom)
    - Plan: [plans/grammar-constrained-fst.md](plans/grammar-constrained-fst.md)
- [ ] **Implement Grammar-Constrained Decoding (FST-FSA/PDA) v2**
    - Status: ⏳ Pending
    - Plan: [plans/grammar-constrained-v2.md](plans/grammar-constrained-v2.md)
- [ ] **Implement Speculative Constrained Decoding**
    - Status: ⏳ Pending
    - Plan: [plans/speculative-constrained-decoding.md](plans/speculative-constrained-decoding.md)

## 🐛 Bug Fixes
- [x] **Fix `json_object` response format compatibility in `EndAnchoredAgent`**
    - Status: ✅ Done
    - Issue: Some models/servers do not support `json_object` and require `json_schema` or `text`.
