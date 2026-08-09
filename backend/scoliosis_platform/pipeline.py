"""Application service that composes Version 1A modules into one analysis workflow."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from scoliosis_platform.config import PipelineConfig
from scoliosis_platform.dataset import load_image, load_landmarks
from scoliosis_platform.domain import CobbMeasurement, StudyLandmarks
from scoliosis_platform.geometry import calculate_cobb_angle, validate_measurement
from scoliosis_platform.reports import write_reports
from scoliosis_platform.visualization import save_annotated_image

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AnalysisArtifacts:
    """Paths and domain result returned by a completed analysis run."""

    measurement: CobbMeasurement
    study: StudyLandmarks
    annotated_image_path: Path
    json_report_path: Path
    markdown_report_path: Path


def analyze_study(
    image_path: Path,
    landmark_path: Path,
    output_directory: Path,
    config: PipelineConfig,
) -> AnalysisArtifacts:
    """Load, normalize, calculate, validate, visualize, and report one study."""

    LOGGER.info("Loading image from %s", image_path)
    image = load_image(image_path)
    LOGGER.info("Loading landmarks from %s", landmark_path)
    source_study = load_landmarks(
        landmark_path,
        annotation_format=config.annotation_format,
        coordinate_space=config.coordinate_space,
    )
    study = source_study.to_pixels(image.width, image.height)
    LOGGER.info("Calculating Cobb angle from %d vertebrae", len(study.vertebrae))
    measurement = validate_measurement(
        calculate_cobb_angle(study),
        study.reference_cobb_angle_degrees,
        config.reference_tolerance_degrees,
    )

    annotated_path = save_annotated_image(
        output_directory / "annotated.png",
        image.pixels,
        study,
        measurement,
        landmark_radius=config.landmark_radius,
        line_width=config.line_width,
        dpi=config.dpi,
    )
    json_path, markdown_path = write_reports(output_directory, study, measurement)
    LOGGER.info("Analysis complete: %.2f degrees", measurement.angle_degrees)
    return AnalysisArtifacts(measurement, study, annotated_path, json_path, markdown_path)
