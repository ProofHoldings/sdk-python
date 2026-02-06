"""Tests for polling/waitForCompletion across resources."""

from __future__ import annotations

from typing import Any

import pytest

from proof_sdk.errors import PollingTimeoutError
from proof_sdk.resources.verifications import Verifications
from proof_sdk.resources.sessions import Sessions
from proof_sdk.resources.verification_requests import VerificationRequests


@pytest.mark.asyncio
class TestVerificationPolling:
    async def test_returns_immediately_for_terminal(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "ver_1", "status": "verified"}
        v = Verifications(mock_http)

        result = await v.wait_for_completion("ver_1", interval=0.01, timeout=0.1)

        assert result["status"] == "verified"
        assert mock_http.get.await_count == 1

    async def test_polls_until_terminal(self, mock_http: Any) -> None:
        mock_http.get.side_effect = [
            {"id": "ver_1", "status": "pending"},
            {"id": "ver_1", "status": "pending"},
            {"id": "ver_1", "status": "verified"},
        ]
        v = Verifications(mock_http)

        result = await v.wait_for_completion("ver_1", interval=0.01, timeout=5.0)

        assert result["status"] == "verified"
        assert mock_http.get.await_count == 3

    async def test_timeout_raises(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "ver_1", "status": "pending"}
        v = Verifications(mock_http)

        with pytest.raises(PollingTimeoutError):
            await v.wait_for_completion("ver_1", interval=0.01, timeout=0.05)

    @pytest.mark.parametrize("status", ["verified", "failed", "expired", "revoked"])
    async def test_recognizes_all_terminal_states(self, mock_http: Any, status: str) -> None:
        mock_http.get.return_value = {"id": "ver_1", "status": status}
        v = Verifications(mock_http)

        result = await v.wait_for_completion("ver_1", interval=0.01, timeout=0.1)
        assert result["status"] == status


@pytest.mark.asyncio
class TestSessionPolling:
    async def test_returns_for_terminal(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "ses_1", "status": "verified"}
        s = Sessions(mock_http)

        result = await s.wait_for_completion("ses_1", interval=0.01, timeout=0.1)
        assert result["status"] == "verified"

    @pytest.mark.parametrize("status", ["verified", "failed", "expired"])
    async def test_recognizes_all_terminal_states(self, mock_http: Any, status: str) -> None:
        mock_http.get.return_value = {"id": "ses_1", "status": status}
        s = Sessions(mock_http)

        result = await s.wait_for_completion("ses_1", interval=0.01, timeout=0.1)
        assert result["status"] == status

    async def test_timeout_raises(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "ses_1", "status": "pending"}
        s = Sessions(mock_http)

        with pytest.raises(PollingTimeoutError):
            await s.wait_for_completion("ses_1", interval=0.01, timeout=0.05)


@pytest.mark.asyncio
class TestVerificationRequestPolling:
    async def test_returns_for_terminal(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "vr_1", "status": "completed"}
        vr = VerificationRequests(mock_http)

        result = await vr.wait_for_completion("vr_1", interval=0.01, timeout=0.1)
        assert result["status"] == "completed"

    @pytest.mark.parametrize("status", ["completed", "expired", "cancelled"])
    async def test_recognizes_all_terminal_states(self, mock_http: Any, status: str) -> None:
        mock_http.get.return_value = {"id": "vr_1", "status": status}
        vr = VerificationRequests(mock_http)

        result = await vr.wait_for_completion("vr_1", interval=0.01, timeout=0.1)
        assert result["status"] == status

    async def test_timeout_raises(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "vr_1", "status": "pending"}
        vr = VerificationRequests(mock_http)

        with pytest.raises(PollingTimeoutError):
            await vr.wait_for_completion("vr_1", interval=0.01, timeout=0.05)
