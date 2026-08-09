"""Radiograph image loading isolated behind a small OpenCV adapter.

OpenCV reads grayscale and common raster files reliably and is already part of the selected stack.
DICOM needs metadata-aware handling and is intentionally deferred rather than silently treating a
medical image as an ordinary bitmap.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray

SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


@dataclass(frozen=True, slots=True)
class LoadedImage:
    """Decoded grayscale image plus source metadata needed by later stages."""

    pixels: NDArray[np.uint8]
    path: Path

    @property
    def width(self) -> int:
        """Image width in pixels."""

        return int(self.pixels.shape[1])

    @property
    def height(self) -> int:
        """Image height in pixels."""

        return int(self.pixels.shape[0])


def load_image(path: Path) -> LoadedImage:
    """Load a supported radiograph as a two-dimensional uint8 grayscale array."""

    if path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
        raise ValueError(
            f"Unsupported image format '{path.suffix}'. Supported: "
            f"{', '.join(sorted(SUPPORTED_IMAGE_SUFFIXES))}"
        )
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    pixels = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if pixels is None:
        raise ValueError(f"OpenCV could not decode image: {path}")
    if pixels.ndim != 2 or pixels.size == 0:
        raise ValueError(f"Expected a non-empty grayscale image: {path}")
    typed_pixels: NDArray[np.uint8] = np.asarray(pixels, dtype=np.uint8)
    return LoadedImage(pixels=typed_pixels, path=path.resolve())
