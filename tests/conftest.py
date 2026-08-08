"""Shared test fixtures for Version 1A."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fixture_directory() -> Path:
    """Return the repository's deterministic fixture directory."""

    return Path(__file__).parent / "fixtures"
