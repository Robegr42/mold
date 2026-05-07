# Proposal: The Sequential List Processor

## 1. Overview
Small Language Models (SLMs) under 14B parameters often suffer from "list exhaustion" or "premature stopping" when asked to extract a long list of items from a large text in a single pass. The **Sequential List Processor** (SLP) addresses this by decomposing the extraction task into a multi-turn, stateful loop. Instead of asking "Find all items," the system asks "Find the next item," maintaining a record of previous extractions to guide the model through the text.

## 2. Architecture
The SLP consists of a controller loop (Python-side) and a specific iterative prompt.

### 2.1 Component Diagram
1. **Input Handler**: Receives the raw text and the target schema.
2. **State Manager**: Maintains the list of `extracted_items`.
3. **Iterative Prompt Generator**: Constructs the prompt for each turn, including the text and the current `extracted_items`.
4. **SLM (Inference)**: Processes the prompt and returns a single item or a termination sentinel.
5. **Validator & Parser**: Parses the JSON output and checks for the termination sentinel.
6. **Deduplicator**: Ensures the model doesn't get stuck in a loop by comparing the new item against the state.

## 3. The Incremental Next Item Loop

### 3.1 Logic Flow
1. **Initialize**: `extracted_items = []`, `finished = False`.
2. **While `not finished`**:
    a. Construct a prompt containing the source text and `extracted_items`.
    b. Call SLM.
    c. Parse output.
    d. If output matches `[DONE]`:
        - Set `finished = True`.
    e. Else if output is a valid JSON object:
        - Add to `extracted_items`.
        - Optional: Update a "context window" if the text is extremely long (moving pointer).
    f. Safety Check: If `len(extracted_items)` exceeds a hard limit or the model repeats an item N times, break (avoid infinite loops).

## 4. Prompt Templates

### 4.1 System Prompt
```markdown
You are a precision extraction assistant. Your task is to extract exactly ONE item from the provided text based on the user's schema.

Rules:
1. Extract the NEXT item that has not been extracted yet.
2. If there are no more items to extract, you MUST output the termination sentinel: [DONE].
3. Output only the JSON object for the item or the sentinel. Do not provide conversational filler.
4. Accuracy is paramount. Do not hallucinate items.
```

### 4.2 Iterative User Prompt
```markdown
### Source Text
{{ source_text }}

### Items Already Extracted
{{ extracted_items_json }}

### Instruction
Based on the Source Text, identify the next item that fits the following schema:
{{ schema }}

If no more items exist, output "[DONE]". Otherwise, output the JSON for the next item.

### Output
```

## 5. Termination Sentinels
To ensure reliable loop control with SLMs, the sentinel must be:
1. **Distinct**: `[DONE]` or `###END###` are unlikely to appear naturally in JSON or the source text.
2. **Top-Level**: The model should output the sentinel as its entire response to simplify parsing.
3. **Instruction-Reinforced**: The system prompt and user prompt both define the sentinel clearly.

## 6. State-Aware Extractions
To prevent the model from re-extracting the same item (a common SLM failure mode), the "State-Aware" mechanism uses two strategies:

### 6.1 Negative Constraints (In-Prompt State)
By including `{{ extracted_items_json }}` in the prompt, we provide the model with a "negative list." This serves as a "Do Not Extract These" list.

### 6.2 Deduplication Logic (Controller-Side)
The controller maintains a hash set of extracted items (normalized). If the model returns an item that is already in the set, the controller can:
1. Re-prompt with a "Wait, you already found that, look further in the text" instruction.
2. Terminate the loop if it happens repeatedly (indicating the model is stuck).

## 7. SLM-Specific Optimizations (< 14B)
- **Constraint Handling**: SLMs often ignore negative constraints if the list gets too long. If `extracted_items` grows large, summarize them or only show the last 5-10 to keep the prompt focused while maintaining the "Where was I?" context.
- **Logit Bias (Advanced)**: If the model is prone to rambling, one can apply logit bias to the first token to favor `{` (for JSON) or `[` (for the sentinel).
- **One-at-a-time**: Forcing the model to focus on a single object significantly reduces hallucination and field-mixing compared to "Extract all as a JSON list."

## 8. Implementation Example (Pseudo-code)

```python
def sequential_extraction(text, schema):
    extracted_items = []
    seen_hashes = set()
    
    while len(extracted_items) < MAX_ITEMS:
        prompt = build_prompt(text, schema, extracted_items)
        response = call_slm(prompt).strip()
        
        if response == "[DONE]":
            break
            
        try:
            item = json.loads(response)
            item_hash = hash_item(item)
            
            if item_hash in seen_hashes:
                # Handle repetition: skip or break
                break 
                
            extracted_items.append(item)
            seen_hashes.add(item_hash)
        except JSONDecodeError:
            # Handle parsing error
            continue
            
    return extracted_items
```
