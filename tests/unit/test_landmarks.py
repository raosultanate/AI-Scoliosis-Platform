"""Tests for canonical and legacy annotation adapters."""

from __future__ import annotations

from pathlib import Path

import pytest

from scoliosis_platform.dataset.landmarks import load_landmarks
from scoliosis_platform.domain import CoordinateSpace


def test_load_json_and_scale_normalized_coordinates(fixture_directory: Path) -> None:
    study = load_landmarks(fixture_directory / "synthetic_landmarks.json")
    assert study.coordinate_space is CoordinateSpace.NORMALIZED
    scaled = study.to_pixels(width=500, height=1000)
    assert scaled.vertebrae[0].top_left.x == pytest.approx(200.0)
    assert scaled.vertebrae[0].top_left.y == pytest.approx(186.603)


def test_load_csv_auto_detects_pixels(tmp_path: Path) -> None:
    annotation = tmp_path / "landmarks.csv"
    annotation.write_text(
        "label,ordinal,top_left_x,top_left_y,top_right_x,top_right_y,"
        "bottom_left_x,bottom_left_y,bottom_right_x,bottom_right_y\n"
        "T4,0,10,20,30,20,10,40,30,40\n",
        encoding="utf-8",
    )
    study = load_landmarks(annotation)
    assert study.coordinate_space is CoordinateSpace.PIXEL
    assert study.vertebrae[0].label == "T4"


def test_flat_text_requires_four_points_per_vertebra(tmp_path: Path) -> None:
    annotation = tmp_path / "bad.txt"
    annotation.write_text("0 0\n1 0\n0 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="multiple of four"):
        load_landmarks(annotation)
