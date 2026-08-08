"""Dataset input adapters for images and clinician landmarks."""

from scoliosis_platform.dataset.images import LoadedImage, load_image
from scoliosis_platform.dataset.landmarks import load_landmarks

__all__ = ["LoadedImage", "load_image", "load_landmarks"]
