"""Official Python SDK for the proof.holdings verification API."""

from .client import Proof
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

# Backward compatibility aliases (deprecated — will be removed in v2.0)
ProofHoldings = Proof  #: .. deprecated:: Use :class:`Proof` instead.
ProofHoldingsError = ProofError  #: .. deprecated:: Use :class:`ProofError` instead.

__all__ = [
    "Proof",
    "ProofError",
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
