"""Main Proof client."""

from __future__ import annotations

from .credentials import DEFAULT_BASE_URL  # noqa: F401 — still importable from here, as before
from .credentials import missing_key_message, resolve_api_key, resolve_base_url
from .http import HttpClient
from .jwks.key_set_cache import DEFAULT_MAX_JWKS_AGE_SECONDS
from .resources import (
    Verifications,
    VerificationRequests,
    Proofs,
    Sessions,
    Streams,
    WebhookDeliveries,
    Authorizations,
    Confirmations,
    Hitl,
    HitlKeys,
    Templates,
    Profiles,
    PublicProfiles,
    ProofMe,
    Me,
    Circles,
    Delegations,
)

DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2


class Proof:
    """Official Python client for the proof.holdings API.

    Usage::

        import asyncio
        from proof_sdk import Proof

        async def main():
            proof = Proof("pk_live_...")

            # Create a verification
            v = await proof.verifications.create(
                type="phone", channel="whatsapp", identifier="+1234567890"
            )

            # Wait for completion
            result = await proof.verifications.wait_for_completion(v["id"])

            await proof.close()

        asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_jwks_age: float = DEFAULT_MAX_JWKS_AGE_SECONDS,
    ) -> None:
        # With a key it is used as given. Without one — ``Proof()`` — it is resolved the way
        # ``npx @proof-holdings/mcp-server login`` expects: a non-empty PROOF_API_KEY, else the
        # entry saved for this client's base URL in ~/.proof-holdings/credentials. An explicit
        # empty key is an error and never reads either. The base URL is the explicit argument,
        # else a non-empty PROOF_BASE_URL, else the default.
        resolved_base_url = resolve_base_url(base_url)
        if api_key == "":
            raise ValueError('api_key is required. Pass your key as: Proof("pk_live_...")')
        resolved = resolve_api_key(explicit=api_key, base_url=resolved_base_url)
        if resolved.api_key is None:
            raise ValueError(missing_key_message(resolved_base_url, resolved.notice))

        self._http = HttpClient(
            api_key=resolved.api_key,
            base_url=resolved_base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.verifications = Verifications(self._http)
        self.verification_requests = VerificationRequests(self._http)
        self.proofs = Proofs(self._http, max_jwks_age=max_jwks_age)
        self.sessions = Sessions(self._http)
        self.streams = Streams(self._http)
        self.webhook_deliveries = WebhookDeliveries(self._http)
        self.authorizations = Authorizations(self._http)
        self.confirmations = Confirmations(self._http)
        self.hitl = Hitl(self._http)
        self.hitl_keys = HitlKeys(self._http)
        self.templates = Templates(self._http)
        self.profiles = Profiles(self._http)
        self.public_profiles = PublicProfiles(self._http)
        self.proof_me = ProofMe(self._http)
        self.me = Me(self._http)
        self.circles = Circles(self._http)
        self.delegations = Delegations(self._http)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.close()

    async def __aenter__(self) -> Proof:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
