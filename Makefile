.PHONY: test lint

# Run tests using pytest
test:
	uv run pytest tests/ -v

# Run ruff linter
lint:
	uv run ruff check src/ tests/
