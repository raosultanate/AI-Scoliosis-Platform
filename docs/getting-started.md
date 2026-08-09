# Getting started

## Prerequisites

- Python 3.10 or later
- A raster radiograph and matching landmark file
- No model weights, GPU, or training environment are needed for Version 1A

## Install and verify

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python apps/generate_synthetic_fixture.py
pytest
```

## Run one study

```bash
scoliosis-v1a analyze \
  --image tests/fixtures/synthetic_xray.png \
  --landmarks tests/fixtures/synthetic_landmarks.json \
  --output-dir data/outputs/synthetic \
  --config config/v1a.yaml
```

Outputs are `annotated.png`, `measurement.json`, and `report.md`. The command fails loudly on an
unsupported image, malformed landmarks, duplicate vertebral order, insufficient vertebrae, or a
zero-length endplate.

## Run the FastAPI demonstration

Start the development server after installing the project:

```bash
make api
```

In a second terminal, run the existing deterministic fixture through the HTTP boundary:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/demo/synthetic
```

The JSON response contains the calculated angle, selected endplates, validation result, and URLs
for the generated PNG, JSON, and Markdown artifacts. Interactive documentation is available at
`http://127.0.0.1:8000/docs`.

Open `http://127.0.0.1:8000` for the responsive browser experience. A selected PNG or JPEG is
previewed locally in the browser and is not uploaded. Until automated landmark detection is
connected, the application offers the bundled 30° synthetic example and refuses to invent a result
for a real X-ray. Current readiness is also available from:

```bash
curl http://127.0.0.1:8000/api/v1/capabilities
```

## Run in Docker

Docker Compose builds the image, starts the API, creates a persistent artifact volume, and applies
the container security settings documented in `api/README.md`:

```bash
docker compose up --build
```

When the service is healthy, verify it from a second terminal:

```bash
make docker-smoke
```

Stop it with `docker compose down`. This preserves generated artifacts. Add `--volumes` only when
you intentionally want to delete the artifact volume.

## Real dataset integration checklist

1. Confirm the dataset license permits the intended research use.
2. Document provenance, patient de-identification, annotation definition, vertebral ordering,
   coordinate space, image orientation, and reference-angle methodology.
3. Copy source data under `data/raw/` (ignored by Git); do not commit protected health information.
4. Add a dataset-specific `LandmarkReader` only if JSON, CSV, or flat TXT cannot represent it.
5. Add at least one deterministic parser test and one known clinical case approved for development.
6. Compare algorithmic end-vertebra selection to the dataset's measurement protocol before treating
   reference error as meaningful.

## Configuration

`config/v1a.yaml` owns non-secret defaults. Set `SCOLIOSIS_CONFIG` to choose another file and
`SCOLIOSIS_LOG_LEVEL` to override logging. Paths are CLI arguments and are never hardcoded.
