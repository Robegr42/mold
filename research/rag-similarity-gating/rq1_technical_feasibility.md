# Research Asset: RQ1 - Technical Feasibility & Implementation Strategy

## 1. FAISS Gating Implementation (0.65 Similarity)
The `RAGModule.get_few_shot_examples` uses FAISS `IndexFlatL2`. In FAISS, L2 distances ($d^2$) are returned. We must convert these to a similarity score (often $1 / (1 + d^2)$ or $e^{-d^2}$).

*   **Conversion**: For normalized embeddings, $similarity = 1 - (d^2 / 2)$.
*   **Gate Logic**: We will check `min(D[0])` for the best retrieved match. If $1 - (\min(D[0]) / 2) < 0.65$, we trigger the Zero-Shot pivot.

## 2. Dynamic Pivot Strategy in `run()`
To implement the pivot without re-instantiation, we modify the `run()` methods of `SlimChampionAgent` and `StableChampionAgent` to be conditional:

```python
# In SlimChampionAgent.run():
few_shots = self.rag.get_few_shot_examples(task, k=self.rag_k)
# Check score of best result (D[0][0])
best_score = 1 - (D[0][0] / 2) 

if best_score < 0.65:
    few_shots = [] # Zero-Shot mode
    # Hints remain fixed as requested by user
```

## 3. Minimal Structural Changes
*   **RAGModule**: Update `get_few_shot_examples` to return `(List[Examples], float)` where `float` is the similarity score.
*   **Agent Classes**: Update the `run` loop to perform the conditional check on the returned similarity score and set `few_shots` to `[]` if the gate triggers.
*   **Hints**: Since the user explicitly requested **not** to modify hints dynamically, the agent will continue using the standard hint count, ensuring the agent logic remains as lean as possible.
