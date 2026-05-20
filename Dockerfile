# GenSIE 2026 Submission Dockerfile
# Optimized for CPU-only, isolated environment (No Internet)

# Use a lightweight Python base
FROM python:3.13-slim

# Set environment variables for isolation and performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PARTICIPANT_PATH="gensie.baseline.OfficialParticipant" \
    # Challenge mandatory connection variables
    OPENAI_BASE_URL="" \
    OPENAI_API_KEY="sk-dummy"

# Install uv for efficient dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# 1. Install dependencies first (leverage Docker caching)
# Note: We exclude dev dependencies for a smaller footprint
COPY pyproject.toml uv.lock README.md ./
RUN uv pip install --system --no-cache .

# 2. Pre-download lightweight embedding models for offline use
# The challenge environment has NO internet access.
RUN python3 -c "from fastembed import TextEmbedding; \
    cache_dir = '/app/models'; \
    TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir=cache_dir); \
    print('Embedding model pre-cached successfully.')"

# 3. Copy the full project source
COPY . .

# 4. Final configuration
EXPOSE 8000

# Entrypoint must start the FastAPI server as per GenSIE spec
# Using --host 0.0.0.0 is mandatory for container networking
ENTRYPOINT ["gensie", "serve", "--host", "0.0.0.0", "--port", "8000"]
