"""Filesystem settings for the FastAPI application."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class ApiSettings:
    """Paths used by API routes and the artifact server."""

    project_root: Path
    output_root: Path

    @classmethod
    def from_environment(cls) -> ApiSettings:
        """Create settings from optional environment overrides."""

        project_root = Path(os.getenv("SCOLIOSIS_PROJECT_ROOT", str(_project_root()))).resolve()
        output_root = Path(
            os.getenv(
                "SCOLIOSIS_API_OUTPUT_DIR",
                str(project_root / "data" / "outputs" / "api"),
            )
        ).resolve()
        return cls(project_root=project_root, output_root=output_root)

    @property
    def synthetic_image_path(self) -> Path:
        """Bundled synthetic image used by the demo endpoint."""

        return self.project_root / "tests" / "fixtures" / "synthetic_xray.png"

    @property
    def synthetic_landmark_path(self) -> Path:
        """Bundled synthetic landmarks used by the demo endpoint."""

        return self.project_root / "tests" / "fixtures" / "synthetic_landmarks.json"

    @property
    def pipeline_config_path(self) -> Path:
        """Version 1A pipeline configuration used by the demo endpoint."""

        return self.project_root / "config" / "v1a.yaml"
