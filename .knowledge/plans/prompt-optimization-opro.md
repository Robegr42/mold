---
id: prompt-optimization-opro
created: 2026-04-23
modified: 2026-04-23
type: plan
status: active
expires: 2026-04-30
phases:
  - name: Phase 1 Rigid Formatting Templates
    done: false
    goal: Create "Follow the Format" (FF) templates combining instructions, schema, and context.
  - name: Phase 2 OPRO Evaluation Logic
    done: false
    goal: Build an evaluator that computes JSON validation rewards for LLM outputs.
  - name: Phase 3 Optimizer Implementation
    done: false
    goal: Implement the iterative optimization loop that proposes prompt variations.
  - name: Phase 4 Agent Integration
    done: false
    goal: Create an agent that uses the best optimized prompt layout.
---

# Plan: Prompt Optimization (OPRO) with Rigid Formatting

## Context
Iteratively refining the natural language instructions within a prompt using an automated optimizer can maximize structural adherence without changing model weights. This approach relies on "Follow the Format" (FF) or f-String templates to rigidly combine task instructions, the expected JSON schema, and the input context. An optimizer (like OPRO) proposes prompt variations and evaluates them based on JSON validation rewards.

## Phases

### Phase 1: Rigid Formatting Templates
**Goal:** Create "Follow the Format" (FF) or f-String templates combining instructions, schema, and context.

**Deliverable:** A template engine or set of base prompt templates that can rigidly enforce formatting guidelines.

**Done when:**
- [ ] Base templates that place strict constraints around data fields are designed.
- [ ] The schema and documents can be correctly injected into these templates.

### Phase 2: OPRO Evaluation Logic
**Goal:** Build an evaluator that computes JSON validation rewards for LLM outputs.

**Deliverable:** A scoring function that takes LLM output and validates it against the target schema, returning a quantifiable reward score.

**Done when:**
- [ ] Scoring function parses LLM output and extracts JSON.
- [ ] Validation against target schema works and issues rewards for valid keys, correct types, and lack of hallucinations.
- [ ] Evaluator outputs a scalar reward score.

### Phase 3: Optimizer Implementation
**Goal:** Implement the iterative optimization loop that proposes prompt variations and selects the best based on rewards.

**Deliverable:** An optimization script/module that drives the OPRO process, simulating multiple prompt versions and evaluating them.

**Done when:**
- [ ] An initial set of prompt variations is generated automatically.
- [ ] A script runs the LLM generation loop across variations and scores outputs.
- [ ] The script selects the highest-reward prompt template.

### Phase 4: Agent Integration
**Goal:** Create an agent (`OPROAgent`) that uses the best optimized prompt layout.

**Deliverable:** New pipeline agent integrated into the baseline structure.

**Done when:**
- [ ] `OPROAgent` is implemented to load the static, pre-optimized prompt template.
- [ ] Agent is registered in `OfficialParticipant`.
- [ ] Agent successfully extracts JSON in production format.

## Success Criteria
- Near 100% JSON format compliance achieved using pure prompt engineering and no structural API constraints.
- Evaluation metrics demonstrate improved robustness against edge cases over baseline.

## Risks & Mitigations
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Optimization is slow and expensive | High | Use a smaller validation dataset or faster local model for the optimizer loop. |
| OPRO gets stuck in local maxima | Medium | Ensure high temperature and prompt diversity during the variation generation step. |

## Related
- Research: `structured_extraction_strategies.md` (Section 2.2)
