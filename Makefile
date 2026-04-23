.PHONY: test lint

# Run tests using pytest
test:
	pytest tests/ -v

# Run ruff linter
lint:
	ruff check src/ tests/
