"""Line construction and angle primitives.

All functions are pure and independent of image or plotting libraries. An endplate's orientation is
normalized to `[-90, 90)` degrees because a line has no directional arrow. Degenerate endplates are
rejected instead of allowing an undefined result to propagate.
"""

from __future__ import annotations

import math

from scoliosis_platform.domain import Endplate, EndplateKind, Point, VertebraLandmarks


def endplates_for(vertebra: VertebraLandmarks) -> tuple[Endplate, Endplate]:
    """Build superior and inferior endplate segments from four corner landmarks."""

    return (
        Endplate(
            vertebra_label=vertebra.label,
            vertebra_ordinal=vertebra.ordinal,
            kind=EndplateKind.TOP,
            left=vertebra.top_left,
            right=vertebra.top_right,
        ),
        Endplate(
            vertebra_label=vertebra.label,
            vertebra_ordinal=vertebra.ordinal,
            kind=EndplateKind.BOTTOM,
            left=vertebra.bottom_left,
            right=vertebra.bottom_right,
        ),
    )


def orientation_degrees(start: Point, end: Point) -> float:
    """Return line orientation in `[-90, 90)` degrees in image coordinates."""

    delta_x = end.x - start.x
    delta_y = end.y - start.y
    if math.isclose(delta_x, 0.0, abs_tol=1e-12) and math.isclose(delta_y, 0.0, abs_tol=1e-12):
        raise ValueError("Cannot determine orientation of a zero-length endplate")
    angle = math.degrees(math.atan2(delta_y, delta_x))
    return ((angle + 90.0) % 180.0) - 90.0


def acute_angle_between(first: Endplate, second: Endplate) -> float:
    """Return the smaller angle between two undirected lines in `[0, 90]` degrees."""

    first_angle = orientation_degrees(first.left, first.right)
    second_angle = orientation_degrees(second.left, second.right)
    difference = abs(first_angle - second_angle) % 180.0
    return min(difference, 180.0 - difference)
