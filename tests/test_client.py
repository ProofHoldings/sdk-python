"""Tests for ProofHoldings client construction."""

import pytest

from proof_sdk import ProofHoldings


class TestClientConstruction:
    def test_rejects_empty_key(self) -> None:
        with pytest.raises(ValueError, match="api_key is required"):
            ProofHoldings("")

    def test_creates_with_valid_key(self) -> None:
        client = ProofHoldings("pk_test_123")
        assert client.verifications is not None
        assert client.verification_requests is not None
        assert client.proofs is not None
        assert client.sessions is not None
        assert client.webhook_deliveries is not None

    def test_accepts_custom_options(self) -> None:
        client = ProofHoldings(
            "pk_test_123",
            base_url="https://custom.api.com",
            timeout=5.0,
            max_retries=5,
        )
        assert client._http.base_url == "https://custom.api.com"

    def test_strips_trailing_slash(self) -> None:
        client = ProofHoldings("pk_test_123", base_url="https://api.example.com/")
        assert client._http.base_url == "https://api.example.com"
