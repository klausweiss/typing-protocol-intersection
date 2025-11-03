.PHONY: help
help:
	@echo "Available targets:"
	@echo "  install       - Install package and dependencies"
	@echo "  test          - Run tests with coverage"
	@echo "  lint          - Run all linters (mypy, ruff check, ruff format --check, pylint)"
	@echo "  format        - Format code with ruff"
	@echo "  all           - Run lint and test"
	@echo "  clean         - Remove build artifacts and cache files"

.PHONY: install
install:
	uv sync --all-extras --dev

.PHONY: test
test:
	uv run pytest -vv --cov=typing_protocol_intersection

.PHONY: lint
lint:
	uv run mypy typing_protocol_intersection
	uv run ruff check .
	uv run ruff format --check .
	uv run pylint typing_protocol_intersection tests

.PHONY: format
format:
	uv run ruff format .

.PHONY: all
all: lint test

.PHONY: clean
clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
