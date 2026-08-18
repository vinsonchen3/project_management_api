import pytest

from httpx import AsyncClient
from tests.conftest import create_test_user, login_user, auth_header

BASE_URL = "/api/v1"


# ============================================================
# GET /users/me
# ============================================================


@pytest.mark.anyio
async def test_get_me_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.get(
        f"{BASE_URL}/users/me",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user["id"]
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]


@pytest.mark.anyio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get(
        f"{BASE_URL}/users/me",
    )

    assert response.status_code == 401


# ============================================================
# PATCH /users/me
# ============================================================


@pytest.mark.anyio
async def test_update_me_username(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        f"{BASE_URL}/users/me",
        headers=auth_header(token),
        json={
            "username": "updateduser",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"


@pytest.mark.anyio
async def test_update_me_email(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        f"{BASE_URL}/users/me",
        headers=auth_header(token),
        json={
            "email": "new@example.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "new@example.com"


@pytest.mark.anyio
async def test_update_me_duplicate_username(client: AsyncClient):
    await create_test_user(
        client,
        username="user1",
        email="user1@example.com",
    )

    await create_test_user(
        client,
        username="user2",
        email="user2@example.com",
    )

    token = await login_user(
        client,
        email="user1@example.com",
    )

    response = await client.patch(
        f"{BASE_URL}/users/me",
        headers=auth_header(token),
        json={
            "username": "user2",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("Username 'user2' is already in use.")


@pytest.mark.anyio
async def test_update_me_duplicate_email(client: AsyncClient):
    await create_test_user(
        client,
        username="user1",
        email="user1@example.com",
    )

    await create_test_user(
        client,
        username="user2",
        email="user2@example.com",
    )

    token = await login_user(
        client,
        email="user1@example.com",
    )

    response = await client.patch(
        f"{BASE_URL}/users/me",
        headers=auth_header(token),
        json={
            "email": "user2@example.com",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("Email 'user2@example.com' is already in use.")


@pytest.mark.anyio
async def test_update_me_unauthorized(client: AsyncClient):
    response = await client.patch(
        f"{BASE_URL}/users/me",
        json={
            "username": "updateduser",
        },
    )

    assert response.status_code == 401


# ============================================================
# PATCH /users/change-password
# ============================================================


@pytest.mark.anyio
async def test_change_password_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        f"{BASE_URL}/users/change-password",
        headers=auth_header(token),
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 204

    # Old password should no longer work.
    old_login = await client.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )

    assert old_login.status_code == 401

    # New password should work.
    new_login = await client.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "newpassword123",
        },
    )

    assert new_login.status_code == 200


@pytest.mark.anyio
async def test_change_password_wrong_current_password(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        f"{BASE_URL}/users/change-password",
        headers=auth_header(token),
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == ("Invalid email or password.")


@pytest.mark.anyio
async def test_change_password_unauthorized(client: AsyncClient):
    response = await client.patch(
        f"{BASE_URL}/users/change-password",
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 401
