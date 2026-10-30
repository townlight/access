"""Workflow helpers for CivicAccess public-use release."""

from __future__ import annotations

from dataclasses import dataclass

from civicaccess.access_review import DISCLAIMER


@dataclass(frozen=True)
class AccessibleFormPlan:
    status: str
    missing_fields: tuple[str, ...]
    checklist: tuple[str, ...]
    fix: str | None
    disclaimer: str = DISCLAIMER


@dataclass(frozen=True)
class PublishingWorkflowPlan:
    status: str
    steps: tuple[str, ...]
    blockers: tuple[str, ...]
    fix: str | None
    disclaimer: str = DISCLAIMER


@dataclass(frozen=True)
class AdaTitleIiReviewPlan:
    status: str
    checklist: tuple[str, ...]
    reviewer_required: bool
    fix: str | None
    disclaimer: str = DISCLAIMER


@dataclass(frozen=True)
class TaggedPdfExpectationPlan:
    status: str
    checklist: tuple[str, ...]
    fix: str | None
    disclaimer: str = DISCLAIMER


def build_accessible_form_plan(*, form_name: str, fields: tuple[str, ...]) -> AccessibleFormPlan:
    missing_fields = tuple(field for field in ("name", "contact", "request") if field not in _normalized(fields))
    if not form_name.strip() or missing_fields:
        return AccessibleFormPlan(
            status="needs-fixes",
            missing_fields=missing_fields,
            checklist=(
                "Give the form a descriptive title.",
                "Label every required field in text.",
                "Provide help text for contact and request fields.",
                "Keep validation errors next to the fields they describe.",
            ),
            fix="Add the missing required fields and labels before publishing the form.",
        )
    return AccessibleFormPlan(
        status="form-plan-created",
        missing_fields=(),
        checklist=(
            "Use visible labels for every input.",
            "Keep keyboard focus order aligned with reading order.",
            "Show actionable validation errors beside each field.",
            "Preserve submissions with the publication record.",
        ),
        fix=None,
    )


def build_publishing_workflow_plan(
    *, title: str, has_review: bool, has_plain_language: bool, has_translation_review: bool
) -> PublishingWorkflowPlan:
    blockers: list[str] = []
    if not title.strip():
        blockers.append("missing-publication-title")
    if not has_review:
        blockers.append("missing-accessibility-review")
    if not has_plain_language:
        blockers.append("missing-plain-language-summary")
    if not has_translation_review:
        blockers.append("missing-translation-review")
    return PublishingWorkflowPlan(
        status="blocked" if blockers else "publication-workflow-created",
        blockers=tuple(blockers),
        steps=(
            "Run accessibility review and resolve high-severity findings.",
            "Attach plain-language summary and preserve source text.",
            "Route multilingual variants to a qualified human reviewer.",
            "Package the accessible export and retention record.",
            "Record staff approval before publication.",
        ),
        fix="Complete each blocker before publication." if blockers else None,
    )


def build_ada_title_ii_review_plan(*, service_area: str, has_coordinator_review: bool) -> AdaTitleIiReviewPlan:
    if not service_area.strip() or not has_coordinator_review:
        return AdaTitleIiReviewPlan(
            status="needs-staff-review",
            reviewer_required=True,
            checklist=(
                "Name the public service, program, or activity being reviewed.",
                "Confirm communication access needs and alternate formats.",
                "Record ADA coordinator or qualified staff review.",
                "Preserve remediation notes with the publication record.",
            ),
            fix="Add the service area and route the package to the ADA coordinator or qualified reviewer.",
        )
    return AdaTitleIiReviewPlan(
        status="review-support-package-created",
        reviewer_required=True,
        checklist=(
            "Service area named.",
            "Access needs and alternate formats checked.",
            "Coordinator or qualified staff review recorded.",
            "Remediation notes preserved.",
        ),
        fix=None,
    )


def build_tagged_pdf_expectations(*, heading_levels: tuple[int, ...]) -> TaggedPdfExpectationPlan:
    if not heading_levels:
        return TaggedPdfExpectationPlan(
            status="needs-headings",
            checklist=(
                "Add one H1 for the document title.",
                "Use H2 and H3 headings in reading order.",
                "Confirm PDF tags preserve the same heading order.",
            ),
            fix="Add heading levels before generating a tagged PDF package.",
        )
    skipped = any(current - previous > 1 for previous, current in zip(heading_levels, heading_levels[1:]))
    if heading_levels[0] != 1 or skipped:
        return TaggedPdfExpectationPlan(
            status="needs-fixes",
            checklist=(
                "Start with one H1.",
                "Do not skip heading levels.",
                "Verify tag order in the exported PDF before publication.",
            ),
            fix="Repair the heading order before creating the PDF export.",
        )
    return TaggedPdfExpectationPlan(
        status="tagged-pdf-plan-created",
        checklist=(
            "Heading order starts at H1.",
            "No heading levels are skipped.",
            "PDF tags and reading order must be verified before publication.",
        ),
        fix=None,
    )


def _normalized(fields: tuple[str, ...]) -> set[str]:
    return {field.strip().casefold() for field in fields}
