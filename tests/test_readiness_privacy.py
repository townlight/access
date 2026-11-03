"""Unauthenticated readiness must never disclose configured credentials."""
import json
from types import SimpleNamespace

import townlight_access.main as main


def test_both_public_readiness_responses_omit_database_connection_details(monkeypatch):
    url = 'postgresql+psycopg2://synthetic-user:synthetic-password@private-host/example'
    monkeypatch.setenv('TOWNLIGHT_ACCESS_REVIEW_DB_URL', url)
    monkeypatch.setattr(main, '_get_review_repository', lambda: SimpleNamespace(
        schema_status=lambda: SimpleNamespace(ready=True, schema_version='test', expected_schema_version='test'),
        review_count=lambda: 0))
    for endpoint in (main.ready, main.readiness):
        payload = endpoint()
        assert payload['ready'] is True
        assert 'review_database_url' not in payload
        encoded = json.dumps(payload)
        for value in ('synthetic-user', 'synthetic-password', 'private-host', url):
            assert value not in encoded
