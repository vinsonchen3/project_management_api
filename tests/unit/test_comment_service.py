import pytest
from unittest.mock import AsyncMock

from app.services.comment_service import CommentService
from app.db.models.comment import Comment
from app.db.models.project import Project
from app.db.models.task import Task
from app.db.models.user import User
from app.core.exceptions import (
    CommentNotFoundError,
    TaskNotFoundError,
    PermissionDeniedError,
)


@pytest.fixture
def comment_repo():
    return AsyncMock()


@pytest.fixture
def task_repo():
    return AsyncMock()


@pytest.fixture
def comment_service(comment_repo, task_repo):
    return CommentService(comment_repo, task_repo)


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
        project_id=project.id,
    )
    task.project = project
    return task


@pytest.fixture
def comment(task, owner):
    comment = Comment(
        id=1,
        content="Original comment",
        author_id=owner.id,
        task_id=task.id,
    )
    comment.task = task
    return comment


# ============================================================
# create_comment
# ============================================================

@pytest.mark.anyio
async def test_create_comment(
    comment_service,
    task_repo,
    comment_repo,
    task,
    member,
):
    created_comment = Comment(id=1, content="Hello")
    task_repo.get_by_id_with_project_members.return_value = task
    comment_repo.create.return_value = created_comment

    result = await comment_service.create_comment(
        current_user=member,
        content="Hello",
        task_id=task.id,
    )

    assert result is created_comment

    comment_repo.create.assert_awaited_once_with(
        content="Hello",
        author_id=member.id,
        task_id=task.id,
    )


@pytest.mark.anyio
async def test_create_comment_task_not_found(
    comment_service,
    task_repo,
    member,
):
    task_repo.get_by_id_with_project_members.return_value = None

    with pytest.raises(TaskNotFoundError):
        await comment_service.create_comment(
            member,
            "Hello",
            999,
        )

    comment_service.comment_repo.create.assert_not_awaited()


@pytest.mark.anyio
async def test_create_comment_non_member_denied(
    comment_service,
    task_repo,
    task,
):
    non_member = User(id=3)
    task_repo.get_by_id_with_project_members.return_value = task

    with pytest.raises(PermissionDeniedError):
        await comment_service.create_comment(
            non_member,
            "Hello",
            task.id,
        )

    comment_service.comment_repo.create.assert_not_awaited()


# ============================================================
# get_comment
# ============================================================

@pytest.mark.anyio
async def test_get_comment(
    comment_service,
    comment_repo,
    comment,
    member,
):
    comment_repo.get_by_id_with_task_project_members.return_value = comment

    result = await comment_service.get_comment(
        member,
        comment.id,
    )

    assert result is comment


@pytest.mark.anyio
async def test_get_comment_not_found(
    comment_service,
    comment_repo,
    member,
):
    comment_repo.get_by_id_with_task_project_members.return_value = None

    with pytest.raises(CommentNotFoundError):
        await comment_service.get_comment(member, 999)


# ============================================================
# update_comment
# ============================================================

@pytest.mark.anyio
async def test_update_comment(
    comment_service,
    comment_repo,
    comment,
    owner,
):
    comment_repo.get_by_id_with_task_project_members.return_value = comment
    comment_repo.update.return_value = comment

    result = await comment_service.update_comment(
        current_user=owner,
        comment_id=comment.id,
        content="Updated comment",
    )

    assert result is comment
    assert comment.content == "Updated comment"

    comment_repo.update.assert_awaited_once_with(comment)


@pytest.mark.anyio
async def test_update_comment_non_author_denied(
    comment_service,
    comment_repo,
    comment,
    member,
):
    comment_repo.get_by_id_with_task_project_members.return_value = comment

    with pytest.raises(PermissionDeniedError):
        await comment_service.update_comment(
            member,
            comment.id,
            "Updated",
        )

    comment_repo.update.assert_not_awaited()


# ============================================================
# delete_comment
# ============================================================

@pytest.mark.anyio
async def test_delete_comment(
    comment_service,
    comment_repo,
    comment,
    owner,
):
    comment_repo.get_by_id_with_task_project_members.return_value = comment

    result = await comment_service.delete_comment(
        owner,
        comment.id,
    )

    assert result is None
    comment_repo.delete.assert_awaited_once_with(comment)


@pytest.mark.anyio
async def test_delete_comment_non_author_denied(
    comment_service,
    comment_repo,
    comment,
    member,
):
    comment_repo.get_by_id_with_task_project_members.return_value = comment

    with pytest.raises(PermissionDeniedError):
        await comment_service.delete_comment(
            member,
            comment.id,
        )

    comment_repo.delete.assert_not_awaited()


# ============================================================
# get_task_comments
# ============================================================

@pytest.mark.anyio
async def test_get_task_comments(
    comment_service,
    task_repo,
    comment_repo,
    task,
    member,
):
    comments = [Comment(id=1), Comment(id=2)]

    task_repo.get_by_id_with_project_members.return_value = task
    comment_repo.get_task_comments.return_value = comments

    result = await comment_service.get_task_comments(
        member,
        task.id,
    )

    assert result == comments

    comment_repo.get_task_comments.assert_awaited_once_with(task.id)