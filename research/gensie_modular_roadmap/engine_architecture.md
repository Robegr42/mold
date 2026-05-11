# Modular Engine Architecture: GenSIE Champion Pipeline

This document outlines the design for the Modular Engine Architecture, a core component of the GenSIE Champion pipeline. This architecture provides a unified interface for various extraction strategies and ensures consistent application of grounding and invariant rules.

## 1. Standardized Engine Interface

To ensure interoperability between different extraction strategies, all engines must implement the `IExtractionEngine` interface. This allows the pipeline to switch between strategies (e.g., Grounded vs. Two-Pass) based on model performance and task complexity.

### 1.1 Interface Definition

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ExtractionResult(BaseModel):
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    engine_name: str
    model_id: str

class IExtractionEngine(ABC):
    """
    Standard interface for all GenSIE extraction engines.
    """
    
    @abstractmethod
    def extract(self, text: str, schema: Dict[str, Any]) -> ExtractionResult:
        """
        Executes the extraction process using the specific engine strategy.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Returns the identifier for the engine."""
        pass
```

### 1.2 Strategy Wrappers

The three core strategies are wrapped as follows:

- **`GroundedNullEngine`**: Implements direct extraction with explicit grounding instructions and the "Null Rule" invariant.
- **`EndAnchoredNullEngine`**: Re-orders the prompt so that the schema and extraction instructions follow the source text (End-Anchoring), specifically optimized for decoder-only models.
- **`TwoPassNIEngine`**: 
    - **Pass 1**: Identifies entity anchors and relevant text spans.
    - **Pass 2**: Populates the JSON schema using the identified anchors.
    - **NI (Natural Invariants)**: Applies a set of base constraints to ensure logical consistency.

## 2. Model-Specific Selection Criteria

Based on performance evaluations (referencing `pipeline_ranking_report.md`), the selection of the optimal engine depends on the underlying model's architecture and instruction-following strengths.

| Model | Recommended Engine | Selection Rationale |
| :--- | :--- | :--- |
| **Llama 3.1 / 3.3 (8B/70B)** | `Two-Pass-NI` | Llama models demonstrate superior reasoning across multi-step prompts. The two-pass approach minimizes hallucination by decoupling discovery from formatting. |
| **Qwen 2.5 (7B/72B)** | `End-Anchored-Null` | Qwen models show high sensitivity to schema placement. Placing the schema at the end of the prompt (End-Anchoring) maximizes schema adherence and reduces "context drift" in technical extractions. |
| **Fallback (Any)** | `Grounded-Null` | Used when latency is a priority. Provides a robust baseline with grounding checks without the overhead of multiple passes. |

### Selection Logic Pseudocode:

```python
def select_engine(model_id: str, complexity: str) -> IExtractionEngine:
    if "qwen" in model_id.lower():
        return EndAnchoredNullEngine(model_id)
    elif "llama" in model_id.lower():
        if complexity == "high":
            return TwoPassNIEngine(model_id)
        return GroundedNullEngine(model_id)
    return GroundedNullEngine(model_id)
```

## 3. Consistent Application of the "Null Rule"

The "Null Rule" (returning `null` for any schema field not present in the text) is the primary defense against hallucination. To ensure consistency, we use a Mixin-based approach and a post-extraction Auditor.

### 3.1 The Invariant Prompt Mixin

Every engine uses a common component to inject the Null Rule into the system prompt.

```python
class InvariantPromptMixin:
    NULL_RULE_INSTRUCTION = (
        "INVARIANT: If the information required by a field is NOT explicitly "
        "present in the provided text, you MUST return 'null' for that field. "
        "DO NOT use your internal knowledge to fill in missing data."
    )

    def apply_invariants(self, system_prompt: str) -> str:
        return f"{system_prompt}\n\n{self.NULL_RULE_INSTRUCTION}"
```

### 3.2 Post-Extraction Auditor

To catch "soft hallucinations" (where the model generates a plausible but ungrounded value), an `Auditor` agent or validator checks the engine's output.

1.  **Strict Schema Validation**: Ensures the output is valid JSON and matches the schema.
2.  **Grounding Check**: For every non-null value, the Auditor verifies if the value (or a close semantic match) exists in the source text.
3.  **Null Enforcement**: If a value fails the grounding check, it is automatically converted to `null`.

## 4. Architecture Diagram (Conceptual)

```
[Source Text + Schema]
      |
      v
[Engine Selector]  <-- (Model ID: Qwen/Llama)
      |
      +-----> [Grounded-Null Engine]
      +-----> [End-Anchored-Null Engine]
      +-----> [Two-Pass-NI Engine]
      |
      v
[Invariant Mixin]  <-- (Apply Null Rule)
      |
      v
[Extraction Result]
      |
      v
[Auditor / Validator] --> [Final JSON]
```
