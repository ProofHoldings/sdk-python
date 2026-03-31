"""Proofs resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import (
    ProofStatusResponse,
    RevocationList,
    RevokeProofResponse,
    ValidateProofResponse,
)


class Proofs:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._jwks_url = f"{http.base_url}/.well-known/jwks.json"
        self._jwks_client: Any = None

    async def validate(self, proof_token: str) -> ValidateProofResponse:
        """Validate a proof token online (checks revocation status). Public endpoint — no API key required."""
        body: dict[str, Any] = {"proof_token": proof_token}
        return await self._http.post("/api/v1/proofs/validate", body)

    async def revoke(self, id: str, reason: str | None = None) -> RevokeProofResponse:
        """Revoke a proof by verification ID."""
        body: dict[str, Any] = {}
        if reason is not None:
            body["reason"] = reason
        return await self._http.post(f"/api/v1/proofs/{quote(id, safe="")}/revoke", body)

    async def status(self, id: str) -> ProofStatusResponse:
        """Get the status of a proof by verification ID."""
        return await self._http.get(f"/api/v1/proofs/{quote(id, safe="")}/status")

    async def list_revoked(self) -> RevocationList:
        """Get the revocation list."""
        return await self._http.get("/api/v1/proofs/revoked")

    async def verify_offline(self, token: str) -> ValidateProofResponse:
        """Verify a proof token offline using JWKS public keys.

        The JWKS is fetched once and cached. Call ``refresh_jwks()`` to
        invalidate the cache (e.g. after key rotation).

        Requires the ``PyJWT`` and ``cryptography`` packages.
        Install with: ``pip install proof-holdings[jwt]``
        """
        try:
            import jwt
            from jwt import PyJWKClient
        except ImportError:
            raise ImportError(
                "Offline verification requires PyJWT and cryptography. "
                "Install with: pip install proof-holdings[jwt]"
            )

        try:
            if self._jwks_client is None:
                self._jwks_client = PyJWKClient(self._jwks_url, cache_keys=True)

            signing_key = self._jwks_client.get_signing_key_from_jwt(token)

            # Get algorithm from the JWKS key itself rather than hardcoding
            algorithm = signing_key.key_type
            alg_map = {"RSA": "RS256", "EC": "ES256"}
            algorithms = [alg_map.get(algorithm, "RS256")]

            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=algorithms,
                issuer="proof.holdings",
                options={"verify_exp": True},
                leeway=5,
            )
            return {
                "valid": True,
                "payload": {
                    "iss": payload.get("iss"),
                    "sub": payload.get("sub"),
                    "iat": payload.get("iat"),
                    "exp": payload.get("exp"),
                    "type": payload.get("type"),
                    "channel": payload.get("channel"),
                    "identifier_hash": payload.get("identifier_hash"),
                    "verified_at": payload.get("verified_at"),
                    "user_id": payload.get("user_id"),
                },
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def refresh_jwks(self) -> None:
        """Force-refresh the cached JWKS (e.g. after key rotation)."""
        self._jwks_client = None
