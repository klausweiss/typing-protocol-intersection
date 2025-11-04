.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install package and dependencies
	uv sync --all-extras --dev

.PHONY: build
build: ## Build the package (wheel and sdist)
	uv build

.PHONY: upload
upload: ## Upload package to PyPI repository (REPO=testpypi or pypi, default: testpypi)
	@if [ -z "$(REPO)" ]; then \
		echo "Uploading to testpypi (default)..."; \
		uv run twine upload dist/* -r testpypi; \
	elif [ "$(REPO)" = "pypi" ]; then \
		echo "Uploading to production PyPI..."; \
		uv run twine upload dist/*; \
	elif [ "$(REPO)" = "testpypi" ]; then \
		echo "Uploading to testpypi..."; \
		uv run twine upload dist/* -r testpypi; \
	else \
		echo "Error: Invalid REPO value. Use 'pypi' or 'testpypi'"; \
		exit 1; \
	fi

.PHONY: check-build
check-build: ## Check the built package for common issues
	uv run twine check dist/*

.PHONY: test
test: ## Run tests with coverage
	uv run pytest -vv --cov=typing_protocol_intersection

.PHONY: test-version
test-version: ## Run tests with specific Python and mypy versions (PYTHON=3.10 [MYPY=1.5.0])
	@if [ -z "$(PYTHON)" ]; then \
		echo "Error: PYTHON version must be specified. Usage: make test-version PYTHON=3.10 [MYPY=1.5.0]"; \
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
test-all: ## Run tests across all supported Python versions with mypy 1.5.0 and latest
	@$(MAKE) test-version PYTHON=3.10 MYPY=1.5.0
	@$(MAKE) test-version PYTHON=3.10
	@$(MAKE) test-version PYTHON=3.11 MYPY=1.5.0
	@$(MAKE) test-version PYTHON=3.11
	@$(MAKE) test-version PYTHON=3.12 MYPY=1.5.0
	@$(MAKE) test-version PYTHON=3.12
	@$(MAKE) test-version PYTHON=3.13 MYPY=1.5.0
	@$(MAKE) test-version PYTHON=3.13
	@$(MAKE) test-version PYTHON=3.14 MYPY=1.5.0
	@$(MAKE) test-version PYTHON=3.14
	@$(MAKE) test-version PYTHON=3.14t MYPY=1.5.0
	@$(MAKE) test-version PYTHON=3.14t

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

.PHONY: bump-mypy
bump-mypy: ## Prepare PR for new mypy version (fetches latest or use VERSION=x.y.z)
	@if [ -n "$(VERSION)" ]; then \
		./tools/prepare-pr-after-mypy-bump.sh $(VERSION); \
	else \
		./tools/prepare-pr-after-mypy-bump.sh; \
	fi
