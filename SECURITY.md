# Security

Townlight Access version: `0.4.0`.

Townlight Access is self-hosted municipal software. It provides advisory accessibility, plain-language, multilingual draft, and ADA Title II review-support workflows; it does not make legal, certification, translation, or publication decisions.

Persistent writes (saving reviews and records exports) require the `CIVICACCESS_TRUSTED_WRITE_TOKEN` server secret, sent as the `X-CivicAccess-Write-Token` header and compared in constant time. The token is **never embedded in served HTML**: the staff surface provides a field where the operator pastes it, and it is kept only in the browser session. The public surface (`/civicaccess`) analyzes content statelessly and never persists. When the write token is not configured, persistence-backed writes fail closed (HTTP 503) rather than accepting unauthenticated writes.

Report vulnerabilities privately through the Townlight project maintainers. Do not include secrets, resident data, or protected municipal records in public issues.
