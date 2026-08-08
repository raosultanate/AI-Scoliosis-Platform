"""Deterministic tests for the clinically central geometry primitives."""

from __future__ import annotations

import pytest

from scoliosis_platform.domain import Point, StudyLandmarks, VertebraLandmarks
from scoliosis_platform.geometry import (
    calculate_cobb_angle,
    orientation_degrees,
    validate_measurement,
)


def _vertebra(label: str, ordinal: int, top_dy: float, bottom_dy: float) -> VertebraLandmarks:
    return VertebraLandmarks(
        label=label,
        ordinal=ordinal,
        top_left=Point(0, 10),
        top_right=Point(10, 10 + top_dy),
        bottom_left=Point(0, 20),
        bottom_right=Point(10, 20 + bottom_dy),
    )


def test_orientation_uses_image_coordinate_convention() -> None:
    assert orientation_degrees(Point(0, 0), Point(1, 1)) == pytest.approx(45.0)
    assert orientation_degrees(Point(1, 1), Point(0, 0)) == pytest.approx(45.0)


def test_calculate_cobb_selects_maximum_valid_craniocaudal_pair() -> None:
    study = StudyLandmarks(
        study_id="geometry",
        vertebrae=(
            _vertebra("T4", 0, 2.679492, 1.763270),
            _vertebra("T8", 1, 0.0, 0.0),
            _vertebra("T12", 2, -1.763270, -2.679492),
        ),
    )
    result = calculate_cobb_angle(study)
    assert result.angle_degrees == pytest.approx(30.0, abs=1e-5)
    assert result.upper_endplate.vertebra_label == "T4"
    assert result.lower_endplate.vertebra_label == "T12"


def test_validation_boundary_is_inclusive() -> None:
    study = StudyLandmarks(
        study_id="validation",
        vertebrae=(_vertebra("A", 0, 0, 0), _vertebra("B", 1, 0, 0)),
    )
    validated = validate_measurement(calculate_cobb_angle(study), 5.0, 5.0)
    assert validated.absolute_error_degrees == pytest.approx(5.0)
    assert validated.within_tolerance is True


def test_degenerate_endplate_is_rejected() -> None:
    bad = VertebraLandmarks("A", 0, Point(1, 1), Point(1, 1), Point(0, 2), Point(2, 2))
    good = _vertebra("B", 1, 0, 0)
    with pytest.raises(ValueError, match="zero-length"):
        calculate_cobb_angle(StudyLandmarks("bad", (bad, good)))
