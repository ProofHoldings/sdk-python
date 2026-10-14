"""Where the key comes from when ``Proof()`` is given none.

The chain is the MCP server's (``mcp/src/credentials.ts``, the reference): a non-empty
``PROOF_API_KEY``, else the entry ``npx @proof-holdings/mcp-server login`` saved for exactly this
base URL in ``~/.proof-holdings/credentials``, else none. It runs ONLY when the key argument is
omitted — an explicit key is used as given, and an explicit empty one is the caller's error and
never reads the environment or the file (a multi-tenant host passing a tenant's key must not fall
through to its own). The shared cases in ``sdks/shared/fixtures/credentials/cases.json`` hold this
module and the other three SDKs to the reference.

Standard library only: the client imports this on every construction.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

#: The scoped command, never the bare bin name: through npx the unscoped name resolves to a package somebody else publishes.
LOGIN_COMMAND = "npx @proof-holdings/mcp-server login"
DEFAULT_BASE_URL = "https://api.proof.holdings"

KeySource = Literal["explicit", "env", "file", "none"]

_DEFAULT_PORTS = {"http": 80, "https": 443}


@dataclass(frozen=True)
class ResolvedKey:
    api_key: str | None
    source: KeySource
    #: Why the file could not be used, when it exists but was not read — never a key.
    notice: str | None = None


class CredentialsFileError(Exception):
    """The file exists but cannot be read or is not a credentials file this version understands."""


def default_credentials_path() -> Path:
    return Path.home() / ".proof-holdings" / "credentials"


def credential_key(base_url: str) -> str:
    """Origin plus path, no trailing slash — the entry name the login saves under.

    ``https://API.Proof.Holdings:443/`` → ``https://api.proof.holdings``;
    ``http://localhost:3000/proxy/`` → ``http://localhost:3000/proxy``. Raises ``ValueError`` for
    anything without a scheme and a host.
    """
    parts = urlsplit(base_url)
    scheme = parts.scheme.lower()
    host = parts.hostname
    if not scheme or not host:
        raise ValueError(f"not a URL: {base_url!r}")
    if ":" in host:
        host = f"[{host}]"
    port = parts.port
    origin = f"{scheme}://{host}"
    if port is not None and port != _DEFAULT_PORTS.get(scheme):
        origin += f":{port}"
    return origin + parts.path.rstrip("/")


def resolve_base_url(explicit: str | None = None, env: Mapping[str, str] | None = None) -> str:
    """Explicit, else a non-empty ``PROOF_BASE_URL``, else the default."""
    environment = os.environ if env is None else env
    if explicit is not None:
        return explicit
    return environment.get("PROOF_BASE_URL") or DEFAULT_BASE_URL


def _is_version_one(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value == 1


def _is_stored_credential(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    api_key = value.get("api_key")
    return (
        isinstance(api_key, str)
        and api_key.startswith("pk_")
        and isinstance(value.get("key_id"), str)
        and isinstance(value.get("name"), str)
        and isinstance(value.get("created_at"), str)
        and value.get("environment") in ("production", "test")
    )


def read_credentials_file(path: Path) -> dict[str, Any] | None:
    """The parsed file, ``None`` when there is none, ``CredentialsFileError`` when it is unreadable or malformed."""
    try:
        # Replacement characters, like the reference's ``readFileSync(file, 'utf8')``: a file that is
        # not UTF-8 then fails as "not valid JSON" below instead of raising out of the constructor.
        raw = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None
    except OSError as e:
        raise CredentialsFileError(f"cannot read {path}: {e}") from e
    try:
        parsed = json.loads(raw)
    except Exception as e:  # noqa: BLE001 — the reference's bare catch: ValueError, and RecursionError on deep nesting
        raise CredentialsFileError(f"{path} is not valid JSON") from e
    if (
        not isinstance(parsed, dict)
        or not _is_version_one(parsed.get("version"))
        or not isinstance(parsed.get("credentials"), dict)
    ):
        raise CredentialsFileError(f"{path} is not a version 1 Proof credentials file")
    for key, value in parsed["credentials"].items():
        if not _is_stored_credential(value):
            raise CredentialsFileError(f"{path} has a malformed entry for {key}")
    return parsed


def resolve_api_key(
    *,
    explicit: str | None = None,
    base_url: str,
    path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> ResolvedKey:
    """The chain.

    An explicit key as given (the constructor decides whether ``""`` is acceptable), else a
    non-empty ``PROOF_API_KEY``, else the saved entry for exactly ``base_url``, else none. A broken
    file or a base URL that is not a URL never raises here — it becomes a notice on the ``none``
    answer.
    """
    if explicit is not None:
        return ResolvedKey(explicit, "explicit")
    environment = os.environ if env is None else env
    env_key = environment.get("PROOF_API_KEY")
    if env_key:
        return ResolvedKey(env_key, "env")
    if path is None:
        try:
            path = default_credentials_path()
        except (RuntimeError, OSError):
            # No home directory to look in: the same answer as no file.
            return ResolvedKey(None, "none")
    try:
        contents = read_credentials_file(path)
    except CredentialsFileError as e:
        return ResolvedKey(
            None,
            "none",
            f"ignoring the saved credentials — {e}. Fix or delete {path}, then run {LOGIN_COMMAND}.",
        )
    if contents is None:
        return ResolvedKey(None, "none")
    try:
        key = credential_key(base_url)
    except ValueError:
        return ResolvedKey(
            None,
            "none",
            f"the base URL {json.dumps(base_url)} is not a URL, so the saved credentials in {path} were not read.",
        )
    entry = contents["credentials"].get(key)
    if entry is None:
        return ResolvedKey(None, "none")
    return ResolvedKey(entry["api_key"], "file")


def missing_key_message(base_url: str, notice: str | None = None) -> str:
    """The one message a missing key produces, whatever road the caller tried."""
    message = (
        'api_key is required. Pass your key as: Proof("pk_live_..."), set PROOF_API_KEY, '
        f"or run `{LOGIN_COMMAND}` to save one for {base_url}."
    )
    return f"{message} {notice}" if notice else message
