"""Typed HTTP response contracts for the research API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class PointResponse(BaseModel):
    """One image-space coordinate returned in an analysis report."""

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class EndplateResponse(BaseModel):
    """The exact vertebral endplate selected for the Cobb measurement."""

    model_config = ConfigDict(extra="forbid")

    vertebra_label: str
    vertebra_ordinal: int
    kind: Literal["top", "bottom"]
    left: PointResponse
    right: PointResponse


class ValidationResponse(BaseModel):
    """Optional comparison between the calculated and reference angle."""

    model_config = ConfigDict(extra="forbid")

    reference_angle_degrees: float | None
    absolute_error_degrees: float | None
    tolerance_degrees: float | None
    within_tolerance: bool | None


class MeasurementResponse(BaseModel):
    """Versioned, auditable Cobb-angle report returned by the API."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    software_version: str
    study_id: str
    method: str
    coordinate_space: Literal["pixel"]
    cobb_angle_degrees: float
    upper_orientation_degrees: float
    lower_orientation_degrees: float
    upper_endplate: EndplateResponse
    lower_endplate: EndplateResponse
    validation: ValidationResponse
    disclaimer: str


class ArtifactLinks(BaseModel):
    """Relative URLs for artifacts created by one completed analysis."""

    model_config = ConfigDict(extra="forbid")

    annotated_image_url: str
    measurement_json_url: str
    markdown_report_url: str


class AnalysisResponse(BaseModel):
    """Successful synthetic analysis plus links to its generated files."""

    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    status: Literal["completed"]
    measurement: MeasurementResponse
    artifacts: ArtifactLinks


class AnalysisCapabilitiesResponse(BaseModel):
    """Public feature flags used by the browser upload experience."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["synthetic_demo"]
    real_xray_upload_enabled: bool
    automated_landmark_detection: bool
    accepted_image_types: tuple[Literal["image/png", "image/jpeg"], ...]
    max_upload_size_mb: int
    message: str


class HealthResponse(BaseModel):
    """Minimal process-health response."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: Literal["ai-scoliosis-platform"]
