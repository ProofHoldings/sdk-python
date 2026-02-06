"""Official Python SDK for the proof.holdings verification API."""

from .client import ProofHoldings
from .errors import (
    ProofHoldingsError,
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
    "ProofHoldings",
    "ProofHoldingsError",
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
    "VERSION",
]
