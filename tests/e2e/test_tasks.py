import pytest
from httpx import AsyncClient

from tests.conftest import (
    create_test_user,
    login_user,
    auth_header,
)

BASE_URL = "/api/v1"


async def create_project(
    client: AsyncClient,
    token: str,
) -> dict:
    response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={
            "name": "Test Project",
            "description": "Test project",
        },
    )

    assert response.status_code == 201
    return response.json()


async def create_task(
    client: AsyncClient,
    token: str,
    project_id: int,
) -> dict:
    response = await client.post(
        f"{BASE_URL}/projects/{project_id}/tasks",
        headers=auth_header(token),
        json={
            "title": "Test Task",
            "description": "Test description",
        },
    )

    assert response.status_code == 201
    return response.json()


# ============================================================
# get
# ============================================================


@pytest.mark.anyio
async def test_get_task(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    response = await client.get(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == task["id"]
    assert response.json()["title"] == "Test Task"


@pytest.mark.anyio
async def test_get_nonexistent_task(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.get(
        f"{BASE_URL}/tasks/999999",
        headers=auth_header(token),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_non_member_cannot_get_task(
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

    project = await create_project(client, owner_token)
    task = await create_task(client, owner_token, project["id"])

    await create_test_user(
        client,
        username="outsider",
        email="outsider@example.com",
    )
    outsider_token = await login_user(
        client,
        email="outsider@example.com",
    )

    response = await client.get(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(outsider_token),
    )

    assert response.status_code == 403


# ============================================================
# update
# ============================================================


@pytest.mark.anyio
async def test_update_task(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    response = await client.patch(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(token),
        json={
            "title": "Updated Task",
            "description": "Updated description",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["description"] == "Updated description"


@pytest.mark.anyio
async def test_update_nonexistent_task(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        f"{BASE_URL}/tasks/999999",
        headers=auth_header(token),
        json={"title": "Updated"},
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_non_member_cannot_update_task(
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

    project = await create_project(client, owner_token)
    task = await create_task(client, owner_token, project["id"])

    await create_test_user(
        client,
        username="outsider",
        email="outsider@example.com",
    )
    outsider_token = await login_user(
        client,
        email="outsider@example.com",
    )

    response = await client.patch(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(outsider_token),
        json={"title": "Hacked"},
    )

    assert response.status_code == 403


# ============================================================
# delete
# ============================================================


@pytest.mark.anyio
async def test_delete_task(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    response = await client.delete(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(token),
    )

    assert response.status_code == 204

    response = await client.get(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(token),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_nonexistent_task(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.delete(
        f"{BASE_URL}/tasks/999999",
        headers=auth_header(token),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_non_member_cannot_delete_task(
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

    project = await create_project(client, owner_token)
    task = await create_task(client, owner_token, project["id"])

    await create_test_user(
        client,
        username="outsider",
        email="outsider@example.com",
    )
    outsider_token = await login_user(
        client,
        email="outsider@example.com",
    )

    response = await client.delete(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(outsider_token),
    )

    assert response.status_code == 403


# ============================================================
# assignees
# ============================================================


@pytest.mark.anyio
async def test_assign_and_remove_assignee(
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

    project = await create_project(client, owner_token)
    task = await create_task(client, owner_token, project["id"])

    member = await create_test_user(
        client,
        username="member",
        email="member@example.com",
    )

    response = await client.post(
        f"{BASE_URL}/projects/{project['id']}/members",
        headers=auth_header(owner_token),
        params={"user_id": member["id"]},
    )
    assert response.status_code == 200

    # Assign
    response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/assignees",
        headers=auth_header(owner_token),
        json={"user_id": member["id"]},
    )

    assert response.status_code == 200

    # Verify assignment
    response = await client.get(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(owner_token),
    )

    assert response.status_code == 200
    assert any(user["id"] == member["id"] for user in response.json()["assignees"])

    # Remove
    response = await client.delete(
        f"{BASE_URL}/tasks/{task['id']}/assignees/{member['id']}",
        headers=auth_header(owner_token),
    )

    assert response.status_code == 200

    # Verify removal
    response = await client.get(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(owner_token),
    )

    assert response.status_code == 200
    assert all(user["id"] != member["id"] for user in response.json()["assignees"])


@pytest.mark.anyio
async def test_cannot_assign_non_project_member(
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

    project = await create_project(client, owner_token)
    task = await create_task(client, owner_token, project["id"])

    outsider = await create_test_user(
        client,
        username="outsider",
        email="outsider@example.com",
    )

    response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/assignees",
        headers=auth_header(owner_token),
        json={"user_id": outsider["id"]},
    )

    assert response.status_code == 403


@pytest.mark.anyio
async def test_assign_nonexistent_user(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/assignees",
        headers=auth_header(token),
        json={"user_id": 999999},
    )

    assert response.status_code == 404


# ============================================================
# comments
# ============================================================


@pytest.mark.anyio
async def test_create_and_get_comments(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/comments",
        headers=auth_header(token),
        json={"content": "Test comment"},
    )

    assert response.status_code == 201
    comment = response.json()

    assert comment["content"] == "Test comment"

    response = await client.get(
        f"{BASE_URL}/tasks/{task['id']}/comments",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    comments = response.json()
    assert len(comments) == 1
    assert comments[0]["id"] == comment["id"]


@pytest.mark.anyio
async def test_non_member_cannot_create_comment(
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

    project = await create_project(client, owner_token)
    task = await create_task(client, owner_token, project["id"])

    await create_test_user(
        client,
        username="outsider",
        email="outsider@example.com",
    )
    outsider_token = await login_user(
        client,
        email="outsider@example.com",
    )

    response = await client.post(
        f"{BASE_URL}/tasks/{task['id']}/comments",
        headers=auth_header(outsider_token),
        json={"content": "Unauthorized comment"},
    )

    assert response.status_code == 403


# ============================================================
# validation
# ============================================================


@pytest.mark.anyio
async def test_update_task_invalid_data(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    project = await create_project(client, token)
    task = await create_task(client, token, project["id"])

    response = await client.patch(
        f"{BASE_URL}/tasks/{task['id']}",
        headers=auth_header(token),
        json={
            "title": "",
        },
    )

    assert response.status_code == 422
