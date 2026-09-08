from fastapi.testclient import TestClient
import tomllib
from pathlib import Path

import civicaccess
from civicaccess.main import app


client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]


def test_package_version_is_040() -> None:
    assert civicaccess.__version__ == "0.4.0"


def test_pyproject_uses_published_civiccore_release_wheel() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = data["project"]["dependencies"]

    assert data["tool"]["hatch"]["metadata"]["allow-direct-references"] is True
    assert (
        "civiccore @ https://github.com/townlight/core/releases/download/"
        "v1.2.0/civiccore-1.2.0-py3-none-any.whl#sha256=a94ce958e36fb03c8d961e4db4672ce5bcfa25765c57d75886e999cf15703ec7"
    ) in dependencies
    assert "civiccore==1.1.0" not in dependencies
    assert "civiccore==1.0.0" not in dependencies


def test_root_endpoint_states_runtime_boundary() -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()

    assert payload["name"] == "CivicAccess"
    assert payload["version"] == "0.4.0"
    assert payload["status"] == "standalone readiness candidate"
    assert "staff interfaces" in payload["message"]
    assert "does not provide legal advice" in payload["message"]
    assert "/civicaccess/staff" in payload["next_step"]


def test_health_endpoint_reports_versions() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["service"] == "civicaccess"
    assert payload["version"] == "0.4.0"
    assert payload["civiccore_version"] == "1.2.0"
