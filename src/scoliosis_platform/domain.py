"""Typed domain objects shared across the Version 1A pipeline.

This module exists so dataset adapters, geometry, visualization, and reports communicate through
stable types rather than through loader-specific dictionaries. Coordinates use image convention:
the origin is at the top-left, x increases rightward, and y increases downward.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Point:
    """A two-dimensional point expressed in image pixel coordinates."""

    x: float
    y: float

    def scaled(self, width: int, height: int) -> Point:
        """Convert a normalized point to pixels using image width and height."""

        return Point(self.x * width, self.y * height)


@dataclass(frozen=True, slots=True)
class VertebraLandmarks:
    """Four clinician-supplied corners of one vertebral body.

    `ordinal` is cranio-caudal ordering and is deliberately separate from `label`: some datasets
    omit anatomical level names but still provide a reliable point order.
    """

    label: str
    ordinal: int
    top_left: Point
    top_right: Point
    bottom_left: Point
    bottom_right: Point

    def to_pixels(self, width: int, height: int) -> VertebraLandmarks:
        """Return a copy whose normalized coordinates have been scaled to pixels."""

        return VertebraLandmarks(
            label=self.label,
            ordinal=self.ordinal,
            top_left=self.top_left.scaled(width, height),
            top_right=self.top_right.scaled(width, height),
            bottom_left=self.bottom_left.scaled(width, height),
            bottom_right=self.bottom_right.scaled(width, height),
        )


class CoordinateSpace(str, Enum):
    """Coordinate space declared by an annotation document."""

    PIXEL = "pixel"
    NORMALIZED = "normalized"


@dataclass(frozen=True, slots=True)
class StudyLandmarks:
    """All landmarks and optional clinical reference associated with one image."""

    study_id: str
    vertebrae: tuple[VertebraLandmarks, ...]
    coordinate_space: CoordinateSpace = CoordinateSpace.PIXEL
    reference_cobb_angle_degrees: float | None = None
    source_path: Path | None = None

    def ordered_vertebrae(self) -> tuple[VertebraLandmarks, ...]:
        """Return vertebrae in cranio-caudal order and reject duplicate ordinals."""

        ordered = tuple(sorted(self.vertebrae, key=lambda item: item.ordinal))
        ordinals = [item.ordinal for item in ordered]
        if len(set(ordinals)) != len(ordinals):
            raise ValueError("Vertebra ordinals must be unique within a study")
        return ordered

    def to_pixels(self, width: int, height: int) -> StudyLandmarks:
        """Scale normalized landmarks; return pixel landmarks unchanged."""

        if width <= 0 or height <= 0:
            raise ValueError("Image width and height must be positive")
        if self.coordinate_space is CoordinateSpace.PIXEL:
            return self
        return StudyLandmarks(
            study_id=self.study_id,
            vertebrae=tuple(item.to_pixels(width, height) for item in self.vertebrae),
            coordinate_space=CoordinateSpace.PIXEL,
            reference_cobb_angle_degrees=self.reference_cobb_angle_degrees,
            source_path=self.source_path,
        )


class EndplateKind(str, Enum):
    """The superior (top) or inferior (bottom) vertebral endplate."""

    TOP = "top"
    BOTTOM = "bottom"


@dataclass(frozen=True, slots=True)
class Endplate:
    """A named line segment derived from a vertebra's corner landmarks."""

    vertebra_label: str
    vertebra_ordinal: int
    kind: EndplateKind
    left: Point
    right: Point


@dataclass(frozen=True, slots=True)
class CobbMeasurement:
    """An auditable Cobb-angle result and its optional reference comparison."""

    angle_degrees: float
    upper_endplate: Endplate
    lower_endplate: Endplate
    upper_orientation_degrees: float
    lower_orientation_degrees: float
    reference_angle_degrees: float | None = None
    absolute_error_degrees: float | None = None
    within_tolerance: bool | None = None
    tolerance_degrees: float | None = None
