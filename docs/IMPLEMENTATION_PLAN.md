<a id="civicaccess-implementation-plan"></a>

# Townlight Access Implementation Plan

Townlight Access v0.2.0 is a corrective demotion after the mistaken v1.0.0 publication. It contains deterministic accessible forms, accessible publishing workflows, WCAG review support, plain-language rewrites, multilingual draft variants, ADA Title II review support, tagged-PDF expectations, records-ready exports, persistence for review records, readiness gates, Townlight Core v1.2.0 release-wheel alignment, and an API-backed public review UI, but it is not finished, shipping, city-ready, product-ready, or public-use ready.

## Verification Bar

- Unit and adversarial tests must pass.
- `bash scripts/verify-release.sh` must pass.
- Browser QA must cover desktop and mobile public UI states: loading, success, empty, error, partial/degraded, console, focus, and copy.
- Release docs must keep human reviewers responsible and must not claim certified ADA compliance, legal advice, official translation certification, live LLM behavior, or final publication approval.
