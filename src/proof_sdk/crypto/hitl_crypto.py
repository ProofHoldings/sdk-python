"""HITL End-to-End Encryption — Crypto Module.

Implements the envelope spec from docs/ENCRYPTION_ENVELOPE.md.
Uses the ``cryptography`` library (>= 41.0.0).

Two modes:
- Encrypt-only: agent has public key, encrypts messages for the approver
- Encrypt+decrypt: approver has password, decrypts messages
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
from typing import Any, TypedDict

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ENVELOPE_VERSION = 1
_MESSAGE_ALG = "RSA-OAEP-256+AES-256-GCM"
_PRIVATE_KEY_ALG = "PBKDF2-SHA256+AES-256-GCM"
_AES_KEY_BYTES = 32
_AES_IV_BYTES = 12
_AES_TAG_BYTES = 16
_RSA_EK_BYTES = 512  # 4096-bit RSA
_PBKDF2_ITERATIONS = 600_000
_PBKDF2_SALT_BYTES = 16
_PBKDF2_KEY_BYTES = 32
_KID_RE = re.compile(r"^[a-f0-9]{64}$")

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class CiphertextEnvelope(TypedDict):
    v: int
    alg: str
    ek: str
    iv: str
    ct: str
    tag: str
    kid: str


class CiphertextEnvelopeV2(TypedDict):
    v: int
    alg: str
    ek: str
    approver_ek: dict[str, str]  # authorization_id -> base64url wrapped AES key
    iv: str
    ct: str
    tag: str
    kid: str


class EncryptedPrivateKey(TypedDict):
    v: int
    alg: str
    iv: str
    ct: str
    tag: str
    salt: str
    kid: str


# ---------------------------------------------------------------------------
# Base64url helpers
# ---------------------------------------------------------------------------


def _to_b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _from_b64url(s: str) -> bytes:
    # Add padding
    padding_needed = 4 - len(s) % 4
    if padding_needed != 4:
        s += "=" * padding_needed
    return base64.urlsafe_b64decode(s)


# ---------------------------------------------------------------------------
# Key Identifier
# ---------------------------------------------------------------------------


def compute_kid(public_key_pem: str) -> str:
    """Compute kid = lowercase_hex(SHA-256(DER-encoded SPKI public key bytes))."""
    pub_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    der = pub_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    return hashlib.sha256(der).hexdigest()


# ---------------------------------------------------------------------------
# RSA Key Generation
# ---------------------------------------------------------------------------


def generate_key_pair() -> tuple[str, str]:
    """Generate an RSA-4096 key pair. Returns (public_key_pem, private_key_pem)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return public_pem, private_pem


# ---------------------------------------------------------------------------
# PBKDF2
# ---------------------------------------------------------------------------


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from password + salt using PBKDF2-SHA256 at 600k iterations."""
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=_PBKDF2_KEY_BYTES, salt=salt, iterations=_PBKDF2_ITERATIONS)
    return kdf.derive(password.encode("utf-8"))


# ---------------------------------------------------------------------------
# AES-256-GCM
# ---------------------------------------------------------------------------


def _aes_gcm_encrypt(key: bytes, iv: bytes, plaintext: bytes, aad: bytes) -> tuple[bytes, bytes]:
    aesgcm = AESGCM(key)
    ct_and_tag = aesgcm.encrypt(iv, plaintext, aad)
    # cryptography library appends the 16-byte tag to the ciphertext
    ct = ct_and_tag[:-_AES_TAG_BYTES]
    tag = ct_and_tag[-_AES_TAG_BYTES:]
    return ct, tag


def _aes_gcm_decrypt(key: bytes, iv: bytes, ct: bytes, tag: bytes, aad: bytes) -> bytes:
    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(iv, ct + tag, aad)
    except Exception:
        raise ValueError("Decryption failed")


# ---------------------------------------------------------------------------
# RSA-OAEP-SHA256 wrap/unwrap
# ---------------------------------------------------------------------------

_OAEP_PADDING = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None,
)


def _rsa_oaep_wrap(public_key_pem: str, plaintext: bytes) -> bytes:
    pub_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    return pub_key.encrypt(plaintext, _OAEP_PADDING)  # type: ignore[union-attr]


def _rsa_oaep_unwrap(private_key_pem: str, ciphertext: bytes) -> bytes:
    priv_key = serialization.load_pem_private_key(private_key_pem.encode("utf-8"), password=None)
    try:
        return priv_key.decrypt(ciphertext, _OAEP_PADDING)  # type: ignore[union-attr]
    except Exception:
        raise ValueError("Decryption failed")


# ---------------------------------------------------------------------------
# Envelope Validation
# ---------------------------------------------------------------------------


def validate_message_envelope(obj: Any) -> bool:
    """Validate a message ciphertext envelope."""
    if not isinstance(obj, dict):
        return False
    if obj.get("v") not in (1, 2):
        return False
    if obj.get("alg") != _MESSAGE_ALG:
        return False
    try:
        if len(_from_b64url(obj.get("ek", ""))) != _RSA_EK_BYTES:
            return False
        if len(_from_b64url(obj.get("iv", ""))) != _AES_IV_BYTES:
            return False
        if len(_from_b64url(obj.get("tag", ""))) != _AES_TAG_BYTES:
            return False
    except Exception:
        return False
    if not obj.get("ct"):
        return False
    if not _KID_RE.match(obj.get("kid", "")):
        return False
    if obj.get("v") == 2:
        approver_ek = obj.get("approver_ek")
        if not isinstance(approver_ek, dict):
            return False
        try:
            for wrapped in approver_ek.values():
                if not isinstance(wrapped, str) or len(_from_b64url(wrapped)) != _RSA_EK_BYTES:
                    return False
        except Exception:
            return False
        allowed = {"v", "alg", "ek", "approver_ek", "iv", "ct", "tag", "kid"}
    else:
        allowed = {"v", "alg", "ek", "iv", "ct", "tag", "kid"}
    if set(obj.keys()) != allowed:
        return False
    return True


def validate_private_key_envelope(obj: Any) -> bool:
    """Validate an encrypted private key envelope."""
    if not isinstance(obj, dict):
        return False
    if obj.get("v") != 1:
        return False
    if obj.get("alg") != _PRIVATE_KEY_ALG:
        return False
    try:
        if len(_from_b64url(obj.get("iv", ""))) != _AES_IV_BYTES:
            return False
        if len(_from_b64url(obj.get("tag", ""))) != _AES_TAG_BYTES:
            return False
        if len(_from_b64url(obj.get("salt", ""))) != _PBKDF2_SALT_BYTES:
            return False
    except Exception:
        return False
    if not obj.get("ct"):
        return False
    if not _KID_RE.match(obj.get("kid", "")):
        return False
    allowed = {"v", "alg", "iv", "ct", "tag", "salt", "kid"}
    if set(obj.keys()) != allowed:
        return False
    return True


# ---------------------------------------------------------------------------
# Message Encryption (Section 4.1)
# ---------------------------------------------------------------------------


def encrypt_message(
    plaintext: str,
    public_key_pem: str,
    hitl_id: str,
    *,
    _aes_key: bytes | None = None,
    _iv: bytes | None = None,
) -> CiphertextEnvelope:
    """Encrypt a confirmation message. AAD = ``{hitl_id}``."""
    aes_key = _aes_key or os.urandom(_AES_KEY_BYTES)
    iv = _iv or os.urandom(_AES_IV_BYTES)
    aad = hitl_id.encode("utf-8")

    ct, tag = _aes_gcm_encrypt(aes_key, iv, plaintext.encode("utf-8"), aad)
    ek = _rsa_oaep_wrap(public_key_pem, aes_key)
    kid = compute_kid(public_key_pem)

    return CiphertextEnvelope(
        v=_ENVELOPE_VERSION,
        alg=_MESSAGE_ALG,
        ek=_to_b64url(ek),
        iv=_to_b64url(iv),
        ct=_to_b64url(ct),
        tag=_to_b64url(tag),
        kid=kid,
    )


def encrypt_message_v2(
    plaintext: str,
    owner_public_key_pem: str,
    hitl_id: str,
    approver_keys: dict[str, str],
    *,
    _aes_key: bytes | None = None,
    _iv: bytes | None = None,
) -> CiphertextEnvelopeV2:
    """Encrypt a confirmation message with multi-recipient wrapping (v2).

    Wraps the AES content key with the owner's public key AND each approver's
    public key, so every enrolled approver can decrypt with their own key.
    AAD = ``{hitl_id}``.

    :param approver_keys: Map of authorization_id -> approver PEM public key.
    """
    aes_key = _aes_key or os.urandom(_AES_KEY_BYTES)
    iv = _iv or os.urandom(_AES_IV_BYTES)
    aad = hitl_id.encode("utf-8")

    ct, tag = _aes_gcm_encrypt(aes_key, iv, plaintext.encode("utf-8"), aad)
    ek = _rsa_oaep_wrap(owner_public_key_pem, aes_key)
    kid = compute_kid(owner_public_key_pem)

    approver_ek = {
        authz_id: _to_b64url(_rsa_oaep_wrap(approver_pem, aes_key))
        for authz_id, approver_pem in approver_keys.items()
    }

    return CiphertextEnvelopeV2(
        v=2,
        alg=_MESSAGE_ALG,
        ek=_to_b64url(ek),
        approver_ek=approver_ek,
        iv=_to_b64url(iv),
        ct=_to_b64url(ct),
        tag=_to_b64url(tag),
        kid=kid,
    )


def decrypt_message(
    envelope: CiphertextEnvelope,
    private_key_pem: str,
    hitl_id: str,
) -> str:
    """Decrypt a confirmation message envelope. AAD = ``{hitl_id}``."""
    if not validate_message_envelope(envelope):
        raise ValueError("Decryption failed")

    ek = _from_b64url(envelope["ek"])
    iv = _from_b64url(envelope["iv"])
    ct = _from_b64url(envelope["ct"])
    tag = _from_b64url(envelope["tag"])
    aad = hitl_id.encode("utf-8")

    aes_key = _rsa_oaep_unwrap(private_key_pem, ek)
    return _aes_gcm_decrypt(aes_key, iv, ct, tag, aad).decode("utf-8")


# ---------------------------------------------------------------------------
# Private Key Encryption (Section 4.2)
# ---------------------------------------------------------------------------


def encrypt_private_key(
    private_key_pem: str,
    password: str,
    public_key_pem: str,
    hitl_id: str,
    user_id: str,
) -> EncryptedPrivateKey:
    """Encrypt an RSA private key with a user password for storage. AAD = ``{hitl_id}:{user_id}``."""
    salt = os.urandom(_PBKDF2_SALT_BYTES)
    derived_key = derive_key(password, salt)
    iv = os.urandom(_AES_IV_BYTES)
    aad = f"{hitl_id}:{user_id}".encode("utf-8")

    priv_key = serialization.load_pem_private_key(private_key_pem.encode("utf-8"), password=None)
    private_key_der = priv_key.private_bytes(
        serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )

    ct, tag = _aes_gcm_encrypt(derived_key, iv, private_key_der, aad)
    kid = compute_kid(public_key_pem)

    return EncryptedPrivateKey(
        v=_ENVELOPE_VERSION,
        alg=_PRIVATE_KEY_ALG,
        iv=_to_b64url(iv),
        ct=_to_b64url(ct),
        tag=_to_b64url(tag),
        salt=_to_b64url(salt),
        kid=kid,
    )


def decrypt_private_key(
    envelope: EncryptedPrivateKey,
    password: str,
    hitl_id: str,
    user_id: str,
) -> str:
    """Decrypt an RSA private key using the user's password. Returns PEM string."""
    if not validate_private_key_envelope(envelope):
        raise ValueError("Decryption failed")

    salt = _from_b64url(envelope["salt"])
    derived_key = derive_key(password, salt)
    iv = _from_b64url(envelope["iv"])
    ct = _from_b64url(envelope["ct"])
    tag = _from_b64url(envelope["tag"])
    aad = f"{hitl_id}:{user_id}".encode("utf-8")

    private_key_der = _aes_gcm_decrypt(derived_key, iv, ct, tag, aad)
    priv_key = serialization.load_der_private_key(private_key_der, password=None)
    return priv_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ).decode("utf-8")


# ---------------------------------------------------------------------------
# Full Key Setup (convenience)
# ---------------------------------------------------------------------------


def generate_encryption_key_pair(
    password: str, hitl_id: str, user_id: str
) -> dict[str, Any]:
    """Generate RSA-4096 key pair and encrypt private key with password.

    Returns dict with ``public_key_pem``, ``encrypted_private_key``, ``kdf_salt``, ``kid``.
    """
    public_pem, private_pem = generate_key_pair()
    encrypted = encrypt_private_key(private_pem, password, public_pem, hitl_id, user_id)
    kid = compute_kid(public_pem)
    return {
        "public_key_pem": public_pem,
        "encrypted_private_key": encrypted,
        "kdf_salt": encrypted["salt"],
        "kid": kid,
    }
