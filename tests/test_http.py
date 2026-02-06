"""Tests for HTTP client retry logic and error handling."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from proof_sdk.errors import (
    NetworkError,
    NotFoundError,
    RequestTimeoutError,
    ServerError,
    ValidationError,
)
from proof_sdk.http import HttpClient


def make_client(max_retries: int = 0) -> HttpClient:
    return HttpClient(
        api_key="pk_test_123",
        base_url="https://api.example.com",
        timeout=5.0,
        max_retries=max_retries,
    )


def mock_response(status_code: int, json_data: dict | None = None, headers: dict | None = None) -> httpx.Response:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.headers = headers or {}
    return resp


@pytest.mark.asyncio
class TestSuccessfulRequests:
    async def test_get_returns_json(self) -> None:
        client = make_client()
        mock_resp = mock_response(200, {"id": "ver_123"})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            result = await client.get("/api/v1/verifications/ver_123")
            assert result == {"id": "ver_123"}
            mock_http.request.assert_awaited_once()

    async def test_post_sends_json_body(self) -> None:
        client = make_client()
        mock_resp = mock_response(200, {"id": "ver_new"})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            await client.post("/api/v1/verifications", {"type": "phone"})
            call_kwargs = mock_http.request.call_args
            assert call_kwargs.kwargs.get("json") == {"type": "phone"} or call_kwargs[1].get("json") == {"type": "phone"}

    async def test_filters_none_params(self) -> None:
        client = make_client()
        mock_resp = mock_response(200, {"data": []})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            await client.get("/api/v1/verifications", {"status": "verified", "type": None})
            call_kwargs = mock_http.request.call_args
            params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
            assert params == {"status": "verified"}


@pytest.mark.asyncio
class TestErrorHandling:
    async def test_400_raises_validation_error(self) -> None:
        client = make_client()
        mock_resp = mock_response(400, {"error": {"code": "invalid", "message": "Bad"}})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            with pytest.raises(ValidationError):
                await client.get("/test")

    async def test_404_raises_not_found(self) -> None:
        client = make_client()
        mock_resp = mock_response(404, {"error": {"code": "not_found", "message": "Not found"}})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            with pytest.raises(NotFoundError):
                await client.get("/test")

    async def test_500_raises_server_error(self) -> None:
        client = make_client()
        mock_resp = mock_response(500, {})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            with pytest.raises(ServerError):
                await client.get("/test")


@pytest.mark.asyncio
class TestRetryLogic:
    async def test_retries_500_and_succeeds(self) -> None:
        client = make_client(max_retries=1)
        fail_resp = mock_response(500, {})
        ok_resp = mock_response(200, {"ok": True})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.side_effect = [fail_resp, ok_resp]
            mock_get_client.return_value = mock_http

            with patch("proof_sdk.http.asyncio.sleep", new_callable=AsyncMock):
                result = await client.get("/test")
                assert result == {"ok": True}
                assert mock_http.request.await_count == 2

    async def test_exhausts_retries_on_500(self) -> None:
        client = make_client(max_retries=1)
        fail_resp = mock_response(500, {})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = fail_resp
            mock_get_client.return_value = mock_http

            with patch("proof_sdk.http.asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(ServerError):
                    await client.get("/test")
                assert mock_http.request.await_count == 2

    async def test_retries_on_timeout(self) -> None:
        client = make_client(max_retries=1)
        ok_resp = mock_response(200, {"ok": True})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.side_effect = [httpx.ReadTimeout("timeout"), ok_resp]
            mock_get_client.return_value = mock_http

            with patch("proof_sdk.http.asyncio.sleep", new_callable=AsyncMock):
                result = await client.get("/test")
                assert result == {"ok": True}

    async def test_raises_timeout_after_exhausting_retries(self) -> None:
        client = make_client(max_retries=0)

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.side_effect = httpx.ReadTimeout("timeout")
            mock_get_client.return_value = mock_http

            with pytest.raises(RequestTimeoutError):
                await client.get("/test")

    async def test_raises_network_error_after_exhausting_retries(self) -> None:
        client = make_client(max_retries=0)

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.side_effect = httpx.ConnectError("ECONNREFUSED")
            mock_get_client.return_value = mock_http

            with pytest.raises(NetworkError):
                await client.get("/test")


class TestBackoff:
    def test_exponential_with_cap(self) -> None:
        assert HttpClient._backoff(0) == 1.0
        assert HttpClient._backoff(1) == 2.0
        assert HttpClient._backoff(2) == 4.0
        assert HttpClient._backoff(3) == 8.0
        assert HttpClient._backoff(4) == 10.0  # Capped at 10
        assert HttpClient._backoff(10) == 10.0
