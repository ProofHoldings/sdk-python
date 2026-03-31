"""Domains resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import Domain, DomainCheckResponse, DomainVerificationResponse, SuccessResponse


class Domains:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> dict[str, Any]:
        """List all domains."""
        return await self._http.get("/api/v1/me/domains")

    async def add(self, **kwargs: Any) -> Domain:
        """Add a domain."""
        return await self._http.post("/api/v1/me/domains", kwargs)

    async def get(self, domain_id: str) -> Domain:
        """Get a domain by ID."""
        return await self._http.get(f"/api/v1/me/domains/{quote(domain_id, safe='')}")

    async def delete(self, domain_id: str) -> SuccessResponse:
        """Delete a domain."""
        return await self._http.delete(f"/api/v1/me/domains/{quote(domain_id, safe='')}")

    async def oauth_url(self, domain_id: str) -> dict[str, Any]:
        """Get OAuth URL for DNS provider authorization."""
        return await self._http.post(f"/api/v1/me/domains/{quote(domain_id, safe='')}/oauth-url")

    async def verify(self, domain_id: str) -> DomainVerificationResponse:
        """Verify domain ownership."""
        return await self._http.post(f"/api/v1/me/domains/{quote(domain_id, safe='')}/verify")

    async def connect_cloudflare(self, domain_id: str, **kwargs: Any) -> SuccessResponse:
        """Connect Cloudflare to a domain."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/connect/cloudflare", kwargs
        )

    async def connect_godaddy(self, domain_id: str, **kwargs: Any) -> SuccessResponse:
        """Connect GoDaddy to a domain."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/connect/godaddy", kwargs
        )

    async def connect_provider(self, domain_id: str, provider: str, **kwargs: Any) -> SuccessResponse:
        """Connect a DNS provider to a domain."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/connect/{quote(provider, safe='')}",
            kwargs,
        )

    async def add_provider(self, domain_id: str, provider: str, **kwargs: Any) -> SuccessResponse:
        """Add an additional verification provider to an already-verified domain."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/add-provider/{quote(provider, safe='')}",
            kwargs,
        )

    async def get_providers(self) -> dict[str, Any]:
        """Get metadata for all supported DNS providers."""
        return await self._http.get("/api/v1/me/dns-providers")

    async def verify_with_credentials(self, domain_id: str) -> DomainCheckResponse:
        """Verify domain with existing credentials."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/verify-with-credentials"
        )

    async def check_credentials(self, domain_id: str) -> SuccessResponse:
        """Check if credentials have access to domain."""
        return await self._http.get(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/check-credentials"
        )

    async def start_email_verification(self, domain_id: str, **kwargs: Any) -> dict[str, Any]:
        """Start email verification for a domain."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/verify-email", kwargs
        )

    async def confirm_email_code(self, domain_id: str, **kwargs: Any) -> DomainCheckResponse:
        """Confirm email verification code."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/verify-email/confirm", kwargs
        )

    async def resend_email(self, domain_id: str, **kwargs: Any) -> SuccessResponse:
        """Resend email verification."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/verify-email/resend", kwargs
        )

    async def email_setup(self, domain_id: str, **kwargs: Any) -> SuccessResponse:
        """Setup email sending for a domain."""
        return await self._http.post(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/email-setup", kwargs
        )

    async def email_status(self, domain_id: str) -> dict[str, Any]:
        """Check email sending status for a domain."""
        return await self._http.get(
            f"/api/v1/me/domains/{quote(domain_id, safe='')}/email-status"
        )
