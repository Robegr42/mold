Hallo, colleague. I’m putting together a research plan for the **GenSIE 2026 shared task** (https://uhgia.org/gensie/), and I’d value your help in surveying the most promising techniques for it. The task is **General‑purpose Schema‑guided Information Extraction** from Spanish‑language texts. In a nutshell:

*   For each instance we get a **Spanish text** (legal, medical, news, etc.) and a **JSON Schema** that describes the structure of the desired output.
*   The system must produce a **strictly valid, properly nested JSON object** that faithfully extracts only the information present in the source text.
*   The challenge is **zero‑shot** – the schemas seen at test time will be completely new, so we cannot fine‑tune on a fixed ontology.
*   We must use **Small Language Models (<14B)** – specifically **Llama 3, Salamandra or Qwen** – and we are **explicitly forbidden from any form of weight fine‑tuning** (no LoRA, no QLoRA, etc.).
*   The evaluation penalises **hallucinations** heavily: if the gold output contains a value and we return `null` (or vice‑versa), we get zero for that field. Lists are matched with an order‑independent bipartite algorithm.
*   The metric is a custom **Flattened Schema Scoring** that treats rigid types (numbers, dates, booleans, enum strings) as exact‑match and free‑text fields as a hybrid semantic‑lexical similarity.
*   There is also an **Efficiency leaderboard** – the “Performance‑to‑Cost Ratio” – that divides the mean F1 by total token consumption (input + output tokens across all steps).

The inference environment is an **offline NVIDIA A100 GPU**; we can talk only to the organiser’s OpenAI‑compatible API. Allowed inference‑time techniques include **prompt engineering, RAG, grammar‑constrained decoding, synthetic few‑shot generation, chain‑of‑thought, ReAct, self‑consistency, self‑correction loops**, etc.

Given all of that, **what family of techniques would you recommend as the backbone of a state‑of‑the‑art solution?** Please weigh the trade‑offs between **accuracy and token efficiency**, and outline a rough pipeline that could work under the strict no‑training and zero‑shot constraints. If possible, also point to any recent (2024–2026) papers or tools that might be directly transferable.
