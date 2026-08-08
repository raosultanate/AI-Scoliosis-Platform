"""Integration test covering image-to-report composition."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from scoliosis_platform.config import PipelineConfig
from scoliosis_platform.pipeline import analyze_study


def test_pipeline_creates_traceable_artifacts(tmp_path: Path, fixture_directory: Path) -> None:
    image_path = tmp_path / "image.png"
    assert cv2.imwrite(str(image_path), np.full((1000, 500), 80, dtype=np.uint8))
    output = tmp_path / "output"
    artifacts = analyze_study(
        image_path,
        fixture_directory / "synthetic_landmarks.json",
        output,
        PipelineConfig(reference_tolerance_degrees=0.01),
    )
    assert artifacts.measurement.angle_degrees == pytest.approx(30.0, abs=0.001)
    assert artifacts.measurement.within_tolerance is True
    assert artifacts.annotated_image_path.is_file()
    report = json.loads(artifacts.json_report_path.read_text(encoding="utf-8"))
    assert report["upper_endplate"]["vertebra_label"] == "T4"
    assert report["lower_endplate"]["vertebra_label"] == "T12"
    assert "Research software" in report["disclaimer"]
