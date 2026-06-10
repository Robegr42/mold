# GenSIE 2026 Submission Dockerfile
# Optimized for CPU-only, isolated environment (No Internet)

# Use a lightweight Python base
FROM python:3.13-slim

# Set environment variables for isolation and performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PARTICIPANT_PATH="gensie.baseline.OfficialParticipant" \
    OPENAI_BASE_URL="" \
    OPENAI_API_KEY="sk-dummy"

# Install uv for efficient dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# 1. Install dependencies first (for better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 2. Pre-download lightweight embedding models for offline use
# The challenge environment has NO internet access.
# We ensure the cache is in a known location and accessible.
ENV FASTEMBED_CACHE_PATH="/app/models"
RUN python3 -c "from fastembed import TextEmbedding; \
    TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir='$FASTEMBED_CACHE_PATH'); \
    print('Embedding model pre-cached successfully.')"

# 3. Copy source code and install the project
COPY . .
RUN uv sync --frozen --no-dev

# 4. Final configuration
EXPOSE 8000

# Use the absolute path to the installed script to avoid runtime resolution
# 'uv sync' installs the project and its scripts into the environment.
ENTRYPOINT ["gensie", "serve", "--host", "0.0.0.0", "--port", "8000"]
