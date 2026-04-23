# Plan: Sandbox Environment Setup

## Context
The project requires a Docker-based sandbox environment to run tools safely and consistently. A custom Dockerfile has been prepared but the build is currently pending due to local environment restrictions/permissions.

## Objectives
1. Build the `mold-sandbox` Docker image.
2. Verify the sandbox using `sandbox.sh`.
3. Install project dependencies within the sandbox.

## Steps
1. **Docker Build**:
   - The user must run the build command manually if permissions persist:
     `sudo docker build -t mold-sandbox -f .opencode/sandbox/mold.dockerfile .opencode/sandbox/`
2. **Verification**:
   - Run a simple command through the wrapper:
     `.opencode/sandbox/sandbox.sh create whoami`
3. **Dependency Installation**:
   - Use `uv` within the sandbox to sync the project environment.
     `.opencode/sandbox/sandbox.sh create uv sync`

## Success Criteria
- `sandbox.sh` no longer shows the "Sandbox is not setup" warning.
- `python3 --version` inside the sandbox returns `3.13.x`.
- `uv` is available in the path.
