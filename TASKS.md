# Project Tasks

## Infrastructure
- [x] Fix token usage reporting for MIRA, ARCANE, and VIGIL pipelines (See plan: plans/fix-token-usage-reporting.md)
- [/] Adapt MIRA, VIGIL, and ARCANE pipelines to the new evaluation logic (See plan: plans/evaluation-analysis-report.md)
    - [x] Tune the `Extract-or-Null` invariant (soften aggressive pruning)
    - [ ] Enforce strict date formatting in prompts
    - [ ] Enhance complex schema handling in `compress_schema_to_ts`
    - [x] Conduct Null Invariant comparative study (mira -> vigil, arcane)
    - [x] Conduct Vigil-specific pass optimization for Null Invariant
    - [ ] Conduct Mira-specific pass optimization for Null Invariant
