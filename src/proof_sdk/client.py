"""Main Proof client."""

from __future__ import annotations

from .http import HttpClient
from .resources import (
    Verifications,
    VerificationRequests,
    Proofs,
    Sessions,
    WebhookDeliveries,
    Templates,
    Profiles,
    Projects,
    Billing,
    Phones,
    Emails,
    Assets,
    Auth,
    Settings,
    ApiKeys,
)

DEFAULT_BASE_URL = "https://api.proof.holdings"
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
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        if not api_key:
            raise ValueError('api_key is required. Pass your key as: Proof("pk_live_...")')

        self._http = HttpClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.verifications = Verifications(self._http)
        self.verification_requests = VerificationRequests(self._http)
        self.proofs = Proofs(self._http)
        self.sessions = Sessions(self._http)
        self.webhook_deliveries = WebhookDeliveries(self._http)
        self.templates = Templates(self._http)
        self.profiles = Profiles(self._http)
        self.projects = Projects(self._http)
        self.billing = Billing(self._http)
        self.phones = Phones(self._http)
        self.emails = Emails(self._http)
        self.assets = Assets(self._http)
        self.auth = Auth(self._http)
        self.settings = Settings(self._http)
        self.api_keys = ApiKeys(self._http)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.close()

    async def __aenter__(self) -> Proof:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
