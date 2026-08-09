"""Render landmarks, endplates, and a selected Cobb measurement over a radiograph.

The public figure-building function returns a Matplotlib `Figure`, making visual structure testable
without file I/O. Calculation occurs before this module and is never inferred from drawn pixels.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from scoliosis_platform.domain import CobbMeasurement, StudyLandmarks
from scoliosis_platform.geometry.lines import endplates_for

matplotlib.use("Agg")


def create_annotated_figure(
    image: NDArray[np.uint8],
    study: StudyLandmarks,
    measurement: CobbMeasurement,
    *,
    landmark_radius: int = 4,
    line_width: int = 2,
) -> Figure:
    """Create an annotated figure from pixel-space landmarks and a Cobb measurement."""

    if image.ndim != 2:
        raise ValueError("Visualization expects a two-dimensional grayscale image")
    figure = Figure(figsize=(7, 10), layout="tight")
    axis = figure.subplots()
    axis.imshow(image, cmap="gray", vmin=0, vmax=255)

    for vertebra in study.ordered_vertebrae():
        points = (
            vertebra.top_left,
            vertebra.top_right,
            vertebra.bottom_left,
            vertebra.bottom_right,
        )
        axis.scatter(
            [point.x for point in points],
            [point.y for point in points],
            s=landmark_radius**2,
            c="#00e5ff",
            edgecolors="black",
            linewidths=0.4,
            zorder=3,
        )
        for endplate in endplates_for(vertebra):
            axis.plot(
                [endplate.left.x, endplate.right.x],
                [endplate.left.y, endplate.right.y],
                color="#f7d154",
                linewidth=max(1, line_width - 1),
                alpha=0.75,
            )
        axis.text(
            min(point.x for point in points) - 5,
            sum(point.y for point in points) / 4,
            vertebra.label,
            color="white",
            fontsize=7,
            horizontalalignment="right",
            verticalalignment="center",
            bbox={"facecolor": "black", "alpha": 0.45, "pad": 1, "edgecolor": "none"},
        )

    colors = ("#ff3b30", "#34c759")
    for color, endplate in zip(
        colors, (measurement.upper_endplate, measurement.lower_endplate), strict=True
    ):
        axis.plot(
            [endplate.left.x, endplate.right.x],
            [endplate.left.y, endplate.right.y],
            color=color,
            linewidth=line_width + 1,
            zorder=4,
        )

    axis.set_title(
        f"Cobb angle: {measurement.angle_degrees:.2f}°\n"
        f"{measurement.upper_endplate.vertebra_label} → "
        f"{measurement.lower_endplate.vertebra_label}",
        fontsize=12,
    )
    axis.set_axis_off()
    return figure


def save_annotated_image(
    output_path: Path,
    image: NDArray[np.uint8],
    study: StudyLandmarks,
    measurement: CobbMeasurement,
    *,
    landmark_radius: int = 4,
    line_width: int = 2,
    dpi: int = 150,
) -> Path:
    """Render and atomically save a PNG visualization."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = create_annotated_figure(
        image,
        study,
        measurement,
        landmark_radius=landmark_radius,
        line_width=line_width,
    )
    temporary = output_path.with_name(f"{output_path.stem}.tmp{output_path.suffix}")
    figure.savefig(temporary, dpi=dpi, format=output_path.suffix.lstrip(".") or "png")
    temporary.replace(output_path)
    figure.clear()
    return output_path
