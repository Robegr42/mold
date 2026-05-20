# Plan: Pipelines In Dev Analysis Report

## 🎯 Objective
Create a profound, publication-ready markdown report analyzing the extraction pipelines (`two-pass-null`, `gated-stable-champion`, `audited-synthetic`) tested in the `pipelines_in_dev` experiment. The report will balance accuracy metrics with operational constraints and include detailed error profiling.

## 📚 Background & Context
The evaluations in `results/pipelines_in_dev/` revealed significant differences between our top three architectures. While complex pipelines like `audited-synthetic` (A.R.C.A.N.E.) pushed F1 scores higher, they introduced operational hazards, specifically severe timeouts (>60s) on complex schemas. This report synthesizes these findings.

## 🛠️ Implementation Steps

### Step 1: Data Aggregation & Metric Extraction
- Read all JSON files in `results/pipelines_in_dev/`.
- Extract aggregate metrics (Precision, Recall, Micro-F1) for each model/pipeline.
- Extract efficiency metrics: Avg Time (s), Avg Tokens, and Peak Time (identifying timeout triggers).

### Step 2: Detailed Error Profiling
- Parse the `errors` array across pipelines.
- Categorize errors into:
    - **Omissions:** (`Missing: field`)
    - **Hallucinations:** (`Hallucinated: field`)
    - **Structural/Semantic:** (`Incorrect: field`)
- Calculate the distribution to reveal the "error flavor" of each pipeline.

### Step 3: Visual Generation (Mermaid)
- Draft Mermaid diagrams for the report:
    - A **Quadrant Chart** comparing F1 Score vs. Average Latency.
    - A comparative table or chart illustrating the Error Distribution.

### Step 4: Report Drafting (`research/pipelines_in_dev_analysis_report.md`)
Structure the report:
1.  **Executive Summary:** High-level conclusions.
2.  **Accuracy vs. Efficiency:** F1 vs. latency. Highlight the timeout issues.
3.  **Error Profiling:** Analysis of how invariants and gating impact error types.
4.  **Architectural Recommendations:** Guidance on M.I.R.A., V.I.G.I.L., and A.R.C.A.N.E.

## 🧪 Verification
- Ensure markdown and Mermaid render correctly.
- Verify metrics match the raw JSON data.