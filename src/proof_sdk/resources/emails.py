"""Emails resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import SuccessResponse, UserEmail


class Emails:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> list[UserEmail]:
        """List all emails for the authenticated user."""
        return await self._http.get("/api/v1/me/emails")

    async def remove(self, email_id: str) -> SuccessResponse:
        """Remove an email by ID."""
        eid = quote(email_id, safe="")
        return await self._http.delete(f"/api/v1/me/emails/{eid}")

    async def set_primary(self, email_id: str) -> UserEmail:
        """Set an email as the primary email."""
        eid = quote(email_id, safe="")
        return await self._http.put(f"/api/v1/me/emails/{eid}/primary")

    async def start_add(self, *, email: str) -> dict[str, Any]:
        """Start adding a new email.

        Args:
            email: The email address to add.
        """
        return await self._http.post("/api/v1/me/emails/add", {"email": email})

    async def get_add_status(self, session_id: str) -> dict[str, Any]:
        """Get the status of an email add session."""
        sid = quote(session_id, safe="")
        return await self._http.get(f"/api/v1/me/emails/add/{sid}")

    async def verify_otp(self, session_id: str, *, code: str) -> UserEmail:
        """Verify an email using an OTP code.

        Args:
            session_id: The add session ID.
            code: The OTP code from the verification email.
        """
        sid = quote(session_id, safe="")
        return await self._http.post(f"/api/v1/me/emails/add/{sid}/verify", {"code": code})

    async def resend_otp(self, session_id: str) -> SuccessResponse:
        """Resend the email OTP."""
        sid = quote(session_id, safe="")
        return await self._http.post(f"/api/v1/me/emails/add/{sid}/resend")
