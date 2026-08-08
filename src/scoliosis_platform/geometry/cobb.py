"""Deterministic landmark-based Cobb angle selection and validation.

For Version 1A the automatic policy evaluates the superior endplate of every possible upper
vertebra against the inferior endplate of every caudally lower vertebra, returning the pair with
the largest acute line angle. This is explicit and reproducible, but it is not a substitute for a
clinician selecting end vertebrae. Multi-curve identification is intentionally deferred.
"""

from __future__ import annotations

from dataclasses import replace

from scoliosis_platform.domain import CobbMeasurement, EndplateKind, StudyLandmarks
from scoliosis_platform.geometry.lines import (
    acute_angle_between,
    endplates_for,
    orientation_degrees,
)


def calculate_cobb_angle(study: StudyLandmarks) -> CobbMeasurement:
    """Calculate the maximum Cobb angle from ordered clinician-provided landmarks.

    Args:
        study: Landmarks already converted to pixel coordinates.

    Returns:
        The maximum measurement and exact endplates used.

    Raises:
        ValueError: If fewer than two vertebrae exist or an endplate is degenerate.
    """

    vertebrae = study.ordered_vertebrae()
    if len(vertebrae) < 2:
        raise ValueError("At least two vertebrae are required for Cobb angle calculation")

    candidates: list[CobbMeasurement] = []
    for upper_index, upper_vertebra in enumerate(vertebrae[:-1]):
        upper_endplate = next(
            plate for plate in endplates_for(upper_vertebra) if plate.kind is EndplateKind.TOP
        )
        for lower_vertebra in vertebrae[upper_index + 1 :]:
            lower_endplate = next(
                plate
                for plate in endplates_for(lower_vertebra)
                if plate.kind is EndplateKind.BOTTOM
            )
            candidates.append(
                CobbMeasurement(
                    angle_degrees=acute_angle_between(upper_endplate, lower_endplate),
                    upper_endplate=upper_endplate,
                    lower_endplate=lower_endplate,
                    upper_orientation_degrees=orientation_degrees(
                        upper_endplate.left, upper_endplate.right
                    ),
                    lower_orientation_degrees=orientation_degrees(
                        lower_endplate.left, lower_endplate.right
                    ),
                )
            )

    # Deterministic tie-breaking: the earliest upper then earliest lower vertebra wins.
    return max(candidates, key=lambda item: item.angle_degrees)


def validate_measurement(
    measurement: CobbMeasurement,
    reference_angle_degrees: float | None,
    tolerance_degrees: float,
) -> CobbMeasurement:
    """Attach a reference comparison without mutating the computed geometry."""

    if tolerance_degrees < 0:
        raise ValueError("Reference tolerance must be non-negative")
    if reference_angle_degrees is None:
        return replace(measurement, tolerance_degrees=tolerance_degrees)
    if not 0.0 <= reference_angle_degrees <= 180.0:
        raise ValueError("Reference Cobb angle must be between 0 and 180 degrees")
    absolute_error = abs(measurement.angle_degrees - reference_angle_degrees)
    return replace(
        measurement,
        reference_angle_degrees=reference_angle_degrees,
        absolute_error_degrees=absolute_error,
        within_tolerance=absolute_error <= tolerance_degrees,
        tolerance_degrees=tolerance_degrees,
    )
