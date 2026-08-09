PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
DOCKER_IMAGE ?= ai-scoliosis-platform:local
DOCKER_PORT ?= 8000

.PHONY: install lock test lint typecheck verify fixture demo api \
	docker-build docker-run docker-up docker-down docker-config docker-smoke

install:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install --require-hashes -r requirements-dev.lock.txt
	$(VENV_PYTHON) -m pip install --no-deps -e .

# Regenerate the hash-pinned lock files after changing pyproject.toml deps.
lock:
	uv pip compile pyproject.toml --python-version 3.12 --generate-hashes \
		-o requirements.lock.txt
	uv pip compile pyproject.toml --extra dev --python-version 3.12 --generate-hashes \
		-o requirements-dev.lock.txt

test:
	$(VENV_PYTHON) -m pytest -q --cov=backend/scoliosis_platform --cov-report=term-missing

lint:
	$(VENV_PYTHON) -m ruff check .

typecheck:
	$(VENV_PYTHON) -m mypy backend

verify: test lint typecheck

fixture:
	$(VENV_PYTHON) apps/generate_synthetic_fixture.py

demo: fixture
	.venv/bin/scoliosis-v1a analyze --image tests/fixtures/synthetic_xray.png \
		--landmarks tests/fixtures/synthetic_landmarks.json \
		--output-dir data/outputs/synthetic --config config/v1a.yaml

api:
	$(VENV_PYTHON) -m uvicorn scoliosis_platform.api:app --reload

docker-build:
	docker build --tag $(DOCKER_IMAGE) .

docker-run:
	docker run --rm --init \
		--publish $(DOCKER_PORT):8000 \
		--read-only \
		--tmpfs /tmp:rw,noexec,nosuid,size=64m \
		--cap-drop ALL \
		--security-opt no-new-privileges \
		--mount type=volume,src=ai-scoliosis-artifacts,dst=/app/data/outputs/api \
		$(DOCKER_IMAGE)

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-config:
	docker compose config --quiet

docker-smoke:
	curl --fail --silent http://127.0.0.1:$(DOCKER_PORT)/health
	curl --fail --silent --request POST \
		http://127.0.0.1:$(DOCKER_PORT)/api/v1/demo/synthetic
