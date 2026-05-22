# Evaluation Analysis Report: Pipeline Competitiveness

## Background & Motivation
The user reported a significant drop in the competitiveness of their advanced pipelines (`mira` [formerly `two-pass-null`], `vigil` [formerly `gated-stable-champion`], and `arcane` [formerly `audited-synthetic`]) under the new evaluation logic compared to the legacy methods used until 05/19/26.

This plan details the root causes found in the recent commits to `src/gensie/eval.py` and proposes a strategy to adapt the pipelines to these new constraints.

## Root Cause Analysis
An analysis of the evaluation codebase reveals four major changes that disproportionately affect pipelines employing the "Extract-or-Null" strategy (`use_null=True`):

### 1. Case C - The Hard Null Penalty (Hallucinations)
- **Legacy Behavior:** If the gold standard expected a specific value but the system aggressively output `null`, the evaluator fell through to the semantic similarity logic. It compared the string `"None"` against the expected text, often awarding partial credit.
- **New Behavior:** A `null` vs value mismatch now scores a hard `0.0`.
- **Impact:** The advanced pipelines use `InvariantPromptMixin` with `use_null=True`, which enforces a strict rule: "If information is absent, return `null`." This makes them over-cautious. Previously, this pruning was forgiven with partial credit; now, missing a field completely zeros out its score.

### 2. Case A - Rigid Dates
- **Legacy Behavior:** Date fields (`format: date`, `time`, `date-time`) were evaluated using semantic similarity, allowing flexibility in formatting.
- **New Behavior:** Date fields are now classified as **Rigid**, requiring an exact lexical match to score `1.0`.
- **Impact:** Even if the pipelines extract the correct date, any formatting discrepancy results in a `0.0`.

### 3. Global Micro-F1 Normalization
- **Legacy Behavior:** The True Positive Score (TPS) was normalized per-instance (divided by the max number of keys) before being averaged across the dataset (a Macro-F1 approach).
- **New Behavior:** The evaluation now uses a true Global Micro-F1. Raw similarities are summed across the entire test set before normalization.
- **Impact:** Instances with complex, deeply nested schemas (containing many keys) now carry significantly more weight in the final score. If the pipelines struggle to maintain structure or extract all fields in deep schemas, their global score will plummet relative to simpler tasks.

### 4. "Gap Closed" Leaderboard Metric
- **Legacy Behavior:** Rankings were based on raw F1 scores.
- **New Behavior:** The primary ranking metric is `Gap Closed = max(0, (F1_system - F1_baseline) / (1 - F1_baseline))`. 
- **Impact:** The score measures relative improvement over the baseline. If the baseline performs well on certain models, absolute gains appear smaller, masking the advanced pipelines' raw performance advantages.

## Proposed Strategy
To restore the competitiveness of `mira`, `vigil`, and `arcane`, we must adapt them to the new evaluation constraints.

### 1. Tune the `Extract-or-Null` Invariant
- **Action:** Re-evaluate `use_null=True` in `src/gensie/baseline.py`.
- **Details:** The current rule is too aggressive for the new hard null penalty. We should consider disabling it (`use_null=False`) or modifying the `InvariantPromptMixin` to provide softer reasoning hints (e.g., "Extract the value if confidently present, otherwise attempt to infer from context before returning null").

### 2. Enforce Strict Date Formatting
- **Action:** Add a formatting invariant to the prompts.
- **Details:** When generating the prompt, explicitly instruct the model to format all dates and times according strictly to the schema's expected format (e.g., ISO 8601).

### 3. Enhance Complex Schema Handling
- **Action:** Improve `compress_schema_to_ts`.
- **Details:** Ensure that the TypeScript compression does not lose critical nested details that the model needs to achieve high recall on complex schemas.

### 4. Null Invariant Comparative Study
- **Action:** Determine the optimal configuration for the `null` invariant.
- **Details:** Conduct an experimental ablation to compare performance (Micro-F1) with and without the `null` invariant enabled.
- **Execution:** 
    1. Test first with the `mira` pipeline. 
    2. If performance improves under one configuration, extend the test to the `vigil` and `arcane` pipelines.

### 5. Vigil-Specific Pass Optimization for Null Invariant
- **Action:** Determine if applying the (softened) `null` invariant to only one pass improves `vigil` performance.
- **Details:** The previous study showed `vigil` performs better with the invariant enabled globally. This task further refines that by checking if isolating the invariant to the Reasoning step or the Extraction step is even better.
- **Execution:**
    1. Test `vigil` with `use_null` enabled ONLY in Pass 1 (Reasoning).
    2. Test `vigil` with `use_null` enabled ONLY in Pass 2 (Extraction).
    3. Compare these results with the global `use_null=True` baseline from Step 4.
    4. Set the most performant configuration as the new default for `vigil`.

### 6. Mira-Specific Pass Optimization for Null Invariant
- **Action:** Determine the optimal configuration for the `null` invariant across `mira`'s two passes.
- **Details:** Currently, `mira` only applies the `null` invariant to Step 1 (Reasoning). This task will investigate if enabling it in Step 2 (Extraction) improves results.
- **Execution:**
    1. Refactor `mira` to support per-pass `use_null` toggles.
    2. Test `mira` with `use_null` enabled ONLY in Step 2 (Extraction).
    3. Test `mira` with `use_null` enabled in BOTH Step 1 and Step 2.
    4. Compare these results with the current benchmarks (None enabled vs Step 1 enabled).
    5. Choose and adopt the best configuration for `mira`.

### 7. Standardize Mira Initialization
- **Action:** Refactor `MIRAAgent.__init__` to follow the parameterless, environment-first pattern used by `VIGILAgent`.
- **Details:**
    1. Remove explicit constructor parameters (`use_ts`, `use_null`, etc.).
    2. Read all configuration values from environment variables (e.g., `GENSIE_MIRA_USE_TS`, `GENSIE_MIRA_NULL_P1`, `GENSIE_MIRA_NULL_P2`).
    3. Remove the redundant legacy `use_null` parameter in favor of the granular per-pass toggles.
    4. Update `OfficialParticipant` to instantiate `MIRAAgent()` without arguments.

### 8. Arcane-Specific Pass Optimization for Null Invariant
- **Action:** Determine the optimal configuration for the `null` invariant across `arcane`'s passes.
- **Details:** This task investigates if isolating the `null` invariant to Step 2 (Extraction) or enabling it globally yields better results.
- **Experimental Results (Model: qwen/qwen3-1.7b, Dataset: data/starter, N=20):**
    -   **None (Current Default):** F1 = 0.7205
    -   **Pass 2 Only (Step 2 Only):** F1 = 0.7403
    -   **Both Passes (Global):** F1 = 0.7433 (Winner)
- **Execution:**
    1. Refactor `arcane` to support per-pass `use_null` toggles and parameterless initialization.
    2. Adopt the **Pass 2 Only** configuration. *Note: While global enabling was slightly better in experiments (0.7433 vs 0.7403), we chose "Pass 2 Only" (0.7403) for consistency with `mira` and `vigil`.*
    3. Update `OfficialParticipant` to use the new defaults.


## Verification
- Run local evaluations using the `gensie eval` command against the `data/starter/` dataset.
- Monitor the aggregate metrics to ensure Micro-F1 has improved and that the pipelines perform better with the adjusted invariants.
