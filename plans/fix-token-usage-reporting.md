# Plan: Fix Token Usage Reporting for MIRA, ARCANE, and VIGIL Pipelines

## Objective
Enable accurate token usage reporting for `MIRAAgent`, `ARCANEAgent`, and `VIGILAgent` by correctly integrating the `UsageTracker` into their `run()` methods. This ensures that the `X-GenSIE-Token-Usage` header is correctly populated by the server, satisfying the GenSIE 2026 reporting recommendations and allowing the `eval` command to display token statistics.

## Architectural Impact
- **Consistency:** Aligns the reporting mechanism of all advanced agents with the `BasicAgent` and the official GenSIE specification.
- **Accuracy:** Captures all LLM calls made during a task, including multi-pass reasoning, retries, and auxiliary calls from the `ArchitectModule` (synthesis and hints).
- **Transparency:** Provides the evaluator with a complete tally of tokens via the standard response header.

## File Operations

### Modified Files:
- `src/gensie/baseline.py`:
    - Update `ArchitectModule` methods to accept an optional `UsageTracker`.
    - Update `MIRAAgent.run()`, `ARCANEAgent.run()`, and `VIGILAgent.run()` to use `self.usage`.

## Step-by-Step Execution

### Step 1: Update `ArchitectModule` in `src/gensie/baseline.py`
Modify `ArchitectModule` to ensure that any LLM calls it makes are attributed to the agent's current task usage.

1.  **Update `get_reasoning_hints`**: Add an optional `usage: Optional[UsageTracker] = None` parameter and call `usage.add(response.usage)` after the completion call.
2.  **Update `synthesize_example`**: Add an optional `usage: Optional[UsageTracker] = None` parameter. Call `usage.add(response.usage)` after both the initial synthesis call and the self-correction pass call.

### Step 2: Update `MIRAAgent.run` in `src/gensie/baseline.py`
1.  Initialize by calling `self.usage.reset()`.
2.  Replace the local `total_tokens` variable with calls to `self.usage.add(getattr(response, "usage", None))` after every `self.client.chat.completions.create` call (Pass 1, Pass 2, and Fallback Pass).
3.  Update the `result["_tokens"]` assignment to use `self.usage.snapshot()["total_tokens"]` for internal consistency.
4.  Ensure error responses also include the `_tokens` field if applicable.

### Step 3: Update `ARCANEAgent.run` in `src/gensie/baseline.py`
1.  Initialize by calling `self.usage.reset()`.
2.  Pass `self.usage` as an argument to `self.architect.synthesize_example(task, model, usage=self.usage)`.
3.  Replace the local `total_tokens` variable with calls to `self.usage.add(getattr(response, "usage", None))` after each completion call.
4.  Update `result["_tokens"]` to use `self.usage.snapshot()["total_tokens"]`.

### Step 4: Update `VIGILAgent.run` in `src/gensie/baseline.py`
1.  Initialize by calling `self.usage.reset()`.
2.  Pass `self.usage` as an argument to `self.architect.get_reasoning_hints(..., usage=self.usage)`.
3.  Replace the local `total_tokens` variable with calls to `self.usage.add(getattr(response, "usage", None))` after each completion call.
4.  Update `result["_tokens"]` to use `self.usage.snapshot()["total_tokens"]`.

### Step 5: Address the `_tokens` Field
- **Recommendation:** Keep the `_tokens` field in the response dictionary for now to maintain backward compatibility with any direct callers and existing tests (like `test_two_pass_agent.py`), but update its value to be the aggregate from `self.usage`.
- **Note:** The `eval` command and official leaderboard prioritize the `X-GenSIE-Token-Usage` header, so the header fix is the primary goal.

## Testing Strategy

### 1. Unit Testing
Run existing tests to ensure no regressions in agent logic or JSON structure:
```bash
pytest tests/test_two_pass_agent.py
pytest tests/test_audited_synthetic_agent.py
```

### 2. Manual Verification (Mock Server Call)
Verify that the `X-GenSIE-Token-Usage` header is present and correct when running the server:
1.  Start the agent server: `gensie serve`
2.  Call the `mira` pipeline using `curl` or a Python script and inspect headers:
    ```bash
    curl -i -X POST "http://localhost:8000/run?pipeline=mira&model=gpt-4o-mini" \
         -H "Content-Type: application/json" \
         -d '{"id": "test", "instruction": "Extract name", "input_text": "My name is Juan", "target_schema": {"type": "object", "properties": {"name": {"type": "string"}}}}'
    ```
3.  Confirm the presence of `X-GenSIE-Token-Usage` in the output headers.

### 3. End-to-End Evaluation
Run the `eval` command and verify that the "Tokens" column and "Token usage" summary table are populated:
```bash
gensie eval --data data/starter --model gpt-4o-mini --pipeline mira --limit 5
```
