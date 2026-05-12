# Analysis of Champion Pipeline Failures (Llama-3.2-3B)

## 1. Root Cause Analysis

Based on empirical testing and codebase inspection, the poor performance (F1 ~0.35) and task failures (status FAIL) of the `champion` pipeline on the `llama-3.2-3b-instruct` model are caused by three primary factors:

### A. Aggressive Timeouts (The "FAIL" Root Cause)
The `ChampionAgent` implements a `ThreadPoolExecutor` with a hard **45-second timeout** for its internal ensemble pipelines.
* **Observation:** A single extraction task for `medical_drug_001` takes approximately **79 seconds** on the current hardware/model configuration.
* **Impact:** The internal futures are killed before they return, leading to an empty results list and the agent returning an error JSON: `{"error": "Pipeline timeout or failure"}`. This results in a 0.0 TPS score and a "FAIL" status in the evaluation report.

### B. Missing Architectural Invariants
While `TwoPassAgent` and other core agents use the `InvariantPromptMixin`, the `ChampionAgent` was not updated to include these critical grounding guardrails.
* **Missing Feature:** It doesn't use the **"Extract-or-Null"** rule or **TypeScript Schema Compression**.
* **Impact:** The 3B model defaults to "hallucination by completion," using its internal weights (e.g., knowing Paracetamol side effects) instead of grounding itself in the provided text.

### C. Complexity Overload for Small Models
The `champion` pipeline forces the 3B model through a very high-friction path:
1. **Architect Module:** One LLM call for hints.
2. **Strict Reasoning Schema:** Pass 1 forces a JSON reasoning structure (`thought_process`, `evidence_segments`). Small models struggle to maintain reasoning quality when constrained by JSON syntax in the same turn.
3. **ReAct Auditor:** A secondary audit loop (also using the 3B model) that is either hitting the 50s "safety" budget or aggressively nullifying correct data due to poor verification competence.

---

## 2. Proposed Solutions

### Solution 1: Hardening the Champion (High Effort, High Potential)
Integrate the foundational invariants and relax the constraints.
1. **Apply `InvariantPromptMixin`:** Inject "Extract-or-Null" and "TS Schema" into both Pass 1 and Pass 2.
2. **Relax Timeouts:** Increase the `ThreadPoolExecutor` timeout to **120 seconds** and the Auditor budget to **150 seconds**.
3. **Hybrid Reasoning:** Switch Pass 1 from a strict JSON reasoning schema to a **free-text Spanish analysis** (similar to `TwoPassAgent`), which is more native to the model's training.
4. **Shared Model Instance:** Ensure `SentenceTransformer` is shared across modules to save memory and initialization time.

### Solution 2: The "Slim Champion" (Medium Effort, High Stability)
Simplify the pipeline to play to the 3B model's strengths.
1. **Remove Ensembling:** The 3B model's outputs are often consistent in their failure modes; ensembling them (N=2) adds latency without significant diversity.
2. **Remove ReAct Auditor:** Rely on a stronger Pass 2 grounding prompt instead of a secondary audit loop that consumes tokens and time.
3. **Focus on RAG + Invariants:** Keep the dynamic few-shot examples but ensure they are formatted using the same TS schema as the prompt.

### Solution 3: Invariant-Boosted Two-Pass (Low Effort, Proven)
If the goal is survival with high F1, the `TwoPassAgent` with all invariants enabled (`use_ts=True, use_null=True, use_dialect=True`) is currently the most robust path. The "Champion" might simply be over-engineered for a model of this scale.

---

## 3. Recommended Action
I recommend **Solution 1** (Hardening) as a first step to see if we can save the "Champion" vision. If F1 does not cross the 0.55 threshold, we should pivot to **Solution 2**.
