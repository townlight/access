from fastapi.testclient import TestClient

from townlight_access.access_review import review_accessibility
from townlight_access.exports import build_accessible_export
from townlight_access.main import app
from townlight_access.multilingual import create_language_variant
from townlight_access.plain_language import rewrite_plain_language
from townlight_access.workflows import (
    build_accessible_form_plan,
    build_ada_title_ii_review_plan,
    build_publishing_workflow_plan,
    build_tagged_pdf_expectations,
)


client = TestClient(app)


def test_accessibility_review_returns_actionable_findings() -> None:
    result = review_accessibility(title="", body="Short public notice.", has_alt_text=False, language="en")

    assert result.status == "needs-fixes"
    assert result.findings[0].code == "missing-title"
    assert result.findings[0].fix
    assert result.findings[1].wcag_reference == "WCAG 1.1.1 Non-text Content"
    assert "does not replace legal review" in result.disclaimer
    assert result.next_steps


def test_plain_language_rewrite_keeps_human_review_boundary() -> None:
    result = rewrite_plain_language("Residents must remit payment prior to the deadline.")

    assert "pay before" in result.rewritten
    assert result.review_required is True
    assert "source_text_preserved" in result.provenance
    assert "certified accessibility audit" in result.disclaimer


def test_language_variant_is_sample_and_review_required() -> None:
    result = create_language_variant(text="Contact the city for help.", language="es")

    assert result.language == "es"
    assert "comuniquese" in result.text
    assert result.review_required is True
    assert result.status == "sample-created"


def test_accessible_export_preserves_records_context() -> None:
    result = build_accessible_export(title="Budget Hearing Notice")

    assert result.title == "Budget Hearing Notice"
    assert "Preserve source text and rewrite provenance for records requests." in result.checklist
    assert "municipal record" in result.retention_note
    assert result.status == "checklist-created"


def test_workflow_helpers_cover_public_use_scope() -> None:
    form = build_accessible_form_plan(form_name="Service Request", fields=("name", "contact", "request"))
    publishing = build_publishing_workflow_plan(
        title="Budget Hearing",
        has_review=True,
        has_plain_language=True,
        has_translation_review=True,
    )
    ada = build_ada_title_ii_review_plan(service_area="Public meetings", has_coordinator_review=True)
    pdf = build_tagged_pdf_expectations(heading_levels=(1, 2, 2, 3))

    assert form.status == "form-plan-created"
    assert publishing.status == "publication-workflow-created"
    assert ada.status == "review-support-package-created"
    assert pdf.status == "tagged-pdf-plan-created"


def test_api_review_success_shape() -> None:
    response = client.post(
        "/api/v1/townlight_access/review",
        json={"title": "", "body": "A public notice.", "has_alt_text": False, "language": "en"},
        headers={"X-Townlight-Access-Write-Token": "test-write-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "needs-fixes"
    assert payload["findings"][0]["fix"]
    assert payload["next_steps"]
    assert payload["review_id"]


def test_api_analyze_is_public_and_stateless() -> None:
    response = client.post(
        "/api/v1/townlight_access/analyze",
        json={"title": "", "body": "A public notice.", "has_alt_text": False, "language": "en"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "needs-fixes"
    assert payload["findings"][0]["fix"]
    assert payload["next_steps"]
    assert payload["persisted"] is False
    assert "review_id" not in payload


def test_api_review_validation_is_actionable() -> None:
    missing = client.post("/api/v1/townlight_access/review", json={"title": "Notice"})
    oversized = client.post(
        "/api/v1/townlight_access/review",
        json={"title": "Notice", "body": "x" * 5001, "has_alt_text": True, "language": "en"},
    )

    assert missing.status_code == 422
    missing_detail = missing.json()["detail"]
    assert "body" in missing_detail["fields"]
    assert "fields array" in missing_detail["fix"]
    assert oversized.status_code == 422
    assert "body" in oversized.json()["detail"]["fields"]


def test_api_plain_language_and_language_variant() -> None:
    plain = client.post(
        "/api/v1/townlight_access/plain-language",
        json={"text": "Please remit payment prior to the deadline."},
    )
    variant = client.post(
        "/api/v1/townlight_access/language-variant",
        json={"text": "Contact the city for help.", "language": "vi"},
    )

    assert plain.status_code == 200
    assert "pay before" in plain.json()["rewritten"]
    assert variant.status_code == 200
    assert variant.json()["review_required"] is True


def test_api_public_use_workflow_routes() -> None:
    form = client.post(
        "/api/v1/townlight_access/forms",
        json={"form_name": "Public Records Request", "fields": ["name", "contact", "request"]},
    )
    workflow = client.post(
        "/api/v1/townlight_access/publishing-workflow",
        json={
            "title": "Budget Hearing",
            "has_review": True,
            "has_plain_language": True,
            "has_translation_review": True,
        },
    )
    ada = client.post(
        "/api/v1/townlight_access/ada-title-ii",
        json={"service_area": "Public meetings", "has_coordinator_review": True},
    )
    pdf = client.post("/api/v1/townlight_access/tagged-pdf", json={"heading_levels": [1, 2, 3]})
    export = client.post("/api/v1/townlight_access/export", json={"title": "Budget", "format": "pdf"})

    assert form.json()["status"] == "form-plan-created"
    assert workflow.json()["status"] == "publication-workflow-created"
    assert ada.json()["status"] == "review-support-package-created"
    assert pdf.json()["status"] == "tagged-pdf-plan-created"
    assert export.json()["status"] == "checklist-created"
    assert all(response.status_code == 200 for response in (form, workflow, ada, pdf, export))


def test_adversarial_inputs_are_actionable_and_non_certifying() -> None:
    empty_review = client.post(
        "/api/v1/townlight_access/analyze",
        json={"title": "", "body": "", "has_alt_text": False, "language": "en"},
    )
    unsupported_language = client.post(
        "/api/v1/townlight_access/language-variant",
        json={"text": "Contact the city.", "language": "tlh"},
    )
    unsupported_export = client.post(
        "/api/v1/townlight_access/export",
        json={"title": "Budget", "format": "docx"},
    )
    blocked_workflow = client.post("/api/v1/townlight_access/publishing-workflow", json={})
    bad_pdf = client.post("/api/v1/townlight_access/tagged-pdf", json={"heading_levels": [2, 4]})

    assert empty_review.json()["findings"][0]["code"] == "missing-body"
    assert unsupported_language.json()["status"] == "unsupported-language-placeholder"
    assert "Add a reviewed translation workflow" in unsupported_language.json()["fix"]
    assert unsupported_export.json()["status"] == "unsupported-format"
    assert "Choose html, pdf, markdown, or txt" in unsupported_export.json()["fix"]
    assert blocked_workflow.json()["status"] == "blocked"
    assert blocked_workflow.json()["fix"] == "Complete each blocker before publication."
    assert bad_pdf.json()["status"] == "needs-fixes"
    assert "certified ada compliance" not in str(empty_review.json()).lower()


def test_public_ui_route_is_accessible_and_honest() -> None:
    response = client.get("/townlight_access")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    text = response.text
    assert '<a class="skip-link" href="#main">Skip to main content</a>' in text
    assert '<main id="main" tabindex="-1">' in text
    assert "v0.5.0 standalone readiness candidate" in text
    assert 'id="runReview"' in text
    assert 'fetch("/api/v1/townlight_access/analyze"' in text
    assert "result.replaceChildren()" in text
    assert "result.innerHTML" not in text
    assert "Show empty state" not in text
    assert "Show error state" not in text
    assert "Partial review pending" in text
    assert "Review could not finish" in text
    assert "does not provide legal advice" in text
    assert "official translation certification" in text
    assert "zoning" not in text.casefold()


def test_staff_ui_route_is_api_wired_and_contract_aware() -> None:
    response = client.get("/townlight_access/staff")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    text = response.text
    assert '<a class="skip-link" href="#main">Skip to main content</a>' in text
    assert "Saved review queue" in text
    assert 'fetch("/api/v1/townlight_access/readiness")' in text
    assert 'fetch("/api/v1/townlight_access/integration-contracts")' in text
    assert 'fetch("/api/v1/townlight_access/reviews")' in text
    assert 'records-export' in text
    assert "X-Townlight-Access-Write-Token" in text
    assert 'id="writeToken"' in text
    assert "currentToken()" in text
    assert "result.innerHTML" not in text


def test_staff_page_never_leaks_the_write_token(monkeypatch) -> None:
    monkeypatch.setenv("TOWNLIGHT_ACCESS_TRUSTED_WRITE_TOKEN", "super-secret-sentinel-do-not-leak")
    response = client.get("/townlight_access/staff")

    assert response.status_code == 200
    # The server secret must never appear in HTML served from an unauthenticated GET.
    assert "super-secret-sentinel-do-not-leak" not in response.text
