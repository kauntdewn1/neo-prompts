# VEO - Modern Video Generation Engine
# Makefile for development and deployment

.PHONY: help install dev-install test clean setup run generate batch config

# Default target
help:
	@echo "🚀 VEO - Modern Video Generation Engine"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install production dependencies"
	@echo "  dev-install  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  clean        Clean up temporary files"
	@echo "  setup        Setup environment and credentials"
	@echo "  run          Run VEO CLI"
	@echo "  generate     Generate video from prompt (example)"
	@echo "  batch        Generate videos from prompts file (example)"
	@echo "  config       Show current configuration"

# Production installation
install:
	pip install -r requirements.txt

# Development installation
dev-install:
	pip install -r requirements.txt
	pip install black isort flake8 mypy pytest pytest-asyncio

# Run tests
test:
	python -m pytest tests/ -v --tb=short

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Setup environment
setup:
	@echo "🔧 Setting up VEO environment..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp env.example .env; \
		echo "⚠️  Please edit .env file with your API keys"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "📦 Installing dependencies..."
	make install
	@echo "✅ Setup complete! Edit .env file and run 'make generate' to test"

# Run VEO CLI
run:
	python main.py --help

# Example: Generate video from prompt
generate:
	python main.py generate "A beautiful sunset over mountains" --aspect 16:9 --duration 8

# Example: Batch generation
batch:
	@echo "Creating example prompts file..."
	@echo "A cat playing with a ball" > prompts.txt
	@echo "A dog running in the park" >> prompts.txt
	@echo "A bird flying over the ocean" >> prompts.txt
	python main.py batch prompts.txt --count 2
	@rm -f prompts.txt

# Show configuration
config:
	python main.py config

# Development helpers
format:
	black veo/ main.py
	isort veo/ main.py

lint:
	flake8 veo/ main.py
	mypy veo/ main.py

# Quick test
quick-test:
	python main.py config

# Prompt management
prompts:
	python scripts/prompt_manager.py list

show-prompt:
	python scripts/prompt_manager.py show $(PROMPT)

create-prompt:
	python scripts/prompt_manager.py create $(NAME) --content "$(CONTENT)"

generate-prompt:
	python scripts/prompt_manager.py generate $(PROMPT)

batch-prompts:
	python scripts/prompt_manager.py batch --category projects