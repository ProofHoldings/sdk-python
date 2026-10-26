"""Code written against proof-holdings-sdk 1.1.0 must keep working on every 1.x release.

Each case imports a type the way 1.1.0 code could and checks it still declares the keys 1.1.0
declared, with the annotation 1.1.0 gave them. A later API change removed or reshaped these types;
the generator keeps their 1.1.0 keys (marked deprecated) instead of dropping or retyping them.
If a case fails, a 1.x release would break its users.
"""

import re

from proof_sdk import types

V110_KEYS = {
    "BrandingSettings": {
        "business_name": "NotRequired[str]",
        "logo_url": "NotRequired[Optional[str]]",
        "primary_color": "NotRequired[str]",
        "support_email": "NotRequired[str]",
        "email_theme": 'NotRequired[Literal["dark", "light"]]',
    },
    "ProfileTemplate": {
        "channel": "TemplateChannel",
        "message_type": "str",
        "subject": "NotRequired[str]",
        "body": "str",
        "button_text": "NotRequired[str]",
        "button_url_template": "NotRequired[str]",
        "is_custom": "bool",
        "is_active": "bool",
    },
    "CreateSessionRequest": {
        "phone": "str",
        "channel": 'NotRequired[Literal["whatsapp", "telegram", "sms"]]',
    },
    "Session": {
        "id": "ObjectId",
        "status": 'Literal["pending", "verified", "expired"]',
        "challenge": "NotRequired[Challenge]",
        "proof": "NotRequired[Proof]",
        "created_at": "str",
        "expires_at": "str",
    },
    "HealthResponse": {
        "status": 'Literal["ok", "healthy", "degraded", "unhealthy"]',
        "timestamp": "Union[str, float]",
    },
    "SettingsResponse": {
        "branding": "BrandingSettings",
        "webhook": "WebhookSettingsResponse",
        "proof_expiry_days": "Optional[int]",
    },
    "UpdateSettingsResponse": {
        "success": "bool",
        "branding": "BrandingSettings",
        "webhook": "WebhookSettingsResponse",
        "proof_expiry_days": "Optional[int]",
    },
}


def _unquoted(text: str) -> str:
    return text.replace('"', "").replace("'", "")


def _annotation(type_name: str, key: str) -> str:
    raw = getattr(types, type_name).__annotations__[key]
    # `from __future__ import annotations` keeps annotations as text: a plain string before
    # Python 3.14, a ForwardRef (with its quotes re-written) from 3.14 on. Quotes are cosmetic.
    return _unquoted(getattr(raw, "__forward_arg__", raw))


def test_v110_types_still_import() -> None:
    from proof_sdk.types import BrandingSettings, ProfileTemplate  # noqa: F401


def _literal_values(annotation: str) -> "set[str] | None":
    """The values of a `Literal[...]` (optionally inside `NotRequired[...]`), else None."""
    match = re.fullmatch(r"(?:NotRequired\[)?Literal\[(.*?)\]\]?", annotation)
    return {v.strip() for v in match.group(1).split(",")} if match else None


def test_v110_keys_keep_their_v110_annotations() -> None:
    for type_name, keys in V110_KEYS.items():
        assert hasattr(types, type_name), f"{type_name} was removed"
        for key, annotation in keys.items():
            assert key in getattr(types, type_name).__annotations__, f"{type_name}.{key} was removed"
            actual, expected = _annotation(type_name, key), _unquoted(annotation)
            released_values = _literal_values(expected)
            if released_values is not None:
                # A Literal may gain the API's new values; it must keep every released one.
                assert released_values <= (_literal_values(actual) or set()), f"{type_name}.{key} lost a value"
            else:
                assert actual == expected, f"{type_name}.{key} changed type"


def test_v110_shapes_still_build() -> None:
    branding: types.BrandingSettings = {"business_name": "Acme", "email_theme": "light"}
    request: types.UpdateSettingsRequest = {"branding": branding, "proof_expiry_days": 30}
    session_request: types.CreateSessionRequest = {"phone": "+15550001111", "channel": "sms"}
    assert request["branding"]["business_name"] == "Acme"
    assert session_request["phone"] == "+15550001111"
