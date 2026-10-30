"""Plain-language rewrite helpers for CivicAccess."""

from __future__ import annotations

from dataclasses import dataclass

from civicaccess.access_review import DISCLAIMER


@dataclass(frozen=True)
class PlainLanguageRewrite:
    original: str
    rewritten: str
    reading_level: str
    review_required: bool
    provenance: tuple[str, ...]
    disclaimer: str = DISCLAIMER


JARGON_MAP = {
    "pursuant to": "under",
    "commence": "start",
    "terminate": "end",
    "remit payment": "pay",
    "prior to": "before",
    "subsequent to": "after",
}


def rewrite_plain_language(text: str) -> PlainLanguageRewrite:
    """Apply deterministic sample rewrites and require human review."""

    rewritten = text.strip()
    for source, replacement in JARGON_MAP.items():
        rewritten = rewritten.replace(source, replacement).replace(source.title(), replacement.title())
    if not rewritten:
        rewritten = "Add the public-facing text that should be rewritten."
    return PlainLanguageRewrite(
        original=text,
        rewritten=rewritten,
        reading_level="sample plain-language pass; not a certified reading-level score",
        review_required=True,
        provenance=(
            "source_text_preserved",
            "deterministic_jargon_map_applied",
            "human_review_required_before_publication",
        ),
    )
