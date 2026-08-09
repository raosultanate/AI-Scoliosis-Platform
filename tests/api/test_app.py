"""End-to-end tests for the initial FastAPI application boundary."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scoliosis_platform.api import ApiSettings, create_app


def _client(project_root: Path, output_root: Path) -> TestClient:
    app = create_app(ApiSettings(project_root=project_root, output_root=output_root))
    return TestClient(app)


def test_health_endpoint(fixture_directory: Path, tmp_path: Path) -> None:
    with _client(fixture_directory.parents[1], tmp_path / "outputs") as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ai-scoliosis-platform"}


def test_public_website_and_assets_are_served(
    fixture_directory: Path, tmp_path: Path
) -> None:
    with _client(fixture_directory.parents[1], tmp_path / "outputs") as client:
        page = client.get("/")
        script = client.get("/assets/app.js")

    assert page.status_code == 200
    assert "What is the Cobb angle in this X-ray?" in page.text
    assert 'id="xray-input"' in page.text
    assert script.status_code == 200
    assert script.headers["content-type"].startswith("text/javascript")


def test_capabilities_are_honest_about_model_readiness(
    fixture_directory: Path, tmp_path: Path
) -> None:
    with _client(fixture_directory.parents[1], tmp_path / "outputs") as client:
        response = client.get("/api/v1/capabilities")

    assert response.status_code == 200
    assert response.json() == {
        "mode": "synthetic_demo",
        "real_xray_upload_enabled": False,
        "automated_landmark_detection": False,
        "accepted_image_types": ["image/png", "image/jpeg"],
        "max_upload_size_mb": 10,
        "message": (
            "The browser can preview an X-ray locally, but automated landmark detection "
            "is not connected yet. The bundled synthetic demonstration is available."
        ),
    }


def test_synthetic_case_runs_through_api(fixture_directory: Path, tmp_path: Path) -> None:
    with _client(fixture_directory.parents[1], tmp_path / "outputs") as client:
        response = client.post("/api/v1/demo/synthetic")
        assert response.status_code == 201
        payload = response.json()

        assert payload["status"] == "completed"
        assert payload["measurement"]["cobb_angle_degrees"] == pytest.approx(30.0, abs=0.001)
        assert payload["measurement"]["upper_endplate"]["vertebra_label"] == "T4"
        assert payload["measurement"]["lower_endplate"]["vertebra_label"] == "T12"
        assert payload["measurement"]["validation"]["within_tolerance"] is True
        assert "Research software" in payload["measurement"]["disclaimer"]

        annotated = client.get(payload["artifacts"]["annotated_image_url"])
        measurement = client.get(payload["artifacts"]["measurement_json_url"])
        report = client.get(payload["artifacts"]["markdown_report_url"])

    assert annotated.status_code == 200
    assert annotated.headers["content-type"] == "image/png"
    assert annotated.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert measurement.status_code == 200
    assert measurement.json()["cobb_angle_degrees"] == pytest.approx(30.0, abs=0.001)
    assert report.status_code == 200
    assert "Calculated Cobb angle: **30.00°**" in report.text
