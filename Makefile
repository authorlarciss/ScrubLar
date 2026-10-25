.PHONY: help install install-pip lock lint lint-imports typecheck format format-check check ci test run evaluate clean

PYTHON := python3
VENV := .venv
PRECOMMIT := $(VENV)/bin/pre-commit
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
LINT_IMPORTS := $(VENV)/bin/lint-imports
MYPY := $(VENV)/bin/mypy

help:
	@echo "Доступные команды:"
	@echo "  make install       — установить зависимости через uv sync (рекомендуется)"
	@echo "  make install-pip   — установить зависимости через venv+pip (fallback)"
	@echo "  make lock          — обновить uv.lock после изменения зависимостей"
	@echo "  make lint          — ruff check"
	@echo "  make lint-imports  — import-linter"
	@echo "  make typecheck     — mypy (strict, nu + tau)"
	@echo "  make format        — ruff format + ruff check --fix"
	@echo "  make format-check  — ruff format --check (без изменений)"
	@echo "  make check         — format-check + lint + lint-imports + test"
	@echo "  make ci            — алиас make check"
	@echo "  make test          — pytest"
	@echo "  make run           — запуск nu.main"
	@echo "  make evaluate      — запуск omega.scripts.evaluate"
	@echo "  make clean         — удалить кэши и venv"

install:
	@command -v uv >/dev/null 2>&1 || (echo "uv not found. Install it or use 'make install-pip'."; exit 1)
	uv sync --extra dev
	$(PRECOMMIT) install

install-pip:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e ".[dev]"
	$(PRECOMMIT) install

lock:
	@command -v uv >/dev/null 2>&1 || (echo "uv not found."; exit 1)
	uv lock

lint:
	$(RUFF) check nu tau

lint-imports:
	$(LINT_IMPORTS)

typecheck:
	$(MYPY) nu tau

format:
	$(RUFF) format nu tau
	$(RUFF) check --fix nu tau

format-check:
	$(RUFF) format --check nu tau

check: format-check lint lint-imports typecheck test

ci: check

test:
	$(PYTEST)

run:
	$(VENV)/bin/python -m nu.main

evaluate:
	PYTHONPATH=. $(VENV)/bin/python omega/scripts/evaluate.py $(ARGS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(VENV)
	rm -rf .import_linter_cache
	rm -rf .coverage htmlcov .mypy_cache
