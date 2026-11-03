import hashlib
import json

from fastapi.testclient import TestClient

from townlight_access.main import app
from townlight_access.record_artifact import build_record_artifact


def test_export_contains_the_actual_source_findings_and_actor_provenance():
    client = TestClient(app)
    headers = {"X-Townlight-Access-Write-Token": "test-write-token"}
    source = "The hearing begins on Friday at 6 p.m. Bring your written comments."
    saved = client.post("/api/v1/townlight_access/review", headers=headers, json={
        "title": "Hearing", "body": source, "has_alt_text": False, "language": "en",
    })
    assert saved.status_code == 200
    response = client.post(
        f"/api/v1/townlight_access/reviews/{saved.json()['review_id']}/records-export", headers=headers,
    )
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert hashlib.sha256(artifact["content"].encode()).hexdigest() == artifact["sha256"]
    record = json.loads(artifact["content"].split("```json\n", 1)[1].rsplit("\n```", 1)[0])
    assert record["review"]["body"] == source
    assert record["review"]["findings"][0]["code"] == "missing-alt-text"
    assert record["audit_events"]
    assert all(event["actor"] == "shared-token-staff" for event in record["audit_events"])
    assert record["identity_scope"] == "shared token; individual identity not established"


def test_artifact_keeps_markup_as_data_without_changing_source():
    source = "```\n<script>alert('sample')</script>\nRÃ©sumÃ©"
    artifact = build_record_artifact({"source": source})
    assert "<script>" not in artifact["content"]
    record = json.loads(artifact["content"].split("```json\n", 1)[1].rsplit("\n```", 1)[0])
    assert record["source"] == source
