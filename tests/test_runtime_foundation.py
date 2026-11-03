from fastapi.testclient import TestClient
import tomllib
from pathlib import Path

import townlight_access
from townlight_access.main import app


client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]


def test_package_version_is_040() -> None:
    assert townlight_access.__version__ == "0.5.0"


def test_pyproject_uses_coordinated_townlight_core_candidate() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = data["project"]["dependencies"]

    assert data["tool"]["hatch"]["metadata"]["allow-direct-references"] is True
    assert "townlight-core==1.3.0.dev2" in dependencies
    assert "townlight_core==1.1.0" not in dependencies
    assert "townlight_core==1.0.0" not in dependencies


def test_root_endpoint_states_runtime_boundary() -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()

    assert payload["name"] == "Townlight Access"
    assert payload["version"] == "0.5.0"
    assert payload["status"] == "standalone readiness candidate"
    assert "staff interfaces" in payload["message"]
    assert "does not provide legal advice" in payload["message"]
    assert "/townlight_access/staff" in payload["next_step"]


def test_health_endpoint_reports_versions() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["service"] == "townlight_access"
    assert payload["version"] == "0.5.0"
    assert payload["townlight_core_version"] == "1.3.0.dev2"
