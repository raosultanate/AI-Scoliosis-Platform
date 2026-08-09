# API

The initial FastAPI boundary wraps the existing framework-independent `analyze_study` service. It
does not contain separate Cobb-angle logic.

Run the development server from the repository root:

```bash
uvicorn scoliosis_platform.api:app --reload
```

Then run the bundled deterministic 30-degree case:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/demo/synthetic
```

Useful URLs:

- `GET /` — responsive, non-medical-user-friendly browser experience
- `GET /health` — process health
- `GET /api/v1/capabilities` — current upload and model-readiness flags
- `POST /api/v1/demo/synthetic` — run the existing synthetic fixture through the full pipeline
- `GET /artifacts/{analysis_id}/{filename}` — retrieve generated outputs
- `GET /docs` — interactive OpenAPI documentation

The browser can preview a selected PNG or JPEG locally, but it does not upload or analyze a real
X-ray while automated landmark detection is unavailable. It says so directly and offers the safe
synthetic case instead; this prevents the research preview from fabricating a medical result.

Each synthetic request receives an isolated artifact directory under `data/outputs/api/`. Override
that location with `SCOLIOSIS_API_OUTPUT_DIR`. The endpoint is explicitly a research demonstration;
real X-ray transmission, authentication, DICOM, model inference, and clinical use remain out of
scope.

## Docker

Build and run the complete API stack:

```bash
docker compose up --build
```

Or use the Make targets:

```bash
make docker-build
make docker-run
```

The container:

- runs Uvicorn as the non-root `appuser` account;
- listens on container port `8000`;
- includes `config/v1a.yaml` and the bundled synthetic fixtures;
- writes artifacts only to `/app/data/outputs/api`;
- reports health through `GET /health` and a Docker `HEALTHCHECK`;
- keeps generated artifacts in the `scoliosis-artifacts` named volume under Compose;
- uses a read-only root filesystem, ephemeral `/tmp`, dropped capabilities, and
  `no-new-privileges` under Compose.

Override the host port when necessary:

```bash
SCOLIOSIS_PORT=8080 docker compose up --build
```

Stop the service without deleting its artifact volume:

```bash
docker compose down
```

Delete the named volume only when its generated artifacts are no longer needed:

```bash
docker compose down --volumes
```
