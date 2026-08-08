"""Adapters for clinician-provided vertebral landmark annotations.

JSON is the canonical project format. CSV supports tabular interchange. TXT accepts the common
four-points-per-vertebra layout, one `x y` pair per line. Adding a public dataset should require a
new reader here, not changes to geometry or rendering.
"""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
from typing import Any, Protocol

from scoliosis_platform.domain import CoordinateSpace, Point, StudyLandmarks, VertebraLandmarks


class LandmarkReader(Protocol):
    """Interface implemented by dataset-specific annotation readers."""

    def read(self, path: Path) -> StudyLandmarks:
        """Parse `path` into the canonical domain model."""


def _number(value: Any, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} must be numeric") from error
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def _point(value: Any, field: str) -> Point:
    if isinstance(value, dict):
        return Point(_number(value.get("x"), f"{field}.x"), _number(value.get("y"), f"{field}.y"))
    if isinstance(value, list) and len(value) == 2:
        return Point(_number(value[0], f"{field}[0]"), _number(value[1], f"{field}[1]"))
    raise ValueError(f"{field} must be an [x, y] array or an object with x and y")


def _coordinate_space(value: str, points: tuple[Point, ...] = ()) -> CoordinateSpace:
    normalized = value.strip().lower()
    if normalized == "auto":
        if points and all(0.0 <= coordinate <= 1.0 for p in points for coordinate in (p.x, p.y)):
            return CoordinateSpace.NORMALIZED
        return CoordinateSpace.PIXEL
    try:
        return CoordinateSpace(normalized)
    except ValueError as error:
        raise ValueError("coordinate_space must be 'pixel', 'normalized', or 'auto'") from error


def _validate(study: StudyLandmarks) -> StudyLandmarks:
    if not study.study_id.strip():
        raise ValueError("study_id must not be empty")
    if not study.vertebrae:
        raise ValueError("At least one vertebra annotation is required")
    study.ordered_vertebrae()
    if study.coordinate_space is CoordinateSpace.NORMALIZED:
        for vertebra in study.vertebrae:
            for point in (
                vertebra.top_left,
                vertebra.top_right,
                vertebra.bottom_left,
                vertebra.bottom_right,
            ):
                if not (0.0 <= point.x <= 1.0 and 0.0 <= point.y <= 1.0):
                    raise ValueError("Normalized landmark coordinates must be within [0, 1]")
    return study


class JsonLandmarkReader:
    """Read the canonical versioned JSON annotation schema."""

    def read(self, path: Path) -> StudyLandmarks:
        """Parse a JSON document and validate required vertebral corners."""

        with path.open(encoding="utf-8") as stream:
            document = json.load(stream)
        if not isinstance(document, dict):
            raise ValueError("Landmark JSON root must be an object")
        rows = document.get("vertebrae")
        if not isinstance(rows, list):
            raise ValueError("Landmark JSON must contain a 'vertebrae' array")
        vertebrae = tuple(
            VertebraLandmarks(
                label=str(row.get("label", f"V{index + 1:02d}")),
                ordinal=int(row.get("ordinal", index)),
                top_left=_point(row.get("top_left"), f"vertebrae[{index}].top_left"),
                top_right=_point(row.get("top_right"), f"vertebrae[{index}].top_right"),
                bottom_left=_point(row.get("bottom_left"), f"vertebrae[{index}].bottom_left"),
                bottom_right=_point(row.get("bottom_right"), f"vertebrae[{index}].bottom_right"),
            )
            for index, row in enumerate(rows)
        )
        points = tuple(
            point
            for item in vertebrae
            for point in (item.top_left, item.top_right, item.bottom_left, item.bottom_right)
        )
        reference = document.get("reference_cobb_angle_degrees")
        study = StudyLandmarks(
            study_id=str(document.get("study_id", path.stem)),
            vertebrae=vertebrae,
            coordinate_space=_coordinate_space(
                str(document.get("coordinate_space", "auto")), points
            ),
            reference_cobb_angle_degrees=(
                None if reference is None else _number(reference, "reference_cobb_angle_degrees")
            ),
            source_path=path.resolve(),
        )
        return _validate(study)


class CsvLandmarkReader:
    """Read one vertebra per row from a named-column CSV file."""

    REQUIRED_COLUMNS = {
        "label",
        "ordinal",
        "top_left_x",
        "top_left_y",
        "top_right_x",
        "top_right_y",
        "bottom_left_x",
        "bottom_left_y",
        "bottom_right_x",
        "bottom_right_y",
    }

    def __init__(self, coordinate_space: str = "auto") -> None:
        self._coordinate_space = coordinate_space

    def read(self, path: Path) -> StudyLandmarks:
        """Parse CSV rows into a study, auto-detecting normalized coordinates by default."""

        with path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            missing = self.REQUIRED_COLUMNS - set(reader.fieldnames or ())
            if missing:
                raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
            vertebrae = tuple(self._row_to_vertebra(row, index) for index, row in enumerate(reader))
        points = tuple(
            point
            for item in vertebrae
            for point in (item.top_left, item.top_right, item.bottom_left, item.bottom_right)
        )
        return _validate(
            StudyLandmarks(
                study_id=path.stem,
                vertebrae=vertebrae,
                coordinate_space=_coordinate_space(self._coordinate_space, points),
                source_path=path.resolve(),
            )
        )

    @staticmethod
    def _row_to_vertebra(row: dict[str, str], index: int) -> VertebraLandmarks:
        return VertebraLandmarks(
            label=row["label"],
            ordinal=int(row["ordinal"]),
            top_left=Point(
                _number(row["top_left_x"], "top_left_x"), _number(row["top_left_y"], "top_left_y")
            ),
            top_right=Point(
                _number(row["top_right_x"], "top_right_x"),
                _number(row["top_right_y"], "top_right_y"),
            ),
            bottom_left=Point(
                _number(row["bottom_left_x"], "bottom_left_x"),
                _number(row["bottom_left_y"], "bottom_left_y"),
            ),
            bottom_right=Point(
                _number(row["bottom_right_x"], "bottom_right_x"),
                _number(row["bottom_right_y"], "bottom_right_y"),
            ),
        )


class FlatTextLandmarkReader:
    """Read four sequential `x y` corner pairs per vertebra from plain text."""

    def __init__(self, coordinate_space: str = "auto") -> None:
        self._coordinate_space = coordinate_space

    def read(self, path: Path) -> StudyLandmarks:
        """Parse lines in top-left, top-right, bottom-left, bottom-right order."""

        points: list[Point] = []
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw_line.split("#", maxsplit=1)[0].strip()
            if not line:
                continue
            values = re.split(r"[\s,]+", line)
            if len(values) != 2:
                raise ValueError(f"Line {line_number} must contain exactly two coordinates")
            points.append(
                Point(
                    _number(values[0], f"line {line_number} x"),
                    _number(values[1], f"line {line_number} y"),
                )
            )
        if len(points) % 4 != 0:
            raise ValueError("Flat landmark files must contain a multiple of four points")
        vertebrae = tuple(
            VertebraLandmarks(
                label=f"V{index // 4 + 1:02d}",
                ordinal=index // 4,
                top_left=points[index],
                top_right=points[index + 1],
                bottom_left=points[index + 2],
                bottom_right=points[index + 3],
            )
            for index in range(0, len(points), 4)
        )
        return _validate(
            StudyLandmarks(
                study_id=path.stem,
                vertebrae=vertebrae,
                coordinate_space=_coordinate_space(self._coordinate_space, tuple(points)),
                source_path=path.resolve(),
            )
        )


def load_landmarks(
    path: Path, annotation_format: str = "auto", coordinate_space: str = "auto"
) -> StudyLandmarks:
    """Select a landmark reader by explicit format or filename suffix."""

    if not path.is_file():
        raise FileNotFoundError(f"Landmark annotation not found: {path}")
    selected = (
        path.suffix.lower().lstrip(".")
        if annotation_format == "auto"
        else annotation_format.lower()
    )
    readers: dict[str, LandmarkReader] = {
        "json": JsonLandmarkReader(),
        "csv": CsvLandmarkReader(coordinate_space),
        "txt": FlatTextLandmarkReader(coordinate_space),
    }
    try:
        reader = readers[selected]
    except KeyError as error:
        raise ValueError(
            f"Unsupported annotation format '{selected}'; choose json, csv, or txt"
        ) from error
    return reader.read(path)
