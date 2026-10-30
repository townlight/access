"""FastAPI runtime foundation for CivicAccess."""

import hmac
import os
from pathlib import Path

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.engine import make_url

from civicaccess import __version__
from civicaccess.access_review import (
    AccessibilityReviewRepository,
    StoredAccessibilityReview,
    review_accessibility,
)
from civicaccess.exports import build_accessible_export
from civicaccess.multilingual import create_language_variant
from civicaccess.plain_language import rewrite_plain_language
from civicaccess.public_ui import render_public_lookup_page, render_staff_page
from civicaccess.workflows import (
    build_accessible_form_plan,
    build_ada_title_ii_review_plan,
    build_publishing_workflow_plan,
    build_tagged_pdf_expectations,
)


app = FastAPI(
    title="CivicAccess",
    version=__version__,
    description="Accessibility, plain-language, multilingual, and ADA review support for CivicSuite.",
)

_review_repository: AccessibilityReviewRepository | None = None
_review_db_url: str | None = None


class AccessibilityReviewRequest(BaseModel):
    title: str = Field(default="", max_length=500)
    body: str = Field(max_length=5000)
    has_alt_text: bool = False
    language: str = Field(default="en", min_length=1, max_length=80)


class PlainLanguageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class LanguageVariantRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    language: str = Field(min_length=1, max_length=80)


class AccessibleExportRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    format: str = Field(default="html", min_length=1, max_length=40)


class AccessibleFormRequest(BaseModel):
    form_name: str = Field(default="", max_length=500)
    fields: list[str] = Field(default_factory=list, max_length=100)


class PublishingWorkflowRequest(BaseModel):
    title: str = Field(default="", max_length=500)
    has_review: bool = False
    has_plain_language: bool = False
    has_translation_review: bool = False


class AdaTitleIiReviewRequest(BaseModel):
    service_area: str = Field(default="", max_length=500)
    has_coordinator_review: bool = False


class TaggedPdfExpectationRequest(BaseModel):
    heading_levels: list[int] = Field(default_factory=list, max_length=200)


@app.get("/")
def root() -> dict[str, str]:
    """Return current product state without overstating unshipped behavior."""

    return {
        "name": "CivicAccess",
        "version": __version__,
        "status": "standalone readiness candidate",
        "message": (
            "CivicAccess provides local accessibility review support with accessible-form planning, publishing workflow checks, WCAG-aligned review records, plain-language rewrites, multilingual sample variants, ADA Title II review-support packages, tagged-PDF expectations, records-ready export checklists, and API-backed public and staff interfaces. "
            "It does not provide legal advice, certified ADA compliance, official translation certification, live LLM calls, or final publication approval."
        ),
        "next_step": "Open /civicaccess/staff to review saved publication work and export records-ready packages.",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return dependency/version health for deployment smoke checks."""

    return {
        "status": "ok",
        "service": "civicaccess",
        "version": __version__,
        "civiccore_version": CIVICCORE_VERSION,
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    fields = sorted(
        {
            ".".join(str(part) for part in error.get("loc", [])[1:])
            for error in exc.errors()
            if len(error.get("loc", [])) > 1
        }
    )
    field_list = ", ".join(fields) if fields else "request body"
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "message": f"CivicAccess could not validate: {field_list}.",
                "fix": (
                    "Send a JSON body that includes the required field names listed in "
                    "the fields array, using strings for text inputs and booleans for yes/no inputs."
                ),
                "fields": fields,
            }
        },
    )


@app.get("/ready")
def ready() -> dict[str, object]:
    """Return public-use readiness for local review-record persistence."""

    return _readiness_payload()


@app.get("/api/v1/civicaccess/readiness")
def readiness() -> dict[str, object]:
    """Return detailed CivicAccess local persistence readiness for operators."""

    return _readiness_payload()


@app.get("/civicaccess", response_class=HTMLResponse)
def public_civicaccess_page() -> str:
    """Return the accessible public sample UI."""

    return render_public_lookup_page()


@app.get("/civicaccess/staff", response_class=HTMLResponse)
def staff_civicaccess_page() -> str:
    """Return the staff publication review workspace.

    The page never embeds the server write token; the operator supplies it in the UI.
    """

    return render_staff_page()


@app.post("/api/v1/civicaccess/analyze")
def analyze_accessibility(request: AccessibilityReviewRequest) -> dict[str, object]:
    """Stateless public accessibility analysis. No persistence, no token required."""

    review = review_accessibility(
        title=request.title,
        body=request.body,
        has_alt_text=request.has_alt_text,
        language=request.language,
    )
    return {
        "status": review.status,
        "findings": [finding.__dict__ for finding in review.findings],
        "disclaimer": review.disclaimer,
        "next_steps": list(review.next_steps),
        "persisted": False,
    }


@app.post("/api/v1/civicaccess/review")
def accessibility_review(
    request: AccessibilityReviewRequest,
    x_civicaccess_write_token: str | None = Header(default=None),
) -> dict[str, object]:
    _authorize_persistent_write(x_civicaccess_write_token)
    stored = _get_review_repository().create_review(
        title=request.title,
        body=request.body,
        has_alt_text=request.has_alt_text,
        language=request.language,
    )
    return _stored_review_response(stored)


@app.get("/api/v1/civicaccess/reviews")
def list_accessibility_reviews(limit: int = 25) -> dict[str, object]:
    reviews = _get_review_repository().list_reviews(limit=limit)
    return {
        "status": "ok",
        "count": len(reviews),
        "reviews": [_stored_review_summary(review) for review in reviews],
    }


@app.get("/api/v1/civicaccess/reviews/{review_id}")
def get_accessibility_review(review_id: str) -> dict[str, object]:
    stored = _get_review_repository().get_review(review_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Accessibility review record not found.",
                "fix": "Use a review_id returned by POST /api/v1/civicaccess/review.",
            },
        )
    return _stored_review_response(stored)


@app.post("/api/v1/civicaccess/reviews/{review_id}/records-export")
def export_accessibility_review_record(
    review_id: str,
    x_civicaccess_write_token: str | None = Header(default=None),
) -> dict[str, object]:
    _authorize_persistent_write(x_civicaccess_write_token)
    repository = _get_review_repository()
    stored = repository.get_review(review_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Accessibility review record not found.",
                "fix": "Use a review_id returned by POST /api/v1/civicaccess/review.",
            },
        )
    export = build_accessible_export(title=stored.title or "Untitled accessible publication")
    repository.record_audit_event(action="review.records_export", subject_id=review_id)
    return {
        "status": "records-export-ready",
        "module": "civicaccess",
        "target_module": "civicrecords-ai",
        "review": _stored_review_summary(stored),
        "export": {
            "title": export.title,
            "format": export.format,
            "checklist": list(export.checklist),
            "retention_note": export.retention_note,
            "status": export.status,
            "fix": export.fix,
        },
        "provenance": {
            "source_text_preserved": True,
            "findings_preserved": True,
            "disclaimer_preserved": True,
            "created_at": stored.created_at.isoformat(),
        },
    }


@app.get("/api/v1/civicaccess/integration-contracts")
def integration_contracts() -> dict[str, object]:
    return {
        "status": "ok",
        "module": "civicaccess",
        "provides": [
            {
                "contract": "civicaccess.publication_accessibility_review.v1",
                "endpoint": "/api/v1/civicaccess/review",
                "purpose": "Create a persisted accessibility review before publication.",
            },
            {
                "contract": "civicaccess.records_export.v1",
                "endpoint": "/api/v1/civicaccess/reviews/{review_id}/records-export",
                "target_module": "civicrecords-ai",
                "purpose": "Export review provenance and checklist data for records retention.",
            },
        ],
        "downstream_ready_for": [
            "civiczone public notice text",
            "civicplan policy summaries",
            "civicpermit applicant forms",
            "civicinspect notices",
            "civicgrants public opportunity notices",
            "civicprocure RFP and award packets",
        ],
    }


@app.post("/api/v1/civicaccess/plain-language")
def plain_language_rewrite(request: PlainLanguageRequest) -> dict[str, object]:
    result = rewrite_plain_language(request.text)
    return result.__dict__


@app.post("/api/v1/civicaccess/language-variant")
def language_variant(request: LanguageVariantRequest) -> dict[str, object]:
    result = create_language_variant(text=request.text, language=request.language)
    return result.__dict__


@app.post("/api/v1/civicaccess/forms")
def accessible_form(request: AccessibleFormRequest) -> dict[str, object]:
    result = build_accessible_form_plan(form_name=request.form_name, fields=tuple(request.fields))
    return {
        "status": result.status,
        "missing_fields": list(result.missing_fields),
        "checklist": list(result.checklist),
        "fix": result.fix,
        "disclaimer": result.disclaimer,
    }


@app.post("/api/v1/civicaccess/publishing-workflow")
def publishing_workflow(request: PublishingWorkflowRequest) -> dict[str, object]:
    result = build_publishing_workflow_plan(
        title=request.title,
        has_review=request.has_review,
        has_plain_language=request.has_plain_language,
        has_translation_review=request.has_translation_review,
    )
    return {
        "status": result.status,
        "steps": list(result.steps),
        "blockers": list(result.blockers),
        "fix": result.fix,
        "disclaimer": result.disclaimer,
    }


@app.post("/api/v1/civicaccess/ada-title-ii")
def ada_title_ii_review(request: AdaTitleIiReviewRequest) -> dict[str, object]:
    result = build_ada_title_ii_review_plan(
        service_area=request.service_area,
        has_coordinator_review=request.has_coordinator_review,
    )
    return {
        "status": result.status,
        "checklist": list(result.checklist),
        "reviewer_required": result.reviewer_required,
        "fix": result.fix,
        "disclaimer": result.disclaimer,
    }


@app.post("/api/v1/civicaccess/tagged-pdf")
def tagged_pdf_expectations(request: TaggedPdfExpectationRequest) -> dict[str, object]:
    result = build_tagged_pdf_expectations(heading_levels=tuple(request.heading_levels))
    return {
        "status": result.status,
        "checklist": list(result.checklist),
        "fix": result.fix,
        "disclaimer": result.disclaimer,
    }


@app.post("/api/v1/civicaccess/export")
def accessible_export(request: AccessibleExportRequest) -> dict[str, object]:
    result = build_accessible_export(title=request.title, format=request.format)
    return {
        "title": result.title,
        "format": result.format,
        "checklist": list(result.checklist),
        "retention_note": result.retention_note,
        "status": result.status,
        "fix": result.fix,
    }


def _trusted_write_token() -> str | None:
    return os.environ.get("CIVICACCESS_TRUSTED_WRITE_TOKEN")


def _authorize_persistent_write(provided_token: str | None) -> None:
    expected_token = _trusted_write_token()
    if not expected_token:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicAccess durable write guard is not configured.",
                "fix": "Set CIVICACCESS_TRUSTED_WRITE_TOKEN before enabling persistence-backed writes.",
            },
        )
    if not hmac.compare_digest(provided_token or "", expected_token):
        raise HTTPException(
            status_code=403,
            detail={
                "message": "CivicAccess durable write token is missing or invalid.",
                "fix": "Send the configured X-CivicAccess-Write-Token header for persistence-backed writes.",
            },
        )


def _sync_database_url(url: str) -> str:
    """Convert the supervisor's async DATABASE_URL to a sync psycopg2 URL (non-postgres passes through).

    Rewrites only the scheme so passwords/db names containing scheme-marker substrings survive.
    """

    try:
        parsed = make_url(url)
    except Exception:
        return url
    if parsed.drivername.startswith(("postgresql", "postgres")):
        return parsed.set(drivername="postgresql+psycopg2").render_as_string(hide_password=False)
    return url


def _review_database_url() -> str | None:
    # Explicit per-module override wins (dev SQLite or a pre-built Postgres URL).
    configured = os.environ.get("CIVICACCESS_REVIEW_DB_URL")
    if configured:
        return _sync_database_url(configured)
    # Default to the shared CivicCore Postgres the desktop supervisor injects.
    supervisor_url = os.environ.get("DATABASE_URL")
    if supervisor_url:
        return _sync_database_url(supervisor_url)
    # ponytail: SQLite is the explicit dev fallback only when no shared Postgres is configured.
    data_dir = Path(os.environ.get("CIVICACCESS_DATA_DIR", Path.cwd() / "data")).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir / 'civicaccess-reviews.db'}"


def _get_review_repository() -> AccessibilityReviewRepository:
    global _review_db_url, _review_repository
    db_url = _review_database_url()
    if _review_repository is None or db_url != _review_db_url:
        _dispose_review_repository()
        _review_db_url = db_url
        _review_repository = AccessibilityReviewRepository(db_url=db_url)
    return _review_repository


def _readiness_payload() -> dict[str, object]:
    db_url = _review_database_url()
    repository = _get_review_repository()
    schema_status = repository.schema_status()
    blockers: list[str] = []
    if not schema_status.ready:
        blockers.append("Run the local CivicAccess schema status/migration check.")
    ready_for_public_use = not blockers
    return {
        "status": "ready" if ready_for_public_use else "not-ready",
        "ready": ready_for_public_use,
        "review_database_configured": True,
        "review_database_url": db_url,
        "schema_ready": schema_status.ready,
        "schema_version": schema_status.schema_version,
        "expected_schema_version": schema_status.expected_schema_version,
        "review_count": repository.review_count(),
        "blockers": blockers,
    }


def _dispose_review_repository() -> None:
    global _review_repository
    if _review_repository is not None:
        _review_repository.engine.dispose()
        _review_repository = None


def _stored_review_response(stored: StoredAccessibilityReview) -> dict[str, object]:
    return {
        "review_id": stored.review_id,
        "status": stored.status,
        "findings": [finding.__dict__ for finding in stored.findings],
        "disclaimer": stored.disclaimer,
        "next_steps": [
            "Resolve each high-severity finding before publication.",
            "Have staff or an ADA coordinator review the final publication decision.",
            "Preserve the review record with the source content and publication package.",
        ],
        "title": stored.title,
        "language": stored.language,
        "created_at": stored.created_at.isoformat(),
    }


def _stored_review_summary(stored: StoredAccessibilityReview) -> dict[str, object]:
    return {
        "review_id": stored.review_id,
        "title": stored.title,
        "language": stored.language,
        "status": stored.status,
        "finding_count": len(stored.findings),
        "created_at": stored.created_at.isoformat(),
    }
