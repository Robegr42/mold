# Advanced Semantic Mapping for Rigid Types in SLMs (< 14B)

This report outlines state-of-the-art (SOTA) approaches for semantic mapping in Small Language Models (SLMs) specifically for structured extraction tasks in a Spanish linguistic context. It adheres to GenSIE constraints: zero-shot schemas, inference-time techniques only, and focus on SLMs.

## 1. In-Context Dialectal Synonym Mapping in Schemas

For SLMs, the schema is not just a data structure; it is a **dense instruction set**. Embedding dialectal variations directly into Pydantic or TypeScript descriptions allows the model to "bridge" regional input to a rigid output without a separate training phase.

### Pydantic Implementation Patterns
Using the `description` field in Pydantic v2 to provide "soft" mapping hints.

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class DeviceType(str, Enum):
    COMPUTER = "COMPUTER"
    MOBILE = "MOBILE"
    CAR = "CAR"

class TechnicalExtraction(BaseModel):
    device_category: DeviceType = Field(
        ...,
        description=(
            "Categoría del dispositivo. Mapear 'ordenador' (España) o 'computadora' (LatAm) a COMPUTER. "
            "Mapear 'móvil' (España) o 'celular' (LatAm) a MOBILE. "
            "Mapear 'coche' (España) o 'carro/auto' (LatAm) a CAR."
        )
    )
```

### TypeScript/JSON Schema Patterns
In TypeScript, JSDoc comments or `description` properties in JSON Schema serve the same purpose.

```typescript
interface ExtractionSchema {
  /**
   * Mapear términos regionales de salud:
   * 'inmunitario/defensas' -> AUTOIMMUNE (si el contexto es patológico)
   * 'azúcar en sangre' -> DIABETES_RELATED
   */
  medical_category: "AUTOIMMUNE" | "DIABETES_RELATED" | "GENERAL";
}
```

### Best Practices for SLMs
- **Brevity**: SLMs have limited context windows for high-attention tokens. List synonyms in a concise `Input1/Input2 -> TARGET` format.
- **Dialect Clustering**: Instead of listing every country, cluster by major dialect zones: **Peninsular** (Spain), **Rioplatense** (Arg/Ury), **Mexican/Central**, and **Andean**.
- **Negative Hints**: Explicitly warn against "false friends" (e.g., "No confundir 'coger' (España: tomar) con el uso vulgar en LatAm").

---

## 2. Post-Processing vs. In-Prompt Constraints

There is a fundamental trade-off between **Early-Binding** (forcing a choice during generation) and **Late-Binding** (mapping after generation).

### Early-Binding: Forced Enum Selection (SOTA for SLMs)
Using constrained decoding libraries (e.g., **Outlines**, **vLLM**, **Guidance**) to mask logits.

- **Mechanism**: The model is physically unable to output a token that isn't a valid Enum member.
- **Pros**: 100% schema validity; no "hallucinated" synonyms.
- **Cons**: Can "choke" the model's reasoning. If the model wants to say "ordenador" but is forced to pick `COMPUTER`, the lack of "thinking space" can lead to incorrect selections in complex cases.

### Late-Binding: Free-Text "Pre-selection" + Mapping
A "Two-Pass" or "Shadow Category" approach.

1. **Pass 1 (Extraction)**: The model extracts the raw regional term (e.g., "la guagua").
2. **Pass 2 (Mapping)**: A lightweight script (fuzzy matching) or a second SLM call maps "guagua" to `BUS`.

**Effectiveness Comparison for SLMs (< 14B):**
| Technique | Reliability | Latency | Reasoning Quality |
| :--- | :--- | :--- | :--- |
| **In-Prompt Enum** | Medium | Low | Low |
| **Constrained Decoding** | **High** | **Lowest** | Medium |
| **Two-Pass (Late)** | High | High | **High** |

**GenSIE Recommendation**: Use **Constrained Decoding with Chain-of-Thought (CoT)**. Allow the model to "reason" in Spanish before the rigid JSON block.

```markdown
User: El paciente presenta fallos en el sistema inmunitario.
Model: 
Pensamiento: El término 'sistema inmunitario' se refiere a la respuesta biológica de defensa. En el esquema rígido, esto corresponde a la categoría AUTOIMMUNE.
JSON: {"category": "AUTOIMMUNE"}
```

---

## 3. "Hint-Injecting" vs. "Constraint-Only" Prompting

SLMs often fail with "Negative Constraints" (e.g., "Don't use X"). They perform significantly better with **Positive Lexical Hints**.

### Hint-Injecting (The "Anchor" Pattern)
Injecting a small lexical glossary directly into the system prompt or immediately before the task.

**Best Practices for Spanish Regionalisms:**
- **XML Hint Blocks**: Use `<hints>` tags to isolate lexical anchors.
  ```xml
  <lexicon_mapping>
    Standard: "autobús" -> Regional: ["camión", "guagua", "colectivo", "micro"]
    Standard: "trabajo" -> Regional: ["chamba", "pega", "laburo"]
  </lexicon_mapping>
  ```
- **Property-Level Hints**: Instead of one giant glossary, inject hints specific to the field being extracted. This minimizes "distraction" for the SLM's attention mechanism.

### Constraint-Only (The "Strict" Pattern)
Simply stating "You must only use the values in the Enum."
- **Failure Mode**: SLMs often "drift" and return "Ordenador" even if told to return `COMPUTER` because the Spanish token "Ordenador" has much higher probability in their latent space after seeing a Spanish input.

### Comparison: Hint vs. Constraint
- **Constraint-Only**: "Select from [AUTOIMMUNE, INFECTIOUS]." -> *SLM Result: "inmunitario" (Fails).*
- **Hint-Injected**: "Note: 'inmunitario' and 'defensas' map to AUTOIMMUNE. Select from [AUTOIMMUNE, INFECTIOUS]." -> *SLM Result: "AUTOIMMUNE" (Success).*

## Summary of SOTA Strategy for GenSIE
1. **Schema**: Use Pydantic with inline Spanish synonym mappings in the `description`.
2. **Prompting**: Use **Hint-Injection** via an XML-tagged lexicon mapping.
3. **Inference**: Use **Constrained Decoding** (Logit Masking) to ensure 100% rigid type adherence.
4. **Architecture**: Implement a **Reasoning-First** prompt where the SLM explains the dialectal mapping in natural Spanish *before* outputting the constrained JSON.
