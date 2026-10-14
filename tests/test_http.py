"""Tests for HTTP client retry logic and error handling."""

from __future__ import annotations

import asyncio
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

    async def test_put_sends_json_body(self) -> None:
        client = make_client()
        mock_resp = mock_response(200, {"kid": "abc"})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            await client.put("/api/v1/hitl/h1/keys", {"public_key": "pem"})
            call_kwargs = mock_http.request.call_args
            assert call_kwargs.kwargs.get("json") == {"public_key": "pem"} or call_kwargs[1].get("json") == {"public_key": "pem"}

    async def test_delete_sends_optional_json_body(self) -> None:
        client = make_client()
        mock_resp = mock_response(200, {"status": "revoked"})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            await client.delete("/api/v1/authorizations/auth_1", {"reason": "no longer needed"})
            call_kwargs = mock_http.request.call_args
            assert call_kwargs.kwargs.get("json") == {"reason": "no longer needed"} or call_kwargs[1].get("json") == {"reason": "no longer needed"}

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
class TestNonJsonResponses:
    async def test_binary_success_returns_envelope(self) -> None:
        client = make_client()
        mock_resp = mock_response(200, headers={"content-type": "image/png"})
        mock_resp.content = b"\x89PNG\r\n"

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            result = await client.get("/api/v1/profiles/p/pr_1/avatar")
            assert result == {"data": b"\x89PNG\r\n", "content_type": "image/png"}

    async def test_non_json_empty_body_returns_empty_dict(self) -> None:
        client = make_client()
        mock_resp = mock_response(200, headers={"content-type": "text/plain"})
        mock_resp.content = b""

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            result = await client.get("/api/v1/some/endpoint")
            assert result == {}

    async def test_missing_content_type_keeps_json_path(self) -> None:
        client = make_client()
        mock_resp = mock_response(200, {"id": "x_1"})

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_resp
            mock_get_client.return_value = mock_http

            result = await client.get("/api/v1/whatever")
            assert result == {"id": "x_1"}

    async def test_client_follows_redirects(self) -> None:
        client = make_client()
        try:
            http = client._get_client()
            assert http.follow_redirects is True
        finally:
            await client.close()


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


class _Trickle(httpx.AsyncByteStream):
    """A body that arrives one chunk at a time, ``delay`` seconds apart."""

    def __init__(self, chunks: list[bytes], delay: float) -> None:
        self._chunks = chunks
        self._delay = delay

    async def __aiter__(self):  # type: ignore[override]
        for chunk in self._chunks:
            await asyncio.sleep(self._delay)
            yield chunk


def _public_client_serving(stream: httpx.AsyncByteStream) -> HttpClient:
    http = make_client()
    http._public_client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=stream)),
        follow_redirects=False,
    )
    return http


@pytest.mark.asyncio
class TestFetchPublicDeadline:
    """One wall-clock deadline over the whole transfer, on every supported Python (>= 3.10).

    ``asyncio.timeout`` only exists from 3.11, and since h-verifier-jwks-js-python the key set is read
    through this method too — so a 3.10-only attribute here would fail every offline verification.
    """

    async def test_reads_a_body_without_asyncio_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delattr(asyncio, "timeout", raising=False)
        http = _public_client_serving(_Trickle([b"ab", b"cd"], 0.0))
        status, _, body = await http.fetch_public("https://issuer.example/x", timeout=1.0)
        assert (status, body) == (200, b"abcd")

    async def test_cuts_a_trickling_body_at_the_deadline_without_asyncio_timeout(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delattr(asyncio, "timeout", raising=False)
        http = _public_client_serving(_Trickle([b"x"] * 50, 0.05))
        loop = asyncio.get_running_loop()
        started = loop.time()
        with pytest.raises((TimeoutError, asyncio.TimeoutError)):
            await http.fetch_public("https://issuer.example/x", timeout=0.3)
        assert loop.time() - started < 1.5

    async def test_cuts_a_trickling_body_at_the_deadline(self) -> None:
        http = _public_client_serving(_Trickle([b"x"] * 50, 0.05))
        with pytest.raises((TimeoutError, asyncio.TimeoutError)):
            await http.fetch_public("https://issuer.example/x", timeout=0.3)
