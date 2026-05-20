#!/bin/bash

# Configuration
DATASET="data/dev"
OUTPUT_ROOT="results/pipelines_in_dev"
PORT=8000
URL="http://localhost:$PORT"

# Define Experiment Matrix
PIPELINES=("two-pass-null" "gated-stable-champion" "audited-synthetic")
MODELS=("llama-3.2-3b-instruct" "qwen/qwen3-1.7b" "qwen/qwen3-14b")

# Ensure root output directory exists
mkdir -p "$OUTPUT_ROOT"

# Cleanup function to kill the server
cleanup() {
    if [ -n "$SERVER_PID" ]; then
        echo "Stopping GenSIE Agent Server (PID: $SERVER_PID)..."
        kill "$SERVER_PID" 2>/dev/null
        wait "$SERVER_PID" 2>/dev/null
    fi
}

# Trap exit signals
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

# Run Experiment Matrix
for model in "${MODELS[@]}"; do
    # Create safe filename from model string
    model_name=$(echo "$model" | tr '/' '_')
    
    for pipeline in "${PIPELINES[@]}"; do
        output_file="$OUTPUT_ROOT/${model_name}_${pipeline}.json"

        if [ -f "$output_file" ]; then
            echo "Skipping $model | $pipeline (Result already exists at $output_file)"
            echo
            continue
        fi

        echo "================================================================"
        echo "RUNNING: Model: $model | Pipeline: $pipeline"
        echo "================================================================"
        
        uv run gensie eval2 \
            --data "$DATASET" \
            --url "$URL" \
            --pipeline "$pipeline" \
            --model "$model" \
            --output "$output_file"
            
        echo "Done! Result saved to $output_file"
        echo
    done
done

echo "------------------------------------------------"
echo "All experiments complete. Reports saved to $OUTPUT_ROOT"
