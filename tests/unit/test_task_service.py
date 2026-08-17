import pytest
from unittest.mock import AsyncMock

from app.services.task_service import TaskService
from app.db.enums import TaskStatus
from app.db.models.task import Task
from app.db.models.user import User
from app.db.models.project import Project
from app.core.exceptions import (
    TaskNotFoundError,
    ProjectNotFoundError,
    UserNotFoundError,
    PermissionDeniedError,
    UserNotInProjectError,
)


@pytest.fixture
def task_repo():
    return AsyncMock()


@pytest.fixture
def project_repo():
    return AsyncMock()


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def task_service(task_repo, project_repo, user_repo):
    return TaskService(task_repo, project_repo, user_repo)


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
        owner_id=owner.id,
    )
    project.members = [owner, member]
    return project


@pytest.fixture
def task(project):
    task = Task(
        id=1,
        title="Test Task",
        description="Test description",
        status=TaskStatus.TO_DO,
        project_id=project.id,
    )
    task.project = project
    task.assignees = []
    task.comments = []
    return task


# ============================================================
# create_task
# ============================================================

@pytest.mark.anyio
async def test_create_task(
    task_service,
    project_repo,
    task_repo,
    project,
    member,
):
    created_task = Task(id=1, title="Test Task")
    project_repo.get_by_id_with_members.return_value = project
    task_repo.create.return_value = created_task

    result = await task_service.create_task(
        current_user=member,
        title="Test Task",
        description="Description",
        project_id=1,
    )

    assert result is created_task

    task_repo.create.assert_awaited_once_with(
        title="Test Task",
        description="Description",
        status=TaskStatus.TO_DO,
        project_id=1,
    )


@pytest.mark.anyio
async def test_create_task_project_not_found(
    task_service,
    project_repo,
    member,
):
    project_repo.get_by_id_with_members.return_value = None

    with pytest.raises(ProjectNotFoundError):
        await task_service.create_task(
            member,
            "Test Task",
            None,
            999,
        )


@pytest.mark.anyio
async def test_create_task_non_member_denied(
    task_service,
    project_repo,
    project,
):
    non_member = User(id=3)
    project_repo.get_by_id_with_members.return_value = project

    with pytest.raises(PermissionDeniedError):
        await task_service.create_task(
            non_member,
            "Test Task",
            None,
            project.id,
        )

    task_service.task_repo.create.assert_not_awaited()


# ============================================================
# update_task
# ============================================================

@pytest.mark.anyio
async def test_update_task(
    task_service,
    task_repo,
    task,
    member,
):
    task_repo.get_by_id_with_project_members.return_value = task
    task_repo.update.return_value = task

    result = await task_service.update_task(
        current_user=member,
        task_id=task.id,
        title="Updated",
        description="Updated description",
        status=TaskStatus.COMPLETED,
    )

    assert result is task
    assert task.title == "Updated"
    assert task.description == "Updated description"
    assert task.status == TaskStatus.COMPLETED

    task_repo.update.assert_awaited_once_with(task)


@pytest.mark.anyio
async def test_update_task_not_found(
    task_service,
    task_repo,
    member,
):
    task_repo.get_by_id_with_project_members.return_value = None

    with pytest.raises(TaskNotFoundError):
        await task_service.update_task(
            member,
            999,
            title="Updated",
        )


@pytest.mark.anyio
async def test_update_task_non_member_denied(
    task_service,
    task_repo,
    task,
):
    non_member = User(id=3)
    task_repo.get_by_id_with_project_members.return_value = task

    with pytest.raises(PermissionDeniedError):
        await task_service.update_task(
            non_member,
            task.id,
            title="Updated",
        )

    task_repo.update.assert_not_awaited()


# ============================================================
# delete_task
# ============================================================

@pytest.mark.anyio
async def test_delete_task(
    task_service,
    task_repo,
    task,
    member,
):
    task_repo.get_by_id_with_project_members.return_value = task

    result = await task_service.delete_task(
        member,
        task.id,
    )

    assert result is None
    task_repo.delete.assert_awaited_once_with(task)


# ============================================================
# assign_user
# ============================================================

@pytest.mark.anyio
async def test_assign_user(
    task_service,
    task_repo,
    user_repo,
    task,
    member,
):
    assignee = User(id=3, username="assignee")
    task.project.members.append(assignee)

    task_repo.get_by_id_with_assignees.return_value = task
    user_repo.get_by_id.return_value = assignee
    task_repo.update.return_value = task

    result = await task_service.assign_user(
        current_user=member,
        task_id=task.id,
        user_id=assignee.id,
    )

    assert result is task
    assert assignee in task.assignees

    task_repo.update.assert_awaited_once_with(task)


@pytest.mark.anyio
async def test_assign_user_not_in_project(
    task_service,
    task_repo,
    user_repo,
    task,
    member,
):
    user = User(id=3, username="outsider")

    task_repo.get_by_id_with_assignees.return_value = task
    user_repo.get_by_id.return_value = user

    with pytest.raises(UserNotInProjectError):
        await task_service.assign_user(
            member,
            task.id,
            user.id,
        )

    task_repo.update.assert_not_awaited()


@pytest.mark.anyio
async def test_assign_user_not_found(
    task_service,
    task_repo,
    user_repo,
    task,
    member,
):
    task_repo.get_by_id_with_assignees.return_value = task
    user_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await task_service.assign_user(
            member,
            task.id,
            999,
        )


# ============================================================
# remove_assignee
# ============================================================

@pytest.mark.anyio
async def test_remove_assignee(
    task_service,
    task_repo,
    user_repo,
    task,
    member,
):
    assignee = User(id=3, username="assignee")
    task.assignees.append(assignee)

    task_repo.get_by_id_with_assignees.return_value = task
    user_repo.get_by_id.return_value = assignee
    task_repo.update.return_value = task

    result = await task_service.remove_assignee(
        member,
        task.id,
        assignee.id,
    )

    assert result is task
    assert assignee not in task.assignees

    task_repo.update.assert_awaited_once_with(task)


# ============================================================
# get_task / get_comments / get_assignees
# ============================================================

@pytest.mark.anyio
async def test_get_task(
    task_service,
    task_repo,
    task,
    member,
):
    task_repo.get_by_id_detailed.return_value = task

    result = await task_service.get_task(
        member,
        task.id,
    )

    assert result is task


@pytest.mark.anyio
async def test_get_comments(
    task_service,
    task_repo,
    task,
    member,
):
    comments = []
    task.comments = comments
    task_repo.get_by_id_detailed.return_value = task

    result = await task_service.get_comments(
        member,
        task.id,
    )

    assert result == comments


@pytest.mark.anyio
async def test_get_assignees(
    task_service,
    task_repo,
    task,
    member,
):
    assignees = []
    task.assignees = assignees
    task_repo.get_by_id_with_assignees.return_value = task

    result = await task_service.get_assignees(
        member,
        task.id,
    )

    assert result == assignees