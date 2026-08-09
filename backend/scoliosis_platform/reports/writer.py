"""Write stable JSON and concise Markdown reports.

Reports include the calculation policy and endplate provenance. The schema is intentionally simple
for Version 1A; a future clinical report format should be separately versioned and validated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scoliosis_platform.domain import CobbMeasurement, Endplate, StudyLandmarks


def _point_as_dict(point_x: float, point_y: float) -> dict[str, float]:
    return {"x": round(point_x, 6), "y": round(point_y, 6)}


def _endplate_as_dict(endplate: Endplate) -> dict[str, Any]:
    return {
        "vertebra_label": endplate.vertebra_label,
        "vertebra_ordinal": endplate.vertebra_ordinal,
        "kind": endplate.kind.value,
        "left": _point_as_dict(endplate.left.x, endplate.left.y),
        "right": _point_as_dict(endplate.right.x, endplate.right.y),
    }


def measurement_as_dict(study: StudyLandmarks, measurement: CobbMeasurement) -> dict[str, Any]:
    """Convert a result to the versioned JSON-compatible report schema."""

    return {
        "schema_version": "1.0",
        "software_version": "0.1.0",
        "study_id": study.study_id,
        "method": "maximum_upper_superior_to_lower_inferior_endplate_angle",
        "coordinate_space": "pixel",
        "cobb_angle_degrees": round(measurement.angle_degrees, 6),
        "upper_orientation_degrees": round(measurement.upper_orientation_degrees, 6),
        "lower_orientation_degrees": round(measurement.lower_orientation_degrees, 6),
        "upper_endplate": _endplate_as_dict(measurement.upper_endplate),
        "lower_endplate": _endplate_as_dict(measurement.lower_endplate),
        "validation": {
            "reference_angle_degrees": measurement.reference_angle_degrees,
            "absolute_error_degrees": measurement.absolute_error_degrees,
            "tolerance_degrees": measurement.tolerance_degrees,
            "within_tolerance": measurement.within_tolerance,
        },
        "disclaimer": "Research software only; not for diagnosis or treatment.",
    }


def write_reports(
    output_directory: Path,
    study: StudyLandmarks,
    measurement: CobbMeasurement,
) -> tuple[Path, Path]:
    """Write atomic JSON and Markdown reports and return their paths."""

    output_directory.mkdir(parents=True, exist_ok=True)
    payload = measurement_as_dict(study, measurement)
    json_path = output_directory / "measurement.json"
    markdown_path = output_directory / "report.md"
    _atomic_write(json_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")

    validation = "Not available (annotation supplied no reference angle)."
    if measurement.reference_angle_degrees is not None:
        status = "PASS" if measurement.within_tolerance else "FAIL"
        validation = (
            f"{status}: reference {measurement.reference_angle_degrees:.2f}°, "
            f"absolute error {measurement.absolute_error_degrees:.2f}°, "
            f"tolerance {measurement.tolerance_degrees:.2f}°."
        )
    upper_description = (
        f"{measurement.upper_endplate.vertebra_label} "
        f"({measurement.upper_endplate.kind.value})"
    )
    lower_description = (
        f"{measurement.lower_endplate.vertebra_label} "
        f"({measurement.lower_endplate.kind.value})"
    )
    markdown = f"""# Cobb Angle Analysis — {study.study_id}

> [!warning]
> Research software only. This result is not for diagnosis or treatment.

- Calculated Cobb angle: **{measurement.angle_degrees:.2f}°**
- Upper endplate: {upper_description}
- Lower endplate: {lower_description}
- Validation: {validation}

## Method

The Version 1A policy selects the largest acute angle between the superior endplate of an upper
vertebra and the inferior endplate of a caudally lower vertebra. A clinician should review both
end-vertebra selection and landmark quality.
"""
    _atomic_write(markdown_path, markdown)
    return json_path, markdown_path


def _atomic_write(path: Path, content: str) -> None:
    """Replace a report only after its complete content has been written."""

    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)
