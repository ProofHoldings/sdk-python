"""HITL End-to-End Encryption crypto module."""

from .hitl_crypto import (
    compute_kid,
    derive_key,
    encrypt_message,
    decrypt_message,
    encrypt_private_key,
    decrypt_private_key,
    generate_key_pair,
    generate_encryption_key_pair,
    validate_message_envelope,
    validate_private_key_envelope,
)

__all__ = [
    "compute_kid",
    "derive_key",
    "encrypt_message",
    "decrypt_message",
    "encrypt_private_key",
    "decrypt_private_key",
    "generate_key_pair",
    "generate_encryption_key_pair",
    "validate_message_envelope",
    "validate_private_key_envelope",
]
