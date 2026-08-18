import pytest
from tests.conftest import create_test_user, login_user, auth_header

# ============================================================
# register
# ============================================================


@pytest.mark.anyio
async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data
    assert "password" not in data


@pytest.mark.anyio
async def test_register_duplicate_username(client):
    await create_test_user(
        client,
        username="existinguser",
        email="first@example.com",
    )

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "existinguser",
            "email": "second@example.com",
            "password": "password123",
        },
    )

    print(response.status_code)
    print(response.json())

    assert response.status_code == 409
    assert response.json()["detail"] == ("Username 'existinguser' is already in use.")


@pytest.mark.anyio
async def test_register_duplicate_email(client):
    await create_test_user(
        client,
        username="firstuser",
        email="existing@example.com",
    )

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "seconduser",
            "email": "existing@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Email 'existing@example.com' is already in use."
    )


# ============================================================
# login
# ============================================================


@pytest.mark.anyio
async def test_login_success(client):
    await create_test_user(
        client,
        email="login@example.com",
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)


@pytest.mark.anyio
async def test_login_wrong_password(client):
    await create_test_user(
        client,
        email="login@example.com",
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == ("Invalid email or password.")


@pytest.mark.anyio
async def test_login_nonexistent_user(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == ("Invalid email or password.")


# ============================================================
# validation
# ============================================================


@pytest.mark.anyio
async def test_register_invalid_data(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "",
            "email": "not-an-email",
            "password": "",
        },
    )

    assert response.status_code == 422
