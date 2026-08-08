"""Configuration loading for the Version 1A command-line pipeline.

Defaults live in YAML and the path can be selected with `SCOLIOSIS_CONFIG`. Only runtime concerns
belong here; medical or geometric rules stay in their owning modules.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Validated settings used by a single analysis run."""

    reference_tolerance_degrees: float = 5.0
    annotation_format: str = "auto"
    coordinate_space: str = "auto"
    landmark_radius: int = 4
    line_width: int = 2
    dpi: int = 150
    log_level: str = "INFO"


def load_config(path: Path | None = None) -> PipelineConfig:
    """Load YAML configuration, using `SCOLIOSIS_CONFIG` when `path` is omitted."""

    selected_path = path or Path(os.getenv("SCOLIOSIS_CONFIG", "config/v1a.yaml"))
    if not selected_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {selected_path}")
    with selected_path.open(encoding="utf-8") as stream:
        document: dict[str, Any] = yaml.safe_load(stream) or {}

    pipeline = document.get("pipeline", {})
    visualization = document.get("visualization", {})
    logging_config = document.get("logging", {})
    tolerance = float(pipeline.get("reference_tolerance_degrees", 5.0))
    if tolerance < 0:
        raise ValueError("reference_tolerance_degrees must be non-negative")
    return PipelineConfig(
        reference_tolerance_degrees=tolerance,
        annotation_format=str(pipeline.get("annotation_format", "auto")),
        coordinate_space=str(pipeline.get("coordinate_space", "auto")),
        landmark_radius=int(visualization.get("landmark_radius", 4)),
        line_width=int(visualization.get("line_width", 2)),
        dpi=int(visualization.get("dpi", 150)),
        log_level=os.getenv("SCOLIOSIS_LOG_LEVEL", str(logging_config.get("level", "INFO"))),
    )
