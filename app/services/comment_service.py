from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository

from app.db.models.comment import Comment

from app.core.exceptions import (
    CommentNotFoundError,
    TaskNotFoundError,
    UserNotFoundError,
)


class CommentService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.comment_repository = CommentRepository(db)
        self.task_repository = TaskRepository(db)
        self.user_repository = UserRepository(db)


    async def create_comment(
        self,
        content: str,
        author_id: int,
        task_id: int,
    ) -> Comment:

        # Verify author exists
        author = await self.user_repository.get_by_id(author_id)

        if not author:
            raise UserNotFoundError()


        # Verify task exists
        task = await self.task_repository.get_by_id(task_id)

        if not task:
            raise TaskNotFoundError()


        return await self.comment_repository.create(
            content=content,
            author_id=author_id,
            task_id=task_id,
        )


    async def get_comment(
        self,
        comment_id: int,
    ) -> Comment:

        comment = await self.comment_repository.get_by_id(
            comment_id
        )

        if not comment:
            raise CommentNotFoundError()

        return comment


    async def get_comment_detailed(
        self,
        comment_id: int,
    ) -> Comment:

        comment = await self.comment_repository.get_by_id_with_author(
            comment_id
        )

        if not comment:
            raise CommentNotFoundError()

        return comment


    async def get_task_comments(
        self,
        task_id: int,
    ) -> list[Comment]:

        # Make sure task exists
        task = await self.task_repository.get_by_id(task_id)

        if not task:
            raise TaskNotFoundError()


        return await self.comment_repository.get_task_comments(
            task_id
        )


    async def get_task_comments_detailed(
        self,
        task_id: int,
    ) -> list[Comment]:

        task = await self.task_repository.get_by_id(task_id)

        if not task:
            raise TaskNotFoundError()


        return await self.comment_repository.get_task_comments_with_authors(
            task_id
        )


    async def get_user_comments(
        self,
        user_id: int,
    ) -> list[Comment]:

        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()


        return await self.comment_repository.get_by_author(
            user_id
        )


    async def update_comment(
        self,
        comment_id: int,
        content: str,
        user_id: int,
    ) -> Comment:

        comment = await self.comment_repository.get_by_id(
            comment_id
        )

        if not comment:
            raise CommentNotFoundError()


        # Authorization check
        if comment.author_id != user_id:
            raise PermissionError(
                "You cannot edit this comment"
            )


        comment.content = content

        return await self.comment_repository.update(
            comment
        )


    async def delete_comment(
        self,
        comment_id: int,
        user_id: int,
    ) -> None:

        comment = await self.comment_repository.get_by_id(
            comment_id
        )

        if not comment:
            raise CommentNotFoundError()


        # Authorization check
        if comment.author_id != user_id:
            raise PermissionError(
                "You cannot delete this comment"
            )


        await self.comment_repository.delete(comment)