"""Multilingual variant helpers for CivicAccess."""

from __future__ import annotations

from dataclasses import dataclass

from civicaccess.access_review import DISCLAIMER


@dataclass(frozen=True)
class LanguageVariant:
    language: str
    text: str
    review_required: bool
    status: str
    fix: str
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
            language=language,
            text=SAMPLE_VARIANTS[normalized],
            review_required=True,
            status="sample-created",
            fix="Route this sample to a qualified human reviewer before publication.",
        )
    return LanguageVariant(
        language=language,
        text=f"Sample variant placeholder for {language}: {text.strip()}",
        review_required=True,
        status="unsupported-language-placeholder",
        fix="Add a reviewed translation workflow for this language before using it publicly.",
    )
