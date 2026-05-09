#!/bin/bash
set -e

# Qwen Two-Pass
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-ni --model qwen/qwen3-1.7b --output results/qwen_two_pass_ni.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-ts --model qwen/qwen3-1.7b --output results/qwen_two_pass_ts.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-null --model qwen/qwen3-1.7b --output results/qwen_two_pass_null.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-dialect --model qwen/qwen3-1.7b --output results/qwen_two_pass_dialect.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass --model qwen/qwen3-1.7b --output results/qwen_two_pass_full.json

# Llama 3.2 3B - Grounded
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline grounded-ni --model llama-3.2-3b-instruct --output results/llama_grounded_ni.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline grounded-ts --model llama-3.2-3b-instruct --output results/llama_grounded_ts.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline grounded-null --model llama-3.2-3b-instruct --output results/llama_grounded_null.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline grounded-dialect --model llama-3.2-3b-instruct --output results/llama_grounded_dialect.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline grounded --model llama-3.2-3b-instruct --output results/llama_grounded_full.json

# Llama 3.2 3B - Auditor
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline auditor-ni --model llama-3.2-3b-instruct --output results/llama_auditor_ni.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline auditor-ts --model llama-3.2-3b-instruct --output results/llama_auditor_ts.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline auditor-null --model llama-3.2-3b-instruct --output results/llama_auditor_null.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline auditor-dialect --model llama-3.2-3b-instruct --output results/llama_auditor_dialect.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline auditor --model llama-3.2-3b-instruct --output results/llama_auditor_full.json

# Llama 3.2 3B - End-Anchored
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline end-anchored-ni --model llama-3.2-3b-instruct --output results/llama_end_anchored_ni.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline end-anchored-ts --model llama-3.2-3b-instruct --output results/llama_end_anchored_ts.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline end-anchored-null --model llama-3.2-3b-instruct --output results/llama_end_anchored_null.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline end-anchored-dialect --model llama-3.2-3b-instruct --output results/llama_end_anchored_dialect.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline end-anchored --model llama-3.2-3b-instruct --output results/llama_end_anchored_full.json

# Llama 3.2 3B - Two-Pass
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-ni --model llama-3.2-3b-instruct --output results/llama_two_pass_ni.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-ts --model llama-3.2-3b-instruct --output results/llama_two_pass_ts.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-null --model llama-3.2-3b-instruct --output results/llama_two_pass_null.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass-dialect --model llama-3.2-3b-instruct --output results/llama_two_pass_dialect.json
uv run python -m gensie.cli eval2 --data data/starter/ --pipeline two-pass --model llama-3.2-3b-instruct --output results/llama_two_pass_full.json

echo "ALL EVALUATIONS COMPLETE"
