import subprocess
import sys

from fastapi.testclient import TestClient

import civicaccess.main as main_module
from civicaccess.access_review import SCHEMA_VERSION, AccessibilityReviewRepository
from civicaccess.main import app


client = TestClient(app)


def test_accessibility_review_records_persist_findings(tmp_path) -> None:
    db_path = tmp_path / "reviews.db"
    repository = AccessibilityReviewRepository(db_url=f"sqlite:///{db_path}")

    stored = repository.create_review(
        title="",
        body="Short public notice.",
        has_alt_text=False,
        language="en",
    )
    repository.engine.dispose()

    second_repository = AccessibilityReviewRepository(db_url=f"sqlite:///{db_path}")
    try:
        reloaded = second_repository.get_review(stored.review_id)
    finally:
        second_repository.engine.dispose()

    assert reloaded is not None
    assert reloaded.status == "needs-fixes"
    assert [finding.code for finding in reloaded.findings] == ["missing-title", "missing-alt-text"]
    db_path.unlink()


def test_review_repository_records_schema_status(tmp_path) -> None:
    db_path = tmp_path / "schema-status.db"
    repository = AccessibilityReviewRepository(db_url=f"sqlite:///{db_path}")
    try:
        status = repository.schema_status()
    finally:
        repository.engine.dispose()

    assert status.ready is True
    assert status.schema_version == SCHEMA_VERSION
    assert status.expected_schema_version == SCHEMA_VERSION
    assert status.missing_tables == ()
    assert status.dialect == "sqlite"


def test_db_status_cli_reports_ready_schema(tmp_path) -> None:
    db_path = tmp_path / "schema-cli.db"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "civicaccess.db_admin",
            "--db-url",
            f"sqlite:///{db_path}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "CivicAccess schema ready" in result.stdout
    assert f"version={SCHEMA_VERSION}" in result.stdout
    assert "missing_tables=none" in result.stdout


def test_api_persists_and_retrieves_review_records(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "api-reviews.db"
    monkeypatch.setenv("CIVICACCESS_REVIEW_DB_URL", f"sqlite:///{db_path}")

    try:
        create_response = client.post(
            "/api/v1/civicaccess/review",
            json={"title": "", "body": "A public notice.", "has_alt_text": False, "language": "en"},
            headers={"X-CivicAccess-Write-Token": "test-write-token"},
        )
        review_id = create_response.json()["review_id"]
        get_response = client.get(f"/api/v1/civicaccess/reviews/{review_id}")
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert create_response.status_code == 200
    assert review_id
    assert create_response.json()["status"] == "needs-fixes"
    assert get_response.status_code == 200
    assert get_response.json()["review_id"] == review_id
    assert get_response.json()["findings"][0]["code"] == "missing-title"
    assert get_response.json()["next_steps"]
    db_path.unlink()


def test_default_local_database_makes_readiness_ready(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("CIVICACCESS_REVIEW_DB_URL", raising=False)
    monkeypatch.setenv("CIVICACCESS_DATA_DIR", str(tmp_path / "civicaccess-data"))

    try:
        response = client.get("/api/v1/civicaccess/readiness")
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["ready"] is True
    assert payload["review_database_configured"] is True
    assert payload["schema_ready"] is True
    assert payload["blockers"] == []
    assert "civicaccess-reviews.db" in payload["review_database_url"]


def test_readiness_passes_with_configured_schema(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "ready-runtime.db"
    monkeypatch.setenv("CIVICACCESS_REVIEW_DB_URL", f"sqlite:///{db_path}")

    try:
        response = client.get("/ready")
        repository = main_module._get_review_repository()
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["ready"] is True
    assert payload["review_database_configured"] is True
    assert payload["schema_ready"] is True
    assert payload["review_count"] == 0
    assert payload["blockers"] == []
    repository.engine.dispose()


def test_review_record_lookup_reports_missing_record(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "missing-review.db"
    monkeypatch.setenv("CIVICACCESS_REVIEW_DB_URL", f"sqlite:///{db_path}")

    try:
        response = client.get("/api/v1/civicaccess/reviews/00000000-0000-4000-8000-000000000000")
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert response.status_code == 404
    assert "Use a review_id returned by POST" in response.json()["detail"]["fix"]
    db_path.unlink()


def test_review_record_lookup_uses_default_database(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("CIVICACCESS_REVIEW_DB_URL", raising=False)
    monkeypatch.setenv("CIVICACCESS_DATA_DIR", str(tmp_path / "default-data"))

    try:
        response = client.get("/api/v1/civicaccess/reviews/not-configured")
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert response.status_code == 404
    assert "Use a review_id returned by POST" in response.json()["detail"]["fix"]


def test_review_list_and_records_export_contract(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "api-review-list.db"
    monkeypatch.setenv("CIVICACCESS_REVIEW_DB_URL", f"sqlite:///{db_path}")

    try:
        create_response = client.post(
            "/api/v1/civicaccess/review",
            json={
                "title": "Budget hearing notice",
                "body": "Residents may ask for help before the hearing.",
                "has_alt_text": True,
                "language": "en",
            },
            headers={"X-CivicAccess-Write-Token": "test-write-token"},
        )
        review_id = create_response.json()["review_id"]
        list_response = client.get("/api/v1/civicaccess/reviews")
        export_response = client.post(
            f"/api/v1/civicaccess/reviews/{review_id}/records-export",
            headers={"X-CivicAccess-Write-Token": "test-write-token"},
        )
        contracts_response = client.get("/api/v1/civicaccess/integration-contracts")
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert create_response.status_code == 200
    assert list_response.status_code == 200
    assert list_response.json()["reviews"][0]["review_id"] == review_id
    assert export_response.status_code == 200
    export_payload = export_response.json()
    assert export_payload["status"] == "records-export-ready"
    assert export_payload["target_module"] == "civicrecords-ai"
    assert export_payload["provenance"]["source_text_preserved"] is True
    contracts = contracts_response.json()
    assert contracts["status"] == "ok"
    assert "civicpermit applicant forms" in contracts["downstream_ready_for"]
    db_path.unlink()
