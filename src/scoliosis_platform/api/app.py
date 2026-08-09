"""FastAPI composition root and research-only demonstration routes."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from scoliosis_platform.api.schemas import (
    AnalysisCapabilitiesResponse,
    AnalysisResponse,
    ArtifactLinks,
    HealthResponse,
    MeasurementResponse,
)
from scoliosis_platform.api.settings import ApiSettings
from scoliosis_platform.config import load_config
from scoliosis_platform.pipeline import analyze_study
from scoliosis_platform.reports import measurement_as_dict

LOGGER = logging.getLogger(__name__)


def _artifact_url(output_root: Path, artifact_path: Path) -> str:
    relative_path = artifact_path.resolve().relative_to(output_root.resolve())
    return f"/artifacts/{relative_path.as_posix()}"


def _api_router(settings: ApiSettings) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    @router.get(
        "/capabilities",
        response_model=AnalysisCapabilitiesResponse,
        tags=["operations"],
        summary="Describe which analysis modes are currently available",
    )
    async def analysis_capabilities() -> AnalysisCapabilitiesResponse:
        return AnalysisCapabilitiesResponse(
            mode="synthetic_demo",
            real_xray_upload_enabled=False,
            automated_landmark_detection=False,
            accepted_image_types=("image/png", "image/jpeg"),
            max_upload_size_mb=10,
            message=(
                "The browser can preview an X-ray locally, but automated landmark detection "
                "is not connected yet. The bundled synthetic demonstration is available."
            ),
        )

    @router.post(
        "/demo/synthetic",
        response_model=AnalysisResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["demo"],
        summary="Run the deterministic synthetic 30-degree case",
    )
    async def analyze_synthetic_case() -> AnalysisResponse:
        """Run the existing Version 1A pipeline against bundled research fixtures."""

        analysis_id = uuid4().hex
        output_directory = settings.output_root / analysis_id
        try:
            config = load_config(settings.pipeline_config_path)
            artifacts = await run_in_threadpool(
                analyze_study,
                settings.synthetic_image_path,
                settings.synthetic_landmark_path,
                output_directory,
                config,
            )
        except (FileNotFoundError, OSError, ValueError) as error:
            shutil.rmtree(output_directory, ignore_errors=True)
            LOGGER.exception("Synthetic analysis %s failed", analysis_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The bundled synthetic analysis could not be completed.",
            ) from error

        measurement = MeasurementResponse.model_validate(
            measurement_as_dict(artifacts.study, artifacts.measurement)
        )
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            measurement=measurement,
            artifacts=ArtifactLinks(
                annotated_image_url=_artifact_url(
                    settings.output_root, artifacts.annotated_image_path
                ),
                measurement_json_url=_artifact_url(
                    settings.output_root, artifacts.json_report_path
                ),
                markdown_report_url=_artifact_url(
                    settings.output_root, artifacts.markdown_report_path
                ),
            ),
        )

    return router


def create_app(settings: ApiSettings | None = None) -> FastAPI:
    """Build an application with injectable paths for deterministic tests."""

    selected_settings = settings or ApiSettings.from_environment()
    selected_settings.output_root.mkdir(parents=True, exist_ok=True)
    web_root = selected_settings.project_root / "frontend"

    application = FastAPI(
        title="AI Scoliosis Platform API",
        version="0.1.0",
        description=(
            "Research-only API for auditable landmark-based Cobb-angle analysis. "
            "Not for diagnosis or treatment."
        ),
    )

    @application.get("/health", response_model=HealthResponse, tags=["operations"])
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", service="ai-scoliosis-platform")

    @application.get("/", include_in_schema=False, response_class=FileResponse)
    async def website() -> FileResponse:
        return FileResponse(web_root / "index.html")

    application.include_router(_api_router(selected_settings))
    application.mount(
        "/assets",
        StaticFiles(directory=str(web_root), check_dir=True),
        name="website-assets",
    )
    application.mount(
        "/artifacts",
        StaticFiles(directory=str(selected_settings.output_root), check_dir=True),
        name="artifacts",
    )
    return application


app = create_app()
