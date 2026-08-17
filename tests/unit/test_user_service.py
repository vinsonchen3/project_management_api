import pytest
from unittest.mock import AsyncMock, patch

from app.services.user_service import UserService
from app.db.models.user import User
from app.core.exceptions import (
    UserNotFoundError,
    DuplicateEmailError,
    DuplicateUsernameError,
)


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def user_service(user_repo):
    return UserService(user_repo)


@pytest.fixture
def user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="old-hash",
    )


# ============================================================
# create_user
# ============================================================

@pytest.mark.anyio
async def test_create_user(user_service, user_repo):
    user_repo.exists_by_username.return_value = False
    user_repo.exists_by_email.return_value = False

    with patch(
        "app.services.user_service.hash_password",
        return_value="new-hash",
    ) as mock_hash:
        await user_service.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
        )

    mock_hash.assert_called_once_with("password123")

    user_repo.create.assert_awaited_once_with(
        username="testuser",
        email="test@example.com",
        hashed_password="new-hash",
    )


@pytest.mark.anyio
async def test_create_user_duplicate_username(
    user_service,
    user_repo,
):
    user_repo.exists_by_username.return_value = True

    with pytest.raises(DuplicateUsernameError):
        await user_service.create_user(
            username="existing",
            email="test@example.com",
            password="password123",
        )

    user_repo.create.assert_not_awaited()
    user_repo.exists_by_email.assert_not_awaited()


@pytest.mark.anyio
async def test_create_user_duplicate_email(
    user_service,
    user_repo,
):
    user_repo.exists_by_username.return_value = False
    user_repo.exists_by_email.return_value = True

    with pytest.raises(DuplicateEmailError):
        await user_service.create_user(
            username="testuser",
            email="existing@example.com",
            password="password123",
        )

    user_repo.create.assert_not_awaited()


# ============================================================
# get_user
# ============================================================

@pytest.mark.anyio
async def test_get_user(user_service, user_repo, user):
    user_repo.get_by_id.return_value = user

    result = await user_service.get_user(1)

    assert result is user
    user_repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.anyio
async def test_get_user_not_found(user_service, user_repo):
    user_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await user_service.get_user(999)


# ============================================================
# get_users / get_user_by_email
# ============================================================

@pytest.mark.anyio
async def test_get_user_by_email(user_service, user_repo, user):
    user_repo.get_by_email.return_value = user

    result = await user_service.get_user_by_email(
        "test@example.com"
    )

    assert result is user


@pytest.mark.anyio
async def test_get_users(user_service, user_repo):
    users = [User(id=1), User(id=2)]
    user_repo.get_all.return_value = users

    result = await user_service.get_users(offset=10, limit=20)

    assert result == users
    user_repo.get_all.assert_awaited_once_with(
        offset=10,
        limit=20,
    )


# ============================================================
# update_user
# ============================================================

@pytest.mark.anyio
async def test_update_user(
    user_service,
    user_repo,
    user,
):
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = None
    user_repo.update.return_value = user

    with patch(
        "app.services.user_service.hash_password",
        return_value="new-hash",
    ):
        result = await user_service.update_user(
            current_user=user,
            username="newname",
            email="new@example.com",
            password="newpassword",
        )

    assert result is user
    assert user.username == "newname"
    assert user.email == "new@example.com"
    assert user.hashed_password == "new-hash"

    user_repo.update.assert_awaited_once_with(user)


@pytest.mark.anyio
async def test_update_user_duplicate_username(
    user_service,
    user_repo,
    user,
):
    other_user = User(id=2, username="taken")

    user_repo.get_by_username.return_value = other_user

    with pytest.raises(DuplicateUsernameError):
        await user_service.update_user(
            current_user=user,
            username="taken",
        )

    user_repo.update.assert_not_awaited()


@pytest.mark.anyio
async def test_update_user_duplicate_email(
    user_service,
    user_repo,
    user,
):
    other_user = User(id=2, email="taken@example.com")

    user_repo.get_by_email.return_value = other_user

    with pytest.raises(DuplicateEmailError):
        await user_service.update_user(
            current_user=user,
            email="taken@example.com",
        )

    user_repo.update.assert_not_awaited()


# ============================================================
# update_password
# ============================================================

@pytest.mark.anyio
async def test_update_password(
    user_service,
    user_repo,
    user,
):
    user_repo.update.return_value = user

    with patch(
        "app.services.user_service.hash_password",
        return_value="new-hash",
    ) as mock_hash:
        result = await user_service.update_password(
            current_user=user,
            password="newpassword",
        )

    assert result is user
    assert user.hashed_password == "new-hash"

    mock_hash.assert_called_once_with("newpassword")
    user_repo.update.assert_awaited_once_with(user)


# ============================================================
# delete_user
# ============================================================

@pytest.mark.anyio
async def test_delete_user(user_service, user_repo, user):
    result = await user_service.delete_user(user)

    assert result is None
    user_repo.delete.assert_awaited_once_with(user)