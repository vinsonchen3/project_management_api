import pytest
from unittest.mock import AsyncMock, patch

from app.auth.auth_service import AuthService
from app.db.models import User
from app.core.exceptions import InvalidCredentials, InvalidToken


@pytest.fixture
def user_service():
    service = AsyncMock()
    return service


@pytest.fixture
def auth_service(user_service):
    return AuthService(user_service)


@pytest.fixture
def user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed-password",
    )


# ============================================================
# register
# ============================================================

@pytest.mark.anyio
async def test_register_delegates_to_user_service(
    auth_service,
    user_service,
):
    created_user = object()
    user_service.create_user.return_value = created_user

    result = await auth_service.register(
        username="testuser",
        email="test@example.com",
        password="password123",
    )

    assert result is created_user

    user_service.create_user.assert_awaited_once_with(
        username="testuser",
        email="test@example.com",
        password="password123",
    )


# ============================================================
# login
# ============================================================

@pytest.mark.anyio
async def test_login_success(
    auth_service,
    user_service,
    user,
):
    user_service.get_user_by_email.return_value = user

    with (
        patch(
            "app.auth.auth_service.verify_password",
            return_value=True,
        ) as mock_verify,
        patch(
            "app.auth.auth_service.create_access_token",
            return_value="jwt-token",
        ) as mock_create_token,
    ):
        result = await auth_service.login(
            email="test@example.com",
            password="password123",
        )

    assert result == "jwt-token"

    user_service.get_user_by_email.assert_awaited_once_with(
        "test@example.com"
    )

    mock_verify.assert_called_once_with(
        "password123",
        "hashed-password",
    )

    mock_create_token.assert_called_once_with(
        {"sub": "1"}
    )


@pytest.mark.anyio
async def test_login_user_not_found(
    auth_service,
    user_service,
):
    user_service.get_user_by_email.return_value = None

    with pytest.raises(InvalidCredentials):
        await auth_service.login(
            email="missing@example.com",
            password="password123",
        )

    user_service.get_user_by_email.assert_awaited_once_with(
        "missing@example.com",
    )


@pytest.mark.anyio
async def test_login_wrong_password(
    auth_service,
    user_service,
    user,
):
    user_service.get_user_by_email.return_value = user

    with patch(
        "app.auth.auth_service.verify_password",
        return_value=False,
    ):
        with pytest.raises(InvalidCredentials):
            await auth_service.login(
                email="test@example.com",
                password="wrong-password",
            )


# ============================================================
# refresh
# ============================================================

@pytest.mark.anyio
async def test_refresh_success(
    auth_service,
    user_service,
    user,
):
    user_service.get_user.return_value = user

    with (
        patch(
            "app.auth.auth_service.decode_access_token",
            return_value={"sub": "1"},
        ) as mock_decode,
        patch(
            "app.auth.auth_service.create_access_token",
            return_value="new-jwt-token",
        ) as mock_create_token,
    ):
        result = await auth_service.refresh("old-jwt-token")

    assert result == "new-jwt-token"

    mock_decode.assert_called_once_with("old-jwt-token")

    user_service.get_user.assert_awaited_once_with(1)

    mock_create_token.assert_called_once_with(
        {"sub": "1"}
    )


@pytest.mark.anyio
async def test_refresh_missing_subject(
    auth_service,
):
    with patch(
        "app.auth.auth_service.decode_access_token",
        return_value={},
    ):
        with pytest.raises(InvalidToken):
            await auth_service.refresh("jwt-token")


@pytest.mark.anyio
async def test_refresh_invalid_user_id(
    auth_service,
    user_service,
):
    with patch(
        "app.auth.auth_service.decode_access_token",
        return_value={"sub": "not-an-integer"},
    ):
        with pytest.raises(ValueError):
            await auth_service.refresh("jwt-token")


# ============================================================
# change_password
# ============================================================

@pytest.mark.anyio
async def test_change_password_success(
    auth_service,
    user_service,
    user,
):
    user_service.update_password.return_value = user

    with patch(
        "app.auth.auth_service.verify_password",
        return_value=True,
    ) as mock_verify:
        result = await auth_service.change_password(
            current_user=user,
            current_password="old-password",
            new_password="new-password",
        )

    assert result is user

    mock_verify.assert_called_once_with(
        "old-password",
        "hashed-password",
    )

    user_service.update_password.assert_awaited_once_with(
        current_user=user,
        password="new-password",
    )


@pytest.mark.anyio
async def test_change_password_wrong_current_password(
    auth_service,
    user,
):
    with patch(
        "app.auth.auth_service.verify_password",
        return_value=False,
    ):
        with pytest.raises(InvalidCredentials):
            await auth_service.change_password(
                current_user=user,
                current_password="wrong-password",
                new_password="new-password",
            )

    assert user.hashed_password == "hashed-password"