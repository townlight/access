"""PostgreSQL persistence coverage. Gated on TOWNLIGHT_ACCESS_POSTGRES_TEST_URL (the release gate)."""

from __future__ import annotations

import os

import pytest
import sqlalchemy as sa

from townlight_access.access_review import AccessibilityReviewRepository


@pytest.mark.skipif(
    not os.environ.get("TOWNLIGHT_ACCESS_POSTGRES_TEST_URL"),
    reason="TOWNLIGHT_ACCESS_POSTGRES_TEST_URL is required for PostgreSQL persistence coverage.",
)
def test_postgres_persistence_creates_schema_and_round_trips_reviews() -> None:
    db_url = os.environ["TOWNLIGHT_ACCESS_POSTGRES_TEST_URL"]
    engine = sa.create_engine(db_url, future=True)
    with engine.begin() as connection:
        connection.execute(sa.text("DROP SCHEMA IF EXISTS townlight_access CASCADE"))
    engine.dispose()

    repository = AccessibilityReviewRepository(db_url=db_url)
    stored = repository.create_review(
        title="Budget hearing notice",
        body="Residents may ask for help before the hearing.",
        has_alt_text=True,
        language="en",
    )
    repository.record_audit_event(action="review.records_export", subject_id=stored.review_id)

    reloaded = repository.get_review(stored.review_id)
    assert reloaded is not None
    assert reloaded.review_id == stored.review_id
    assert reloaded.title == "Budget hearing notice"

    actions = {event["action"] for event in repository.list_audit_events()}
    assert actions == {"review.create", "review.records_export"}

    status = repository.schema_status()
    assert status.ready is True
    assert status.dialect == "postgresql"

    with repository.engine.begin() as connection:
        schema_exists = connection.execute(
            sa.text(
                "select exists(select 1 from information_schema.schemata "
                "where schema_name='townlight_access')"
            )
        ).scalar_one()
    repository.engine.dispose()
    assert schema_exists is True


@pytest.mark.skipif(
    not os.environ.get("TOWNLIGHT_ACCESS_POSTGRES_TEST_URL"),
    reason="TOWNLIGHT_ACCESS_POSTGRES_TEST_URL is required for PostgreSQL persistence coverage.",
)
def test_postgres_review_and_audit_survive_reconnect() -> None:
    """Durability proof for the DEFAULT store: data persists in the cluster across a fresh engine.

    This is the property the desktop supervisor's wholesale Data/postgres backup relies on; the
    end-to-end supervisor backup/restore is exercised on a clean VM in Phase D.
    """

    db_url = os.environ["TOWNLIGHT_ACCESS_POSTGRES_TEST_URL"]
    engine = sa.create_engine(db_url, future=True)
    with engine.begin() as connection:
        connection.execute(sa.text("DROP SCHEMA IF EXISTS townlight_access CASCADE"))
    engine.dispose()

    repository = AccessibilityReviewRepository(db_url=db_url)
    stored = repository.create_review(
        title="Durable", body="text", has_alt_text=True, language="en"
    )
    repository.record_audit_event(action="review.records_export", subject_id=stored.review_id)
    repository.engine.dispose()  # drop the connection/engine â€” simulate a process restart

    reconnected = AccessibilityReviewRepository(db_url=db_url)
    try:
        reloaded = reconnected.get_review(stored.review_id)
        actions = {event["action"] for event in reconnected.list_audit_events()}
    finally:
        reconnected.engine.dispose()

    assert reloaded is not None
    assert reloaded.review_id == stored.review_id
    assert {"review.create", "review.records_export"} <= actions
