import pytest

from httpx import AsyncClient
from tests.conftest import create_test_user, login_user, auth_header

BASE_URL = "/api/v1"


# ============================================================
# PROJECT CRUD
# ============================================================


@pytest.mark.anyio
async def test_create_project(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={
            "name": "Test Project",
            "description": "Test description",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test description"


@pytest.mark.anyio
async def test_get_projects(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={"name": "Project 1"},
    )

    await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={"name": "Project 2"},
    )

    response = await client.get(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    projects = response.json()
    assert len(projects) == 2


@pytest.mark.anyio
async def test_get_project(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={"name": "Test Project"},
    )

    project_id = create_response.json()["id"]

    response = await client.get(
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == project_id


@pytest.mark.anyio
async def test_update_project(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={"name": "Old Name"},
    )

    project_id = create_response.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(token),
        json={"name": "New Name"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.anyio
async def test_delete_project(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={"name": "Delete Me"},
    )

    project_id = create_response.json()["id"]

    response = await client.delete(
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 204

    get_response = await client.get(
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(token),
    )

    assert get_response.status_code == 404


# ============================================================
# PROJECT PERMISSIONS
# ============================================================


@pytest.mark.anyio
async def test_non_member_cannot_access_project(
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

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(owner_token),
        json={"name": "Private Project"},
    )

    project_id = create_response.json()["id"]

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
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(outsider_token),
    )

    assert response.status_code == 403


@pytest.mark.anyio
async def test_member_can_access_project(
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

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(owner_token),
        json={"name": "Shared Project"},
    )

    project_id = create_response.json()["id"]

    member = await create_test_user(
        client,
        username="member",
        email="member@example.com",
    )

    member_id = member["id"]

    await client.post(
        f"{BASE_URL}/projects/{project_id}/members",
        headers=auth_header(owner_token),
        params={"user_id": member_id},
    )

    member_token = await login_user(
        client,
        email="member@example.com",
    )

    response = await client.get(
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(member_token),
    )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_member_cannot_update_project(
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

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(owner_token),
        json={"name": "Project"},
    )

    project_id = create_response.json()["id"]

    member = await create_test_user(
        client,
        username="member",
        email="member@example.com",
    )

    await client.post(
        f"{BASE_URL}/projects/{project_id}/members",
        headers=auth_header(owner_token),
        params={"user_id": member["id"]},
    )

    member_token = await login_user(
        client,
        email="member@example.com",
    )

    response = await client.patch(
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(member_token),
        json={"name": "Hacked"},
    )

    assert response.status_code == 403


# ============================================================
# MEMBERS
# ============================================================


@pytest.mark.anyio
async def test_add_and_get_member(
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

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(owner_token),
        json={"name": "Team Project"},
    )

    project_id = create_response.json()["id"]

    member = await create_test_user(
        client,
        username="member",
        email="member@example.com",
    )

    response = await client.post(
        f"{BASE_URL}/projects/{project_id}/members",
        headers=auth_header(owner_token),
        params={"user_id": member["id"]},
    )

    assert response.status_code == 200

    members_response = await client.get(
        f"{BASE_URL}/projects/{project_id}/members",
        headers=auth_header(owner_token),
    )

    assert members_response.status_code == 200

    member_ids = {user["id"] for user in members_response.json()}

    assert member["id"] in member_ids


@pytest.mark.anyio
async def test_remove_member(
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

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(owner_token),
        json={"name": "Team Project"},
    )

    project_id = create_response.json()["id"]

    member = await create_test_user(
        client,
        username="member",
        email="member@example.com",
    )

    await client.post(
        f"{BASE_URL}/projects/{project_id}/members",
        headers=auth_header(owner_token),
        params={"user_id": member["id"]},
    )

    response = await client.delete(
        f"{BASE_URL}/projects/{project_id}/members/{member['id']}",
        headers=auth_header(owner_token),
    )

    assert response.status_code == 200

    member_token = await login_user(
        client,
        email="member@example.com",
    )

    project_response = await client.get(
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(member_token),
    )

    assert project_response.status_code == 403


@pytest.mark.anyio
async def test_member_can_leave_project(
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

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(owner_token),
        json={"name": "Team Project"},
    )

    project_id = create_response.json()["id"]

    member = await create_test_user(
        client,
        username="member",
        email="member@example.com",
    )

    await client.post(
        f"{BASE_URL}/projects/{project_id}/members",
        headers=auth_header(owner_token),
        params={"user_id": member["id"]},
    )

    member_token = await login_user(
        client,
        email="member@example.com",
    )

    response = await client.delete(
        f"{BASE_URL}/projects/{project_id}/members/me",
        headers=auth_header(member_token),
    )

    assert response.status_code == 204

    project_response = await client.get(
        f"{BASE_URL}/projects/{project_id}",
        headers=auth_header(member_token),
    )

    assert project_response.status_code == 403


@pytest.mark.anyio
async def test_owner_cannot_leave_project(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    create_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={"name": "Project"},
    )

    project_id = create_response.json()["id"]

    response = await client.delete(
        f"{BASE_URL}/projects/{project_id}/members/me",
        headers=auth_header(token),
    )

    assert response.status_code == 403


# ============================================================
# TASKS THROUGH PROJECT ROUTES
# ============================================================


@pytest.mark.anyio
async def test_create_and_get_project_tasks(
    client: AsyncClient,
):
    await create_test_user(client)
    token = await login_user(client)

    project_response = await client.post(
        f"{BASE_URL}/projects/",
        headers=auth_header(token),
        json={"name": "Task Project"},
    )

    project_id = project_response.json()["id"]

    task_response = await client.post(
        f"{BASE_URL}/projects/{project_id}/tasks",
        headers=auth_header(token),
        json={
            "title": "Test Task",
            "description": "Task description",
        },
    )

    assert task_response.status_code == 201

    task = task_response.json()
    assert task["title"] == "Test Task"
    assert task["project_id"] == project_id

    response = await client.get(
        f"{BASE_URL}/projects/{project_id}/tasks",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
