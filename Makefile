.PHONY: help install install-dev run parse clean format lint typecheck test test-cov build

# Default target
help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation commands
install:  ## Install production dependencies
	uv sync

install-dev:  ## Install all dependencies including dev and test
	uv sync --all-extras

# Runtime commands
run:  ## Run the chatbot
	uv run python main.py

parse:  ## Run data parsing
	uv run python parse_data.py

# Development commands
format:  ## Format code with black
	uv run black .

lint:  ## Run linting with ruff
	uv run ruff check .

lint-fix:  ## Run linting with automatic fixes
	uv run ruff check --fix .

typecheck:  ## Run type checking with mypy
	uv run mypy .

# Testing commands (для будущего использования)
test:  ## Run tests
	uv run pytest

test-cov:  ## Run tests with coverage
	uv run pytest --cov=. --cov-report=term-missing --cov-report=html

# Development workflow
dev-setup:  ## Complete development setup
	uv sync --all-extras
	uv run pre-commit install

check-all:  ## Run all checks (format, lint, typecheck)
	uv run black --check .
	uv run ruff check .
	uv run mypy .

# Cleanup commands
clean:  ## Clean cache and temporary files
	uv cache clean
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache
	rm -rf .ruff_cache

clean-db:  ## Remove database and reparse
	rm -rf data/chatbot.db
	$(MAKE) parse

# Build and distribution
build:  ## Build the package
	uv build

# Update dependencies
update:  ## Update all dependencies
	uv lock --upgrade
	uv sync

# Show project info
info:  ## Show project information
	uv show
	uv tree
