"""Official Python SDK for the proof.holdings verification API."""

from .client import Proof
from .credentials import LOGIN_COMMAND, ResolvedKey, resolve_api_key, resolve_base_url
from .errors import (
    ProofError,
    ValidationError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServerError,
    NetworkError,
    RequestTimeoutError,
    PollingTimeoutError,
)
from .version import VERSION

__all__ = [
    "Proof",
    "ProofError",
    "ValidationError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "RequestTimeoutError",
    "PollingTimeoutError",
    "LOGIN_COMMAND",
    "ResolvedKey",
    "resolve_api_key",
    "resolve_base_url",
    "VERSION",
]
