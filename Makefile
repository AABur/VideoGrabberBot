.PHONY: help run tests test check format lint mypy
.DEFAULT_GOAL := help

# Default Python command using uv
PY := uv run python
PYTEST := uv run pytest
MYPY := uv run mypy
RUFF := uv run ruff

# Help command
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

# Run the bot
run: ## Run the bot
	$(PY) run.py

# Run all tests with coverage
tests: ## Run all tests with coverage and generate HTML report
	$(PYTEST) --cov=bot --cov-report=term-missing --cov-report=html

# Run a specific test (usage: make test test_file.py::test_function)
test: ## Run specific test with coverage report (e.g., make test test_config.py or test_config.py::test_function)
	@if [ -z "$(filter-out test,$@)" ]; then \
		echo "Usage: make test <test_file.py::test_function_name>"; \
	else \
		$(PYTEST) tests/$(filter-out test,$@) --cov=bot --cov-report=term-missing --cov-report=html; \
	fi

# Format code
format: ## Format code with ruff
	$(RUFF) format .

# Lint code
lint: ## Lint code with ruff
	$(RUFF) check .

# Type check
mypy: ## Run type checking with mypy
	$(MYPY) .

# Run all checks (format, lint, type check)
check: format lint mypy ## Run all checks (format, lint, type check)