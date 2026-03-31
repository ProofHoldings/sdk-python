# Python SDK — proof.holdings

## Overview
Python client SDK for the proof.holdings API. PyPI package `proof-holdings`, Python module `proof_sdk`. All resource methods have TypedDict return type annotations for IDE/type-checker support.

## Architecture
- `src/proof_sdk/client.py` — Main client, API key auth, resource accessors
- `src/proof_sdk/http.py` — HTTP layer (httpx), error handling
- `src/proof_sdk/resources/*.py` — 25 resource modules (verifications, proofs, sessions, authorizations, confirmations, etc.)
- `src/proof_sdk/types.py` — Auto-generated TypedDict definitions
- `tests/` — Test suite

## Type System
- Types are auto-generated from OpenAPI spec via `scripts/generate-sdk-types.ts`
- Propagated via `scripts/propagate-sdk-types.ts`
- Return annotations are TypedDict classes (structural, not nominal)
- **Runtime returns are plain dicts** — TypedDicts are documentation/IDE hints only, no runtime validation
- **Do not edit `src/proof_sdk/types.py` manually** — regenerate with `npm run sdk:generate-types`

## Key Patterns
- All resource methods return `dict` at runtime, annotated as TypedDict for static analysis
- URL path parameters escaped with `quote(id, safe="")`
- Error responses raise `ProofError` with status code and message
- `http.py` `delete()` accepts optional `json` body parameter for DELETE-with-body requests (used by authorizations revoke)
- Python reserved keywords in generated types are suffixed with `_` (e.g., `from` becomes `from_`) -- handled by `PYTHON_RESERVED` set in `scripts/generate-sdk-types.ts`
