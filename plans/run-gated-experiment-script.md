### Objective
Create a bash script `run_gated_experiment.sh` to compare `GatedStableChampionAgent` and `StableChampionAgent` using the `qwen/qwen3-1.7b` model on the `data/starter` dataset.

### Architectural Impact
- **Automation**: Streamlines the process of starting the agent server, running multiple evaluations, and cleaning up resources.
- **Reproducibility**: Ensures that experiments are conducted under identical conditions (model, dataset, server configuration).
- **Resource Management**: Implements robust process handling to prevent orphaned server instances.

### File Operations
- **New File**: `run_gated_experiment.sh` in the repository root.
- **Output Directory**: `results/gated_vs_stable/` (Automatically created if it doesn't exist).

### Step-by-Step Execution

1.  **Script Infrastructure**: Define environment variables for the model, dataset, and output paths. Implement a `cleanup` function using the `trap` command to ensure the background server process is killed even if the script fails.
2.  **Server Management**: Start the server in the background using `uv run gensie serve`. Implement a polling loop using `curl` to check the `http://localhost:8000/info` endpoint.
3.  **Evaluation Execution**: Execute `uv run gensie eval2` for both `stable-champion` and `gated-stable-champion` pipelines.
4.  **Cleanup & Verification**: Ensure the server process is terminated and verify that JSON reports are generated in the target directory.

### Full Script Content

```bash
#!/bin/bash

# Configuration
MODEL="qwen/qwen3-1.7b"
DATASET="data/starter"
OUTPUT_DIR="results/gated_vs_stable"
PORT=8000
URL="http://localhost:$PORT"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Cleanup function to kill the server
cleanup() {
    if [ -n "$SERVER_PID" ]; then
        echo "Stopping GenSIE Agent Server (PID: $SERVER_PID)..."
        kill "$SERVER_PID" 2>/dev/null
        wait "$SERVER_PID" 2>/dev/null
    fi
}

# Trap exit signals (EXIT, INT, TERM)
trap cleanup EXIT INT TERM

# Start the server in the background
echo "Starting GenSIE Agent Server..."
uv run gensie serve --port $PORT &
SERVER_PID=$!

# Wait for the server to be ready
echo "Waiting for server to be ready at $URL/info..."
MAX_RETRIES=30
RETRY_COUNT=0
until curl -s "$URL/info" > /dev/null; do
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Error: Server failed to start after $MAX_RETRIES retries."
        exit 1
    fi
done
echo "Server is ready!"

# Run evaluation for stable-champion
echo "Evaluating pipeline: stable-champion..."
uv run gensie eval2 \
    --data "$DATASET" \
    --url "$URL" \
    --pipeline "stable-champion" \
    --model "$MODEL" \
    --output "$OUTPUT_DIR/stable_champion_report.json"

# Run evaluation for gated-stable-champion
echo "Evaluating pipeline: gated-stable-champion..."
uv run gensie eval2 \
    --data "$DATASET" \
    --url "$URL" \
    --pipeline "gated-stable-champion" \
    --model "$MODEL" \
    --output "$OUTPUT_DIR/gated_stable_champion_report.json"

echo "------------------------------------------------"
echo "Experiment complete. Reports saved to $OUTPUT_DIR"

# Verification
if [ -f "$OUTPUT_DIR/stable_champion_report.json" ] && [ -f "$OUTPUT_DIR/gated_stable_champion_report.json" ]; then
    echo "Verification SUCCESS: Both result files created."
else
    echo "Verification FAILURE: One or more result files missing."
    exit 1
fi
```

### Testing Strategy
- **Permission Setup**: Run `chmod +x run_gated_experiment.sh`.
- **Execution Monitoring**: Verify the polling phase succeeds and both evaluations complete without errors.
- **Output Inspection**: Confirm that `results/gated_vs_stable/stable_champion_report.json` and `results/gated_vs_stable/gated_stable_champion_report.json` contain valid evaluation metrics.
- **Cleanup Check**: Confirm that no `uvicorn` or `gensie serve` processes remain after the script exits.
