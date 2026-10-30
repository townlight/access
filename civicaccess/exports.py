"""Records-ready accessibility export helpers for CivicAccess."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccessibleExport:
    title: str
    format: str
    checklist: tuple[str, ...]
    retention_note: str
    status: str
    fix: str | None


def build_accessible_export(*, title: str, format: str = "html") -> AccessibleExport:
    """Build a deterministic records-ready export checklist."""

    normalized_format = format.strip().lower()
    supported_formats = {"html", "pdf", "markdown", "txt"}
    if normalized_format not in supported_formats:
        return AccessibleExport(
            title=title.strip() or "Untitled accessible publication",
            format=normalized_format or "missing",
            checklist=(),
            retention_note="No export package should be published until the format is supported.",
            status="unsupported-format",
            fix="Choose html, pdf, markdown, or txt so CivicAccess can produce the accessibility checklist.",
        )

    return AccessibleExport(
        title=title.strip() or "Untitled accessible publication",
        format=normalized_format,
        checklist=(
            "Declare document language.",
            "Use heading order without skipped levels.",
            "Provide alt text or decorative-image marking.",
            "For PDF output, preserve tagged headings and reading order before publication.",
            "Preserve source text and rewrite provenance for records requests.",
        ),
        retention_note="Keep the source, rewritten text, reviewer, and publication timestamp with the municipal record.",
        status="checklist-created",
        fix=None,
    )
