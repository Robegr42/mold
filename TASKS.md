# Project Tasks

## Infrastructure
- [x] Fix token usage reporting for MIRA, ARCANE, and VIGIL pipelines (See plan: plans/fix-token-usage-reporting.md)
- [/] Adapt MIRA, VIGIL, and ARCANE pipelines to the new evaluation logic (See plan: plans/evaluation-analysis-report.md)
    - [x] Tune the `Extract-or-Null` invariant (soften aggressive pruning)
    - [x] Enforce strict date formatting in prompts
    - [x] Enhance complex schema handling in `compress_schema_to_ts`
    - [x] Conduct Null Invariant comparative study (mira -> vigil, arcane)
    - [x] Conduct Vigil-specific pass optimization for Null Invariant
    - [x] Conduct Mira-specific pass optimization for Null Invariant
    - [x] Standardize Mira initialization (parameterless __init__)
    - [x] Conduct Arcane-specific pass optimization for Null Invariant
    - [ ] Revive legacy agents: EAGLE, SAGE, AURA (See plan: plans/revive-legacy-agents.md)
    - [x] Standardize pipeline defaults and remove environment overrides
