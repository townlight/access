<a id="civicaccess-agent-contract"></a>

# Townlight Access Agent Contract

## Source Of Truth

- Upstream suite spec: `townlight/townlight/docs/CivicSuiteUnifiedSpec.md`, especially section 12.
- Suite ADRs: `townlight/townlight/docs/architecture/`.
- Townlight Access supports accessibility and public-trust workflows across modules; it does not replace ADA coordinators, legal counsel, translators, or certified auditors.

## Non-Negotiables

- Townlight Access never claims certified ADA compliance.
- Townlight Access never provides legal advice.
- Multilingual variants must be marked as requiring human review.
- Plain-language rewrites must preserve source/rewrite provenance for records requests.
- Public-facing warnings must be actionable and explain the fix path.
- Townlight Access depends on Townlight Core; Townlight Core must never depend on Townlight Access.
- Code is AGPL-3.0-only, with the TownLight Public Institution Exception for qualifying deployments. Docs are CC BY 4.0.

## Placeholder Package Warning

Do not import from Townlight Core placeholder packages until Townlight Core ships real implementations for them: `audit`, `auth`, `catalog`, `connectors`, `exemptions`, `ingest`, `notifications`, `onboarding`, `scaffold`, `search`, `verification`.

## Milestone Rule

Work one milestone at a time. When a milestone is done, report what changed, audit it once, fix findings once, re-audit once, then continue immediately unless there is a true blocker.
