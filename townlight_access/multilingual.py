"""Multilingual variant helpers for Townlight Access."""

from __future__ import annotations

from dataclasses import dataclass

from townlight_access.access_review import DISCLAIMER


@dataclass(frozen=True)
class LanguageVariant:
    source_text: str
    language: str
    text: str
    review_required: bool
    status: str
    fix: str
    translation_performed: bool = False
    disclaimer: str = DISCLAIMER


SAMPLE_VARIANTS = {
    "es": "Muestra: comuniquese con la ciudad para recibir ayuda con este aviso.",
    "vi": "Mau: lien he voi thanh pho de duoc tro giup ve thong bao nay.",
}


def create_language_variant(*, text: str, language: str) -> LanguageVariant:
    """Return an explicitly sample multilingual variant."""

    normalized = language.strip().casefold()
    if normalized in SAMPLE_VARIANTS:
        return LanguageVariant(
            source_text=text,
            language=language,
            text=SAMPLE_VARIANTS[normalized],
            review_required=True,
            status="sample-created",
            fix="This fixed sample does not translate your input. Use the Windows local-model draft workflow or a qualified translator for the actual source text; qualified human review remains required.",
        )
    return LanguageVariant(
        source_text=text,
        language=language,
        text=f"Sample variant placeholder for {language}: {text.strip()}",
        review_required=True,
        status="unsupported-language-placeholder",
        fix="Add a reviewed translation workflow for this language before using it publicly.",
    )
