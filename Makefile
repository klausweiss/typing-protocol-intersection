.PHONY: help
help:
	@echo "Available targets:"
	@echo "  install                - Install package and dependencies"
	@echo "  test                   - Run tests with coverage"
	@echo "  test-all               - Run tests across all supported Python versions"
	@echo "  test-version           - Run tests with specific Python and mypy versions"
	@echo "                           Usage: make test-version PYTHON=3.10 MYPY=0.920"
	@echo "                           MYPY is optional (defaults to latest)"
	@echo "  lint                   - Run all linters (mypy, ruff check, ruff format --check, pylint)"
	@echo "  format                 - Format code with ruff"
	@echo "  all                    - Run lint and test"
	@echo "  clean                  - Remove build artifacts and cache files"

.PHONY: install
install:
	uv sync --all-extras --dev

.PHONY: test
test:
	uv run pytest -vv --cov=typing_protocol_intersection

# Run tests with a specific Python and optionally mypy version
# Usage: make test-version PYTHON=3.10 [MYPY=0.920]
# The MYPY parameter is optional and defaults to the latest version
.PHONY: test-version
test-version:
	@if [ -z "$(PYTHON)" ]; then \
		echo "Error: PYTHON version must be specified. Usage: make test-version PYTHON=3.10 [MYPY=0.920]"; \
		exit 1; \
	fi
	@if [ -n "$(MYPY)" ]; then \
		echo "Running tests on Python $(PYTHON) with mypy==$(MYPY)..."; \
		uv run --python $(PYTHON) --with mypy==$(MYPY) pytest -vv --cov=typing_protocol_intersection; \
	else \
		echo "Running tests on Python $(PYTHON) with latest mypy..."; \
		uv run --python $(PYTHON) pytest -vv --cov=typing_protocol_intersection; \
	fi

# Run tests across all supported Python versions (3.10-3.14) with both
# the oldest supported mypy version (0.920) and the latest version
.PHONY: test-all
test-all:
	@$(MAKE) test-version PYTHON=3.10 MYPY=0.920
	@$(MAKE) test-version PYTHON=3.10
	@$(MAKE) test-version PYTHON=3.11 MYPY=0.920
	@$(MAKE) test-version PYTHON=3.11
	@$(MAKE) test-version PYTHON=3.12 MYPY=0.920
	@$(MAKE) test-version PYTHON=3.12
	@$(MAKE) test-version PYTHON=3.13 MYPY=0.920
	@$(MAKE) test-version PYTHON=3.13
	@$(MAKE) test-version PYTHON=3.14 MYPY=0.920
	@$(MAKE) test-version PYTHON=3.14

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
