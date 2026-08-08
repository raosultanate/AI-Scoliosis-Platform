# AI Scoliosis Platform

Production-oriented foundation for a long-lived medical imaging platform. The active scope is
**Version 1A**: consume clinician-provided vertebral landmarks, compute Cobb angle geometry,
validate against an optional reference, and produce traceable visual and machine-readable output.

> [!CAUTION]
> This is research software, not a medical device. It must not be used for diagnosis or treatment.
> Clinical validation, quality management, privacy, security, regulatory review, and human oversight
> are outside this first engineering milestone and are required before clinical use.

## Version 1A boundaries

- Included: PNG/JPEG/TIFF/BMP loading, JSON/CSV/flat-text landmark adapters, endplate
  geometry, deterministic Cobb calculation, reference comparison, annotation, JSON/Markdown report.
- Excluded: ML, neural networks, training, PyTorch, DICOM, APIs, databases, and web applications.
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
mypy src
```

## Inputs

The canonical JSON format is documented in [docs/annotation-schema.md](docs/annotation-schema.md).
Coordinates can be pixels or normalized to `[0, 1]`. CSV and common flat landmark text are also
supported. Dataset-specific formats belong behind the `LandmarkReader` interface.

## Repository map

```text
apps/                       runnable utilities
config/                     non-secret defaults
src/scoliosis_platform/
  dataset/                  images and landmark adapters
  geometry/                 pure geometric computation
  visualization/            rendering only
  reports/                  serialization and human-readable reports
tests/                      deterministic unit/integration tests
docs/                       engineering and usage documentation
obsidian/                   project knowledge vault and handoff memory
data/                       git-ignored runtime data
models/ training/ inference/ database/ api/  reserved for later versions
```

Start with [docs/getting-started.md](docs/getting-started.md) and
[obsidian/00 Home/Project Home.md](obsidian/00%20Home/Project%20Home.md).

