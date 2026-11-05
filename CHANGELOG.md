# Changelog

Notable changes to [`proof-holdings-sdk`](https://pypi.org/project/proof-holdings-sdk/) (import name
`proof_sdk`). Source: [ProofHoldings/sdk-python](https://github.com/ProofHoldings/sdk-python).

## 1.4.0 — 2026-11-05

The signing-key rotation (#513), on top of 1.3.0. These are additions; nothing written for 1.3.0
stops working at run time (one typing change under "Changed").

### Added

- `proofs.token(id)`, `proofs.list_reissued(since, *, page=None, limit=None)` and
  `proofs.delegation_token(handle)`: the token pull of the signing-key rotation
  (`GET /api/v1/proofs/{id}/token`, `GET /api/v1/proofs?reissued_since=`,
  `GET /api/v1/proofs/delegation-token/{handle}`, the last a public endpoint). A proof of one of the account's own verified assets is read by the signed-in owner: with a live API key `token` answers 403 `owner_session_required` whatever its status, `list_reissued` leaves it out and no `proof.reissued` webhook names it. `since` is a
  timezone-aware `datetime` (a naive one raises `ValueError`) or a string sent as given. TypedDicts
  `ProofTokenResponse`, `ReissuedProofListResponse`, `ReissuedProofItem` and
  `DelegationTokenResponse`.
- `JWK` gains the optional `proof_purpose`, `not_before`, `not_after`, `max_token_lifetime` and
  `proof_legacy`; `JWKS` gains `proof_tombstones` (`JWKSTombstone`), the revoked keys.
- The webhook event literals include `proof.reissued` and `delegation.reissued`.

### Changed

- `JWKS.proof_tombstones` is a required key, so a `JWKS` literal without it no longer type-checks.

### Deprecated

- Delegation `scope` (delegation schema 2.0: a delegation carries no scope): the `scope` argument of
  `delegations.create` is now optional — a value given is sent as is, ignored by the server and answered with a
  `Deprecation` header — and the `scope` key of the delegation response types is the scope a delegation issued
  before schema 2.0 was stored with, otherwise `[]`. Removed in the next major (`sdks/shared/NEXT_MAJOR.md`).

## 1.3.0 — 2026-11-03

### Added

- `billing.top_up(auto_top_up=True)` and `billing.auto_top_up(enabled=True)` now answer `403 owner_session_required`: switching automatic top-ups on charges the saved card later with no one present, so it is the account owner's act on the dashboard. Switching them off still works. Plain top-ups are unchanged. `TwoFAActionType` gains `"auto_top_up_change"`, the dashboard's step-up for switching them on; it gates no SDK call.
- `SubscriptionResponse` gains `scheduled_plan` and `scheduled_change_at` (both optional, `None` when nothing is scheduled): the plan a downgrade made on the billing page moves the account to at the end of the paid period, and when. Absent from an API that predates plan changes.
- `TwoFAActionType` gains `"plan_change"`: the step-up a dashboard session gives before a plan upgrade charges the saved card. It gates no SDK call — plan changes have no API-key address.
- `WebhookDeliveryListQuery` gains `endpoint_id` and `profile_id` (`NotRequired["ObjectId"]`), the delivery-list filters by webhook endpoint and by sub-account. A field the API document annotates where it references a shared type is now generated as that type rather than `Any`. Fields 1.2.0 shipped as `Any` stay `Any` until the next major (listed in `sdks/shared/NEXT_MAJOR.md`).
- `billing` resource: `subscription()`, `checkout(...)`, `portal(...)`, `top_up(...)`, `balance()`, `balance_ledger(...)` and `auto_top_up(...)` over `/api/v1/billing/*` — the subscription, Stripe checkout and portal links, and the prepaid balance. `top_up` and `auto_top_up` take `amount` as the int `10`, `50` or `200` (euros). Their redirect URLs must be on `proof.holdings` (or `localhost`): the API refuses any other host. The four writes are refused to a key bound to one sub-account (`403 account_key_required`). Returns the generated `SubscriptionResponse`, `CheckoutResponse`, `PortalResponse`, `TopUpResponse`, `BalanceResponse` and `LedgerListResponse`.
- `BalanceEmptyError` (402 `balance_empty`), with `top_up_url`, `used`, `included` and `balance` (euro cents). Once billing is live, any method that creates a proof request can raise it when the plan's included proofs are used and the prepaid balance is empty; proofs already issued keep working.
- `BillingUnavailableError` (503 `billing_unavailable`), a `ServerError`: checkout, portal and top-up while billing is not live.
- `TwoFAActionType` gains `"phone_primary"` and `"email_primary"`, the step-ups for making a phone or email the primary one, which the API already accepted. The published list is now derived from the server's policy, so it no longer falls behind it.
- `WebhookDelivery["token_omitted_reason"]` (`NotRequired`, `"source_gone"` | `"token_absent"` | `"token_changed"` |
  `None`): why the last send carried `proof_token: null`. A delivery's stored `payload` now holds every `proof_token` as
  `None` — the body POSTed to the receiver still carries the token. Webhook receivers: a retried delivery carries the same `proof_token` as the first attempt, or `proof_token: null` with `token_omitted_reason` ∈ {`source_gone`, `token_absent`, `token_changed`} — never a different token. Absent from an API that predates it.
- `confirmations.verify_decision_signature(confirmation, public_key)` checks the approver's own
  signature on a decision, locally, against the public key you hold: your HITL config's own key for an
  owner decision, the key you recorded when an approver enrolled for theirs. It answers `"verified"`,
  `"unsigned"` (no signed evidence), `"key_mismatch"` (the decision carries another key),
  `"input_mismatch"` (the signed input names another confirmation, action or comment) or
  `"signature_invalid"`. The key is required: a key the server sent is no evidence against the server.
  The key must be an RSA public key PEM (`PUBLIC KEY` or `RSA PUBLIC KEY`) with a 4096- to 16384-bit
  modulus and an odd exponent from 3 to 2^31 - 1; any other key answers `signature_invalid`.
- `webhook_endpoints`: manage several webhook endpoints, each scoped to every sub-account (`scope="all"`)
  or to chosen ones (`scope="selected"` + `profile_ids`) — `list`, `create`, `retrieve`, `update`,
  `delete` and `rotate_secret` (`/api/v1/webhook-endpoints*`). Each endpoint has its own signing
  secret, returned once: by `create` and by `rotate_secret`. `update(description=None)` clears the
  description; `delete` returns `None` (the server answers 204).
- `profiles.rotate_callback_secret(profile_id)` replaces a sub-account's callback signing secret (what
  signs its `callback_url` deliveries) and returns the new one, once, as `{profile_id, secret}`.
- `confirmations.list()` takes `profile_id`: only that sub-account's confirmations (sent through its HITL configs or created by its API keys). A key bound to another sub-account is refused with `403 profile_mismatch`.
- `Template` carries `last_fallback_at` and `last_fallback_variables`: when a message last went out with the platform default instead of the template, because rendering it would have left a raw `{{variable}}`, and the variable names that caused it. Both are cleared when the template is saved again.
- `TemplateSendablePair`, and `sendable` on the `templates.list()` response: what is sent — each channel and message type some message is sent for, with the variables its sends fill. `TemplateSendWarning`, and `warnings` on the template save and preview responses: a template that would never be sent as written is still saved (200, as before), and each warning says why — `template_not_sent` for a pair no message is sent for, `template_variable_not_filled` (with `variables`) for a variable that message never fills. `sendable` and `warnings` are optional: an API that predates them omits the fields, so read their absence as an empty list. The live template tests read `telegram/verification_request` instead of an SMS template, which is never sent.
- Generated response types for operations whose contract named the generic `SuccessResponse` or the public `PublicProfile` while the API sent something else: `ProfileOwnerResponse` (a sub-account as its owner sees it, with `PublicProofItem` and `ProfileOwnerLink`) and `ProfileOwnerListResponse` for the profile reads, writes and lists; `ClaimUsernameResponse`; `PublicProofsResponse` for the shown-proofs updates; `ExtendVerificationRequestResponse` and `ShareVerificationRequestEmailResponse`. Types only: the `profiles` methods these responses come from (`list`, `create`, `retrieve`, `update`, `set_primary`) still return plain dicts, and nothing on the wire changed.
- Generated response types for the domain and DNS-credential operations and the public profile reads, which the contract described as `SuccessResponse`, a bare `Domain` or `PublicProfile`: `DomainListResponse`, `DomainDetailResponse` (with `DomainVerificationInstructions`), `DomainVerificationResult` for the DNS check and the emailed-code confirmation, `DomainEmailVerificationResponse`, `DomainCredentialCheckResponse` (with `DomainCredentialAccess`), `DnsCredentialResponse`, the domain parts `DomainDnsRecord`, `DomainResendStatus` and `DomainEmailVerificationState`, and `PublicProfileView` (with `PublicProfileProof` and `PublicProfileLink`) for the two public profile reads. Types only: the methods that call these routes still return plain dicts, and nothing on the wire changed.
- Generated response types for operations the contract described only as an open object: `UsageResponse` (with `UsageBalance`, `UsageTopChannel` and `UsagePeriod`) for the usage read; `DnsProvidersResponse` (with `DnsProviderMetadataItem`, camelCase as the API sends it) and `DnsCredentialListResponse` for the DNS providers and saved credentials, whose items are `DnsCredentialResponse`, which gains the optional `last_used_at`, `last_validated_at` and `validation_error` the list sends; `TemplateDefaultsResponse` for the platform default templates; `OwnVerificationRequestListResponse` and `IncomingVerificationRequestListResponse` (with `OwnVerificationRequestListItem` and `IncomingVerificationRequestListItem`) for the account's own request lists; `HitlKeysResponse`, `HitlKeysPutResponse`, `HitlApproverKeysResponse` and `HitlApproverKey` for a HITL config's keypair and its approvers' keys, where a key holding `confirmations:create` without `hitl:read` is sent only `public_key` and `kid` (and `authorization_id`), and `public_key` is null when the stored key material cannot be read; `DelegationCarriersResponse` (with `DelegationCarrier`) for where a delegation is still visible; and `RefreshSessionResponse` for the session renewal (camelCase as sent; kept as it is because the dashboard reads these names). Types only: the methods that call these routes still return plain dicts, and nothing on the wire changed.
- Generated response types for the public verification-request recipient flow and Lookalike Watch, which the contract described only as an open object: `PublicVerificationRequest` for the public read; `VerificationRequestExistingProofs` for the recipient's reusable proofs; `StartAssetVerificationResponse` for starting an asset, one flat type whose type- and channel-specific fields are optional; `AssetCredentialsCheck` for the saved DNS credential check; `AssetAutoVerifyResult`, `AssetCodeSubmitResult` and `AssetVerificationCheckResult` for auto-verify, code submission and the DNS/HTTP check; `VerificationRequestAssetStatus` for the asset status poll; and `LookalikeWatchSubscription`, `LookalikeAlertList` (with `LookalikeAlert`) and `LookalikeReportList` (with `LookalikeReport`) for Lookalike Watch, whose pages carry `page`, `limit` and `total` but no `total_pages`. Types only: no method's return type changed, and nothing on the wire changed.
- Generated response types for the account-session flows whose contract named the generic `SuccessResponse`: `AddPhoneSessionResponse` and `AddPhoneStatusResponse` for adding a phone; `AddEmailSessionResponse`, `AddEmailStatusResponse` and `VerifyEmailOtpResponse` for adding an email; `TwoFactorSessionResponse`, `TwoFactorEmailSelectionResponse` (the `requires_email_selection` answer), `TwoFactorStatusResponse`, `TwoFactorVerifyResponse` and `TwoFactorMagicLinkResponse` for a 2FA step-up; `UserDomainVerificationSessionResponse`, `UserDomainVerificationStatusResponse` and `UserDomainVerificationCheckResponse` for the self-service domain check; and `SmsNumbersByRegion`, the three SMS numbers the phone-add and 2FA sessions list. Types only: no client method returns these types (the session streams' polling fallbacks read three of these endpoints as plain dicts), and nothing on the wire changed.
- A confirmation carries `resends`: each "Send again" (`POST /api/v1/confirmations/{id}/resend`) with when it happened, whether a dashboard session or which API key asked, and the channels it went to (by authorization id or `owner`, never a phone number or link), the last 50 kept. Absent from an API that predates it.

### Changed

- A `503 billing_unavailable` is no longer retried: it raises `BillingUnavailableError` after one request. Every other 5xx is retried as before. Before, a 402 raised a plain `ProofError`; it now raises `BalanceEmptyError`, a `ProofError` subclass, so existing `except` clauses still match.
- The API now documents `AccountDeletionCancelledResponse.ok`, `AccountDeletionCancelTokenCheck.valid`, and `success` on `IdentifierRemovedResponse`, `DomainRemovedResponse` and `ProjectDeletedResponse` as booleans (always `true`); they were declared as a literal `true`, which the type generator published as `Literal["true"]`. The fields keep their released annotation in 1.x, because code written for 1.x relies on it, and become `bool` in the next major (listed in `sdks/shared/NEXT_MAJOR.md`).
- `confirmations.approval_link()` is documented as what it is: the HITL config owner's link, decided
  with the config's own key. It is not an approver's link; an approver's link goes only to their own
  channel, which `POST /api/v1/confirmations/{id}/resend` ("Send again") sends it to again. Every call returns the same owner link until "Send again" reaches the owner; "Send again" replaces it, and the next call returns a new one — the replaced owner link answers `410 approval_link_superseded`, as an approver's earlier links do once "Send again" reaches them. Calling it again cancels nothing.
- The generated `SubmitChallengeRequest` type now carries `code`, the field the API accepts. `code` is optional in the type, so a body written for an earlier 1.x release keeps type-checking. `challenge_code` and `source_identifier`, which the API never accepted, stay exactly as 1.x shipped them (`challenge_code` still required), marked deprecated, and go in the next major version; until then the type cannot describe a body carrying `code` alone, so send that body as a plain dict, as `verifications.submit()` does. A new `SubmitChallengeResponse` type describes what submitting a code returns; `verifications.submit()` is unchanged.
- The generated `Domain` type now describes what the API sends: every field `GET /me/domains` returns is declared (`detected_provider`, `dns_records`, `verified_providers`, `resend`, `email_verification` and the rest), each added one `NotRequired` unless it has always been sent, and `DomainStatus` gains `verifying`, `expired`, `revoking` and `reverification_required`. `provider` and `email_sending_enabled`, which the API never sent, stay as 1.x shipped them, marked deprecated (read `detected_provider` and `for_email_sending`), and go in the next major version. `PublicProfile` is likewise kept and marked deprecated: no endpoint returns it; the public reads return `PublicProfileView`. It is removed in the next major (listed in `sdks/shared/NEXT_MAJOR.md`).
- `profiles.list_templates`, `update_template`, `delete_template` and `preview_template` are now documented as removed in the next major. They still emit their `DeprecationWarning` and send the request, exactly as in 1.2.0, so a call fails with the server's answer: 410 `endpoint_retired`, naming the replacement, or the authentication or validation error that comes first.

### Fixed

- `proofs.verify_offline()` refuses a correctly signed token that lacks the claims the issuer requires of a proof (a non-empty `type`, `channel` and `identifier_hash`, and a `user_id` or `tenant_id`), answering `valid: False` with `reason` `invalid`, as `POST /proofs/validate` does. It used to answer `valid: True` for anything signed with the proof key, including a data-export download receipt.
- The SDK imports on Python 3.10 and 3.11, which `requires-python = ">=3.10"` admits. 1.1.0 and 1.2.0 raised `SyntaxError: f-string: unmatched '('` on `import proof_sdk` there: path f-strings in `proofs`, `verifications`, `verification_requests` and `webhook_deliveries` nested `safe=""` inside a double-quoted f-string, which Python accepts only from 3.12 (PEP 701). The unit tests now run on 3.10 as well as 3.12.
- `TopUpRequest.amount` and `AutoTopUpRequest.amount` also accept the ints `10`, `50` and `200`: `Literal["10", "50", "200", 10, 50, 200]`. 1.2.0 typed them only as the strings, which the API refuses, so a correct integer failed type-checking. The strings stay for 1.x code and go in the next major (listed in `sdks/shared/NEXT_MAJOR.md`). No released method sends either type.
- `CheckoutResponse` and `PortalResponse` name the fields the API sends, `checkout_url` and `portal_url`. They declared `url`, which the API never sent. `url` stays in both types, as released, for 1.x code that names it — but no response carries it, so read `checkout_url` / `portal_url` (a `resp["url"]` raises `KeyError`). It is removed in the next major (listed in `sdks/shared/NEXT_MAJOR.md`).
- `verifications.list(channel=...)` filters by channel. The API used to drop the `channel` filter and return every channel; it now applies it, and refuses an unknown channel with `400 validation_error`.
- `verifications.wait_for_completion()`, `verifications.stream()` and
  `streams.verification_events()` end on `cancelled`, the status of the losing channel in a
  multi-channel verification. They used to keep polling until the timeout.
- The README's `proofs.revoke()` example passes `reason="user_request"`. It passed `"User requested"`, which the API refuses with `400 validation_error`: `reason` takes only `user_request`, `fraud`, `key_compromise`, `asset_transferred` or `other`, now named in the method's docstring, which also says that `reason=None` sends no reason and the API records `user_request`, and that a delegation proof (`ph_dlg_*`) refuses `asset_transferred`. The parameter stays `str | None` through 1.x; narrowing it is listed in `sdks/shared/NEXT_MAJOR.md`.

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

### Fixed

- `streams.auth_session_events()` never ended on a finished sign-in: it waited for `authenticated`, which
  is not an auth-session status. It now ends on `verified`, `expired`, and `completed_elsewhere`, a new
  terminal status: an email sign-in that the person finished in a different browser from the one that
  started it ("Sign in here" on the emailed link's page). That session never reaches `verified` and
  issues no cookies to the starter.

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
