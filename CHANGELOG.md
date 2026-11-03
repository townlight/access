# Changelog

## [0.5.0] - Unreleased naming candidate

- Rename the principal distribution/import to the Townlight Access identities and pair with Townlight Core 1.3.0.dev2.
- Preserve complete saved review exports and durable source/output draft provenance in the Windows workflow; distinguish standalone samples from model-generated translations.
- Fresh-install candidate only; no legacy database upgrade or import shim. Existing data and historical release identities are preserved.
- Signed Windows installer acceptance and publication remain pending; source implementation is not installed verification.


All notable changes to Townlight Access will be documented in this file.

The format follows Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

## [0.4.0] - 2026-06-28

City-core hardening: closes probe gaps #2 (authz), #3 (audit), and #4 (backup/restore), and makes the shared CivicCore PostgreSQL the default review store.

### Added

- Added a trusted-write guard: persistent writes (`POST /api/v1/civicaccess/review`, `POST /api/v1/civicaccess/reviews/{id}/records-export`) now require the `CIVICACCESS_TRUSTED_WRITE_TOKEN` server secret, sent as the `X-CivicAccess-Write-Token` header. Missing/invalid token returns 403; unconfigured guard fails closed with 503. (Probe gap #2.)
- Added `POST /api/v1/civicaccess/analyze`: a stateless, public, no-persistence accessibility check. The public `/civicaccess` surface now uses it, so public users can no longer write city records.
- Added a persisted `audit_events` table and module audit events on writes/exports: `review.create` is committed atomically in the same transaction as the review record; `review.records_export` emits a standalone audit row on export. (Probe gap #3.)
- Added durability proofs: a Postgres reconnect round-trip for the default store (review + audit survive a fresh engine) and a SQLite dev-fallback backup/restore round-trip. (Probe gap #4.)
- Added a mandatory PostgreSQL release gate: `verify-release.sh` and CI require `CIVICACCESS_POSTGRES_TEST_URL` so PostgreSQL persistence coverage cannot be skipped, plus `tests/test_postgres_persistence.py`.

### Changed

- Defaulted the review store to the shared CivicCore PostgreSQL: the module reads the supervisor's `DATABASE_URL` (asyncpg) and derives a sync psycopg2 URL. `CIVICACCESS_REVIEW_DB_URL` still overrides; SQLite is now an explicit dev fallback rather than the default.
- Moved `psycopg2-binary` from dev/optional dependencies to a runtime dependency so the PostgreSQL default works out of the box.
- Renamed the schema migration id to `civicaccess-windows-local-state-v1` to match the CivicCore Windows Local module convention.
- Staff `/civicaccess/staff` surface sends an operator-supplied write token (entered in the UI, kept in the browser session) on save and export. The server secret is never embedded in served HTML.

## [0.3.0] - 2026-06-25

### Added

- Added default local SQLite review persistence so installed CivicAccess is ready without hidden environment setup.
- Added `/civicaccess/staff` for saved review queue, readiness, integration contracts, and records-ready export operations.
- Added `GET /api/v1/civicaccess/reviews`, `POST /api/v1/civicaccess/reviews/{review_id}/records-export`, and `GET /api/v1/civicaccess/integration-contracts`.

### Changed

- Aligned CivicAccess to the published CivicCore v1.2.0 release wheel and SHA256.
- Wired the public `/civicaccess` review form to the accessibility review API.
- Added local schema status and `/ready` readiness gates for review-record persistence.
- Added bounded request models and actionable validation errors for public API payloads.
- Changed readiness from environment-gated optional persistence to default local persistence with explicit override support.

## [0.2.0] - 2026-05-21

### Corrected

- Corrected the false `v1.0.0` release label after the independent CivicSuite release-integrity audit found CivicAccess does not meet the Section 2 FINISHED and SHIPPING bar.
- Set the honest current label to `v0.2.0` and superseded the mistaken `v1.0.0` posture without deleting the historical record.
- Current classification: scaffold - deterministic accessibility/plain-language support exists, but real AI, real municipal data/search, production-grade frontend, and public-use gate proof remain absent.
- CivicAccess must not be described as finished, shipping, city-ready, product-ready, or public-use ready until a future independent audit signs off against the full Section 2 gate.

## [1.0.0] - 2026-05-21

### Added

- Public-use CivicAccess support release covering accessible forms, accessible publishing workflow checks, WCAG-aligned review support, plain-language rewrites, multilingual draft variants, ADA Title II review-support packages, tagged-PDF expectations, records-ready exports, and a functional `/civicaccess` UI.
- New deterministic workflow endpoints for forms, publishing workflow, ADA Title II review support, and tagged-PDF expectations.
- Adversarial tests for empty content, unsupported language placeholders, unsupported export formats, blocked publishing workflows, missing persisted records, unavailable persistence, and non-certification boundaries.
- Browser QA evidence for desktop and mobile public UI states.

### Changed

- Aligned CivicAccess to `civiccore==1.1.0`.
- Updated release gates, CI, documentation, and package artifacts for `1.0.0`.

## [0.1.1] - 2026-04-28

### Added

- Production-depth accessibility review persistence slice with `CIVICACCESS_REVIEW_DB_URL`, persisted review requests/findings, and retrieval by `review_id`.

### Changed

- Aligned CivicAccess to `civiccore==0.3.0` while preserving the v0.1 accessibility foundation behavior.
- Updated version surfaces, release gate, CI CivicCore wheel install, documentation, and health-contract tests for the v0.1.1 dependency-alignment release.

## [0.1.0] - 2026-04-27

### Added

- Professional repository scaffold, documentation, issue templates, PR template, and release gates.
- FastAPI runtime foundation with root, health, and public UI endpoints.
- Deterministic sample accessibility review with WCAG-aligned actionable findings.
- Plain-language rewrite helper with human-review boundary.
- Multilingual variant helper with human-review boundary.
- Records-ready accessible export checklist.
- Accessible public sample UI at `/civicaccess` with browser QA coverage.
