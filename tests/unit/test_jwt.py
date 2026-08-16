from datetime import timedelta

import pytest

from app.auth.jwt import create_access_token, decode_access_token
from app.core.exceptions import InvalidToken


def test_create_access_token_contains_subject_and_claims():
    token = create_access_token({"sub": "123"})

    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert "exp" in payload
    assert "iat" in payload


def test_create_access_token_with_custom_expiration():
    token = create_access_token(
        {"sub": "123"},
        expires_delta=timedelta(minutes=30),
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert payload["exp"] > payload["iat"]


def test_decode_invalid_token():
    with pytest.raises(InvalidToken):
        decode_access_token("not-a-real-token")


def test_decode_expired_token():
    token = create_access_token(
        {"sub": "123"},
        expires_delta=timedelta(seconds=-1),
    )
    with pytest.raises(InvalidToken):
        decode_access_token(token)
