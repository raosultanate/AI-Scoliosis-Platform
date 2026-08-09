# AI Scoliosis Platform

Production-oriented foundation for a long-lived medical imaging platform. The active scope is
**Version 1A**: consume clinician-provided vertebral landmarks, compute Cobb angle geometry,
validate against an optional reference, and produce traceable visual and machine-readable output.
An initial FastAPI boundary and responsive browser experience expose the deterministic synthetic
case for web integration work.

> [!CAUTION]
> This is research software, not a medical device. It must not be used for diagnosis or treatment.
> Clinical validation, quality management, privacy, security, regulatory review, and human oversight
> are outside this first engineering milestone and are required before clinical use.

## Version 1A boundaries

- Included: PNG/JPEG/TIFF/BMP loading, JSON/CSV/flat-text landmark adapters, endplate
  geometry, deterministic Cobb calculation, reference comparison, annotation, JSON/Markdown report.
- Included web slice: an upload-first landing page, local PNG/JPEG preview, plain-language model
  readiness messaging, the working synthetic analysis, and annotated results.
- Included API slice: health and capability checks, synthetic analysis, OpenAPI docs, and
  generated-artifact retrieval.
- Excluded: ML, neural networks, training, PyTorch, DICOM, databases, transmission or analysis of
  uploaded real X-rays, and authentication.
- A Cobb result records the exact vertebrae, endplates, and signed/acute angles used, so it is
  auditable rather than only returning a scalar.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
scoliosis-v1a analyze \
  --image tests/fixtures/synthetic_xray.png \
  --landmarks tests/fixtures/synthetic_landmarks.json \
  --output-dir data/outputs/synthetic
```

To create the deterministic synthetic fixture first:

```bash
python apps/generate_synthetic_fixture.py
```

Run verification:

```bash
pytest
ruff check .
mypy backend
```

Run the research API:

```bash
uvicorn scoliosis_platform.api:app --reload
curl -X POST http://127.0.0.1:8000/api/v1/demo/synthetic
```

Open `http://127.0.0.1:8000` for the responsive browser experience or
`http://127.0.0.1:8000/docs` for the interactive API documentation. See
[api/README.md](api/README.md) for the endpoint contract and configuration. The selected real image
stays in the browser for preview only; the API currently analyzes the bundled synthetic case, not
uploaded radiographs.

Run the complete application with Docker Compose:

```bash
docker compose up --build
```

The API is available at `http://127.0.0.1:8000`, generated artifacts are retained in a named Docker
volume, and the container exposes a health check at `/health`. Run `make docker-smoke` in another
terminal to verify both health and the synthetic analysis endpoint.

## Inputs

The canonical JSON format is documented in [docs/annotation-schema.md](docs/annotation-schema.md).
Coordinates can be pixels or normalized to `[0, 1]`. CSV and common flat landmark text are also
supported. Dataset-specific formats belong behind the `LandmarkReader` interface.

## Repository map

```text
apps/                       runnable utilities
config/                     non-secret defaults
frontend/                   static browser UI (no build step)
backend/scoliosis_platform/
  dataset/                  images and landmark adapters
  geometry/                 pure geometric computation
  visualization/            rendering only
  reports/                  serialization and human-readable reports
  api/                      FastAPI composition, schemas, and demo endpoint
tests/                      deterministic unit/integration tests
docs/                       engineering and usage documentation
obsidian/                   project knowledge vault and handoff memory
data/                       git-ignored runtime data
models/ training/ inference/ database/       reserved for later versions
```

Start with [docs/getting-started.md](docs/getting-started.md) and
[obsidian/00 Home/Project Home.md](obsidian/00%20Home/Project%20Home.md).
