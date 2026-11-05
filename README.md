# proof-holdings-sdk

Official Python SDK for the [proof.holdings](https://proof.holdings) verification API.

## Installation

```bash
pip install proof-holdings-sdk
```

For offline JWT verification:

```bash
pip install 'proof-holdings-sdk[jwt]'
```

## Quick Start

```python
import asyncio
from proof_sdk import Proof

async def main():
    async with Proof("pk_live_...") as proof:
        # Create a phone verification
        v = await proof.verifications.create(
            type="phone",
            channel="whatsapp",
            identifier="+1234567890",
        )
        print(f"Verification {v['id']} created: {v['status']}")

        # Wait for user to complete verification
        result = await proof.verifications.wait_for_completion(v["id"])
        print(f"Result: {result['status']}")

asyncio.run(main())
```

## Resources

### Verifications

```python
# Create
v = await proof.verifications.create(type="domain", channel="dns", identifier="example.com")

# Retrieve
v = await proof.verifications.retrieve("ver_abc123")

# List with filters
page = await proof.verifications.list(status="verified", type="phone", limit=10)

# Trigger DNS/HTTP check
v = await proof.verifications.verify("ver_abc123")

# Submit OTP code
v = await proof.verifications.submit("ver_abc123", code="ABC123")

# Poll until complete
v = await proof.verifications.wait_for_completion("ver_abc123", interval=2.0, timeout=300.0)

# WABA (WhatsApp Business) verification
v = await proof.verifications.create(type="waba", channel="waba_otp", identifier="+37069199199")
# OTP is sent via WhatsApp — submit with proof.verifications.submit(v["id"], code="123456")

# Telegram Bot verification
v = await proof.verifications.create(
    type="telegram_bot", channel="telegram_bot_token", identifier="@mybusinessbot"
)
# Submit bot token with proof.verifications.submit(v["id"], code="bot_token_here")
```

### Verification Requests (Multi-Asset)

```python
# Create multi-asset request
req = await proof.verification_requests.create(
    assets=[
        {"type": "phone", "required": True},
        {"type": "email", "identifier": "user@example.com"},
    ],
    reference_id="user_123",
    callback_url="https://yourapp.com/webhook",
    expires_in=86400,  # 24 hours in seconds
)
print(f"Send user to: {req['verification_url']}")

# Poll until complete
result = await proof.verification_requests.wait_for_completion(req["id"])
```

### Proofs

```python
# Validate online (checks revocation)
result = await proof.proofs.validate("eyJhbGciOi...")

# Revoke
response = await proof.proofs.revoke("ver_abc123", reason="user_request")

# Get revocation list
revoked = await proof.proofs.list_revoked()

# After a signing-key rotation: list what was re-signed, page by page, then pull the current tokens.
# `since` is a timezone-aware datetime or an ISO-8601 string with an offset.
from datetime import datetime, timezone
since = datetime(2026, 10, 1, tzinfo=timezone.utc)
page, total_pages = 1, 1
while page <= total_pages:
    reissued = await proof.proofs.list_reissued(since, page=page, limit=100)
    total_pages = reissued["pagination"]["total_pages"]
    for item in reissued["data"]:
        if item["proof_id"].startswith("ph_dlg_"):
            pulled = await proof.proofs.delegation_token(item["proof_id"])  # public, no key needed
        else:
            pulled = await proof.proofs.token(item["proof_id"])
    page += 1

# Offline verification (requires proof-holdings-sdk[jwt]) — no API call with your key. Reads two public
# documents: the JWKS for the signature, and the issuer's status list for revocation, which is
# checked by default.
result = await proof.proofs.verify_offline("eyJhbGciOi...")
if not result["valid"]:
    # "revoked" | "suspended" | "expired" | "invalid" | "status_unavailable"
    # | "key_revoked" | "jwks_stale" | "wrong_key_purpose" | "outside_key_window"
    # | "token_lifetime_exceeded" | "unknown_key" — see "Key rotation" below
    print(result["reason"])

# "status_unavailable" means the revocation status could NOT be read — an unreachable list, one
# that failed its own checks, or a slot the list does not cover. It is a refusal to guess, not a
# claim that the proof is withdrawn. A token minted without a status-list slot stays valid and
# reports revocation_checked=False, exactly as the issuer's own validate answers for it.

# Signature only, for an air-gapped check against a warm key cache:
signature_only = await proof.proofs.verify_offline("eyJhbGciOi...", check_revocation=False)
assert signature_only["revocation_checked"] is False  # never assume it was checked
```

### Sessions (Phone-First Flow)

```python
session = await proof.sessions.create(channel="telegram")
print(f"Deep link: {session['deep_link']}")
print(f"QR code: {session['qr_code']}")

# Poll until verified
result = await proof.sessions.wait_for_completion(session["id"])
```

### Webhook Deliveries

```python
# List deliveries
deliveries = await proof.webhook_deliveries.list(status="failed")

# Retry a failed delivery
result = await proof.webhook_deliveries.retry("del_abc123")
```

### Webhook Endpoints

Each endpoint signs its deliveries with its own secret. The secret is returned **once** — by
`create` and by `rotate_secret` — and never by `list`, `retrieve` or `update` (they carry
`secret_set` only), so store it when you receive it.

```python
# Create an endpoint for every sub-account (scope="selected" + profile_ids for chosen ones)
endpoint = await proof.webhook_endpoints.create(
    url="https://yourapp.com/webhooks/proof",
    scope="all",
    events=["verification.completed", "proof.revoked"],
)
secret = endpoint["secret"]  # returned only now

# List, retrieve, update (description=None clears the description)
endpoints = await proof.webhook_endpoints.list()
endpoint = await proof.webhook_endpoints.retrieve(endpoint["id"])
await proof.webhook_endpoints.update(endpoint["id"], status="disabled")

# Rotate the signing secret (the new one is returned once), then delete
rotated = await proof.webhook_endpoints.rotate_secret(endpoint["id"])
await proof.webhook_endpoints.delete(endpoint["id"])

# Rotate a sub-account's callback signing secret (what signs its callback_url deliveries)
callback = await proof.profiles.rotate_callback_secret("profile_id")
new_secret = callback["secret"]  # returned only now
```

## Key rotation


`verify_offline` fetches and caches the issuer's key set (JWKS) itself and follows its rotation
rules. The cached set is reused for 10 minutes; a `kid` it does not know triggers one refetch, at
most once every 30 seconds.

**Retiring the legacy keys.** The keys Proof signed with before this rotation scheme — the legacy
keys — are retired once. Proof re-signs the live tokens they signed under a current key, and revokes
the legacy keys no earlier than 30 days after that re-signing. From then on an old copy that names
its key answers `key_revoked`, and one with no `kid` does not verify at all. A token that was
already superseded, revoked or expired when they were re-signed, or that changed while it was read,
or that the re-signing refused or could not match to its record, stays on the legacy key and stops
verifying when they are revoked. Replace every copy you handed out or published with the re-signed
token (see `key_revoked` below).

- **`key_revoked`** — the issuer revoked the key that signed the token, after a suspected compromise
  or at the retirement of the legacy keys. The result carries
  `pull_hint: {"issuer_origin", "handle"}`: where to fetch the re-signed token (`handle` is the
  proof's `proof_id`, or a delegation's `sub`). The handle is read from the token itself, whose
  signature a revoked key no longer vouches for: URL-encode it before building a request from it —
  `proofs.token(handle)` for a `ph_ctl_` handle and `proofs.delegation_token(handle)` for a
  `ph_dlg_` one do that for you. `proofs.token` serves only a proof your own account owns — any
  other answers 404 — so a re-signed token of someone else's proof comes from whoever holds it;
  `proofs.delegation_token` is public. An API key is refused the token of one of the account's own
  verified assets (403 `owner_session_required`), and `proofs.list_reissued` does not list those for
  a key: read it signed in, in the dashboard. A revocation takes effect only after two key-set
  fetches at least 5 minutes apart both carry it, and is then kept for a year.
- **`jwks_stale`** — the key set could not be refreshed and the cached copy is older than
  `max_jwks_age` (seconds; default 24 hours, at most 25 days; `Proof(key, max_jwks_age=...)`). The
  result carries `cache_age_seconds`. Call `refresh_jwks()` once the issuer is reachable.
- **`wrong_key_purpose`**, **`outside_key_window`**, **`token_lifetime_exceeded`** — the key belongs
  to another token family, the token was signed outside the key's validity window, or it lives
  longer than the key allows. **`unknown_key`** — no published key matches the token's `kid`.

Revoked-key tombstones are kept in memory only — they are not persisted, so a restarted process
learns them again from the issuer. `clear_tombstones()` forgets them on purpose. `refresh_jwks()`
makes the next verification refetch the key set (and drops the cached status list); it does not
forget tombstones. A tombstone naming a key last seen live is logged as a warning on the
`proof_sdk` logger.

**What a rotation changes.** `iat` is when the token was signed; `verified_at` is when the control
it attests was verified. A token re-signed after a key revocation keeps every claim but `iat` — the
same `jti`, `exp` and `verified_at`, under a new `kid`; a proof token from before `jti` existed also
gains its row's `jti` and `proof_id`. Judge a proof's age by `verified_at`.

**A generic JOSE or JWT library gives signature-only assurance.** Checking the signature against
the JWKS is none of the checks above — a key's purpose, its window and lifetime limit, tombstones,
the status list. Use `verify_offline` or `proofs.validate()`.

**The current `jti` generation is an online check.** Once a proof is verified again,
`proofs.validate()` (`POST /proofs/validate`) answers `superseded` for the earlier token. Offline
verification still accepts that token until its own `exp`: it carries the proof's status-list slot,
shared with the current token, so revoking or suspending the proof stops both.

**Refresh does not revoke.** A token re-issued within its generation — a renewal — leaves the
earlier copy valid until its own `exp`; only a revoked key ends it sooner. To withdraw a token,
revoke the proof.

**Minimum version.** These checks are in `proof-holdings-sdk` 1.0.0 and later; 1.1.0 is the first release on
PyPI. `proofs.token()`, `proofs.list_reissued()` and `proofs.delegation_token()` are in 1.4.0 and later.

## Error Handling

```python
from proof_sdk import Proof, NotFoundError, RateLimitError, RequestTimeoutError, ProofError

async with Proof("pk_live_...") as proof:
    try:
        v = await proof.verifications.retrieve("nonexistent")
    except NotFoundError as e:
        print(f"Not found: {e.code}")
    except RateLimitError:
        print("Rate limited, try again later")
    except ProofError as e:
        print(f"API error {e.status_code}: {e.code} - {e}")
```

## Configuration

```python
proof = Proof(
    "pk_live_...",
    base_url="https://api.proof.holdings",  # Default
    timeout=30.0,                            # Seconds, default 30
    max_retries=2,                           # Default 2
    max_jwks_age=86_400,                     # Offline verification stale bound, seconds (default 24h)
)
```

## Credentials

Sign in once with `npx @proof-holdings/mcp-server login` and construct the client with no key:

```python
proof = Proof()                              # or Proof(base_url="...")
```

When the key argument is omitted it is resolved in this order:

1. `PROOF_API_KEY`, when set and non-empty.
2. The entry for this client's base URL in `~/.proof-holdings/credentials`, the file the login
   command writes. The file is keyed by base URL, so a key saved against staging is never sent
   to production.
3. Otherwise construction raises `ValueError`, naming the three roads: pass the key, set
   `PROOF_API_KEY`, or run `npx @proof-holdings/mcp-server login`.

The base URL is the `base_url` argument, else a non-empty `PROOF_BASE_URL`, else
`https://api.proof.holdings`. An explicit key is used as given, and an explicit empty key
(`Proof("")`) is an error — neither reads the environment or the file.

## Requirements

- Python >= 3.10
- httpx >= 0.25.0
- cryptography >= 41.0.0 (HITL message encryption)
- PyJWT (optional, the `jwt` extra, for offline verification)
