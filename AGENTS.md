# CivicAccess Agent Contract

## Source Of Truth

- Upstream suite spec: `CivicSuite/civicsuite/docs/CivicSuiteUnifiedSpec.md`, especially section 12.
- Suite ADRs: `CivicSuite/civicsuite/docs/architecture/`.
- CivicAccess supports accessibility and public-trust workflows across modules; it does not replace ADA coordinators, legal counsel, translators, or certified auditors.

## Non-Negotiables

- CivicAccess never claims certified ADA compliance.
- CivicAccess never provides legal advice.
- Multilingual variants must be marked as requiring human review.
- Plain-language rewrites must preserve source/rewrite provenance for records requests.
- Public-facing warnings must be actionable and explain the fix path.
- CivicAccess depends on CivicCore; CivicCore must never depend on CivicAccess.
- Code is AGPL-3.0-only, with the TownLight Public Institution Exception for qualifying deployments. Docs are CC BY 4.0.

## Placeholder Package Warning

Do not import from CivicCore placeholder packages until CivicCore ships real implementations for them: `audit`, `auth`, `catalog`, `connectors`, `exemptions`, `ingest`, `notifications`, `onboarding`, `scaffold`, `search`, `verification`.

## Milestone Rule

Work one milestone at a time. When a milestone is done, report what changed, audit it once, fix findings once, re-audit once, then continue immediately unless there is a true blocker.
