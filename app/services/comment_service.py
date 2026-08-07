from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository

from app.db.models.comment import Comment
from app.db.models.project import Project
from app.db.models.user import User

from app.core.exceptions import (
    CommentNotFoundError,
    TaskNotFoundError,
    UserNotFoundError,
    PermissionDeniedError,
)


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        task_repo: TaskRepository,
    ):
        self.comment_repo = comment_repo
        self.task_repo = task_repo

    async def create_comment(
        self,
        current_user: User,
        content: str,
        task_id: int,
    ) -> Comment:
        task = await self.task_repo.get_by_id_with_project_members(task_id)

        if task is None:
            raise TaskNotFoundError(task_id=task_id)

        await self._require_project_member(task.project, current_user)

        return await self.comment_repo.create(
            content=content,
            author_id=current_user.id,
            task_id=task_id,
        )

    async def get_comment(
        self,
        current_user: User,
        comment_id: int,
    ) -> Comment:
        comment = await self.comment_repo.get_by_id_with_task_project_members(
            comment_id
        )

        if comment is None:
            raise CommentNotFoundError(comment_id=comment_id)

        await self._require_project_member(comment.task.project, current_user)

        return comment

    async def get_comment_detailed(
        self,
        current_user: User,
        comment_id: int,
    ) -> Comment:
        comment = await self.comment_repo.get_by_id_detailed(comment_id)

        if comment is None:
            raise CommentNotFoundError(comment_id=comment_id)

        await self._require_project_member(comment.task.project, current_user)

        return comment

    async def get_task_comments(
        self,
        current_user: User,
        task_id: int,
    ) -> list[Comment]:
        task = await self.task_repo.get_by_id_with_project_members(task_id)

        if task is None:
            raise TaskNotFoundError(task_id=task_id)

        await self._require_project_member(task.project, current_user)

        return await self.comment_repo.get_task_comments(task_id)

    async def get_task_comments_detailed(
        self,
        current_user: User,
        task_id: int,
    ) -> list[Comment]:
        task = await self.task_repo.get_by_id_with_project_members(task_id)

        if task is None:
            raise TaskNotFoundError(task_id=task_id)

        await self._require_project_member(task.project, current_user)

        return await self.comment_repo.get_task_comments_with_authors(task_id)

    async def update_comment(
        self,
        current_user: User,
        comment_id: int,
        content: str,
    ) -> Comment:
        comment = await self.comment_repo.get_by_id_with_task_project_members(
            comment_id
        )

        if comment is None:
            raise CommentNotFoundError(comment_id=comment_id)

        await self._require_project_member(comment.task.project, current_user)

        if comment.author_id != current_user.id:
            raise PermissionDeniedError()

        comment.content = content

        return await self.comment_repo.update(comment)

    async def delete_comment(
        self,
        current_user: User,
        comment_id: int,
    ) -> None:
        comment = await self.comment_repo.get_by_id_with_task_project_members(
            comment_id
        )

        if comment is None:
            raise CommentNotFoundError(comment_id=comment_id)

        await self._require_project_member(comment.task.project, current_user)

        if comment.author_id != current_user.id:
            raise PermissionDeniedError()

        await self.comment_repo.delete(comment)

    async def _require_project_member(
        self,
        project: Project,
        current_user: User,
    ) -> None:
        if project.owner_id != current_user.id and current_user not in project.members:
            raise PermissionDeniedError()
