# Failure Mode Deep-Dive: GenSIE with Llama 3.2 3B

## 1. Error Distribution (Dev Dataset)
The `eval2` results categorize failures into three main types: Missing, Incorrect, and Hallucinated.

| Pipeline | Missing | Incorrect | Hallucinated | Total Errors |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline** | 962 | 533 | 63 | 1558 |
| **Grounded** | 855 | 567 | 113 | 1535 |
| **Two-Pass** | 736 | 705 | 128 | 1569 |
| **End-Anchored**| 704 | 763 | 127 | 1594 |

## 2. Key Insights

### The Reasoning Paradox
The `Two-Pass` strategy reduces **Missing** fields (Recall boost) compared to Baseline, but significantly increases **Incorrect** and **Hallucinated** errors. 
*   **Analysis:** The reasoning pass helps the model identify relevant text fragments, but the subsequent mapping to JSON structure introduces "noise" or "drift." The model sometimes "hallucinates" details in the analysis that don't exist in the text, which then get extracted into the final JSON.

### Rigid Type Bottleneck
A vast majority of **Incorrect** errors have a similarity score of `0.00`.
*   **Finding:** These are almost exclusively **Rigid Types** (Enums, Booleans, Integers). 
*   **Root Cause:** Llama 3.2 3B struggles with strict Enum mapping in Spanish. For example, if the schema expects `"AUTOIMMUNE"` and the text mentions `"inmunitario"`, the model fails to perform the semantic mapping required by the GenSIE evaluation's binary scoring for rigid types.

### List Exhaustion Failure
Errors like `key_organizations.1` or `main_cast.0` appearing as **Missing** highlight a failure in exhaustive extraction.
*   **Finding:** The model often stops after extracting a single prominent entity, even when the schema expects an array of all relevant entities. This is a common limitation of small models in long contexts.

## 3. Grounded Strategy vs. Others
The `Grounded` strategy has fewer `Missing` fields than Baseline but more than Two-Pass. However, it maintains a lower count of `Incorrect` errors than Two-Pass. 
*   **Conclusion:** Mandating source quotes acts as a strong "anchor" that prevents the semantic drift seen in the Two-Pass strategy. It forces the model to verify every field against a specific string, which is more effective for SLMs than high-level "analysis."

## 4. Suggested Refinements
*   **Dynamic Enum Synonyms:** For Rigid Types, the prompt should include the Enum options *along with* common Spanish synonyms to help the model perform the mapping.
*   **Iterative List Extraction:** Instead of "Extract all", use instructions like "Extract the first 5..." or "List every mention of..." to encourage exhaustive search.
*   **Quote-to-Rigid Mapping:** Update the `Grounded` strategy to specifically mandate quotes for Rigid Types before selecting the Enum value.
