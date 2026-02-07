# @proof/sdk - Python

Official Python SDK for the [proof.holdings](https://proof.holdings) verification API.

## Installation

```bash
pip install proof-sdk
```

For offline JWT verification:

```bash
pip install proof-sdk[jwt]
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

# Offline verification (requires proof-sdk[jwt])
result = await proof.proofs.verify_offline("eyJhbGciOi...")
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
)
```

## Requirements

- Python >= 3.10
- httpx >= 0.25.0
- PyJWT + cryptography (optional, for offline verification)
