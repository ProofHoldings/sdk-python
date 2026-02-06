"""Main ProofHoldings client."""

from __future__ import annotations

from .http import HttpClient
from .resources import (
    Verifications,
    VerificationRequests,
    Proofs,
    Sessions,
    WebhookDeliveries,
)

DEFAULT_BASE_URL = "https://api.proof.holdings"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2


class ProofHoldings:
    """Official Python client for the proof.holdings API.

    Usage::

        import asyncio
        from proof_sdk import ProofHoldings

        async def main():
            proof = ProofHoldings("pk_live_...")

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
            raise ValueError("api_key is required")

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

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.close()

    async def __aenter__(self) -> ProofHoldings:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
