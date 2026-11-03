# Townlight Access v1.0.0 False Release Evidence

Date: 2026-05-21

## Scope

This file is historical evidence for the mistaken 2026-05-21 v1.0.0 release. Townlight Access is now demoted to v0.2.0; do not use this file as proof that Townlight Access is finished, shipping, city-ready, product-ready, or public-use ready.

- Accessible forms.
- Accessible publishing workflow.
- WCAG review support.
- Plain-language rewrites.
- Multilingual variants.
- ADA Title II review support.
- Tagged-heading PDF expectations.
- Records-ready accessible exports.

## Runtime Surface

- `GET /`
- `GET /health`
- `GET /townlight_access`
- `POST /api/v1/townlight_access/review`
- `GET /api/v1/townlight_access/reviews/{review_id}`
- `POST /api/v1/townlight_access/forms`
- `POST /api/v1/townlight_access/publishing-workflow`
- `POST /api/v1/townlight_access/plain-language`
- `POST /api/v1/townlight_access/language-variant`
- `POST /api/v1/townlight_access/ada-title-ii`
- `POST /api/v1/townlight_access/tagged-pdf`
- `POST /api/v1/townlight_access/export`

## Boundaries

Townlight Access does not provide legal advice, certified ADA compliance, official translation certification, live LLM calls, or final publication approval.

## Local Evidence

Evidence must be refreshed before merge:

- `python -m pytest -q`
- `bash scripts/verify-docs.sh`
- `python -m ruff check .`
- `bash scripts/verify-release.sh`
- Browser QA summary at `docs/browser-qa-townlight_access-v1-summary.md`

## Browser Evidence

- Desktop render: `docs/browser-qa-townlight_access-v1-desktop.png`
- Desktop states: `docs/browser-qa-townlight_access-v1-desktop-states.png`
- Mobile render: `docs/browser-qa-townlight_access-v1-mobile.png`
- Result JSON: `docs/browser-qa-townlight_access-v1-results.json`
