.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install package and dependencies
	uv sync --all-extras --dev

.PHONY: test
test: ## Run tests with coverage
	uv run pytest -vv --cov=typing_protocol_intersection

.PHONY: test-version
test-version: ## Run tests with specific Python and mypy versions (PYTHON=3.10 [MYPY=0.920])
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

.PHONY: test-all
test-all: ## Run tests across all supported Python versions with mypy 0.920 and latest
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
lint: ## Run all linters (mypy, ruff check, ruff format --check, pylint)
	uv run mypy typing_protocol_intersection
	uv run ruff check .
	uv run ruff format --check .
	uv run pylint typing_protocol_intersection tests

.PHONY: format
format: ## Format code with ruff
	uv run ruff format .

.PHONY: all
all: lint test ## Run lint and test

.PHONY: clean
clean: ## Remove build artifacts, cache files, and compiled Python files
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
