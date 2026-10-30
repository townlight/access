"""Deterministic accessibility review helpers for CivicAccess."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine


@dataclass(frozen=True)
class AccessibilityFinding:
    code: str
    severity: str
    message: str
    fix: str
    wcag_reference: str


@dataclass(frozen=True)
class AccessibilityReview:
    status: str
    findings: tuple[AccessibilityFinding, ...]
    disclaimer: str
    next_steps: tuple[str, ...]


@dataclass(frozen=True)
class StoredAccessibilityReview:
    review_id: str
    title: str
    body: str
    has_alt_text: bool
    language: str
    status: str
    findings: tuple[AccessibilityFinding, ...]
    disclaimer: str
    created_at: datetime


DISCLAIMER = (
    "Accessibility review is advisory support only; it does not replace legal review, "
    "a certified accessibility audit, or an ADA coordinator's decision."
)


metadata = sa.MetaData()

SCHEMA_VERSION = "civicaccess-windows-local-state-v1"

accessibility_review_records = sa.Table(
    "accessibility_review_records",
    metadata,
    sa.Column("review_id", sa.String(36), primary_key=True),
    sa.Column("title", sa.String(500), nullable=False),
    sa.Column("body", sa.Text(), nullable=False),
    sa.Column("has_alt_text", sa.Boolean(), nullable=False),
    sa.Column("language", sa.String(80), nullable=False),
    sa.Column("status", sa.String(80), nullable=False),
    sa.Column("findings", sa.JSON(), nullable=False),
    sa.Column("disclaimer", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicaccess",
)

audit_events = sa.Table(
    "audit_events",
    metadata,
    sa.Column("event_id", sa.String(36), primary_key=True),
    sa.Column("action", sa.String(80), nullable=False),
    sa.Column("subject_id", sa.String(80), nullable=True),
    sa.Column("actor", sa.String(120), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicaccess",
)

schema_migrations = sa.Table(
    "schema_migrations",
    metadata,
    sa.Column("schema_version", sa.String(40), primary_key=True),
    sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicaccess",
)


@dataclass(frozen=True)
class SchemaStatus:
    schema_version: str | None
    expected_schema_version: str
    ready: bool
    missing_tables: tuple[str, ...]
    dialect: str


class AccessibilityReviewRepository:
    """SQLAlchemy-backed accessibility review records for local publication workflows."""

    def __init__(self, *, db_url: str | None = None, engine: Engine | None = None) -> None:
        base_engine = engine or create_engine(db_url or "sqlite+pysqlite:///:memory:", future=True)
        if base_engine.dialect.name == "sqlite":
            self.engine = base_engine.execution_options(schema_translate_map={"civicaccess": None})
        else:
            self.engine = base_engine
            with self.engine.begin() as connection:
                connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS civicaccess"))
        self.migrate()

    def migrate(self) -> SchemaStatus:
        """Apply non-destructive local schema setup and return the resulting status."""

        metadata.create_all(self.engine)
        with self.engine.begin() as connection:
            exists = connection.execute(
                sa.select(schema_migrations.c.schema_version).where(
                    schema_migrations.c.schema_version == SCHEMA_VERSION
                )
            ).first()
            if exists is None:
                connection.execute(
                    schema_migrations.insert().values(
                        schema_version=SCHEMA_VERSION,
                        applied_at=datetime.now(UTC),
                    )
                )
        return self.schema_status()

    def schema_status(self) -> SchemaStatus:
        inspector = sa.inspect(self.engine)
        translated_schema = None if self.engine.dialect.name == "sqlite" else "civicaccess"
        available_tables = set(inspector.get_table_names(schema=translated_schema))
        expected_tables = {"accessibility_review_records", "audit_events", "schema_migrations"}
        missing_tables = tuple(sorted(expected_tables - available_tables))
        schema_version = None
        if "schema_migrations" not in missing_tables:
            with self.engine.begin() as connection:
                schema_version = connection.execute(
                    sa.select(schema_migrations.c.schema_version)
                    .order_by(schema_migrations.c.applied_at.desc())
                    .limit(1)
                ).scalar_one_or_none()
        return SchemaStatus(
            schema_version=schema_version,
            expected_schema_version=SCHEMA_VERSION,
            ready=schema_version == SCHEMA_VERSION and not missing_tables,
            missing_tables=missing_tables,
            dialect=self.engine.dialect.name,
        )

    def review_count(self) -> int:
        with self.engine.begin() as connection:
            return connection.execute(sa.select(sa.func.count()).select_from(accessibility_review_records)).scalar_one()

    def create_review(
        self, *, title: str, body: str, has_alt_text: bool, language: str, actor: str = "staff"
    ) -> StoredAccessibilityReview:
        review = review_accessibility(
            title=title,
            body=body,
            has_alt_text=has_alt_text,
            language=language,
        )
        stored = StoredAccessibilityReview(
            review_id=str(uuid4()),
            title=title,
            body=body,
            has_alt_text=has_alt_text,
            language=language,
            status=review.status,
            findings=review.findings,
            disclaimer=review.disclaimer,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                accessibility_review_records.insert().values(
                    review_id=stored.review_id,
                    title=stored.title,
                    body=stored.body,
                    has_alt_text=stored.has_alt_text,
                    language=stored.language,
                    status=stored.status,
                    findings=[_finding_to_dict(finding) for finding in stored.findings],
                    disclaimer=stored.disclaimer,
                    created_at=stored.created_at,
                )
            )
            # Audit the write in the same transaction so the trail cannot drift from the record.
            self.record_audit_event(
                action="review.create",
                subject_id=stored.review_id,
                actor=actor,
                connection=connection,
            )
        return stored

    def record_audit_event(
        self,
        *,
        action: str,
        subject_id: str | None = None,
        actor: str = "staff",
        connection: object | None = None,
    ) -> str:
        """Persist a who/what/when audit row for a write or export action."""

        event_id = str(uuid4())
        statement = audit_events.insert().values(
            event_id=event_id,
            action=action,
            subject_id=subject_id,
            actor=actor,
            created_at=datetime.now(UTC),
        )
        if connection is not None:
            connection.execute(statement)
        else:
            with self.engine.begin() as own_connection:
                own_connection.execute(statement)
        return event_id

    def list_audit_events(self, *, limit: int = 50) -> tuple[dict[str, object], ...]:
        bounded_limit = max(1, min(limit, 200))
        with self.engine.begin() as connection:
            rows = connection.execute(
                sa.select(audit_events)
                .order_by(audit_events.c.created_at.desc())
                .limit(bounded_limit)
            ).mappings().all()
        return tuple(dict(row) for row in rows)

    def get_review(self, review_id: str) -> StoredAccessibilityReview | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(accessibility_review_records).where(
                    accessibility_review_records.c.review_id == review_id
                )
            ).mappings().first()
        if row is None:
            return None
        return _row_to_stored_review(row)

    def list_reviews(self, *, limit: int = 25) -> tuple[StoredAccessibilityReview, ...]:
        bounded_limit = max(1, min(limit, 100))
        with self.engine.begin() as connection:
            rows = connection.execute(
                sa.select(accessibility_review_records)
                .order_by(accessibility_review_records.c.created_at.desc())
                .limit(bounded_limit)
            ).mappings().all()
        return tuple(_row_to_stored_review(row) for row in rows)


def review_accessibility(*, title: str, body: str, has_alt_text: bool, language: str) -> AccessibilityReview:
    """Return deterministic sample accessibility findings without live LLM calls."""

    findings: list[AccessibilityFinding] = []
    if not body.strip():
        findings.append(
            AccessibilityFinding(
                code="missing-body",
                severity="high",
                message="The public text is empty.",
                fix="Add the resident-facing text before running an accessibility review.",
                wcag_reference="WCAG 3.1.5 Reading Level",
            )
        )
    if not title.strip():
        findings.append(
            AccessibilityFinding(
                code="missing-title",
                severity="high",
                message="The document needs a descriptive title.",
                fix="Add a short title that names the service, deadline, or public action.",
                wcag_reference="WCAG 2.4.2 Page Titled",
            )
        )
    if not has_alt_text:
        findings.append(
            AccessibilityFinding(
                code="missing-alt-text",
                severity="high",
                message="At least one image or visual element is missing alternative text.",
                fix="Add concise alt text that explains the purpose of the visual, or mark decorative images as decorative.",
                wcag_reference="WCAG 1.1.1 Non-text Content",
            )
        )
    if len(body.split()) > 80:
        findings.append(
            AccessibilityFinding(
                code="long-copy",
                severity="medium",
                message="The sample text is long enough to need headings or a plain-language summary.",
                fix="Break the content into sections and add a plain-language summary before the detailed text.",
                wcag_reference="WCAG 3.1.5 Reading Level",
            )
        )
    if language.strip().lower() not in {"en", "english"}:
        findings.append(
            AccessibilityFinding(
                code="language-confirmation",
                severity="medium",
                message="The document language should be declared and checked by a qualified reviewer.",
                fix="Set the document language metadata and confirm the translation with a human reviewer.",
                wcag_reference="WCAG 3.1.1 Language of Page",
            )
        )

    return AccessibilityReview(
        status="needs-fixes" if findings else "passes-sample-checks",
        findings=tuple(findings),
        disclaimer=DISCLAIMER,
        next_steps=(
            "Resolve each high-severity finding before publication.",
            "Have staff or an ADA coordinator review the final publication decision.",
            "Preserve the review record with the source content and publication package.",
        ),
    )


def _finding_to_dict(finding: AccessibilityFinding) -> dict[str, str]:
    return {
        "code": finding.code,
        "severity": finding.severity,
        "message": finding.message,
        "fix": finding.fix,
        "wcag_reference": finding.wcag_reference,
    }


def _findings_from_records(records: Iterable[dict[str, str]]) -> tuple[AccessibilityFinding, ...]:
    return tuple(AccessibilityFinding(**record) for record in records)


def _row_to_stored_review(row: object) -> StoredAccessibilityReview:
    data = dict(row)
    return StoredAccessibilityReview(
        review_id=data["review_id"],
        title=data["title"],
        body=data["body"],
        has_alt_text=data["has_alt_text"],
        language=data["language"],
        status=data["status"],
        findings=_findings_from_records(data["findings"]),
        disclaimer=data["disclaimer"],
        created_at=data["created_at"],
    )
