"""Phase A city-core hardening proofs: write authz (#2), audit events (#3), backup/restore (#4)."""

from __future__ import annotations

import shutil

from fastapi.testclient import TestClient

import townlight_access.main as main_module
from townlight_access.access_review import AccessibilityReviewRepository
from townlight_access.main import app


client = TestClient(app)

VALID_HEADER = {"X-Townlight-Access-Write-Token": "test-write-token"}
WRONG_HEADER = {"X-Townlight-Access-Write-Token": "not-the-token"}
REVIEW_BODY = {"title": "Notice", "body": "A public notice.", "has_alt_text": True, "language": "en"}


# --- probe gap #2: persistent writes require the trusted-write token -------------------------------

def test_review_write_rejects_missing_and_wrong_token(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TOWNLIGHT_ACCESS_REVIEW_DB_URL", f"sqlite:///{tmp_path / 'authz.db'}")
    try:
        no_token = client.post("/api/v1/townlight_access/review", json=REVIEW_BODY)
        wrong_token = client.post("/api/v1/townlight_access/review", json=REVIEW_BODY, headers=WRONG_HEADER)
        ok = client.post("/api/v1/townlight_access/review", json=REVIEW_BODY, headers=VALID_HEADER)
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert no_token.status_code == 403
    assert "missing or invalid" in no_token.json()["detail"]["message"]
    assert wrong_token.status_code == 403
    assert ok.status_code == 200
    assert ok.json()["review_id"]


def test_records_export_write_requires_token(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TOWNLIGHT_ACCESS_REVIEW_DB_URL", f"sqlite:///{tmp_path / 'authz-export.db'}")
    try:
        created = client.post("/api/v1/townlight_access/review", json=REVIEW_BODY, headers=VALID_HEADER)
        review_id = created.json()["review_id"]
        no_token = client.post(f"/api/v1/townlight_access/reviews/{review_id}/records-export")
        ok = client.post(
            f"/api/v1/townlight_access/reviews/{review_id}/records-export", headers=VALID_HEADER
        )
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert no_token.status_code == 403
    assert ok.status_code == 200
    assert ok.json()["status"] == "records-export-ready"


def test_write_guard_not_configured_returns_503(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TOWNLIGHT_ACCESS_REVIEW_DB_URL", f"sqlite:///{tmp_path / 'authz-unset.db'}")
    monkeypatch.delenv("TOWNLIGHT_ACCESS_TRUSTED_WRITE_TOKEN", raising=False)
    try:
        response = client.post("/api/v1/townlight_access/review", json=REVIEW_BODY, headers=VALID_HEADER)
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert response.status_code == 503
    assert "TOWNLIGHT_ACCESS_TRUSTED_WRITE_TOKEN" in response.json()["detail"]["fix"]


def test_analyze_is_open_and_never_persists(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TOWNLIGHT_ACCESS_REVIEW_DB_URL", f"sqlite:///{tmp_path / 'analyze.db'}")
    try:
        response = client.post("/api/v1/townlight_access/analyze", json=REVIEW_BODY)
        listed = client.get("/api/v1/townlight_access/reviews")
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    assert response.status_code == 200
    assert response.json()["persisted"] is False
    assert listed.json()["count"] == 0  # analyze wrote nothing


# --- probe gap #3: audit events emitted + persisted on writes/exports ------------------------------

def test_audit_event_persisted_on_review_create(tmp_path) -> None:
    repository = AccessibilityReviewRepository(db_url=f"sqlite:///{tmp_path / 'audit.db'}")
    try:
        stored = repository.create_review(title="N", body="text", has_alt_text=True, language="en")
        events = repository.list_audit_events()
    finally:
        repository.engine.dispose()

    assert len(events) == 1
    assert events[0]["action"] == "review.create"
    assert events[0]["subject_id"] == stored.review_id
    assert events[0]["actor"] == "shared-token-staff"
    assert events[0]["created_at"] is not None


def test_audit_event_persisted_on_records_export(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TOWNLIGHT_ACCESS_REVIEW_DB_URL", f"sqlite:///{tmp_path / 'audit-export.db'}")
    try:
        created = client.post("/api/v1/townlight_access/review", json=REVIEW_BODY, headers=VALID_HEADER)
        review_id = created.json()["review_id"]
        client.post(
            f"/api/v1/townlight_access/reviews/{review_id}/records-export", headers=VALID_HEADER
        )
        events = main_module._get_review_repository().list_audit_events()
    finally:
        main_module._dispose_review_repository()
        main_module._review_db_url = None

    actions = {event["action"] for event in events}
    assert "review.create" in actions
    assert "review.records_export" in actions


# --- probe gap #4: data survives a backup -> restore round-trip ------------------------------------

def test_backup_restore_roundtrip_preserves_records_and_audit(tmp_path) -> None:
    """SQLite dev-fallback durability: back up the live Data dir, lose it, restore, reload.

    The Postgres default store's durability is proven separately in
    tests/test_postgres_persistence.py::test_postgres_review_and_audit_survive_reconnect.
    """

    db_path = tmp_path / "data" / "townlight_access-reviews.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    repository = AccessibilityReviewRepository(db_url=f"sqlite:///{db_path}")
    stored = repository.create_review(title="Hearing", body="text", has_alt_text=True, language="en")

    # Supervisor backup = recursive file copy of the Data dir, taken while the service is live.
    backup_path = tmp_path / "backup" / "townlight_access-reviews.db"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(db_path, backup_path)
    repository.engine.dispose()

    # Lose the live data, then restore from the backup copy.
    db_path.unlink()
    shutil.copy2(backup_path, db_path)

    restored = AccessibilityReviewRepository(db_url=f"sqlite:///{db_path}")
    try:
        reloaded = restored.get_review(stored.review_id)
        audit = restored.list_audit_events()
    finally:
        restored.engine.dispose()

    assert reloaded is not None
    assert reloaded.review_id == stored.review_id
    assert reloaded.status == stored.status
    assert any(event["subject_id"] == stored.review_id for event in audit)
