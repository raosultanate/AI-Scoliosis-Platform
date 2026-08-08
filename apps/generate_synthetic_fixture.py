"""Generate a deterministic non-clinical image for smoke testing Version 1A."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def main() -> None:
    """Write `tests/fixtures/synthetic_xray.png` without modifying annotations."""

    root = Path(__file__).resolve().parents[1]
    output = root / "tests" / "fixtures" / "synthetic_xray.png"
    height, width = 1024, 512
    y_grid, x_grid = np.mgrid[0:height, 0:width]
    radial = np.sqrt(((x_grid - width / 2) / width) ** 2 + ((y_grid - height / 2) / height) ** 2)
    pixels = np.clip(35 + 85 * (1 - radial), 20, 120).astype(np.uint8)

    for index, y_center in enumerate(range(150, 850, 55)):
        x_center = int(width / 2 + 30 * np.sin(index / 2.4))
        cv2.ellipse(pixels, (x_center, y_center), (48, 17), 0, 0, 360, 175, -1)
        cv2.ellipse(pixels, (x_center, y_center), (48, 17), 0, 0, 360, 215, 1)
    cv2.putText(
        pixels,
        "SYNTHETIC - NOT CLINICAL",
        (55, 980),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        230,
        1,
        cv2.LINE_AA,
    )
    if not cv2.imwrite(str(output), pixels):
        raise RuntimeError(f"Could not write fixture to {output}")
    print(output)


if __name__ == "__main__":
    main()
