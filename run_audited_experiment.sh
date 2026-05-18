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

# Run evaluation for gated-stable-champion
echo "Evaluating pipeline: gated-stable-champion..."
uv run gensie eval2 \
    --data "$DATASET" \
    --url "$URL" \
    --pipeline "gated-stable-champion" \
    --model "$MODEL" \
    --output "$OUTPUT_DIR/gated_stable_champion_report.json"

# Run evaluation for audited-synthetic
echo "Evaluating pipeline: audited-synthetic..."
uv run gensie eval2 \
    --data "$DATASET" \
    --url "$URL" \
    --pipeline "audited-synthetic" \
    --model "$MODEL" \
    --output "$OUTPUT_DIR/audited_synthetic_report.json"

echo "------------------------------------------------"
echo "Experiment complete. Reports saved to $OUTPUT_DIR"

# Verification
if [ -f "$OUTPUT_DIR/gated_stable_champion_report.json" ] && [ -f "$OUTPUT_DIR/audited_synthetic_report.json" ]; then
    echo "Verification SUCCESS: Both result files created."
else
    echo "Verification FAILURE: One or more result files missing."
    exit 1
fi
