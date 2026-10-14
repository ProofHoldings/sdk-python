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
response = await proof.proofs.revoke("ver_abc123", reason="User requested")

# Get revocation list
revoked = await proof.proofs.list_revoked()

# Offline verification (requires proof-holdings-sdk[jwt]) — no API call with your key. Reads two public
# documents: the JWKS for the signature, and the issuer's status list for revocation, which is
# checked by default.
result = await proof.proofs.verify_offline("eyJhbGciOi...")
if not result["valid"]:
    # "revoked" | "suspended" | "expired" | "invalid" | "status_unavailable"
    # | "key_revoked" | "jwks_stale" | "wrong_key_purpose" | "outside_key_window"
    # | "token_lifetime_exceeded" | "unknown_key" — see "Signing-key rotation" below
    print(result["reason"])

# "status_unavailable" means the revocation status could NOT be read — an unreachable list, one
# that failed its own checks, or a slot the list does not cover. It is a refusal to guess, not a
# claim that the proof is withdrawn. A token minted without a status-list slot stays valid and
# reports revocation_checked=False, exactly as the issuer's own validate answers for it.

# Signature only, for an air-gapped check against a warm key cache:
signature_only = await proof.proofs.verify_offline("eyJhbGciOi...", check_revocation=False)
assert signature_only["revocation_checked"] is False  # never assume it was checked
```

### Signing-key rotation

`verify_offline` fetches and caches the issuer's key set (JWKS) itself and follows its rotation
rules. The cached set is reused for 10 minutes; a `kid` it does not know triggers one refetch, at
most once every 30 seconds.

- **`key_revoked`** — the issuer revoked the key that signed the token. The result carries
  `pull_hint: {"issuer_origin", "handle"}`: where to fetch the re-signed token (`handle` is the
  proof's `proof_id`, or a delegation's `sub`). The handle is read from the token itself, whose
  signature a revoked key no longer vouches for: URL-encode it before building a request from it. A
  revocation takes effect only after two key-set fetches at least 5 minutes apart both carry it, and
  is then kept for a year.
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
