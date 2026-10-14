"""Tests for polling/waitForCompletion across resources."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest

from proof_sdk.errors import PollingTimeoutError
from proof_sdk.polling import (
    DEFAULT_BACKOFF,
    DEFAULT_INTERVAL,
    DEFAULT_JITTER,
    DEFAULT_MAX_INTERVAL,
    poll_until_complete,
)
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


class TestPollingContract:
    def test_default_constants_match_contract(self) -> None:
        assert DEFAULT_INTERVAL == 2.0
        assert DEFAULT_BACKOFF == 1.5
        assert DEFAULT_MAX_INTERVAL == 30.0
        assert DEFAULT_JITTER == 0.5


@pytest.mark.asyncio
class TestBackoff:
    async def test_interval_grows_between_polls(self) -> None:
        call_times: list[float] = []

        async def retrieve() -> dict[str, Any]:
            call_times.append(time.monotonic())
            return {"status": "pending" if len(call_times) < 4 else "verified"}

        result = await poll_until_complete(
            retrieve,
            ["verified"],
            "Test",
            interval=0.02,
            timeout=5.0,
            backoff=2.0,
            max_interval=1.0,
            jitter=0.0,
        )

        assert result["status"] == "verified"
        assert len(call_times) == 4
        gap1 = call_times[1] - call_times[0]
        gap2 = call_times[2] - call_times[1]
        # Second gap should reflect 2x backoff (with small scheduler noise tolerance)
        assert gap2 > gap1

    async def test_max_interval_caps_backoff(self) -> None:
        call_times: list[float] = []

        async def retrieve() -> dict[str, Any]:
            call_times.append(time.monotonic())
            return {"status": "pending" if len(call_times) < 5 else "verified"}

        result = await poll_until_complete(
            retrieve,
            ["verified"],
            "Test",
            interval=0.01,
            timeout=5.0,
            backoff=10.0,
            max_interval=0.05,
            jitter=0.0,
        )
        assert result["status"] == "verified"
        # All gaps should be capped at max_interval
        gaps = [call_times[i + 1] - call_times[i] for i in range(len(call_times) - 1)]
        for g in gaps[1:]:
            assert g < 0.2  # allow scheduler overhead, but clearly capped


@pytest.mark.asyncio
class TestCancellation:
    async def test_cancel_event_aborts_polling(self) -> None:
        call_count = 0
        cancel = asyncio.Event()

        async def retrieve() -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                cancel.set()
            return {"status": "pending"}

        with pytest.raises(asyncio.CancelledError):
            await poll_until_complete(
                retrieve,
                ["verified"],
                "Test",
                interval=0.01,
                timeout=5.0,
                backoff=1.0,
                max_interval=0.05,
                jitter=0.0,
                cancel_event=cancel,
            )

    async def test_cancel_event_preset_before_call(self) -> None:
        cancel = asyncio.Event()
        cancel.set()

        async def retrieve() -> dict[str, Any]:
            return {"status": "pending"}

        with pytest.raises(asyncio.CancelledError):
            await poll_until_complete(
                retrieve,
                ["verified"],
                "Test",
                interval=0.01,
                timeout=5.0,
                cancel_event=cancel,
            )
