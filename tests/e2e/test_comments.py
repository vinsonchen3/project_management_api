import pytest
from httpx import AsyncClient
from tests.conftest import create_test_user, login_user, auth_header, create_project, create_task

BASE_URL = "/api/v1"


@pytest.mark.anyio
async def test_get_comment(
    client: AsyncClient,
):
    await create_test_user(
        client,
        username="owner",
        email="owner@example.com",
    )
    token = await login_user(
        client,
        email="owner@example.com",
    )

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    create_response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/comments",
        headers=auth_header(token),
        json={"content": "Test comment"},
    )
    assert create_response.status_code == 201

    comment_id = create_response.json()["id"]

    response = await client.get(
        f"{BASE_URL}/comments/{comment_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == comment_id
    assert response.json()["content"] == "Test comment"


@pytest.mark.anyio
async def test_update_comment(
    client: AsyncClient,
):
    await create_test_user(
        client,
        username="owner",
        email="owner@example.com",
    )
    token = await login_user(
        client,
        email="owner@example.com",
    )

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    create_response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/comments",
        headers=auth_header(token),
        json={"content": "Original"},
    )
    comment_id = create_response.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/comments/{comment_id}",
        headers=auth_header(token),
        json={"content": "Updated"},
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Updated"


@pytest.mark.anyio
async def test_delete_comment(
    client: AsyncClient,
):
    await create_test_user(
        client,
        username="owner",
        email="owner@example.com",
    )
    token = await login_user(
        client,
        email="owner@example.com",
    )

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    create_response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/comments",
        headers=auth_header(token),
        json={"content": "Delete me"},
    )
    comment_id = create_response.json()["id"]

    response = await client.delete(
        f"{BASE_URL}/comments/{comment_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 204

    response = await client.get(
        f"{BASE_URL}/comments/{comment_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_non_author_cannot_update_or_delete_comment(
    client: AsyncClient,
):
    await create_test_user(
        client,
        username="owner",
        email="owner@example.com",
    )
    owner_token = await login_user(
        client,
        email="owner@example.com",
    )

    await create_test_user(
        client,
        username="other",
        email="other@example.com",
    )
    other_token = await login_user(
        client,
        email="other@example.com",
    )

    project = await create_project(client, owner_token)
    task = await create_task(client, owner_token, project["id"])

    create_response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/comments",
        headers=auth_header(owner_token),
        json={"content": "Original"},
    )
    comment_id = create_response.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/comments/{comment_id}",
        headers=auth_header(other_token),
        json={"content": "Hacked"},
    )
    assert response.status_code == 403

    response = await client.delete(
        f"{BASE_URL}/comments/{comment_id}",
        headers=auth_header(other_token),
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_non_member_cannot_access_comment(
    client: AsyncClient,
):
    await create_test_user(
        client,
        username="owner",
        email="owner@example.com",
    )
    owner_token = await login_user(
        client,
        email="owner@example.com",
    )

    await create_test_user(
        client,
        username="outsider",
        email="outsider@example.com",
    )
    outsider_token = await login_user(
        client,
        email="outsider@example.com",
    )

    project = await create_project(client, owner_token)
    task = await create_task(client, owner_token, project["id"])

    create_response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/comments",
        headers=auth_header(owner_token),
        json={"content": "Private comment"},
    )
    comment_id = create_response.json()["id"]

    response = await client.get(
        f"{BASE_URL}/comments/{comment_id}",
        headers=auth_header(outsider_token),
    )

    assert response.status_code == 403


@pytest.mark.anyio
async def test_comment_not_found(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.get(
        f"{BASE_URL}/comments/999999",
        headers=auth_header(token),
    )

    assert response.status_code == 404
