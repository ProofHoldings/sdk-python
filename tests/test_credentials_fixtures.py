"""Key and base-URL resolution follows the MCP server's chain (m-implement-sdk-key-resolution).

The shared cases in ``sdks/shared/fixtures/credentials/cases.json`` run here through the PUBLIC
surface — ``Proof(key)`` or ``Proof(base_url=...)`` / ``Proof()`` — with ``HOME`` pointed at a temp
directory holding the case's credentials file and the two variables set from the case. What is
asserted is what reaches the wire: the ``Authorization`` header an ``httpx`` mock transport records
and the origin it was sent to. The same file drives the MCP reference (through the root drift test)
and the other three SDKs, so a rule read differently here fails here.

The origin, not the whole base URL, is compared: ``httpx`` keeps a base path but normalizes the host
and drops a default port. That the path still took part in the FILE lookup is what the
``Authorization`` assertion of ``path_prefix_is_part_of_the_key`` proves.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
import pytest

from proof_sdk import Proof
from proof_sdk.credentials import (
    LOGIN_COMMAND,
    ResolvedKey,
    credential_key,
    resolve_api_key,
    resolve_base_url,
)
from proof_sdk.version import VERSION

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads(
    (ROOT.parent / "shared" / "fixtures" / "credentials" / "cases.json").read_text()
)
ENV_KEYS = ("PROOF_API_KEY", "PROOF_BASE_URL")
CASES = FIXTURE["cases"]

_DEFAULT_PORTS = {"http": 80, "https": 443}


def _origin(url: str) -> tuple[str, str | None, int | None]:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    return scheme, parts.hostname, parts.port or _DEFAULT_PORTS.get(scheme)


def _arrange(case: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point HOME at ``tmp_path``, write the case's file there, set the case's variables."""
    monkeypatch.setenv("HOME", str(tmp_path))
    file = tmp_path / ".proof-holdings" / "credentials"
    if case["file"] is not None:
        file.parent.mkdir(parents=True)
        body = FIXTURE["files"][case["file"]]
        file.write_text(body if isinstance(body, str) else json.dumps(body))
    env = case.get("env", {})
    for key in ENV_KEYS:
        if key in env:
            monkeypatch.setenv(key, env[key])
        else:
            monkeypatch.delenv(key, raising=False)
    return file


def _build(case: dict[str, Any]) -> Proof:
    kwargs = {"base_url": case["base_url"]} if case["base_url"] is not None else {}
    if "explicit" in case:
        return Proof(case["explicit"], **kwargs)
    return Proof(**kwargs)


def _route_to_recorder(proof: Proof, recorded: dict[str, Any]) -> None:
    """The ``tests/integration/conftest.py`` swap: the SDK's own base URL and headers, a mock transport."""

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["authorization"] = request.headers.get("Authorization")
        recorded["url"] = str(request.url)
        return httpx.Response(200, json={})

    http = proof._http
    http._client = httpx.AsyncClient(
        base_url=http.base_url,
        timeout=http._timeout,
        headers={
            "Authorization": f"Bearer {http._api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"proof-sdk-python/{VERSION}",
        },
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
async def test_shared_case(case: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    file = _arrange(case, tmp_path, monkeypatch)

    if case["expect"]["error"]:
        with pytest.raises(ValueError) as raised:
            _build(case)
        message = str(raised.value)
        assert "api_key is required" in message
        if "explicit" in case:
            # Today's error, verbatim: the chain was never consulted.
            assert LOGIN_COMMAND not in message
        else:
            assert LOGIN_COMMAND in message
            assert "PROOF_API_KEY" in message
        assert (str(file) in message) == case["expect"]["notice"]
        return

    proof = _build(case)
    recorded: dict[str, Any] = {}
    _route_to_recorder(proof, recorded)
    try:
        await proof.verifications.retrieve("ver_x")
    finally:
        await proof.close()
    assert recorded["authorization"] == f"Bearer {case['expect']['api_key']}"
    assert _origin(recorded["url"]) == _origin(case["expect"]["base_url"])


class TestResolveApiKeyDirect:
    """One direct case per source."""

    BASE_URL = "https://api.proof.holdings"

    @staticmethod
    def _valid_file(tmp_path: Path) -> Path:
        file = tmp_path / "credentials"
        file.write_text(json.dumps(FIXTURE["files"]["valid"]))
        return file

    def test_explicit_is_used_as_given_even_empty(self, tmp_path: Path) -> None:
        file = tmp_path / "credentials"
        file.write_text("{not json")
        env = {"PROOF_API_KEY": "pk_live_env"}
        assert resolve_api_key(explicit="pk_live_x", base_url=self.BASE_URL, path=file, env=env) == ResolvedKey(
            "pk_live_x", "explicit"
        )
        assert resolve_api_key(explicit="", base_url=self.BASE_URL, path=file, env=env) == ResolvedKey("", "explicit")

    def test_env_wins_without_reading_the_file(self, tmp_path: Path) -> None:
        file = tmp_path / "credentials"
        file.write_text("{not json")
        result = resolve_api_key(base_url=self.BASE_URL, path=file, env={"PROOF_API_KEY": "pk_live_env"})
        assert result == ResolvedKey("pk_live_env", "env")

    def test_file_entry_for_exactly_this_base_url(self, tmp_path: Path) -> None:
        file = self._valid_file(tmp_path)
        assert resolve_api_key(base_url="https://API.Proof.Holdings:443/", path=file, env={}) == ResolvedKey(
            "pk_live_file_production", "file"
        )
        assert resolve_api_key(
            base_url="http://localhost:3000/proxy/", path=file, env={"PROOF_API_KEY": ""}
        ) == ResolvedKey("pk_test_file_proxy", "file")

    def test_a_file_that_is_not_utf8_is_a_notice_not_an_exception(self, tmp_path: Path) -> None:
        # The reference reads with replacement characters and fails at JSON.parse; a decode error
        # must never escape the constructor (SC-4), and the notice must name the file.
        file = tmp_path / "credentials"
        file.write_bytes(b"\xff\xfe{ not utf-8 }")
        result = resolve_api_key(base_url=self.BASE_URL, path=file, env={})
        assert result.source == "none"
        assert result.api_key is None
        assert result.notice is not None
        assert str(file) in result.notice
        assert LOGIN_COMMAND in result.notice

    def test_a_deeply_nested_file_is_a_notice_not_an_exception(self, tmp_path: Path) -> None:
        # CPython's decoder raises RecursionError, not ValueError, on deep nesting; the reference's
        # bare catch turns any parse failure into the notice, and so must this port (SC-4).
        file = tmp_path / "credentials"
        file.write_text("[" * 100_000)
        result = resolve_api_key(base_url=self.BASE_URL, path=file, env={})
        assert result.source == "none"
        assert result.api_key is None
        assert result.notice is not None
        assert str(file) in result.notice

    def test_none_is_silent_without_a_file_and_a_notice_when_it_cannot_be_used(self, tmp_path: Path) -> None:
        missing = tmp_path / "credentials"
        assert resolve_api_key(base_url=self.BASE_URL, path=missing, env={}) == ResolvedKey(None, "none")

        file = self._valid_file(tmp_path)
        assert resolve_api_key(base_url="https://api.staging.proof.holdings", path=file, env={}) == ResolvedKey(
            None, "none"
        )

        broken = resolve_api_key(base_url="not a url", path=file, env={})
        assert broken.source == "none"
        assert broken.api_key is None
        assert broken.notice is not None and str(file) in broken.notice

        file.write_text(json.dumps({"version": 2, "credentials": {}}))
        wrong_version = resolve_api_key(base_url=self.BASE_URL, path=file, env={})
        assert wrong_version.source == "none"
        assert wrong_version.notice is not None
        assert str(file) in wrong_version.notice
        assert LOGIN_COMMAND in wrong_version.notice


def test_credential_key_normalizes_like_the_reference() -> None:
    assert credential_key("https://api.proof.holdings") == "https://api.proof.holdings"
    assert credential_key("https://api.proof.holdings/") == "https://api.proof.holdings"
    assert credential_key("https://API.Proof.Holdings:443/") == "https://api.proof.holdings"
    assert credential_key("http://localhost:3000/proxy/") == "http://localhost:3000/proxy"
    assert credential_key("http://localhost:8080") == "http://localhost:8080"
    with pytest.raises(ValueError):
        credential_key("not a url")


def test_resolve_base_url() -> None:
    staging = "https://api.staging.proof.holdings"
    assert resolve_base_url("http://localhost:3000", {"PROOF_BASE_URL": staging}) == "http://localhost:3000"
    assert resolve_base_url(None, {"PROOF_BASE_URL": staging}) == staging
    assert resolve_base_url(None, {"PROOF_BASE_URL": ""}) == FIXTURE["default_base_url"]
    assert resolve_base_url(None, {}) == FIXTURE["default_base_url"]
