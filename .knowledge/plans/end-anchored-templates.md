---
id: end-anchored-templates
created: 2026-04-23
modified: 2026-04-23
type: plan
status: active
expires: 2026-04-30
phases:
  - name: Phase 1 Delimiter Separation
    done: false
    goal: Update prompt generator to separate instructions and context.
  - name: Phase 2 End-Anchoring
    done: false
    goal: Inject blank JSON schema template at the end of the prompt.
  - name: Phase 3 Agent Integration
    done: false
    goal: Create and test a new agent using this prompt strategy.
---

# Plan: End-Anchored Templates & Delimiter Separation

## Context
When dealing with messy, long-context documents (like OCR'd PDFs or complex clinical reports), small models often suffer from "context-loss" where they forget structural instructions provided early in the prompt. This plan implements a prompt design methodology to combat this by using strict visual separators and placing a blank JSON template at the absolute end of the prompt, ensuring it is the freshest information in the context window.

## Phases

### Phase 1: Delimiter Separation Implementation
**Goal:** Update prompt generator to clearly segregate instructions from the raw input context using strict visual separators (`===` or `###`).

**Deliverable:** A new prompt formatting utility that injects delimiters.

**Done when:**
- [ ] Prompt string clearly separates instructions, schema, and input document using visual delimiters.
- [ ] Tests verify the formatting structure is consistent.

### Phase 2: End-Anchoring Schema Injection
**Goal:** Place a fully-defined, blank JSON template (the target schema) at the absolute end of the prompt.

**Deliverable:** Schema serialization logic that appends the target schema structure to the very end of the prompt payload.

**Done when:**
- [ ] JSON schema is correctly translated into a blank JSON object template.
- [ ] The blank template is appended as the last string in the user prompt payload.

### Phase 3: Agent Integration and Testing
**Goal:** Create a new pipeline agent (`EndAnchoredAgent`) that uses this prompt format instead of default structured outputs.

**Deliverable:** New agent class integrated into the competition pipelines.

**Done when:**
- [ ] `EndAnchoredAgent` is implemented in `src/gensie/baseline.py` (or a new module).
- [ ] Agent is registered in `OfficialParticipant`.
- [ ] Agent successfully extracts data from a sample text using the new format.

## Success Criteria
- The model successfully outputs structurally valid JSON without relying on API-level `response_format` constraints.
- Long-context extractions have fewer dropped schema fields.

## Risks & Mitigations
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Model ignores the blank template and hallucinates keys | Medium | Refine delimiters and emphasize "Fill this template" in the immediate preceding text. |
| Complex schemas are hard to represent as blank templates | High | Build a robust recursive schema-to-template generator. |

## Related
- Research: `structured_extraction_strategies.md` (Section 2.1)
