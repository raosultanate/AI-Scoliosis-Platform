"""FastAPI application for the research scoliosis analysis service."""

from scoliosis_platform.api.app import app, create_app
from scoliosis_platform.api.settings import ApiSettings

__all__ = ["ApiSettings", "app", "create_app"]
