# Changelog

Notable changes to [`proof-holdings-sdk`](https://pypi.org/project/proof-holdings-sdk/) (import name
`proof_sdk`). Source: [ProofHoldings/sdk-python](https://github.com/ProofHoldings/sdk-python).

## 1.2.0 — 2026-10-26

Code written for 1.1.0 keeps working, with the declared exception under "Changed". What the API no
longer has is kept in `proof_sdk.types`, marked deprecated, and is removed in 2.0.

### Added

- The `starter` billing plan in `BillingPlan`: the €9 plan, which the checkout now accepts.

- SMS sessions: `sessions.create(channel="sms")` now works, the same way as SMS sign-in. The person
  texts a short code to one of our numbers; the response carries `sms_code`, `sms_message` and
  `sms_dids`, and `deep_link` is an `sms:` link with the message pre-filled. An SMS proof carries
  `confidence: "standard"`.
- `sessions.create(profile_id=...)` names the sub-account a session is for.

- Message templates belong to a project (sub-account). Every `templates` method except
  `get_defaults` takes a keyword-only `profile_id`, sent as the `profile_id` query parameter.
  Omitted, a project-bound API key uses its own project and any other key the primary project; a
  project-bound key naming another project is refused with 403 `profile_mismatch`.

- The `Session` TypedDict gains `channel`, `phone_number`, `verified_at` and `verification_id`, the
  fields `GET /api/v1/sessions/{id}` returns; `CreateSessionRequest` gains `profile_id`,
  `client_metadata` and `context`.

### Changed

- `authorizations.create` now requires the keyword arguments `hitl_id` and `recipient`, and sends
  them. The server has always required both, so every 1.1.0 call answered 400; it also takes the
  optional `bsuid`. Declared in `sdks/api-breaks/python.json`.

### Deprecated

- `Session`'s `challenge` and `expires_at`: `GET /api/v1/sessions/{id}` never returned them.
- `CreateSessionRequest`'s `phone`: a session no longer takes a phone number (the person shares it in
  the chat), and the server ignores it.
- `BrandingSettings`, `ProfileTemplate`, and `branding` on `SettingsResponse` and
  `UpdateSettingsResponse`: account-level branding is retired, since branding belongs to each project.
  A settings update carrying `branding` is refused with 400 `branding_moved`.

- `authorizations.create(business_name=...)` emits a `DeprecationWarning`. The server ignores the
  field: the consent message names the approval setup's sub-account.
- `profiles.list_templates`, `update_template`, `delete_template` and `preview_template` emit a
  `DeprecationWarning`. The server retired `/api/v1/me/profiles/{id}/templates`
  (410 `endpoint_retired`); use the `templates` methods with `profile_id=`.

## 1.1.0 — 2026-10-14

The first release on PyPI.

### Added

- `Proof()` without a key resolves one: a non-empty `PROOF_API_KEY`, else the entry that
  `npx @proof-holdings/mcp-server login` saved in `~/.proof-holdings/credentials` for the client's base
  URL. The base URL is the `base_url` argument, else `PROOF_BASE_URL`, else
  `https://api.proof.holdings`. An explicit key behaves as before; an explicit empty key is an error.
- `verifications.delete_domain_verification(id)` deletes a domain verification attempt that is not
  verified (pending, verifying or failed). A verified domain is refused with 409 `domain_verified`.
- Types for account deletion and export, identifier, domain and project removal, the artifact claim
  lookup, and the Delegations section of a public profile.
- API-key listings carry `replaced_key_ids`: a key's usage covers every key it replaced.
- The `free` billing plan in `BillingPlan`.
