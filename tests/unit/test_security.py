"""UT-SEC: app.utilities.security - password hashing and JWT creation."""
from datetime import timedelta

import jwt
import pytest

from app.config import get_settings
from app.utilities.security import (
    access_token_cookie_kwargs,
    create_access_token,
    encrypt_password,
    verify_password,
)

pytestmark = pytest.mark.unit


def test_encrypt_password_does_not_store_plaintext():
    hashed = encrypt_password("bobpass")
    assert hashed != "bobpass"
    assert "bobpass" not in hashed


def test_encrypt_password_is_salted():
    assert encrypt_password("same") != encrypt_password("same")


def test_verify_password_accepts_correct_password():
    assert verify_password("bobpass", encrypt_password("bobpass")) is True


def test_verify_password_rejects_wrong_password():
    assert verify_password("wrong", encrypt_password("bobpass")) is False


def _decode(token: str) -> dict:
    s = get_settings()
    return jwt.decode(token, s.secret_key, algorithms=[s.jwt_algorithm])


def test_access_token_carries_subject_role_and_expiry():
    payload = _decode(create_access_token({"sub": "7", "role": "admin"}))
    assert payload["sub"] == "7"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_access_token_does_not_mutate_input_dict():
    data = {"sub": "1"}
    create_access_token(data)
    assert data == {"sub": "1"}


def test_expired_token_is_rejected():
    token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-5))
    with pytest.raises(jwt.ExpiredSignatureError):
        _decode(token)


def test_token_signed_with_other_key_is_rejected():
    forged = jwt.encode(
        {"sub": "1"},
        "some-other-key-that-is-long-enough-for-hs256-123456",
        algorithm="HS256",
    )
    with pytest.raises(jwt.InvalidSignatureError):
        _decode(forged)


def test_cookie_flags_in_development_are_http_only_and_not_secure():
    flags = access_token_cookie_kwargs()
    assert flags["httponly"] is True
    assert flags["secure"] is False
    assert flags["samesite"] == "lax"
