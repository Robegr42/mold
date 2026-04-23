# OpenCode Sandbox - M.O.L.D. Project
# Custom environment for M.O.L.D. project

FROM ubuntu:24.04

# ============================================================
# System tools and utilities
# ============================================================
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    bash \
    bash-completion \
    coreutils \
    findutils \
    grep \
    sed \
    awk \
    vim \
    less \
    man-db \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Python 3.13
# ============================================================
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && apt-get install -y \
    python3.13 \
    python3.13-venv \
    python3.13-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ============================================================
# uv - Package manager
# ============================================================
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# ============================================================
# Project workspace
# ============================================================

# Make sure you copy this section VERBATIM.
# This is necessary for the sandbox.sh command to work.

WORKDIR /project

# Default shell
SHELL ["/bin/bash", "-c"]

# Default command
CMD ["/bin/bash"]