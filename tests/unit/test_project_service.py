import pytest
from unittest.mock import AsyncMock

from app.services.project_service import ProjectService
from app.db.models.project import Project
from app.db.models.user import User
from app.core.exceptions import (
    ProjectNotFoundError,
    UserNotFoundError,
    PermissionDeniedError,
)


@pytest.fixture
def project_repo():
    return AsyncMock()


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def project_service(project_repo, user_repo):
    return ProjectService(project_repo, user_repo)


@pytest.fixture
def owner():
    return User(
        id=1,
        username="owner",
        email="owner@example.com",
        hashed_password="hash",
    )


@pytest.fixture
def member():
    return User(
        id=2,
        username="member",
        email="member@example.com",
        hashed_password="hash",
    )


@pytest.fixture
def project(owner, member):
    project = Project(
        id=1,
        name="Test Project",
        description="Test description",
        owner_id=owner.id,
    )
    project.members = [owner, member]
    return project


# ============================================================
# create / get
# ============================================================

@pytest.mark.anyio
async def test_create_project(
    project_service,
    project_repo,
    owner,
):
    project = Project(id=1, name="Test Project")
    project_repo.create.return_value = project

    result = await project_service.create_project(
        current_user=owner,
        name="Test Project",
        description="Description",
    )

    assert result is project

    project_repo.create.assert_awaited_once_with(
        name="Test Project",
        description="Description",
        owner=owner,
    )


@pytest.mark.anyio
async def test_get_project_success(
    project_service,
    project_repo,
    project,
    member,
):
    project_repo.get_by_id_detailed.return_value = project

    result = await project_service.get_project(
        current_user=member,
        project_id=1,
    )

    assert result is project


@pytest.mark.anyio
async def test_get_project_not_found(
    project_service,
    project_repo,
    member,
):
    project_repo.get_by_id_detailed.return_value = None

    with pytest.raises(ProjectNotFoundError):
        await project_service.get_project(member, 999)


@pytest.mark.anyio
async def test_get_project_non_member_denied(
    project_service,
    project_repo,
    project,
):
    non_member = User(id=3)
    project_repo.get_by_id_detailed.return_value = project

    with pytest.raises(PermissionDeniedError):
        await project_service.get_project(
            non_member,
            project.id,
        )


@pytest.mark.anyio
async def test_get_projects(
    project_service,
    project_repo,
    owner,
):
    projects = [Project(id=1), Project(id=2)]
    project_repo.get_for_user.return_value = projects

    result = await project_service.get_projects(owner)

    assert result == projects
    project_repo.get_for_user.assert_awaited_once_with(owner.id)


# ============================================================
# update / delete
# ============================================================

@pytest.mark.anyio
async def test_update_project(
    project_service,
    project_repo,
    project,
    owner,
):
    project_repo.get_by_id.return_value = project
    project_repo.update.return_value = project

    result = await project_service.update_project(
        current_user=owner,
        project_id=1,
        name="New Name",
        description="New Description",
    )

    assert result is project
    assert project.name == "New Name"
    assert project.description == "New Description"

    project_repo.update.assert_awaited_once_with(project)


@pytest.mark.anyio
async def test_update_project_non_owner_denied(
    project_service,
    project_repo,
    project,
    member,
):
    project_repo.get_by_id.return_value = project

    with pytest.raises(PermissionDeniedError):
        await project_service.update_project(
            current_user=member,
            project_id=1,
            name="New Name",
            description=None,
        )

    project_repo.update.assert_not_awaited()


@pytest.mark.anyio
async def test_delete_project_success(
    project_service,
    project_repo,
    project,
    owner,
):
    project_repo.get_by_id.return_value = project

    result = await project_service.delete_project(
        current_user=owner,
        project_id=1,
    )

    assert result is None
    project_repo.delete.assert_awaited_once_with(project)


# ============================================================
# members
# ============================================================

@pytest.mark.anyio
async def test_add_member(
    project_service,
    project_repo,
    user_repo,
    project,
    owner,
):
    new_user = User(id=3, username="newuser")
    user_repo.get_by_id.return_value = new_user
    project_repo.get_by_id_with_members.return_value = project
    project_repo.update.return_value = project

    result = await project_service.add_member(
        current_user=owner,
        project_id=1,
        user_id=3,
    )

    assert result is project
    assert new_user in project.members
    project_repo.update.assert_awaited_once_with(project)


@pytest.mark.anyio
async def test_add_member_user_not_found(
    project_service,
    project_repo,
    user_repo,
    project,
    owner,
):
    project_repo.get_by_id_with_members.return_value = project
    user_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await project_service.add_member(
            owner,
            project.id,
            999,
        )

    project_repo.update.assert_not_awaited()


@pytest.mark.anyio
async def test_remove_member(
    project_service,
    project_repo,
    user_repo,
    project,
    owner,
    member,
):
    project_repo.get_by_id_with_members.return_value = project
    project_repo.update.return_value = project
    user_repo.get_by_id.return_value = member

    result = await project_service.remove_member(
        owner,
        project.id,
        member.id,
    )

    assert result is project
    assert member not in project.members
    project_repo.update.assert_awaited_once_with(project)


@pytest.mark.anyio
async def test_leave_project(
    project_service,
    project_repo,
    project,
    member,
):
    project_repo.get_by_id_with_members.return_value = project

    result = await project_service.leave_project(
        member,
        project.id,
    )

    assert result is None
    assert member not in project.members
    project_repo.update.assert_awaited_once_with(project)


@pytest.mark.anyio
async def test_owner_cannot_leave_project(
    project_service,
    project_repo,
    project,
    owner,
):
    project_repo.get_by_id_with_members.return_value = project

    with pytest.raises(PermissionDeniedError):
        await project_service.leave_project(
            owner,
            project.id,
        )

    project_repo.update.assert_not_awaited()


# ============================================================
# members / tasks access
# ============================================================

@pytest.mark.anyio
async def test_get_members(
    project_service,
    project_repo,
    project,
    member,
):
    project_repo.get_by_id_with_members.return_value = project

    result = await project_service.get_members(
        member,
        project.id,
    )

    assert result == project.members


@pytest.mark.anyio
async def test_get_tasks(
    project_service,
    project_repo,
    project,
    member,
):
    tasks = []
    project.tasks = tasks
    project_repo.get_by_id_detailed.return_value = project

    result = await project_service.get_tasks(
        member,
        project.id,
    )

    assert result == tasks