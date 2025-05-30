.PHONY: help run tests test check format lint lint-all mypy docker-build docker-run docker-stop docker-logs docker-status docker-clean docker-restart
.DEFAULT_GOAL := help

# Default Python command using uv
PY := uv run python
PYTEST := uv run pytest
MYPY := uv run mypy
RUFF := uv run ruff
FLAKE8 := uv run flake8

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

# Lint code with ruff
lint: ## Lint code with ruff
	$(RUFF) check .

# Lint code with wemake-python-styleguide
lint-wps: ## Lint code with wemake-python-styleguide
	$(FLAKE8) . --select=WPS

# Lint code with all linters
lint-all: format lint lint-wps ## Run all linting (format, ruff lint, wemake-python-styleguide)
	@echo "All linting completed"

# Type check
mypy: ## Run type checking with mypy
	$(MYPY) .

# Run all checks (format, lint, type check)
check: format lint mypy ## Run all checks (format, lint, type check)

# Docker targets
docker-build: ## Build Docker image
	docker build -t videograbberbot .

docker-run: ## Run bot in Docker container (detached) with volume and env
	docker run -d --name videograbberbot --env-file .env -v $(shell pwd)/data:/app/data videograbberbot

docker-stop: ## Stop and remove Docker container
	docker stop videograbberbot || true
	docker rm videograbberbot || true

docker-logs: ## Show Docker container logs
	docker logs -f videograbberbot

docker-status: ## Show Docker images and containers status
	@echo "=== Docker Images ==="
	@docker images | grep -E "(REPOSITORY|videograbberbot)" || echo "No videograbberbot images found"
	@echo ""
	@echo "=== Running Containers ==="
	@docker ps | grep -E "(CONTAINER|videograbberbot)" || echo "No videograbberbot containers running"

docker-clean: docker-stop ## Stop container and remove image
	docker rmi videograbberbot || true

docker-restart: docker-stop docker-build docker-run ## Full restart (stop, build, run)