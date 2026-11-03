"""Coverage for the Phase A persistence default: DATABASE_URL -> sync Postgres, SQLite fallback."""

from __future__ import annotations

import pytest
from sqlalchemy.engine import make_url

import townlight_access.main as main_module


@pytest.mark.parametrize(
    "raw",
    [
        "postgresql+asyncpg://townlight:abc123@127.0.0.1:15432/townlight",
        "postgres+asyncpg://u:p@h:15432/db",
        "postgresql://u:p@h:5432/db",
        "postgres://u:p@h/db",
    ],
)
def test_sync_database_url_flips_scheme_to_psycopg2(raw) -> None:
    src = make_url(raw)
    out = make_url(main_module._sync_database_url(raw))
    assert out.drivername == "postgresql+psycopg2"
    # Everything except the driver must be preserved exactly.
    assert (out.username, out.password, out.host, out.port, out.database) == (
        src.username,
        src.password,
        src.host,
        src.port,
        src.database,
    )


def test_sync_database_url_passes_through_sqlite() -> None:
    assert main_module._sync_database_url("sqlite:///x/y.db") == "sqlite:///x/y.db"


def test_sync_database_url_preserves_credentials_with_marker_substrings() -> None:
    # A password/dbname containing scheme-marker text must survive (no global str.replace mangling).
    raw = make_url("postgresql+asyncpg://u:pw@h:15432/db").set(
        password="x-postgres+asyncpg-y"
    )
    out = make_url(main_module._sync_database_url(raw.render_as_string(hide_password=False)))
    assert out.drivername == "postgresql+psycopg2"
    assert out.password == "x-postgres+asyncpg-y"
    assert out.database == "db"


def test_review_database_url_prefers_supervisor_postgres(monkeypatch) -> None:
    monkeypatch.delenv("TOWNLIGHT_ACCESS_REVIEW_DB_URL", raising=False)
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://townlight:pw@127.0.0.1:15432/townlight"
    )
    assert (
        main_module._review_database_url()
        == "postgresql+psycopg2://townlight:pw@127.0.0.1:15432/townlight"
    )


def test_review_database_url_override_wins_over_supervisor(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://townlight:pw@127.0.0.1:15432/townlight"
    )
    monkeypatch.setenv(
        "TOWNLIGHT_ACCESS_REVIEW_DB_URL", "postgresql+psycopg2://o:o@h:5432/override"
    )
    assert main_module._review_database_url() == "postgresql+psycopg2://o:o@h:5432/override"


def test_review_database_url_falls_back_to_sqlite(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("TOWNLIGHT_ACCESS_REVIEW_DB_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("TOWNLIGHT_ACCESS_DATA_DIR", str(tmp_path / "data"))
    url = main_module._review_database_url()
    assert url.startswith("sqlite:///")
    assert "townlight_access-reviews.db" in url
