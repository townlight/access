CivicAccess
===========

CivicAccess is the CivicSuite module for accessibility, plain-language,
multilingual, and ADA Title II review-support workflows.

Status: v0.4.0 - early release. CivicAccess does NOT give legal advice, certify ADA
compliance, issue official translations, or publish anything on its own - your staff,
ADA coordinator, translators, and legal counsel always make the final call.

This README serves two audiences. Civic staff: see the short version below and
USER-MANUAL.md (Part 1). IT/technical: see the technical section below.
(For rendered architecture diagrams, read README.md / USER-MANUAL.md.)


FOR CIVIC STAFF (the short version)
-----------------------------------

CivicAccess helps your office put out public notices everyone can read - and keep
a record proving you checked.
- Paste a draft into the public checker to get instant, plain-language fixes.
  Nothing is saved - it's a safe place to try things.
- To keep a review on the record, save it in the staff workspace and export a copy
  you can hand to a public-records request.
- It also rewrites jargon, drafts translations for a human reviewer, and walks ADA
  Title II reviews - but never publishes anything on its own.
Full walkthrough: USER-MANUAL.md (Part 1).


FOR IT & TECHNICAL STAFF
------------------------

CivicAccess is a deterministic FastAPI module (Python), pinned to the published
CivicCore v1.2.0 release wheel - no model/LLM calls and no outbound network calls.

Architecture (text sketch; see README.md for the rendered diagram):

  Resident  --> /civicaccess  (public, no token) --+
                                                    +--> CivicAccess (FastAPI) --> PostgreSQL :15432
  City staff --> /civicaccess/staff (write token) --+        |                     (civicaccess schema)
                                                             +-- depends on ----> CivicCore v1.2.0
                                                             +-- records-export -> CivicRecords AI

  All of the above runs inside the Tauri supervisor on the local machine. The
  supervisor injects DATABASE_URL and backs up the whole Data/ directory (which
  includes the PostgreSQL cluster), so CivicAccess data is captured with it.

What it provides:
- A stateless public accessibility checker (/civicaccess): WCAG-aligned issues with
  actionable, standard-referenced fixes. No persistence, no token.
- A token-guarded staff workspace (/civicaccess/staff): save reviews, build
  records-ready exports.
- Plain-language rewrites (source/rewrite provenance preserved).
- Multilingual draft variants, explicitly marked for human review.
- ADA Title II review-support checklists (without claiming certification).
- Accessible-form and tagged-PDF expectation checks; a staff publication workflow.
- A persisted audit trail of every write/export; integration contracts.

Persistence & configuration:
- DATABASE_URL ................. shared CivicCore PostgreSQL (supervisor-injected); the default
- CIVICACCESS_REVIEW_DB_URL .... explicit SQLAlchemy URL override
- CIVICACCESS_DATA_DIR ......... directory for the SQLite dev fallback
- CIVICACCESS_TRUSTED_WRITE_TOKEN .. REQUIRED server secret for persistent writes
  Resolution order: CIVICACCESS_REVIEW_DB_URL -> DATABASE_URL (converted to sync
  psycopg2) -> SQLite dev fallback. Preflight with the civicaccess-db-status script.

Security:
- Persistence-write routes (/review, /reviews/{id}/records-export) require the
  X-CivicAccess-Write-Token header (constant-time compare): missing/invalid -> 403,
  guard not configured -> 503 (fails closed). Read and analyze routes are open.
- The server token is never embedded in served HTML; the staff page provides a
  field where an operator pastes it.
- Every write/export persists an audit_events row; review.create is atomic with the
  record. No model/LLM or outbound network calls.

Developer quickstart:
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install https://github.com/townlight/core/releases/download/v1.2.0/civiccore-1.2.0-py3-none-any.whl
  python -m pip install -e ".[dev]"
  python -m pytest -q
  # Full release gate (requires a real PostgreSQL):
  $env:CIVICACCESS_POSTGRES_TEST_URL = "postgresql+psycopg2://USER:PW@HOST:PORT/DB"
  bash scripts/verify-release.sh

Release status:
v0.4.0 is an early release; probe gaps #1-#4 (clean install, staff/public authz,
audit logging, backup/restore durability) are closed with evidence (PROBE-PROGRESS.md).
City-core membership and a clean-VM accessibility acceptance pass are later phases.
The earlier v1.0.0 release was published in error and is retained only as historical
evidence.


License: Code is Apache 2.0. Documentation is CC BY 4.0.
