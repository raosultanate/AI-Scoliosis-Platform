PYTHON ?= python3
VENV_PYTHON := .venv/bin/python

.PHONY: install test lint typecheck verify fixture demo

install:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e '.[dev]'

test:
	$(VENV_PYTHON) -m pytest -q --cov=src/scoliosis_platform --cov-report=term-missing

lint:
	$(VENV_PYTHON) -m ruff check .

typecheck:
	$(VENV_PYTHON) -m mypy src

verify: test lint typecheck

fixture:
	$(VENV_PYTHON) apps/generate_synthetic_fixture.py

demo: fixture
	.venv/bin/scoliosis-v1a analyze --image tests/fixtures/synthetic_xray.png \
		--landmarks tests/fixtures/synthetic_landmarks.json \
		--output-dir data/outputs/synthetic --config config/v1a.yaml
